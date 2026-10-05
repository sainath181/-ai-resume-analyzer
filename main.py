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
# KEYWORD DATABASE
# ============================================================

KEYWORD_GROUPS = {
    "Programming Languages": [
        "python", "java", "c", "c++", "c#", "javascript", "typescript",
        "go", "golang", "rust", "kotlin", "swift", "php", "ruby",
        "scala", "r", "matlab", "dart", "perl"
    ],

    "Web Technologies": [
        "html", "html5", "css", "css3", "javascript", "react",
        "react.js", "reactjs", "angular", "vue", "vue.js",
        "node.js", "nodejs", "express", "express.js",
        "bootstrap", "tailwind", "next.js", "nextjs",
        "django", "flask", "fastapi", "rest api", "restful api"
    ],

    "Database": [
        "sql", "mysql", "postgresql", "postgres", "mongodb",
        "oracle", "sqlite", "redis", "firebase", "database",
        "database management", "nosql"
    ],

    "Tools": [
        "git", "github", "gitlab", "bitbucket", "visual studio code",
        "vs code", "docker", "postman", "jira", "jenkins",
        "linux", "windows", "npm", "maven", "gradle"
    ],

    "Cloud": [
        "aws", "amazon web services", "azure", "microsoft azure",
        "google cloud", "gcp", "docker", "kubernetes", "terraform"
    ],

    "AI & Data": [
        "artificial intelligence", "ai", "machine learning", "ml",
        "deep learning", "nlp", "natural language processing",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "opencv", "data analysis", "data science"
    ],

    "Engineering": [
        "autocad", "solidworks", "catia", "ansys", "matlab",
        "embedded systems", "microcontroller", "arduino",
        "raspberry pi", "iot", "internet of things"
    ],

    "Business": [
        "sales", "marketing", "finance", "accounting", "excel",
        "microsoft excel", "power bi", "tableau", "business analysis",
        "project management", "communication", "leadership"
    ],

    "Pharmacy": [
        "pharmacology", "pharmaceutics", "pharmaceutical chemistry",
        "clinical pharmacy", "pharmacovigilance", "drug safety",
        "drug development", "quality control", "quality assurance",
        "gmp", "glp", "regulatory affairs"
    ],

    "Soft Skills": [
        "communication", "leadership", "teamwork", "team player",
        "problem solving", "problem-solving", "time management",
        "adaptability", "quick learner", "critical thinking"
    ]
}


SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "career objective",
        "objective"
    ],
    "skills": [
        "skills",
        "technical skills",
        "key skills",
        "technical expertise"
    ],
    "experience": [
        "experience",
        "work experience",
        "employment",
        "professional experience",
        "internship",
        "internships"
    ],
    "projects": [
        "project",
        "projects",
        "academic projects",
        "personal projects"
    ],
    "education": [
        "education",
        "academic qualification",
        "qualifications"
    ],
    "certifications": [
        "certification",
        "certifications",
        "courses",
        "training"
    ],
    "activities": [
        "activities",
        "interests",
        "hobbies",
        "activities & interests"
    ]
}


# ============================================================
# BASIC FUNCTIONS
# ============================================================

def normalize(text):
    text = text.lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text(text):
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        try:
            text = page.extract_text() or ""
            pages.append(text)
        except Exception:
            pages.append("")

    return clean_text("\n".join(pages))


# ============================================================
# KEYWORD MATCHING
# ============================================================

def keyword_exists(text, keyword):
    text = normalize(text)
    keyword = normalize(keyword)

    if keyword == "c":
        return bool(re.search(r"\b(c)\b", text))

    if keyword == "r":
        return bool(re.search(r"\b(r)\b", text))

    escaped = re.escape(keyword)

    return bool(re.search(r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])", text))


def find_job_keywords(job_description):
    found = []

    jd = normalize(job_description)

    for group, keywords in KEYWORD_GROUPS.items():

        for keyword in keywords:

            if keyword_exists(jd, keyword):

                if keyword not in found:
                    found.append(keyword)

    return found


def find_missing_keywords(resume_text, job_description):
    job_keywords = find_job_keywords(job_description)

    missing = []

    for keyword in job_keywords:

        if not keyword_exists(resume_text, keyword):

            missing.append(keyword)

    return job_keywords, missing


