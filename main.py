from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.units import mm

import io
import re
import html
import base64


app = FastAPI(title="Universal AI Resume Suite")


# ============================================================
# KEYWORD GROUPS
# ============================================================

KEYWORD_GROUPS = {
    "Programming Languages": [
        "python", "java", "c", "c++", "c#", "javascript",
        "typescript", "go", "golang", "rust", "kotlin",
        "swift", "php", "ruby", "scala", "r", "matlab", "dart"
    ],

    "Web Technologies": [
        "html", "html5", "css", "css3", "javascript",
        "react", "react.js", "reactjs", "angular", "vue",
        "vue.js", "node.js", "nodejs", "express",
        "express.js", "bootstrap", "tailwind", "next.js",
        "nextjs", "django", "flask", "fastapi",
        "rest api", "restful api"
    ],

    "Database": [
        "sql", "mysql", "postgresql", "postgres",
        "mongodb", "oracle", "sqlite", "redis",
        "firebase", "database", "database management", "nosql"
    ],

    "Tools": [
        "git", "github", "gitlab", "bitbucket",
        "visual studio code", "vs code", "docker",
        "postman", "jira", "jenkins", "linux",
        "windows", "npm", "maven", "gradle"
    ],

    "Cloud": [
        "aws", "amazon web services", "azure",
        "microsoft azure", "google cloud", "gcp",
        "kubernetes", "terraform"
    ],

    "AI & Data": [
        "artificial intelligence", "ai", "machine learning",
        "ml", "deep learning", "nlp",
        "natural language processing", "pandas", "numpy",
        "scikit-learn", "tensorflow", "pytorch",
        "opencv", "data analysis", "data science"
    ],

    "Engineering": [
        "autocad", "solidworks", "catia", "ansys",
        "embedded systems", "microcontroller",
        "arduino", "raspberry pi", "iot",
        "internet of things"
    ],

    "Business": [
        "sales", "marketing", "finance", "accounting",
        "excel", "microsoft excel", "power bi",
        "tableau", "business analysis", "project management"
    ],

    "Pharmacy": [
        "pharmacology", "pharmaceutics",
        "pharmaceutical chemistry", "clinical pharmacy",
        "pharmacovigilance", "drug safety",
        "drug development", "quality control",
        "quality assurance", "gmp", "glp",
        "regulatory affairs"
    ],

    "Soft Skills": [
        "communication", "leadership", "teamwork",
        "team player", "problem solving", "problem-solving",
        "time management", "adaptability",
        "quick learner", "critical thinking"
    ]
}


# ============================================================
# STANDARD CAPITALIZATION
# ============================================================

STANDARD_NAMES = {
    "python": "Python",
    "java": "Java",
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
    "vue": "Vue",
    "vue.js": "Vue.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express",
    "express.js": "Express.js",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "oracle": "Oracle",
    "sqlite": "SQLite",
    "firebase": "Firebase",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "docker": "Docker",
    "postman": "Postman",
    "linux": "Linux",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "google cloud": "Google Cloud",
    "gcp": "GCP",
    "kubernetes": "Kubernetes",
    "artificial intelligence": "Artificial Intelligence",
    "ai": "AI",
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
    "power bi": "Power BI",
    "microsoft excel": "Microsoft Excel",
    "excel": "Excel",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "rest api": "REST API",
    "restful api": "REST API"
}


# ============================================================
# HELPERS
# ============================================================

def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def clean_text(text):
    text = text.replace("\r", "\n")
    text = text.replace("•", "•")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages)


def keyword_exists(text, keyword):
    text = normalize(text)
    keyword = normalize(keyword)

    pattern = r"(?<![a-zA-Z0-9])" + re.escape(keyword) + r"(?![a-zA-Z0-9])"

    return bool(re.search(pattern, text))


def find_job_keywords(job_description):
    found = []

    for group, keywords in KEYWORD_GROUPS.items():
        for keyword in keywords:
            if keyword_exists(job_description, keyword):
                found.append(keyword)

    return list(dict.fromkeys(found))


def find_missing_keywords(resume_text, job_keywords):
    missing = []

    for keyword in job_keywords:
        if not keyword_exists(resume_text, keyword):
            missing.append(keyword)

    return missing


def display_keyword(keyword):
    return STANDARD_NAMES.get(keyword.lower(), keyword)


def get_keyword_group(keyword):
    key = keyword.lower()

    for group, keywords in KEYWORD_GROUPS.items():
        if key in [x.lower() for x in keywords]:
            return group

    return "Technical Skills"


