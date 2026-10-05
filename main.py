from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from docx import Document
from docx.shared import Pt
from pypdf import PdfReader

import io
import re
import html


app = FastAPI(title="Universal AI Resume Suite")


# ============================================================
# SKILL DATABASE
# ============================================================

SKILLS = [
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "rust",
    "php",
    "ruby",
    "kotlin",
    "swift",

    # Web
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "node",
    "express",
    "django",
    "flask",
    "fastapi",
    "rest api",
    "graphql",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "redis",
    "sqlite",
    "database",

    # Cloud / DevOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "jenkins",
    "git",
    "github",
    "gitlab",
    "ci/cd",

    # AI / Data
    "artificial intelligence",
    "ai",
    "machine learning",
    "deep learning",
    "data science",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "nlp",
    "natural language processing",
    "computer vision",

    # Engineering
    "autocad",
    "solidworks",
    "matlab",
    "embedded systems",
    "iot",
    "internet of things",
    "plc",
    "robotics",

    # Business
    "marketing",
    "sales",
    "finance",
    "accounting",
    "project management",
    "business analysis",
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "excel",
    "power bi",
    "tableau",

    # Pharmacy / Life Science
    "pharmacology",
    "pharmaceutics",
    "pharmaceutical",
    "clinical research",
    "clinical trials",
    "drug discovery",
    "quality control",
    "quality assurance",
    "gmp",
    "glp",
    "regulatory affairs",
    "medical coding",
    "pharmacovigilance"
]


# ============================================================
# SECTION DATABASE
# ============================================================

SECTION_NAMES = [
    "summary",
    "objective",
    "profile",
    "skills",
    "technical skills",
    "experience",
    "work experience",
    "employment",
    "internship",
    "education",
    "projects",
    "certifications",
    "certificates",
    "achievements",
    "awards",
    "publications",
    "languages",
    "interests"
]


# ============================================================
# TEXT UTILITIES
# ============================================================

def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def clean_text(text):
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(data):
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception:
        return ""

    pages = []

    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    return "\n".join(pages)


# ============================================================
# SKILL DETECTION
# ============================================================

def find_skills(text):

    normalized = normalize(text)

    found = []

    for skill in SKILLS:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(skill.lower())
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(set(found))


# ============================================================
# JOB DESCRIPTION KEYWORDS
# ============================================================

def extract_job_keywords(job_description):

    return find_skills(job_description)


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_sections(text):

    normalized = normalize(text)

    sections = {}

    for section in SECTION_NAMES:

        if section in normalized:
            sections[section] = True

    return sections


# ============================================================
# FORMAT ANALYZER
# ============================================================