# ============================================================
# SECTION DETECTION
# ============================================================

def find_existing_section(text, section_type):

    lines = text.splitlines()

    aliases = SECTION_ALIASES.get(section_type, [])

    for i, line in enumerate(lines):

        clean = normalize(line)

        for alias in aliases:

            if clean == alias:
                return i

            if clean.startswith(alias + ":"):
                return i

    return -1


def get_section_for_keyword(keyword):

    keyword = normalize(keyword)

    for section, keywords in KEYWORD_GROUPS.items():

        for item in keywords:

            if keyword == normalize(item):
                return section

    return "Skills"


# ============================================================
# FORMAT ANALYSIS
# ============================================================

def analyze_format(resume_text):

    problems = []

    lower = normalize(resume_text)

    if not any(x in lower for x in SECTION_ALIASES["experience"]):
        problems.append(
            "Missing or unclear section: experience / work experience / employment / internship"
        )

    if not any(x in lower for x in SECTION_ALIASES["education"]):
        problems.append("Missing or unclear Education section")

    if not any(x in lower for x in SECTION_ALIASES["skills"]):
        problems.append("Missing or unclear Skills section")

    return problems


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(job_keywords, resume_text):

    if not job_keywords:
        return 0

    matched = 0

    for keyword in job_keywords:

        if keyword_exists(resume_text, keyword):
            matched += 1

    return round((matched / len(job_keywords)) * 100)


# ============================================================
# ADD KEYWORDS TO CORRECT PLACE
# ============================================================

def add_keyword_to_skills_section(text, keyword):

    lines = text.splitlines()

    skills_index = find_existing_section(text, "skills")

    if skills_index == -1:

        # Add a Skills section near the beginning
        new_text = (
            "SKILLS\n"
            "=======\n"
            f"Programming Languages: {keyword}\n\n"
            + text
        )

        return new_text

    target_section = get_section_for_keyword(keyword)

    # Find existing target line
    for i in range(skills_index + 1, min(skills_index + 40, len(lines))):

        line = lines[i].strip()

        lower_line = normalize(line)

        if target_section == "Programming Languages":

            if (
                lower_line.startswith("programming languages:")
                or lower_line.startswith("programming language:")
                or lower_line.startswith("languages:")
            ):

                if keyword.lower() not in lower_line:

                    lines[i] = line.rstrip() + ", " + keyword

                    return "\n".join(lines)

        elif target_section == "Web Technologies":

            if (
                lower_line.startswith("web technologies:")
                or lower_line.startswith("web technology:")
                or lower_line.startswith("frontend:")
                or lower_line.startswith("front end:")
            ):

                if keyword.lower() not in lower_line:

                    lines[i] = line.rstrip() + ", " + keyword

                    return "\n".join(lines)

        elif target_section == "Database":

            if (
                lower_line.startswith("database:")
                or lower_line.startswith("databases:")
                or lower_line.startswith("database technologies:")
            ):

                if keyword.lower() not in lower_line:

                    lines[i] = line.rstrip() + ", " + keyword

                    return "\n".join(lines)

        elif target_section == "Tools":

            if (
                lower_line.startswith("tools:")
                or lower_line.startswith("software:")
                or lower_line.startswith("tools & technologies:")
            ):

                if keyword.lower() not in lower_line:

                    lines[i] = line.rstrip() + ", " + keyword

                    return "\n".join(lines)

        elif target_section == "Cloud":

            if (
                lower_line.startswith("cloud:")
                or lower_line.startswith("cloud technologies:")
                or lower_line.startswith("cloud platforms:")
            ):

                if keyword.lower() not in lower_line:

                    lines[i] = line.rstrip() + ", " + keyword

                    return "\n".join(lines)

    # If exact category line doesn't exist,
    # add a new category inside Skills.

    insert_position = skills_index + 1

    category_order = [
        "Programming Languages",
        "Web Technologies",
        "Database",
        "Tools",
        "Cloud",
        "AI & Data",
        "Engineering",
        "Business",
        "Pharmacy",
        "Soft Skills"
    ]

    # Find end of Skills section
    end_position = len(lines)

    for i in range(skills_index + 1, len(lines)):

        lower = normalize(lines[i])

        for section_aliases in SECTION_ALIASES.values():

            for alias in section_aliases:

                if lower == alias and i > skills_index + 1:
                    end_position = i
                    break

            if end_position != len(lines):
                break

        if end_position != len(lines):
            break

    category_line = f"{target_section}: {keyword}"

    lines.insert(end_position, category_line)

    return "\n".join(lines)


