from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader

import io
import re
import html
import base64

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
        "html", "html5", "css", "css3", "javascript",
        "react", "react.js", "reactjs", "angular", "vue", "vue.js",
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
        "project management"
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


# ============================================================
# STANDARD CAPITALIZATION
# ============================================================

STANDARD_NAMES = {
    "python": "Python",
    "java": "Java",
    "c": "C",
    "c++": "C++",
    "c#": "C#",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "html": "HTML",
    "html5": "HTML5",
    "css": "CSS",
    "css3": "CSS3",
    "react": "React",
    "react.js": "React.js",
    "reactjs": "React.js",
    "angular": "Angular",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "oracle": "Oracle",
    "sqlite": "SQLite",
    "redis": "Redis",
    "firebase": "Firebase",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "docker": "Docker",
    "postman": "Postman",
    "jira": "Jira",
    "jenkins": "Jenkins",
    "linux": "Linux",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "ai": "AI",
    "artificial intelligence": "Artificial Intelligence",
    "machine learning": "Machine Learning",
    "ml": "ML",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "opencv": "OpenCV",
    "matlab": "MATLAB",
    "excel": "Excel",
    "power bi": "Power BI",
    "tableau": "Tableau",
}


# ============================================================
# SECTION NAMES
# ============================================================