def analyze_format(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    score = 100
    problems = []

    if len(text) < 300:
        score -= 25
        problems.append(
            "Very little readable text was detected."
        )

    if len(lines) < 10:
        score -= 15
        problems.append(
            "Resume may have insufficient structured content."
        )

    sections = detect_sections(text)

    section_groups = [
        ["summary", "objective", "profile"],
        ["skills", "technical skills"],
        [
            "experience",
            "work experience",
            "employment",
            "internship"
        ],
        ["education"]
    ]

    for group in section_groups:

        if not any(item in sections for item in group):

            score -= 10

            problems.append(
                "Missing or unclear section: "
                + " / ".join(group)
            )

    if len(text) > 18000:

        score -= 5

        problems.append(
            "Resume contains a large amount of text."
        )

    score = max(0, min(100, score))

    return score, problems


# ============================================================
# ALIASES
# ============================================================

ALIASES = {

    "node.js": [
        "node",
        "nodejs"
    ],

    "rest api": [
        "rest",
        "api"
    ],

    "machine learning": [
        "ml"
    ],

    "artificial intelligence": [
        "ai"
    ],

    "natural language processing": [
        "nlp"
    ],

    "internet of things": [
        "iot"
    ],

    "postgresql": [
        "postgres"
    ],

    "scikit-learn": [
        "sklearn"
    ],

    "javascript": [
        "js"
    ],

    "typescript": [
        "ts"
    ],

    "c++": [
        "cpp"
    ]
}


# ============================================================
# CHECK WHETHER RESUME SUPPORTS KEYWORD
# ============================================================

def resume_supports_keyword(keyword, resume_text):

    normalized = normalize(resume_text)

    keyword = keyword.lower()

    if keyword in normalized:
        return True

    for alias in ALIASES.get(keyword, []):

        if alias in normalized:
            return True

    return False


# ============================================================
# FIND MISSING JOB KEYWORDS
# ============================================================

def find_missing_keywords(resume_text, job_description):

    resume_keywords = set(
        find_skills(resume_text)
    )

    job_keywords = set(
        extract_job_keywords(job_description)
    )

    missing = job_keywords - resume_keywords

    safe_missing = []

    for keyword in sorted(missing):

        # Only add if the resume already contains
        # some evidence for the keyword.
        if resume_supports_keyword(
            keyword,
            resume_text
        ):
            safe_missing.append(keyword)

    return safe_missing


# ============================================================
# SPLIT RESUME INTO SECTIONS
# ============================================================

def split_sections(text):

    lines = text.splitlines()

    sections = {
        "General": []
    }

    current_section = "General"

    for line in lines:

        clean = line.strip()

        if not clean:
            continue

        normalized = clean.lower().strip(": ")

        detected = None

        for section in SECTION_NAMES:

            if normalized == section:
                detected = section.title()
                break

        if detected:

            current_section = detected

            if current_section not in sections:
                sections[current_section] = []

        else:

            sections[current_section].append(clean)

    return sections


# ============================================================
# KEYWORD SECTION
# ============================================================

def keyword_section(keyword):

    technical_keywords = {

        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "c#",
        "go",
        "rust",
        "php",

        "html",
        "css",
        "react",
        "angular",
        "vue",
        "node",
        "node.js",
        "express",
        "django",
        "flask",
        "fastapi",

        "rest api",
        "graphql",

        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "oracle",

        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",

        "git",
        "github",
        "gitlab",

        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",
        "data analysis",

        "pandas",
        "numpy",
        "tensorflow",
        "pytorch",

        "nlp",
        "natural language processing",
        "computer vision"
    }

    if keyword.lower() in technical_keywords:
        return "Skills"

    return "Skills"


# ============================================================
# BUILD OPTIMIZED RESUME
# ============================================================

def build_optimized_resume(
    resume_text,
    safe_missing_keywords
):

    sections = split_sections(resume_text)

    if "Skills" not in sections:

        sections["Skills"] = []

    existing_skills = " ".join(
        sections["Skills"]
    ).lower()

    for keyword in safe_missing_keywords:

        if keyword.lower() not in existing_skills:

            sections["Skills"].append(
                keyword.title()
            )

            existing_skills += " " + keyword.lower()

    output = []

    order = [

        "General",

        "Summary",
        "Objective",
        "Profile",

        "Skills",
        "Technical Skills",

        "Experience",
        "Work Experience",
        "Employment",
        "Internship",

        "Projects",

        "Education",

        "Certifications",
        "Certificates",

        "Achievements",
        "Awards",

        "Publications",

        "Languages",
        "Interests"
    ]

    used = set()

    for section in order:

        if section not in sections:
            continue

        used.add(section)

        if section != "General":

            output.append("")
            output.append(section.upper())
            output.append("=" * len(section))

        for item in sections[section]:

            output.append(item)

    for section, items in sections.items():

        if section in used:
            continue

        output.append("")
        output.append(section.upper())
        output.append("=" * len(section))

        for item in items:
            output.append(item)

    return "\n".join(output).strip()


# ============================================================
# CREATE DOCX
# ============================================================

def create_docx(resume_text):

    document = Document()

    style = document.styles["Normal"]

    style.font.name = "Arial"
    style.font.size = Pt(10.5)

    for line in resume_text.splitlines():

        if not line.strip():

            document.add_paragraph()
            continue

        paragraph = document.add_paragraph()

        paragraph.paragraph_format.space_after = Pt(4)

        if (
            line.isupper()
            and len(line) < 60
        ):

            run = paragraph.add_run(line)

            run.bold = True
            run.font.size = Pt(12)

        elif set(line.strip()) == {"="}:

            continue

        else:

            paragraph.add_run(line)

    output = io.BytesIO()

    document.save(output)

    output.seek(0)

    return output


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():

    return HTMLResponse(
        """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>Universal AI Resume Suite</title>

<style>

body {
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    margin: 0;
    padding: 40px;
}

.container {
    max-width: 850px;
    margin: auto;
    background: white;
    padding: 35px;
    border-radius: 15px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.08);
}

h1 {
    margin-top: 0;
}

label {
    font-weight: bold;
    display: block;
    margin-top: 20px;
    margin-bottom: 8px;
}

input[type=file],
textarea {
    width: 100%;
    box-sizing: border-box;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 8px;
}

textarea {
    min-height: 220px;
    resize: vertical;
}

button {
    margin-top: 25px;
    padding: 13px 25px;
    border: none;
    border-radius: 8px;
    background: #111827;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #374151;
}

.info {
    background: #eef6ff;
    padding: 15px;
    border-radius: 8px;
    margin-top: 20px;
}

</style>

</head>

<body>

<div class="container">

<h1>
Universal AI Resume Suite
</h1>

<p>
Upload your resume and paste the job description.
The system will automatically analyze and optimize
your resume for the job.
</p>

<form
action="/optimize"
method="post"
enctype="multipart/form-data"
>

<label>
Resume PDF
</label>

<input
type="file"
name="resume"
accept=".pdf"
required
>

<label>
Job Description
</label>

<textarea
name="job_description"
placeholder="Paste the complete job description here..."
required
></textarea>

<button type="submit">
Optimize Resume
</button>

</form>

<div class="info">

<strong>Safety:</strong>

The optimizer does not intentionally invent
skills or experience that are not supported
by the original resume.

</div>

</div>

</body>

</html>
"""
    )


# ============================================================
# OPTIMIZE RESUME
# ============================================================

@app.post(
    "/optimize",
    response_class=HTMLResponse
)
async def optimize(

    resume: UploadFile = File(...),

    job_description: str = Form(...)
):

    filename = resume.filename or ""

    if not filename.lower().endswith(".pdf"):

        return HTMLResponse(
            """
            <h2>Please upload a PDF resume.</h2>
            <a href="/">Go Back</a>
            """,
            status_code=400
        )

    data = await resume.read()

    if not data:

        return HTMLResponse(
            """
            <h2>The uploaded resume is empty.</h2>
            <a href="/">Go Back</a>
            """,
            status_code=400
        )

    resume_text = extract_pdf_text(data)

    if not resume_text.strip():

        return HTMLResponse(
            """
            <h2>Could not read text from this PDF.</h2>
            <p>
            Please upload a text-based PDF.
            Scanned-image PDFs require OCR.
            </p>
            <a href="/">Go Back</a>
            """,
            status_code=400
        )

    resume_text = clean_text(resume_text)

    job_description = clean_text(
        job_description
    )

    # --------------------------------------------------------
    # ANALYZE FORMAT
    # --------------------------------------------------------

    format_score, problems = analyze_format(
        resume_text
    )

    # --------------------------------------------------------
    # FIND KEYWORDS
    # --------------------------------------------------------

    resume_keywords = find_skills(
        resume_text
    )

    job_keywords = extract_job_keywords(
        job_description
    )

    matched_keywords = sorted(
        set(resume_keywords)
        &
        set(job_keywords)
    )

    missing_keywords = find_missing_keywords(
        resume_text,
        job_description
    )

    # --------------------------------------------------------
    # ATS SCORE
    # --------------------------------------------------------

    if job_keywords:

        ats_score = round(
            (
                len(matched_keywords)
                /
                len(job_keywords)
            )
            * 100
        )

    else:

        ats_score = 0

    final_score = round(
        (
            ats_score * 0.65
        )
        +
        (
            format_score * 0.35
        )
    )

    # --------------------------------------------------------
    # BUILD OPTIMIZED RESUME
    # --------------------------------------------------------

    optimized_text = build_optimized_resume(
        resume_text,
        missing_keywords
    )

    # --------------------------------------------------------
    # HTML DATA
    # --------------------------------------------------------

    matched_html = "".join(

        f"<li>{html.escape(skill.title())}</li>"

        for skill in matched_keywords
    )

    missing_html = "".join(

        f"<li>{html.escape(skill.title())}</li>"

        for skill in missing_keywords
    )

    problems_html = "".join(

        f"<li>{html.escape(problem)}</li>"

        for problem in problems
    )

    if not matched_html:

        matched_html = (
            "<li>No matching keywords found.</li>"
        )

    if not missing_html:

        missing_html = (
            "<li>No safe missing keywords detected.</li>"
        )

    if not problems_html:

        problems_html = (
            "<li>No major format issues detected.</li>"
        )

    escaped_resume = html.escape(
        optimized_text
    )

    return HTMLResponse(

        f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
Resume Optimization Result
</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    margin: 0;
    padding: 30px;
}}