def add_keyword_to_resume(text, keyword):

    target = get_section_for_keyword(keyword)

    # Important:
    # Only automatically add technical/job keywords.
    # Do not fabricate experience.

    if target in [
        "Programming Languages",
        "Web Technologies",
        "Database",
        "Tools",
        "Cloud",
        "AI & Data",
        "Engineering",
        "Business",
        "Pharmacy",
        "Soft Skills"
    ]:

        return add_keyword_to_skills_section(text, keyword)

    return text


# ============================================================
# BUILD OPTIMIZED RESUME
# ============================================================

def build_optimized_resume(resume_text, missing_keywords):

    optimized = resume_text

    added = []

    for keyword in missing_keywords:

        before = optimized

        optimized = add_keyword_to_resume(
            optimized,
            keyword
        )

        if optimized != before:

            added.append(keyword)

    return optimized, added


# ============================================================
# CREATE DOCX
# ============================================================

def create_docx(text):

    document = Document()

    normal_style = document.styles["Normal"]

    normal_style.font.name = "Arial"
    normal_style.font.size = Pt(10)

    for line in text.splitlines():

        line = line.rstrip()

        if not line:
            document.add_paragraph()
            continue

        # Main headings
        upper = line.upper().strip()

        if (
            upper in [
                "SKILLS",
                "EDUCATION",
                "EXPERIENCE",
                "WORK EXPERIENCE",
                "PROJECTS",
                "CERTIFICATIONS",
                "ACTIVITIES & INTERESTS",
                "SUMMARY",
                "CAREER OBJECTIVE"
            ]
        ):

            p = document.add_paragraph()

            run = p.add_run(line)

            run.bold = True
            run.font.size = Pt(12)

        elif (
            line.startswith("Programming Languages:")
            or line.startswith("Web Technologies:")
            or line.startswith("Database:")
            or line.startswith("Tools:")
            or line.startswith("Cloud:")
            or line.startswith("AI & Data:")
            or line.startswith("Engineering:")
            or line.startswith("Business:")
            or line.startswith("Pharmacy:")
            or line.startswith("Soft Skills:")
        ):

            p = document.add_paragraph()

            run = p.add_run(line)

            run.bold = True

        else:

            document.add_paragraph(line)

    output = io.BytesIO()

    document.save(output)

    output.seek(0)

    return output


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Universal AI Resume Suite</title>

        <style>

        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            padding: 40px;
        }

        .box {
            max-width: 800px;
            margin: auto;
            background: white;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.08);
        }

        h1 {
            text-align: center;
        }

        label {
            display: block;
            margin-top: 20px;
            font-weight: bold;
        }

        input, textarea {
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 8px;
        }

        textarea {
            height: 220px;
        }

        button {
            margin-top: 25px;
            width: 100%;
            padding: 14px;
            background: #111827;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }

        </style>
    </head>

    <body>

        <div class="box">

            <h1>Universal AI Resume Suite</h1>

            <form action="/optimize" method="post" enctype="multipart/form-data">

                <label>Upload Resume PDF</label>

                <input
                    type="file"
                    name="resume"
                    accept=".pdf"
                    required
                >

                <label>Job Description</label>

                <textarea
                    name="job_description"
                    placeholder="Paste the job description here..."
                    required
                ></textarea>

                <button type="submit">
                    Optimize Resume
                </button>

            </form>

        </div>

    </body>
    </html>
    """


# ============================================================
# OPTIMIZE
# ============================================================

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

    file_bytes = await resume.read()

    original_text = extract_pdf_text(file_bytes)

    if not original_text.strip():

        return HTMLResponse(
            "<h2>Could not read text from this PDF.</h2>"
            "<p>Please upload a text-based PDF.</p>",
            status_code=400
        )

    # Find job keywords
    job_keywords, missing_keywords = find_missing_keywords(
        original_text,
        job_description
    )

    # Build corrected resume
    optimized_text, added_keywords = build_optimized_resume(
        original_text,
        missing_keywords
    )

    # Calculate scores AFTER correction
    ats_score = calculate_ats_score(
        job_keywords,
        optimized_text
    )

    format_problems = analyze_format(original_text)

    format_score = max(
        0,
        100 - (len(format_problems) * 10)
    )

    final_score = round(
        (ats_score * 0.7) +
        (format_score * 0.3)
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # The page shows ONLY the corrected resume.
    # The original resume is never displayed.
    # --------------------------------------------------------

    safe_resume = html.escape(optimized_text)

    matched_keywords = [
        keyword
        for keyword in job_keywords
        if keyword_exists(optimized_text, keyword)
    ]

    matched_html = "".join(
        f"<li>{html.escape(k)}</li>"
        for k in matched_keywords
    )

    added_html = "".join(
        f"<li>{html.escape(k)} → {html.escape(get_section_for_keyword(k))}</li>"
        for k in added_keywords
    )

    if not added_html:

        added_html = "<li>No new keywords were added.</li>"

    format_html = "".join(
        f"<li>{html.escape(problem)}</li>"
        for problem in format_problems
    )

    if not format_html:

        format_html = "<li>No major format problems detected.</li>"

    # Store optimized text in a simple encoded form
    import base64

    encoded_resume = base64.b64encode(
        optimized_text.encode("utf-8")
    ).decode("utf-8")

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Resume Optimization Complete</title>

        <style>

        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            padding: 30px;
        }}

        .container {{
            max-width: 1100px;
            margin: auto;
        }}

        .card {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.07);
        }}

        .scores {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .score {{
            flex: 1;
            min-width: 180px;
            padding: 20px;
            border-radius: 10px;
            background: #f0f2f5;
            text-align: center;
        }}

        .score h2 {{
            margin: 0;
            font-size: 32px;
        }}

        .resume {{
            white-space: pre-wrap;
            background: #fafafa;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #ddd;
            line-height: 1.5;
        }}

        button {{
            padding: 13px 20px;
            border: none;
            border-radius: 8px;
            background: #111827;
            color: white;
            cursor: pointer;
            font-size: 15px;
            margin-right: 10px;
        }}

        </style>

    </head>

    <body>

    <div class="container">

        <div class="card">

            <h1>Resume Optimization Complete</h1>

            <p>
            Your resume has been automatically corrected against the supplied job description.
            </p>

        </div>

        <div class="scores">

            <div class="score">
                <h2>{ats_score}%</h2>
                <p>ATS Match</p>
            </div>

            <div class="score">
                <h2>{format_score}%</h2>
                <p>Format Score</p>
            </div>

            <div class="score">
                <h2>{final_score}%</h2>
                <p>Final Score</p>
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
                {added_html}
            </ul>

        </div>

        <div class="card">

            <h2>Format Analysis</h2>

            <ul>
                {format_html}
            </ul>

        </div>

        <div class="card">

            <h2>Corrected Resume</h2>

            <div class="resume">
{safe_resume}
            </div>

        </div>

        <div class="card">

            <form action="/download-docx" method="post">

                <input
                    type="hidden"
                    name="resume_text"
                    value="{html.escape(encoded_resume)}"
                >

                <button type="submit">
                    Download Corrected DOCX
                </button>

            </form>

            <br><br>

            <a href="/">
                Upload Another Resume
            </a>

        </div>

    </div>

    </body>

    </html>
    """


# ============================================================
# DOWNLOAD DOCX
# ============================================================

@app.post("/download-docx")
async def download_docx(resume_text: str = Form(...)):

    import base64

    try:

        decoded = base64.b64decode(
            resume_text
        ).decode("utf-8")

    except Exception:

        decoded = resume_text

    document = create_docx(decoded)

    return StreamingResponse(
        document,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition":
            "attachment; filename=optimized_resume.docx"
        }
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Universal AI Resume Suite"
    }
