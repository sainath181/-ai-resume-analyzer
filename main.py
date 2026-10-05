from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader
import io
import re
import html

app = FastAPI(title="Universal AI Resume Suite")


# =========================================================
# SKILL / KEYWORD DATABASE
# =========================================================

SKILLS = [
    # Programming
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "go", "rust", "php", "ruby", "kotlin", "swift",

    # Web
    "html", "css", "react", "angular", "vue", "node.js", "node",
    "express", "django", "flask", "fastapi", "rest api", "graphql",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "oracle",
    "redis", "sqlite", "database",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes",
    "jenkins", "git", "github", "gitlab", "ci/cd",

    # Data / AI
    "machine learning", "deep learning", "artificial intelligence",
    "ai", "data science", "data analysis", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "nlp",
    "natural language processing", "computer vision",

    # Engineering
    "autocad", "solidworks", "matlab", "embedded systems",
    "iot", "internet of things", "plc", "robotics",

    # Business
    "marketing", "sales", "finance", "accounting",
    "project management", "business analysis",
    "communication", "leadership", "teamwork",
    "problem solving", "excel", "power bi", "tableau",

    # Pharmacy / Life Sciences
    "pharmacology", "pharmaceutics", "pharmaceutical",
    "clinical research", "clinical trials", "drug discovery",
    "quality control", "quality assurance", "gmp", "glp",
    "regulatory affairs", "medical coding", "pharmacovigilance"
]


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


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))

    text_parts = []

    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            pass

    return "\n".join(text_parts).strip()


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


# =========================================================
# FIND SKILLS
# =========================================================

def find_skills(text: str):
    normalized = normalize(text)

    found = []

    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"

        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(set(found))


# =========================================================
# JOB KEYWORD EXTRACTION
# =========================================================

def extract_job_keywords(job_description: str):
    normalized = normalize(job_description)

    found = []

    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"

        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(set(found))


# =========================================================
# CHECK SECTIONS
# =========================================================

def detect_sections(text: str):
    normalized = normalize(text)

    sections = {}

    for section in SECTION_NAMES:
        if section in normalized:
            sections[section] = True

    return sections


# =========================================================
# RESUME FORMAT ANALYSIS
# =========================================================

def analyze_format(text: str):
    lines = [x.strip() for x in text.splitlines() if x.strip()]

    score = 100
    problems = []

    if len(text) < 300:
        score -= 25
        problems.append("Resume contains very little readable text.")

    if len(lines) < 10:
        score -= 15
        problems.append("Resume may have insufficient structured content.")

    sections = detect_sections(text)

    important_groups = [
        ["summary", "objective", "profile"],
        ["skills", "technical skills"],
        ["experience", "work experience", "employment", "internship"],
        ["education"],
    ]

    for group in important_groups:
        if not any(x in sections for x in group):
            score -= 10
            problems.append(
                "Missing or unclear section: " + " / ".join(group)
            )

    if len(text) > 15000:
        score -= 5
        problems.append("Resume contains a large amount of text.")

    score = max(0, min(100, score))

    return score, problems


# =========================================================
# FIND RELEVANT EVIDENCE
# =========================================================

def find_evidence_for_skill(skill: str, resume_text: str):
    """
    Determines whether the resume contains evidence that supports
    using the keyword.

    We intentionally avoid inventing experience.
    """

    normalized_resume = normalize(resume_text)
    skill_lower = skill.lower()

    if skill_lower in normalized_resume:
        return True

    aliases = {
        "node.js": ["node", "nodejs"],
        "rest api": ["rest", "api"],
        "machine learning": ["ml"],
        "artificial intelligence": ["ai"],
        "natural language processing": ["nlp"],
        "internet of things": ["iot"],
        "postgresql": ["postgres"],
        "scikit-learn": ["sklearn"],
        "javascript": ["js"],
        "typescript": ["ts"],
        "c++": ["cpp"],
        "c#": ["c sharp"],
    }

    for alias in aliases.get(skill_lower, []):
        if alias in normalized_resume:
            return True

    return False


# =========================================================
# DETERMINE SAFE MISSING KEYWORDS
# =========================================================

def get_safe_missing_keywords(resume_text: str, job_description: str):
    resume_skills = set(find_skills(resume_text))
    job_skills = set(extract_job_keywords(job_description))

    missing = sorted(job_skills - resume_skills)

    safe_missing = []

    for skill in missing:
        if find_evidence_for_skill(skill, resume_text):
            safe_missing.append(skill)

    return sorted(safe_missing)