# ============================================================
# FORMATTING
# ============================================================

def fix_common_formatting(text):
    text = text.replace("\u00a0", " ")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\s+([,.;:])", r"\1", text)

    text = text.replace("▪", "•")
    text = text.replace("●", "•")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\n[ \t]+", "\n", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def fix_keyword_capitalization(text):
    for original, proper in sorted(
        STANDARD_NAMES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(original) + r"(?![a-zA-Z0-9])"

        text = re.sub(
            pattern,
            proper,
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# ADD MISSING KEYWORDS TO CORRECT SKILLS CATEGORY
# ============================================================

def add_missing_keywords(text, missing_keywords):

    if not missing_keywords:
        return text

    lines = text.splitlines()

    skills_start = -1
    skills_end = len(lines)

    section_names = [
        "education",
        "experience",
        "work experience",
        "project",
        "projects",
        "certifications",
        "activities",
        "activities & interests",
        "interests",
        "strengths"
    ]

    for i, line in enumerate(lines):

        clean = normalize(line)

        if (
            clean in ["technical skills", "skills", "technical skill"]
            or clean.startswith("technical skills")
        ):
            skills_start = i
            break

    if skills_start == -1:

        insert_at = len(lines)

        for i, line in enumerate(lines):

            clean = normalize(line)

            if clean in section_names:
                insert_at = i
                break

        skills_block = [
            "",
            "TECHNICAL SKILLS"
        ]

        for group in KEYWORD_GROUPS.keys():

            group_keywords = []

            for keyword in missing_keywords:

                if get_keyword_group(keyword) == group:
                    group_keywords.append(display_keyword(keyword))

            if group_keywords:
                skills_block.append(
                    f"{group}: " + ", ".join(group_keywords)
                )

        lines[insert_at:insert_at] = skills_block

        return "\n".join(lines)

    for i in range(skills_start + 1, len(lines)):

        clean = normalize(lines[i])

        if clean in section_names or clean.upper() in [
            x.upper() for x in section_names
        ]:
            skills_end = i
            break

    skill_lines = lines[skills_start + 1:skills_end]

    existing_groups = {}

    for i, line in enumerate(skill_lines):

        if ":" in line:

            group = line.split(":", 1)[0].strip()

            existing_groups[group.lower()] = (
                skills_start + 1 + i
            )

    additions = {}

    for keyword in missing_keywords:

        group = get_keyword_group(keyword)
        proper = display_keyword(keyword)

        additions.setdefault(group, []).append(proper)

    offset = 0

    for group, keywords in additions.items():

        group_position = None

        for existing_group, position in existing_groups.items():

            if existing_group == group.lower():
                group_position = position + offset
                break

        if group_position is not None:

            current_line = lines[group_position]

            current_value = current_line.split(":", 1)[1].strip()

            existing_values = [
                x.strip().lower()
                for x in current_value.split(",")
            ]

            for keyword in keywords:

                if keyword.lower() not in existing_values:
                    current_value += ", " + keyword
                    existing_values.append(keyword.lower())

            lines[group_position] = (
                current_line.split(":", 1)[0]
                + ": "
                + current_value
            )

        else:

            insert_position = skills_end + offset

            lines.insert(
                insert_position,
                f"{group}: {', '.join(keywords)}"
            )

            offset += 1

    return "\n".join(lines)


# ============================================================
# FORMAT ANALYSIS
# ============================================================

def analyze_resume_format(text):

    issues = []
    score = 100

    lines = text.splitlines()

    normalized_text = normalize(text)

    if "skills" not in normalized_text:
        issues.append("Skills section not clearly detected.")
        score -= 10

    if "education" not in normalized_text:
        issues.append("Education section not clearly detected.")
        score -= 10

    if "\n\n\n" in text:
        issues.append("Excessive blank lines detected.")
        score -= 5

    if re.search(r" {2,}", text):
        issues.append("Inconsistent spacing detected.")
        score -= 5

    if re.search(r"[•●▪]\s*[•●▪]", text):
        issues.append("Broken bullet formatting detected.")
        score -= 5

    return max(score, 0), issues


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats(job_keywords, corrected_text):

    if not job_keywords:
        return 100

    matched = 0

    for keyword in job_keywords:

        if keyword_exists(corrected_text, keyword):
            matched += 1

    return round((matched / len(job_keywords)) * 100)


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf(text):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm,
        title="Corrected Resume"
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "Name",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        spaceBefore=7,
        spaceAfter=3
    )

    normal_style = ParagraphStyle(
        "NormalResume",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        spaceAfter=2
    )

    skill_style = ParagraphStyle(
        "Skill",
        parent=normal_style,
        leftIndent=0,
        firstLineIndent=0,
        spaceAfter=2
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=normal_style,
        leftIndent=12,
        firstLineIndent=-7,
        spaceAfter=2
    )

    story = []

    lines = text.splitlines()

    # Remove empty beginning/end lines
    lines = [x.strip() for x in lines]

    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop()

    section_titles = {
        "career objective",
        "education",
        "technical skills",
        "skills",
        "project",
        "projects",
        "experience",
        "work experience",
        "certifications",
        "strengths",
        "activities & interests",
        "activities and interests",
        "interests"
    }

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if lines:

        name = lines[0]

        story.append(
            Paragraph(
                html.escape(name),
                name_style
            )
        )

        lines = lines[1:]

    # --------------------------------------------------------
    # CONTACT LINE
    # --------------------------------------------------------

    if lines:

        contact_parts = []

        while lines:

            candidate = lines[0]

            if (
                "@" in candidate
                or "|" in candidate
                or re.search(r"\d{7,}", candidate)
            ):
                contact_parts.append(candidate)
                lines.pop(0)
            else:
                break

        if contact_parts:

            contact = " | ".join(contact_parts)

            story.append(
                Paragraph(
                    html.escape(contact),
                    contact_style
                )
            )

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        normalized = normalize(line)

        # Section heading
        if normalized in section_titles:

            current_section = normalized

            story.append(
                Paragraph(
                    html.escape(line.upper()),
                    section_style
                )
            )

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.6,
                    color=colors.black,
                    spaceBefore=0,
                    spaceAfter=4
                )
            )

            continue

        # Skill category
        if ":" in line and current_section in [
            "technical skills",
            "skills"
        ]:

            category, value = line.split(":", 1)

            paragraph = (
                "<b>"
                + html.escape(category.strip())
                + ":</b> "
                + html.escape(value.strip())
            )

            story.append(
                Paragraph(
                    paragraph,
                    skill_style
                )
            )

            continue

        # Bullet
        if line.startswith(("•", "-", "*")):

            line = re.sub(
                r"^[•\-*]\s*",
                "",
                line
            )

            story.append(
                Paragraph(
                    "• " + html.escape(line),
                    bullet_style
                )
            )

            continue

        # Project title / education title
        if current_section in [
            "project",
            "projects",
            "experience",
            "work experience",
            "education"
        ]:

            if (
                len(line) < 90
                and not line.endswith(".")
                and not line.startswith("CGPA")
                and not line.startswith("Project:")
            ):

                story.append(
                    Paragraph(
                        "<b>"
                        + html.escape(line)
                        + "</b>",
                        normal_style
                    )
                )

                continue

        # Normal paragraph
        story.append(
            Paragraph(
                html.escape(line),
                normal_style
            )
        )

    document.build(story)

    buffer.seek(0)

    return buffer


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
    margin: 0;
    padding: 40px;
}