.container {{
    max-width: 1000px;
    margin: auto;
}}

.card {{
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 3px 15px rgba(0,0,0,.07);
}}

.grid {{
    display: grid;
    grid-template-columns:
        repeat(3, 1fr);
    gap: 15px;
}}

.score {{
    font-size: 42px;
    font-weight: bold;
}}

.box {{
    text-align: center;
}}

textarea {{
    width: 100%;
    min-height: 450px;
    box-sizing: border-box;
    padding: 15px;
    font-family: Arial;
}}

button,
a {{
    display: inline-block;
    padding: 12px 20px;
    border-radius: 7px;
    border: none;
    background: #111827;
    color: white;
    text-decoration: none;
    cursor: pointer;
}}

button:hover,
a:hover {{
    background: #374151;
}}

@media(max-width:700px) {{

    .grid {{
        grid-template-columns: 1fr;
    }}

}}

</style>

</head>

<body>

<div class="container">

<div class="card">

<h1>
Resume Optimization Complete
</h1>

<p>
Your resume has been analyzed against
the supplied job description.
</p>

</div>


<div class="grid">

<div class="card box">

<h3>
ATS Match
</h3>

<div class="score">
{ats_score}%
</div>

</div>


<div class="card box">

<h3>
Format Score
</h3>

<div class="score">
{format_score}%
</div>