# =========================================================
# EXTRACT RESUME SECTIONS
# =========================================================

def split_sections(text: str):
    lines = text.splitlines()

    sections = {}
    current = "General"
    sections[current] = []

    for line in lines:

        clean = line.strip()

        if not clean:
            continue

        normalized = clean.lower().strip(": ")

        matched_section = None

        for section in SECTION_NAMES:
            if normalized == section:
                matched_section = section.title()
                break

        if matched_section:
            current = matched_section

            if current not in sections:
                sections[current] = []

        else:
            sections[current].append(clean)

    return sections


# =========================================================
# PLACE KEYWORDS INTO APPROPRIATE SECTIONS
# =========================================================

def choose_section_for_keyword(skill: str):
    skill_lower = skill.lower()

    technical = {
        "python", "java", "javascript", "typescript",
        "c", "c++", "c#", "go", "rust", "php",
        "html", "css", "react", "angular", "vue",
        "node", "node.js", "express", "django", "flask",
        "fastapi", "rest api", "graphql",
        "sql", "mysql", "postgresql", "mongodb",
        "oracle", "redis", "sqlite",
        "aws", "azure", "gcp", "docker", "kubernetes",
        "git", "github", "gitlab",
        "pandas", "numpy", "tensorflow", "pytorch",
        "scikit-learn", "machine learning",
        "deep learning", "artificial intelligence",
        "nlp", "natural language processing"
    }

    if skill_lower in technical:
        return "Skills"

    business = {
        "marketing", "sales", "finance", "accounting",
        "project management", "business analysis",
        "communication", "leadership", "teamwork",
        "problem solving", "excel", "power bi", "tableau"
    }

    if skill_lower in business:
        return "Skills"

    return "Skills"


# =========================================================
# BUILD OPTIMIZED TEXT
# =========================================================

