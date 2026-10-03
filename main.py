
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdf
import io
import re

app = FastAPI()

def extract_text_from_pdf(file_bytes):
    pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def fix_spelling_and_grammar(text):
    # Dictionary based high-frequency industry standard corrections
    replacements = {
        r"\bautocad\b": "AutoCAD",
        r"\bpython\b": "Python",
        r"\bjava\b": "Java",
        r"\bplc\b": "PLC Systems",
        r"\bbin\b": "been",
        r"\bresponsibilities\b": "Responsibilities",
        r"\bexperiance\b": "Experience",
        r"\bproject\b": "Project",
        r"\bmanagment\b": "Management",
        r"\bengeneering\b": "Engineering",
        r"\bdeveleper\b": "Developer"
    }
    fixed_text = text
    for pattern, replacement in replacements.items():
        fixed_text = re.sub(pattern, replacement, fixed_text, flags=re.IGNORECASE)
    return fixed_text

@app.get("/", response_class=HTMLResponse)
async def read_item():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Resume Parser & Optimizer</title>
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans selection:bg-blue-500 selection:text-white">
        <div class="max-w-4xl mx-auto py-12 px-4 relative">
            <div class="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

            <header class="text-center mb-12 relative">
                <div class="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/30 px-4 py-1.5 rounded-full text-xs font-semibold text-blue-400 mb-4 tracking-wide uppercase">
                    ⚡ AI Auto-Fixer & Professional Formatting Suite
                </div>
                <h1 class="text-5xl font-black tracking-tight text-white mb-3 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-200 to-purple-400">
                    AI Resume Parser & Optimizer
                </h1>
                <p class="text-gray-400 text-lg max-w-2xl mx-auto font-light">
                    Upload your profile to automatically fix spelling mistakes, align layouts, and inject target competencies into a perfect print-ready PDF structure.
                </p>
            </header>

            <div class="bg-slate-900/60 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-slate-800/80 mb-8 relative">
                <div class="flex items-center space-x-3 mb-6 border-b border-slate-800 pb-4">
                    <div class="bg-blue-500/20 p-2 rounded-lg text-blue-400">🎯</div>
                    <h2 class="text-xl font-bold text-white tracking-wide">ATS Optimization Engine</h2>
                </div>

                <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">
                    <div class="group">
                        <label class="block text-sm font-semibold text-slate-300 mb-2">1. Upload Candidate Resume (PDF)</label>
                        <div class="relative bg-slate-950 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-all">
                            <input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer">
                        </div>
                    </div>

                    <div class="group">
                        <label class="block text-sm font-semibold text-slate-300 mb-2">2. Paste Custom Job Description (JD)</label>
                        <textarea name="jd" rows="5" placeholder="Paste target requirements here..." required class="w-full bg-slate-950 text-white p-4 rounded-xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 placeholder:text-slate-600 font-light resize-none transition-all"></textarea>
                    </div>

                    <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 rounded-xl transition duration-300 shadow-lg shadow-blue-500/20 text-md tracking-wide uppercase">
                        Calculate Compatibility Match
                    </button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    resume_text = extract_text_from_pdf(contents)
    clean_text = fix_spelling_and_grammar(resume_text)

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', clean_text)
    phone_match = re.search(r'\+?\d[\d -]{8,12}\d', clean_text)
    email = email_match.group(0) if email_match else "Not Extracted"
    phone = phone_match.group(0) if phone_match else "Not Extracted"

    jd_words = set(re.findall(r'\b\w+\b', jd.lower()))
    resume_words = set(re.findall(r'\b\w+\b', clean_text.lower()))

    stop_words = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are', 'your', 'with'}
    important_jd_keywords = {word for word in jd_words if len(word) > 2 and word not in stop_words}

    matched_skills = important_jd_keywords.intersection(resume_words)
    missing_skills = important_jd_keywords.difference(resume_words)

    match_percentage = int((len(matched_skills) / len(important_jd_keywords)) * 100) if important_jd_keywords else 0
    matched_str = ", ".join([w.upper() for w in list(matched_skills)[:10]]) if matched_skills else "None Detected"
    missing_str = ", ".join([w.upper() for w in list(missing_skills)[:8]]) if missing_skills else "None"

    hidden_input_bullets = []
    ai_rewrite_list = []
    if missing_skills:
        for skill in list(missing_skills)[:3]:
            bullet = f"Utilized {skill.upper()} methodologies and engineering layouts to optimize workflow production configurations and maximize execution safety matrices."
            hidden_input_bullets.append(bullet)
            ai_rewrite_list.append(f"<div class='bg-slate-950 p-4 rounded-xl border border-purple-500/20 mt-3'><p class='text-xs text-purple-400 font-bold tracking-wide uppercase mb-1.5'>🔧 Ready-to-use Bullet Point for {skill.upper()}:</p><p class='text-sm text-slate-300 font-light leading-relaxed'>\\\"{bullet}\\\"</p></div>")
    else:
        ai_rewrite_list.append("<p class='text-sm text-green-400 font-light'>🎉 Perfect Match! No rewrite optimizations required for this target profile state.</p>")
    
    ai_rewrite_str = "".join(ai_rewrite_list)
    bullets_payload = " | ".join(hidden_input_bullets)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI Resume Parser & Optimizer</title>
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div id="report-content" class="max-w-4xl mx-auto py-12 px-4">
            <div class="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 mb-8">
                <h2 class="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">⚡ Extraction Intelligence</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-light">
                    <div><span class="text-slate-500 font-medium">Candidate Profile:</span> <span class="text-white font-semibold">Applicant Details</span></div>
                    <div><span class="text-slate-500 font-medium">Email:</span> <span class="text-slate-300">{email}</span></div>
                    <div><span class="text-slate-500 font-medium">Phone:</span> <span class="text-slate-300">{phone}</span></div>
                </div>
            </div>

            <div class="bg-slate-900/60 p-8 rounded-2xl border border-blue-500/30 shadow-2xl relative mb-8">
                <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
                    <h2 class="text-2xl font-bold text-white tracking-wide flex items-center gap-2">📊 ATS Compatibility Audit Summary</h2>
                    <form action="/download-perfect-resume/" method="post">
                        <input type="hidden" name="orig_text" value="{clean_text.replace('"', '&quot;')}">
                        <input type="hidden" name="bullets" value="{bullets_payload.replace('"', '&quot;')}">
                        <button type="submit" class="bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 px-5 rounded-xl text-xs uppercase tracking-wider transition duration-200 shadow-md shadow-purple-600/20">
                            🤖 Generate Perfect Resume & Download PDF
                        </button>
                    </form>
                </div>

                <div class="flex items-center space-x-6 mb-8 bg-slate-950 p-5 rounded-xl border border-slate-800/50">
                    <div class="text-5xl font-black text-green-400 bg-slate-900 px-6 py-4 rounded-xl border border-green-500/30">{match_percentage}%</div>
                    <div>
                        <p class="text-md text-slate-200 font-medium">Overall ATS Compatibility Score</p>
                    </div>
                </div>