.container {
    max-width: 700px;
    margin: auto;
    background: white;
    padding: 35px;
    border-radius: 12px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.08);
}

h1 {
    text-align: center;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}

label {
    display: block;
    font-weight: bold;
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
    height: 180px;
    resize: vertical;
}

button {
    width: 100%;
    margin-top: 25px;
    padding: 14px;
    background: #111827;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #000;
}

.note {
    margin-top: 20px;
    color: #666;
    font-size: 13px;
    text-align: center;
}

</style>

</head>

<body>

<div class="container">

<h1>Universal AI Resume Suite</h1>

<div class="subtitle">
Optimize your resume for the job description
</div>

<form action="/optimize" method="post" enctype="multipart/form-data">

<label>Upload Resume PDF</label>

<input
    type="file"
    name="resume"
    accept=".pdf"
    required
>

<label>Job Description / Requirements</label>

<textarea
    name="job_description"
    placeholder="Paste the job requirements here..."
    required
></textarea>

<button type="submit">
Analyze & Optimize Resume
</button>

</form>

<div class="note">
Your original resume is never changed.
</div>

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
            "<h2>Could not read text from this PDF.</h2>",
            status_code=400
        )

    # Clean original
    corrected_text = clean_text(original_text)

    # Job keywords
    job_keywords = find_job_keywords(job_description)

    # Missing keywords
    missing_keywords = find_missing_keywords(
        corrected_text,
        job_keywords
    )

    # Formatting
    corrected_text = fix_common_formatting(
        corrected_text
    )

    # Capitalization
    corrected_text = fix_keyword_capitalization(
        corrected_text
    )

    # Add missing keywords to correct category
    corrected_text = add_missing_keywords(
        corrected_text,
        missing_keywords
    )

    # Final formatting
    corrected_text = fix_common_formatting(
        corrected_text
    )

    # Format score
    format_score, format_issues = analyze_resume_format(
        corrected_text
    )

    # ATS
    ats_score = calculate_ats(
        job_keywords,
        corrected_text
    )

    # Final score
    final_score = round(
        (ats_score * 0.7) +
        (format_score * 0.3)
    )

    # Corrections count
    correction_count = (
        len(missing_keywords)
        + len(format_issues)
    )

    # Encode corrected text
    encoded = base64.b64encode(
        corrected_text.encode("utf-8")
    ).decode("utf-8")

    keyword_html = ""

    if missing_keywords:

        items = []

        for keyword in missing_keywords:

            items.append(
                f"<li><b>{html.escape(display_keyword(keyword))}</b>"
                f" → {html.escape(get_keyword_group(keyword))}</li>"
            )

        keyword_html = (
            "<h3>Automatically optimized keywords</h3>"
            "<ul>"
            + "".join(items)
            + "</ul>"
        )

    else:

        keyword_html = """
        <h3>Keywords</h3>
        <p>No missing job keywords detected.</p>
        """

    issues_html = ""

    if format_issues:

        issues_html = (
            "<h3>Formatting checks</h3>"
            "<ul>"
            + "".join(
                f"<li>{html.escape(issue)}</li>"
                for issue in format_issues
            )
            + "</ul>"
        )

    else:

        issues_html = """
        <h3>Formatting checks</h3>
        <p>No major formatting issues detected.</p>
        """

    return f"""
<!DOCTYPE html>
<html>

<head>

<title>Resume Optimization Complete</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    margin: 0;
    padding: 40px;
}}

.container {{
    max-width: 750px;
    margin: auto;
    background: white;
    padding: 35px;
    border-radius: 12px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.08);
}}

h1 {{
    text-align: center;
}}

.success {{
    text-align: center;
    color: #15803d;
    font-size: 18px;
    margin-bottom: 25px;
}}

.scores {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 25px 0;
}}

.score {{
    background: #f3f4f6;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}}

.score strong {{
    display: block;
    font-size: 28px;
}}

.download {{
    display: block;
    width: 100%;
    box-sizing: border-box;
    padding: 15px;
    background: #111827;
    color: white;
    text-decoration: none;
    text-align: center;
    border-radius: 8px;
    font-size: 17px;
    margin-top: 30px;
}}

.download:hover {{
    background: #000;
}}

.back {{
    display: block;
    text-align: center;
    margin-top: 20px;
    color: #555;
}}

ul {{
    line-height: 1.8;
}}

</style>

</head>

<body>

<div class="container">

<h1>Resume Optimization Complete</h1>

<div class="success">
Your resume has been checked and optimized.
</div>

<div class="scores">

<div class="score">
<strong>{ats_score}%</strong>
ATS Match
</div>

<div class="score">
<strong>{format_score}%</strong>
Format Score
</div>

<div class="score">
<strong>{final_score}%</strong>
Final Score
</div>

</div>

<p>
<strong>Corrections / optimizations:</strong>
{correction_count}
</p>

{keyword_html}

{issues_html}

<p>
The corrected resume is not displayed here.
Click below to generate the final professional PDF.
</p>

<form action="/download-pdf" method="post">

<input
    type="hidden"
    name="resume_data"
    value="{encoded}"
>

<button
    type="submit"
    class="download"
>
Download Corrected Resume PDF
</button>

</form>

<a class="back" href="/">
Upload Another Resume
</a>

</div>

</body>

</html>
"""


# ============================================================
# DOWNLOAD PDF
# ============================================================

@app.post("/download-pdf")
async def download_pdf(
    resume_data: str = Form(...)
):

    try:

        corrected_text = base64.b64decode(
            resume_data
        ).decode("utf-8")

    except Exception:

        return HTMLResponse(
            "<h2>Could not generate the resume.</h2>",
            status_code=400
        )

    pdf_buffer = create_pdf(
        corrected_text
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            'attachment; filename="Corrected_Resume.pdf"'
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