SECTION_NAMES = {
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
# TEXT FUNCTIONS
# ============================================================

def normalize(text):
    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
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
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    return clean_text("\n".join(pages))


# ============================================================
# KEYWORD DETECTION
# ============================================================

def keyword_exists(text, keyword):

    text = normalize(text)
    keyword = normalize(keyword)

    if keyword in ["c", "r"]:
        return bool(re.search(r"\b" + re.escape(keyword) + r"\b", text))

    return bool(
        re.search(
            r"(?<![a-z0-9])" +
            re.escape(keyword) +
            r"(?![a-z0-9])",
            text
        )
    )


def find_job_keywords(job_description):

    found = []

    for group, keywords in KEYWORD_GROUPS.items():

        for keyword in keywords:

            if keyword_exists(job_description, keyword):

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
# SECTION / CATEGORY
# ============================================================

def get_keyword_group(keyword):

    keyword = normalize(keyword)

    for group, keywords in KEYWORD_GROUPS.items():

        if keyword in [normalize(x) for x in keywords]:
            return group

    return "Programming Languages"


def display_keyword(keyword):

    keyword = normalize(keyword)

    return STANDARD_NAMES.get(
        keyword,
        keyword.title()
    )


# ============================================================
# FORMAT / TEXT CORRECTION
# ============================================================

def fix_common_formatting(text):

    corrections = 0

    # Remove repeated spaces
    new_text = re.sub(r"[ \t]+", " ", text)

    if new_text != text:
        corrections += 1

    text = new_text

    # Fix spaces before punctuation
    new_text = re.sub(r"\s+([,.;:])", r"\1", text)

    if new_text != text:
        corrections += 1

    text = new_text

    # Normalize bullet characters
    text = text.replace("• •", "•")
    text = text.replace("·", "•")

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text, corrections


def fix_keyword_capitalization(text):

    corrections = 0

    # Longest keywords first
    names = sorted(
        STANDARD_NAMES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for wrong, correct in names:

        pattern = re.compile(
            r"(?<![A-Za-z0-9])" +
            re.escape(wrong) +
            r"(?![A-Za-z0-9])",
            re.IGNORECASE
        )

        new_text = pattern.sub(correct, text)

        if new_text != text:
            corrections += 1
            text = new_text

    return text, corrections


# ============================================================
# ADD MISSING KEYWORDS
# ============================================================

def add_missing_keywords(text, missing_keywords):

    lines = text.splitlines()

    # Find skills section
    skills_index = -1

    for i, line in enumerate(lines):

        clean = normalize(line)

        if clean in [
            "skills",
            "technical skills",
            "key skills",
            "technical expertise"
        ]:

            skills_index = i
            break

    # If no skills section exists
    if skills_index == -1:

        skills_index = 0

        lines.insert(
            0,
            "TECHNICAL SKILLS"
        )

        lines.insert(
            1,
            "Programming Languages: "
        )

    added = []

    for keyword in missing_keywords:

        display = display_keyword(keyword)

        group = get_keyword_group(keyword)

        found = False

        # Search for existing category
        for i in range(
            skills_index + 1,
            min(skills_index + 50, len(lines))
        ):

            lower = normalize(lines[i])

            category_variants = {
                "Programming Languages": [
                    "programming languages:",
                    "programming language:"
                ],

                "Web Technologies": [
                    "web technologies:",
                    "web technology:"
                ],

                "Database": [
                    "database:",
                    "databases:"
                ],

                "Tools": [
                    "tools:",
                    "software:"
                ],

                "Cloud": [
                    "cloud:",
                    "cloud technologies:"
                ],

                "AI & Data": [
                    "ai & data:",
                    "ai:",
                    "data:"
                ],

                "Engineering": [
                    "engineering:"
                ],

                "Business": [
                    "business:"
                ],

                "Pharmacy": [
                    "pharmacy:"
                ],

                "Soft Skills": [
                    "soft skills:"
                ]
            }

            variants = category_variants.get(
                group,
                []
            )

            if any(lower.startswith(v) for v in variants):

                if normalize(display) not in lower:

                    lines[i] = (
                        lines[i].rstrip() +
                        ", " +
                        display
                    )

                    added.append(display)

                found = True
                break

        # Category does not exist
        if not found:

            # Find next major section
            insert_at = len(lines)

            for i in range(
                skills_index + 1,
                len(lines)
            ):

                lower = normalize(lines[i])

                if lower in [
                    "experience",
                    "work experience",
                    "education",
                    "projects",
                    "project",
                    "certifications",
                    "activities",
                    "activities & interests"
                ]:

                    insert_at = i
                    break

            lines.insert(
                insert_at,
                f"{group}: {display}"
            )

            added.append(display)

    return "\n".join(lines), added


# ============================================================
# FORMAT SCORE
# ============================================================

def analyze_resume_format(text):

    issues = []
    score = 100

    lower = normalize(text)

    # Missing sections
    if not any(
        x in lower
        for x in SECTION_NAMES["skills"]
    ):
        issues.append("Skills section is missing.")
        score -= 10

    if not any(
        x in lower
        for x in SECTION_NAMES["education"]
    ):
        issues.append("Education section is missing.")
        score -= 10

    # Broken spacing
    if re.search(r"[ \t]{2,}", text):
        issues.append("Extra spacing detected.")
        score -= 5

    # Excessive blank lines
    if re.search(r"\n{4,}", text):
        issues.append("Excessive blank lines detected.")
        score -= 5

    # Broken bullets
    if "• •" in text:
        issues.append("Broken bullet formatting detected.")
        score -= 5

    score = max(score, 0)

    return score, issues


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats(job_keywords, corrected_resume):

    if not job_keywords:
        return 0

    matched = 0

    for keyword in job_keywords:

        if keyword_exists(
            corrected_resume,
            keyword
        ):
            matched += 1

    return round(
        (matched / len(job_keywords)) * 100
    )


# ============================================================
# CREATE CLEAN DOCX
# ============================================================

def create_docx(text):

    document = Document()

    section = document.sections[0]

    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)

    style = document.styles["Normal"]

    style.font.name = "Arial"
    style.font.size = Pt(10)

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        upper = line.upper()

        # Main headings
        if upper in [
            "SUMMARY",
            "CAREER OBJECTIVE",
            "EDUCATION",
            "EXPERIENCE",
            "WORK EXPERIENCE",
            "PROJECTS",
            "PROJECT",
            "TECHNICAL SKILLS",
            "SKILLS",
            "CERTIFICATIONS",
            "ACTIVITIES & INTERESTS",
            "INTERESTS",
            "HOBBIES"
        ]:

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_before = Pt(7)
            paragraph.paragraph_format.space_after = Pt(3)

            run = paragraph.add_run(
                line.upper()
            )

            run.bold = True
            run.font.size = Pt(12)

            continue

        # Skill categories
        skill_groups = [
            "Programming Languages:",
            "Web Technologies:",
            "Database:",
            "Tools:",
            "Cloud:",
            "AI & Data:",
            "Engineering:",
            "Business:",
            "Pharmacy:",
            "Soft Skills:"
        ]

        if any(
            line.startswith(x)
            for x in skill_groups
        ):

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(2)

            first, rest = line.split(
                ":",
                1
            )

            run = paragraph.add_run(
                first + ":"
            )

            run.bold = True

            paragraph.add_run(
                rest
            )

            continue

        paragraph = document.add_paragraph()

        paragraph.paragraph_format.space_after = Pt(2)

        # Convert bullet lines
        if line.startswith(("•", "-", "*")):

            line = re.sub(
                r"^[•\-\*]\s*",
                "",
                line
            )

            paragraph.style = document.styles["Normal"]

            paragraph.add_run(
                "• " + line
            )

        else:

            paragraph.add_run(line)

    output = io.BytesIO()

    document.save(output)

    output.seek(0)

    return output


# ============================================================
# HOME
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
        font-family: Arial;
        background: #f4f6f8;
        padding: 40px;
    }

    .box {
        max-width: 800px;
        margin: auto;
        background: white;
        padding: 35px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
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
        box-sizing: border-box;
        margin-top: 8px;
        padding: 12px;
        border: 1px solid #ccc;
        border-radius: 8px;
    }

    textarea {
        height: 220px;
    }

    button {
        width: 100%;
        padding: 15px;
        margin-top: 25px;
        border: none;
        border-radius: 8px;
        background: #111827;
        color: white;
        font-size: 16px;
        cursor: pointer;
    }

    </style>

    </head>

    <body>

    <div class="box">

    <h1>Universal AI Resume Suite</h1>

    <form
        action="/optimize"
        method="post"
        enctype="multipart/form-data"
    >

        <label>Upload Resume PDF</label>

        <input
            type="file"
            name="resume"
            accept=".pdf"
            required
        >

        <label>Paste Job Description</label>

        <textarea
            name="job_description"
            placeholder="Paste the complete job description here..."
            required
        ></textarea>

        <button type="submit">
            Analyze & Correct Resume
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

    original_text = extract_pdf_text(
        file_bytes
    )

    if not original_text.strip():

        return HTMLResponse(
            """
            <h2>Unable to read this PDF.</h2>
            <p>Please upload a text-based PDF.</p>
            """,
            status_code=400
        )

    # --------------------------------------------------------
    # STEP 1: FIND JOB KEYWORDS
    # --------------------------------------------------------

    job_keywords = find_job_keywords(
        job_description
    )

    # --------------------------------------------------------
    # STEP 2: FIND MISSING KEYWORDS
    # --------------------------------------------------------

    missing_keywords = []

    for keyword in job_keywords:

        if not keyword_exists(
            original_text,
            keyword
        ):

            missing_keywords.append(
                keyword
            )

    # --------------------------------------------------------
    # STEP 3: FIX FORMATTING
    # --------------------------------------------------------

    corrected_text, formatting_corrections = \
        fix_common_formatting(
            original_text
        )

    # --------------------------------------------------------
    # STEP 4: FIX CAPITALIZATION
    # --------------------------------------------------------

    corrected_text, capitalization_corrections = \
        fix_keyword_capitalization(
            corrected_text
        )

    # --------------------------------------------------------
    # STEP 5: ADD MISSING KEYWORDS
    # --------------------------------------------------------

    corrected_text, added_keywords = \
        add_missing_keywords(
            corrected_text,
            missing_keywords
        )

    # --------------------------------------------------------
    # STEP 6: FORMAT ANALYSIS
    # --------------------------------------------------------

    format_score, format_issues = \
        analyze_resume_format(
            corrected_text
        )

    # --------------------------------------------------------
    # STEP 7: ATS SCORE
    # --------------------------------------------------------

    ats_score = calculate_ats(
        job_keywords,
        corrected_text
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    final_score = round(
        (ats_score * 0.7) +
        (format_score * 0.3)
    )

    total_corrections = (
        formatting_corrections +
        capitalization_corrections +
        len(added_keywords)
    )

    # --------------------------------------------------------
    # SAVE CORRECTED RESUME TEMPORARILY IN MEMORY
    # --------------------------------------------------------

    encoded_resume = base64.b64encode(
        corrected_text.encode("utf-8")
    ).decode("utf-8")

    # --------------------------------------------------------
    # DISPLAY ONLY RESULTS
    # NEVER DISPLAY RESUME TEXT
    # --------------------------------------------------------

    added_html = ""

    for keyword in added_keywords:

        added_html += (
            "<li>" +
            html.escape(keyword) +
            " → " +
            html.escape(
                get_keyword_group(keyword)
            ) +
            "</li>"
        )

    if not added_html:

        added_html = (
            "<li>No new job keywords were required.</li>"
        )

    issues_html = ""

    for issue in format_issues:

        issues_html += (
            "<li>" +
            html.escape(issue) +
            "</li>"
        )

    if not issues_html:

        issues_html = (
            "<li>No major formatting problems detected.</li>"
        )

    # --------------------------------------------------------
    # RESULT PAGE
    # --------------------------------------------------------

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

    <title>Resume Optimization Complete</title>

    <style>

    body {{
        font-family: Arial;
        background: #f4f6f8;
        padding: 40px;
    }}

    .container {{
        max-width: 900px;
        margin: auto;
    }}

    .card {{
        background: white;
        padding: 30px;
        margin-bottom: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    }}

    .success {{
        text-align: center;
    }}

    .success h1 {{
        font-size: 30px;
    }}

    .scores {{
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }}

    .score {{
        flex: 1;
        min-width: 180px;
        background: #f1f3f5;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }}

    .score h2 {{
        font-size: 34px;
        margin: 0;
    }}

    .download {{
        width: 100%;
        padding: 17px;
        border: none;
        border-radius: 9px;
        background: #111827;
        color: white;
        font-size: 17px;
        cursor: pointer;
    }}

    .note {{
        background: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }}

    </style>

    </head>

    <body>

    <div class="container">

        <div class="card success">

            <h1>✅ Resume Optimization Complete</h1>

            <p>
            Your resume has been checked and automatically corrected.
            </p>

            <p>
            Your original uploaded resume has not been changed.
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

            <div class="score">

                <h2>{total_corrections}</h2>

                <p>Corrections</p>

            </div>

        </div>

        <div class="card">

            <h2>🔑 Automatically Added Keywords</h2>

            <ul>

                {added_html}

            </ul>

        </div>

        <div class="card">

            <h2>📐 Format Check</h2>

            <ul>

                {issues_html}

            </ul>

        </div>

        <div class="card">

            <h2>📄 Your Resume Is Ready</h2>

            <p>
            The corrected resume is ready.
            </p>

            <p>
            <b>
            The resume itself is hidden until you download it.
            </b>
            </p>

            <form
                action="/download-docx"
                method="post"
            >

                <input
                    type="hidden"
                    name="resume_text"
                    value="{html.escape(encoded_resume)}"
                >

                <button
                    class="download"
                    type="submit"
                >
                    ⬇ Download Corrected Resume
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


# ============================================================
# DOWNLOAD
# ============================================================

@app.post("/download-docx")
async def download_docx(
    resume_text: str = Form(...)
):

    try:

        corrected_text = base64.b64decode(
            resume_text
        ).decode("utf-8")

    except Exception:

        corrected_text = resume_text

    document = create_docx(
        corrected_text
    )

    return StreamingResponse(
        document,
        media_type=
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

        headers={
            "Content-Disposition":
            "attachment; filename=Corrected_Resume.docx"
        }
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Universal AI Resume Suite"
    }
