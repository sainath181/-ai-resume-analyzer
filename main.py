```python
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import pypdf
import io
import re
import html

app = FastAPI(title="Universal AI Resume Suite")


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_bytes):
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    return "\n".join(pages)


# ============================================================
# SPELLING CORRECTION
# ============================================================

def fix_spelling(text):
    replacements = {
        "experiance": "Experience",
        "managment": "Management",
        "engeneering": "Engineering",
        "developement": "Development",
        "programing": "Programming",
        "analitics": "Analytics",
        "communicaton": "Communication",
        "responsiblities": "Responsibilities",
        "acheivement": "Achievement",
        "achievment": "Achievement",
    }

    for wrong, correct in replacements.items():
        text = re.sub(
            r"\b" + re.escape(wrong) + r"\b",
            correct,
            text,
            flags=re.IGNORECASE,
        )

    return text


# ============================================================
# WORD EXTRACTION
# ============================================================

def get_words(text):
    return set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b", text.lower()))


# ============================================================
# SKILLS DATABASE
# ============================================================

SKILLS = {
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "cpp",
    "c++",
    "csharp",
    "sql",
    "html",
    "css",
    "php",
    "ruby",
    "go",
    "rust",
    "kotlin",
    "swift",

    # Web
    "react",
    "angular",
    "vue",
    "node",
    "nodejs",
    "express",
    "django",
    "flask",
    "fastapi",
    "bootstrap",
    "tailwind",

    # Database
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "redis",
    "firebase",

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

    # AI / Data
    "ai",
    "artificial",
    "intelligence",
    "machine",
    "learning",
    "deep",
    "nlp",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "scikit",
    "matplotlib",
    "tableau",
    "powerbi",
    "analytics",

    # Engineering
    "autocad",
    "solidworks",
    "ansys",
    "revit",
    "staad",
    "plc",
    "scada",
    "matlab",

    # Business
    "marketing",
    "finance",
    "hr",
    "sales",
    "management",
    "business",
    "accounting",
    "strategy",
    "leadership",

    # Pharmacy
    "pharmacy",
    "clinical",
    "drug",
    "pharmacology",
    "formulation",
    "hplc",
    "validation",
    "medical",
    "pharma",
}


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "and",
    "the",
    "is",
    "in",
    "to",
    "of",
    "for",
    "with",
    "a",
    "an",
    "on",
    "that",
    "this",
    "as",
    "by",
    "at",
    "from",
    "it",
    "or",
    "be",
    "are",
    "was",
    "were",
    "will",
    "have",
    "has",
    "had",
    "you",
    "your",
    "our",
    "their",
    "we",
    "they",
    "job",
    "role",
    "candidate",
    "work",
    "working",
    "company",
    "years",
    "year",
    "experience",
}


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():

    return HTMLResponse(
        content="""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Universal AI Resume Suite</title>

<script src="https://cdn.tailwindcss.com"></script>

</head>

<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-black text-gray-100 min-h-screen">

<div class="min-h-screen flex items-center justify-center p-6">

<div class="max-w-xl w-full bg-slate-900/80 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-2xl">

<header class="text-center mb-8">

<div class="inline-flex items-center bg-blue-500/10 border border-blue-500/30 px-4 py-2 rounded-full text-xs font-bold text-blue-400 mb-5 uppercase tracking-widest">

Premium AI Executive Suite

</div>

<h1 class="text-4xl font-black text-white tracking-tight mb-3">

Universal AI Resume Suite

</h1>

<p class="text-slate-400 text-sm">

AI-powered resume analysis and job matching

</p>

<p class="text-slate-500 text-xs mt-2">

Supports B.Tech, M.Tech, MCA, MBA, Pharmacy, Pharm.D and multiple career streams

</p>

</header>


<form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">


<div class="bg-slate-950 p-5 rounded-2xl border border-slate-800">

<label class="block text-xs font-black text-slate-300 uppercase tracking-widest mb-3">

1. Upload Candidate Resume

</label>

<input
type="file"
name="resume"
accept=".pdf"
required
class="block w-full text-sm text-slate-400 cursor-pointer"
>

<p class="text-xs text-slate-600 mt-2">

Only PDF files are supported.

</p>

</div>


<div>

<label class="block text-xs font-black text-slate-300 uppercase tracking-widest mb-3">

2. Paste Job Description

</label>

<textarea
name="jd"
rows="7"
placeholder="Example: Looking for a Python developer with FastAPI, SQL, AWS and Docker experience..."
required
class="w-full bg-slate-950 text-slate-200 p-4 rounded-2xl border border-slate-800 focus:outline-none focus:border-blue-500 text-sm"
></textarea>

</div>


<button
type="submit"
class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-extrabold py-4 rounded-2xl shadow-xl tracking-widest text-xs uppercase transition-all"
>

Optimize Profile State

</button>

</form>

</div>

</div>

</body>
</html>
"""
    )


# ============================================================
# RESUME ANALYZER
# ============================================================

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(
    resume: UploadFile = File(...),
    jd: str = Form(...)
):

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not resume.filename:
        return HTMLResponse(
            "<h1>No resume uploaded.</h1>",
            status_code=400
        )

    if not resume.filename.lower().endswith(".pdf"):
        return HTMLResponse(
            "<h1>Please upload a PDF resume.</h1>",
            status_code=400
        )


    # --------------------------------------------------------
    # Read PDF
    # --------------------------------------------------------

    contents = await resume.read()

    try:
        resume_text = extract_text_from_pdf(contents)
    except Exception as e:
        return HTMLResponse(
            f"""
            <html>
            <body style="font-family:Arial;padding:40px">
            <h1>Unable to read PDF</h1>
            <p>{html.escape(str(e))}</p>
            <a href="/">Go Back</a>
            </body>
            </html>
            """,
            status_code=400
        )


    if not resume_text.strip():

        return HTMLResponse(
            """
            <html>
            <body style="font-family:Arial;padding:40px">

            <h1>Could not extract text from this PDF.</h1>

            <p>
            Your PDF may be scanned/image-based.
            Please upload a text-based PDF for now.
            </p>

            <a href="/">Go Back</a>

            </body>
            </html>
            """,
            status_code=400
        )


    # --------------------------------------------------------
    # Clean text
    # --------------------------------------------------------

    resume_text = fix_spelling(resume_text)

    jd = jd.strip()

    resume_words = get_words(resume_text)
    jd_words = get_words(jd)


    # --------------------------------------------------------
    # Identify job skills
    # --------------------------------------------------------

    required_skills = set()

    for word in jd_words:

        if word in SKILLS:
            required_skills.add(word)

    # Extra meaningful words from JD
    meaningful_words = {
        word
        for word in jd_words
        if len(word) > 2 and word not in STOP_WORDS
    }


    # --------------------------------------------------------
    # Matching
    # --------------------------------------------------------

    matched_skills = required_skills.intersection(resume_words)

    missing_skills = required_skills.difference(resume_words)


    # --------------------------------------------------------
    # If JD contains no recognized skills
    # --------------------------------------------------------

    if required_skills:

        skill_score = (
            len(matched_skills) /
            len(required_skills)
        ) * 100

    else:

        matching_words = meaningful_words.intersection(resume_words)

        if meaningful_words:

            skill_score = (
                len(matching_words) /
                len(meaningful_words)
            ) * 100

        else:

            skill_score = 100


    skill_score = max(0, min(100, int(skill_score)))


    # --------------------------------------------------------
    # General resume checks
    # --------------------------------------------------------

    sections = {
        "Education": ["education", "qualification", "academic"],
        "Experience": ["experience", "employment", "work history"],
        "Projects": ["projects", "project"],
        "Skills": ["skills", "technical skills"],
        "Contact": ["email", "phone", "mobile"],
    }


    section_score = 0

    for keywords in sections.values():

        if any(keyword in resume_text.lower() for keyword in keywords):

            section_score += 1


    section_percentage = int(
        (section_score / len(sections)) * 100
    )


    # --------------------------------------------------------
    # Final ATS score
    # --------------------------------------------------------

    final_score = int(
        (skill_score * 0.70) +
        (section_percentage * 0.30)
    )


    final_score = max(0, min(100, final_score))


    # --------------------------------------------------------
    # Display values
    # --------------------------------------------------------

    matched_display = ", ".join(
        sorted(matched_skills)
    )

    if not matched_display:
        matched_display = "No direct skill matches found."


    missing_display = ", ".join(
        sorted(missing_skills)
    )

    if not missing_display:
        missing_display = "Excellent — no major recognized skills are missing."


    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = []

    if missing_skills:

        for skill in sorted(missing_skills)[:5]:

            recommendations.append(
                f"Consider adding genuine experience or projects involving {skill}."
            )

    if section_score < 5:

        recommendations.append(
            "Make sure your resume contains clear Education, Experience, Projects, Skills and Contact sections."
        )

    if "summary" not in resume_text.lower():

        recommendations.append(
            "Consider adding a short professional summary targeted toward the job."
        )

    if not recommendations:

        recommendations.append(
            "Your resume structure looks strong for this job description."
        )


    # --------------------------------------------------------
    # AI-style project suggestions
    # --------------------------------------------------------

    if "python" in required_skills:

        project_suggestion = (
            "Build a Python-based application demonstrating "
            "Python, APIs, databases and real-world problem solving."
        )

    elif "java" in required_skills:

        project_suggestion = (
            "Build a Java application demonstrating "
            "OOP, database integration and REST APIs."
        )

    elif "react" in required_skills:

        project_suggestion = (
            "Build a responsive React application connected "
            "to a backend API and database."
        )

    elif "machine" in required_skills or "learning" in required_skills:

        project_suggestion = (
            "Build an end-to-end machine learning project "
            "including data preparation, model training and evaluation."
        )

    else:

        project_suggestion = (
            "Build a practical project that demonstrates the "
            "most important skills mentioned in the job description."
        )


    # --------------------------------------------------------
    # Safe HTML
    # --------------------------------------------------------

    safe_filename = html.escape(resume.filename)

    matched_html = html.escape(matched_display)

    missing_html = html.escape(missing_display)

    recommendations_html = ""

    for item in recommendations:

        recommendations_html += (
            "<li class='mb-2'>"
            + html.escape(item)
            + "</li>"
        )


    # --------------------------------------------------------
    # RESULT PAGE
    # --------------------------------------------------------

    result_html = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Resume Analysis</title>

<script src="https://cdn.tailwindcss.com"></script>

<style>

@media print {{

    .no-print {{
        display: none !important;
    }}

    body {{
        background: white !important;
    }}

    .print-card {{
        box-shadow: none !important;
        border: none !important;
    }}

}}

</style>

</head>


<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-black text-gray-100 min-h-screen p-6">


<div class="max-w-4xl mx-auto">


<!-- HEADER -->

<div class="text-center mb-8 no-print">

<div class="inline-block bg-blue-500/10 border border-blue-500/30 px-4 py-2 rounded-full text-xs font-bold text-blue-400 uppercase tracking-widest mb-4">

AI Resume Analyzer

</div>

<h1 class="text-4xl font-black text-white">

ATS Optimization Results

</h1>

<p class="text-slate-400 mt-2">

Analysis completed successfully

</p>

</div>


<!-- SCORE -->

<div class="print-card bg-slate-900/80 border border-slate-800 rounded-3xl p-8 shadow-2xl mb-6">


<div class="text-center">

<p class="text-xs text-slate-400 uppercase tracking-widest font-bold">

Overall ATS Score

</p>

<div class="text-7xl font-black text-blue-400 mt-3">

{final_score}%

</div>

<p class="text-sm text-slate-400 mt-3">

Job compatibility score

</p>

</div>


<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">


<div class="bg-slate-950 rounded-2xl p-5 border border-slate-800">

<p class="text-xs text-slate-500 uppercase font-bold">

Skill Match

</p>

<p class="text-3xl font-black text-green-400 mt-2">

{int(skill_score)}%

</p>

</div>


<div class="bg-slate-950 rounded-2xl p-5 border border-slate-800">

<p class="text-xs text-slate-500 uppercase font-bold">

Resume Structure

</p>

<p class="text-3xl font-black text-purple-400 mt-2">

{section_percentage}%

</p>

</div>


</div>

</div>


<!-- MATCHED SKILLS -->

<div class="print-card bg-slate-900/80 border border-slate-800 rounded-3xl p-7 shadow-xl mb-6">

<h2 class="text-lg font-black text-green-400 uppercase tracking-wider">

Matched Skills

</h2>

<p class="text-slate-300 mt-4 leading-relaxed">

{matched_html}

</p>

</div>


<!-- MISSING SKILLS -->

<div class="print-card bg-slate-900/80 border border-slate-800 rounded-3xl p-7 shadow-xl mb-6">

<h2 class="text-lg font-black text-red-400 uppercase tracking-wider">

Missing / Recommended Skills

</h2>

<p class="text-slate-300 mt-4 leading-relaxed">

{missing_html}

</p>

</div>


<!-- RECOMMENDATIONS -->

<div class="print-card bg-slate-900/80 border border-slate-800 rounded-3xl p-7 shadow-xl mb-6">

<h2 class="text-lg font-black text-purple-400 uppercase tracking-wider">

AI Recommendations

</h2>

<ul class="list-disc list-inside text-slate-300 mt-5 leading-relaxed">

{recommendations_html}

</ul>

</div>


<!-- PROJECT -->

<div class="print-card bg-slate-900/80 border border-slate-800 rounded-3xl p-7 shadow-xl mb-6">

<h2 class="text-lg font-black text-blue-400 uppercase tracking-wider">

Recommended Project

</h2>

<p class="text-slate-300 mt-4 leading-relaxed">

{html.escape(project_suggestion)}

</p>

</div>


<!-- FILE -->

<div class="text-center text-xs text-slate-500 mb-8">

Analyzed Resume: {safe_filename}

</div>


<!-- BUTTONS -->

<div class="flex flex-col sm:flex-row gap-4 justify-center no-print">

<button
onclick="window.print()"
class="bg-gradient-to-r from-blue-600 to-purple-600 px-7 py-4 rounded-xl font-black text-xs uppercase tracking-widest"
>

Download / Print Report

</button>


<a
href="/"
class="bg-slate-800 hover:bg-slate-700 px-7 py-4 rounded-xl font-black text-xs uppercase tracking-widest text-center"
>

Analyze Another Resume

</a>

</div>


</div>

</body>

</html>
"""


    return HTMLResponse(
        content=result_html,
        status_code=200
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "running",
        "project": "Universal AI Resume Suite"
    }
```