def build_optimized_resume(resume_text: str, safe_keywords):
    sections = split_sections(resume_text)

    if "Skills" not in sections:
        sections["Skills"] = []

    existing_skills_text = " ".join(sections["Skills"])

    for keyword in safe_keywords:

        if keyword.lower() not in existing_skills_text.lower():
            sections["Skills"].append(keyword.title())

    output = []

    preferred_order = [
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

    for section in preferred_order:

        if section not in sections:
            continue

        used.add(section)

        if section != "General":
            output.append("")
            output.append(section.upper())
            output.append("-" * len(section))

        for item in sections[section]:
            output.append(item)

    for section, items in sections.items():

        if section in used:
            continue

        output.append("")
        output.append(section.upper())
        output.append("-" * len(section))

        for item in items:
            output.append(item)

    return "\n".join(output).strip()


# =========================================================
# CREATE DOCX
# =========================================================

def create_docx(resume_text: str):
    document = Document()

    normal_style = document.styles["Normal"]
    normal_style.font.name = "Arial"
    normal_style.font.size = Pt(10.5)

    lines = resume_text.splitlines()

    for line in lines:

        if not line.strip():
            document.add_paragraph()
            continue

        paragraph = document.add_paragraph()

        paragraph.paragraph_format.space_after = Pt(4)

        if line.isupper() and len(line) < 60:
            run = paragraph.add_run(line)
            run.bold = True
            run.font.size = Pt(12)
        elif set(line.strip()) == {"-"}:
            continue
        else:
            paragraph.add_run(line)

    output = io.BytesIO()
    document.save(output)
    output.seek(0)

    return output


# =========================================================
# HTML
# =========================================================

def page_html():
    return """
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

<h1>Universal AI Resume Suite</h1>

<p>
Upload your resume and paste the job description.
The system will analyze the resume and automatically optimize
supported keywords.
</p>

<form action="/optimize" method="post" enctype="multipart/form-data">

<label>Resume PDF</label>
<input type="file" name="resume" accept=".pdf" required>

<label>Job Description</label>
<textarea
name="job_description"
placeholder="Paste the complete job description here..."
required></textarea>

<button type="submit">
Optimize Resume
</button>

</form>

<div class="info">
<strong>Important:</strong>
The system does not intentionally invent qualifications or experience.
It only optimizes keywords supported by the resume.
</div>

</div>

</body>
</html>
"""


# =========================================================
# HOME
# =========================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(page_html())


# =========================================================
# OPTIMIZE
# =========================================================

@app.post("/optimize", response_class=HTMLResponse)
async def optimize(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):

    if not resume.filename.lower().endswith(".pdf"):
        return HTMLResponse(
            "<h2>Please upload a PDF resume.</h2>",
            status_code=400
        )

    data = await resume.read()

    if not data:
        return HTMLResponse(
            "<h2>Resume file is empty.</h2>",
            status_code=400
        )

    resume_text = extract_pdf_text(data)

    if not resume_text:
        return HTMLResponse(
            "<h2>Could not extract text from the PDF.</h2>"
            "<p>Please upload a text-based PDF.</p>",
            status_code=400
        )

    resume_text = clean_text(resume_text)

    job_description = clean_text(job_description)

    format_score, problems = analyze_format(resume_text)

    resume_skills = find_skills(resume_text)

    job_keywords = extract_job_keywords(job_description)

    missing_keywords = get_safe_missing_keywords(
        resume_text,
        job_description
    )

    optimized_text = build_optimized_resume(
        resume_text,
        missing_keywords
    )

    matched = sorted(
        set(resume_skills).intersection(set(job_keywords))
    )

    if job_keywords:
        ats_score = round(
            (len(matched) / len(job_keywords)) * 100
        )
    else:
        ats_score = 0

    final_score = round(
        (ats_score * 0.65) +
        (format_score * 0.35)
    )

    docx_file = create_docx(optimized_text)

    safe_original = html.escape(resume.filename)

    missing_html = "".join(
        f"<li>{html.escape(x.title())}</li>"
        for x in missing_keywords
    )

    matched_html = "".join(
        f"<li>{html.escape(x.title())}</li>"
        for x in matched
    )

    problems_html = "".join(
        f"<li>{html.escape(x)}</li>"
        for x in problems
    )

    if not missing_html:
        missing_html = "<li>No safe missing keywords detected.</li>"

    if not matched_html:
        matched_html = "<li>No matching keywords detected.</li>"

    if not problems_html:
        problems_html = "<li>No major format problems detected.</li>"

    safe_resume_text = html.escape(optimized_text)

    return HTMLResponse(
        f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>Resume Analysis</title>

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

.score {{
    font-size: 45px;
    font-weight: bold;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}}

.box {{
    padding: 20px;
    border-radius: 10px;
    background: #f8fafc;
}}

button, a {{
    display: inline-block;
    padding: 12px 20px;
    border-radius: 7px;
    border: none;
    background: #111827;
    color: white;
    text-decoration: none;
    cursor: pointer;
}}

textarea {{
    width: 100%;
    min-height: 400px;
    box-sizing: border-box;
    padding: 15px;
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

<h1>Resume Optimization Complete</h1>

<p>
Original file:
<strong>{safe_original}</strong>
</p>

</div>


<div class="grid">

<div class="card box">

<h3>ATS Match</h3>

<div class="score">
{ats_score}%
</div>

</div>

<div class="card box">

<h3>Format Score</h3>

<div class="score">
{format_score}%
</div>

</div>

<div class="card box">

<h3>Final Score</h3>

<div class="score">
{final_score}%
</div>

</div>

</div>


<div class="card">

<h2>Matched Job Keywords</h2>

<ul>
{matched_html}
</ul>

</div>


<div class="card">

<h2>Automatically Added Keywords</h2>

<ul>
{missing_html}
</ul>

<p>
These were inserted into the optimized Skills section when
supported by information found in the original resume.
</p>

</div>


<div class="card">

<h2>Format / Alignment Checks</h2>

<ul>
{problems_html}
</ul>

</div>


<div class="card">

<h2>Optimized Resume Preview</h2>

<textarea readonly>{safe_resume_text}</textarea>

<br><br>

<form action="/download-docx" method="post">

<textarea name="resume_text" style="display:none">{safe_resume_text}</textarea>

<button type="submit">
Download Optimized DOCX
</button>

</form>

</div>


<div class="card">

<a href="/">
Optimize Another Resume
</a>

</div>

</div>

</body>
</html>
"""
    )


# =========================================================
# DOWNLOAD DOCX
# =========================================================

@app.post("/download-docx")
async def download_docx(resume_text: str = Form(...)):

    resume_text = html.unescape(resume_text)

    file = create_docx(resume_text)

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition":
            'attachment; filename="optimized_resume.docx"'
        }
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": "Universal AI Resume Suite"
    }