</div>


<div class="card box">

<h3>
Final Score
</h3>

<div class="score">
{final_score}%
</div>

</div>

</div>


<div class="card">

<h2>
Matched Job Keywords
</h2>

<ul>
{matched_html}
</ul>

</div>


<div class="card">

<h2>
Automatically Added Keywords
</h2>

<ul>
{missing_html}
</ul>

<p>
Supported keywords are added to the
optimized resume without changing the
original uploaded file.
</p>

</div>


<div class="card">

<h2>
Format Analysis
</h2>

<ul>
{problems_html}
</ul>

</div>


<div class="card">

<h2>
Optimized Resume
</h2>

<textarea readonly>
{escaped_resume}
</textarea>

<br>
<br>

<form
action="/download-docx"
method="post"
>

<textarea
name="resume_text"
style="display:none;"
>{escaped_resume}</textarea>

<button type="submit">
Download Optimized DOCX
</button>

</form>

</div>


<div class="card">

<a href="/">
Upload Another Resume
</a>

</div>

</div>

</body>

</html>
"""
    )


# ============================================================
# DOWNLOAD OPTIMIZED DOCX
# ============================================================

@app.post("/download-docx")
async def download_docx(
    resume_text: str = Form(...)
):

    resume_text = html.unescape(
        resume_text
    )

    file = create_docx(
        resume_text
    )

    return StreamingResponse(

        file,

        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),

        headers={
            "Content-Disposition":
            'attachment; filename="optimized_resume.docx"'
        }
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "application": "Universal AI Resume Suite"
    }
