from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdf, io, re

app = FastAPI()

def extract_text_from_pdf(b):
    pdf_reader = pypdf.PdfReader(io.BytesIO(b))
    return "".join([page.extract_text() or "" for page in pdf_reader.pages])

def fix_spelling(text):
    rep = {"experiance": "Experience", "managment": "Management", "engeneering": "Engineering", "autocad": "AutoCAD", "python": "Python", "java": "Java"}
    for p, r in rep.items(): text = re.sub(r'\b'+p+r'\b', r, text, flags=re.IGNORECASE)
    return text

@app.get("/", response_class=HTMLResponse)
async def read_item():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>AI Resume Parser & Optimizer</title><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div class="max-w-4xl mx-auto py-12 px-4">
            <header class="text-center mb-12">
                <h1 class="text-5xl font-black text-white mb-3">AI Resume Parser & Optimizer</h1>
                <p class="text-gray-400 text-lg">Fix spelling mistakes, align professional layouts, and export clean print-ready resumes instantly.</p>
            </header>
            <div class="bg-slate-900/60 p-8 rounded-2xl border border-slate-800/80 mb-8">
                <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">
                    <div><label class="block text-sm font-semibold text-slate-300 mb-2">1. Upload Candidate Resume (PDF)</label><input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-slate-400 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-blue-600 file:text-white cursor-pointer"></div>
                    <div><label class="block text-sm font-semibold text-slate-300 mb-2">2. Paste Custom Job Description (JD)</label><textarea name="jd" rows="5" required class="w-full bg-slate-950 text-white p-4 rounded-xl border border-slate-800 focus:outline-none"></textarea></div>
                    <button type="submit" class="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg uppercase">Calculate Compatibility Match</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    txt = fix_spelling(extract_text_from_pdf(contents))
    j_w, r_w = set(re.findall(r'\b\w+\b', jd.lower())), set(re.findall(r'\b\w+\b', txt.lower()))
    stop = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are', 'your'}
    imp = {w for w in j_w if len(w) > 2 and w not in stop}
    match, miss = imp.intersection(r_w), imp.difference(r_w)
    pct = int((len(match) / len(imp)) * 100) if imp else 0
    m_str, ms_str = ", ".join(list(match)[:10]).upper(), ", ".join(list(miss)[:8]).upper()
    allowed = {'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'aws', 'git', 'github'}
    valid_skills = [s for s in miss if s.lower() in allowed]
    hd_blt, rw_list = [], []
    if valid_skills:
        for s in valid_skills[:3]:
            bullet = f"Utilized {s.upper()} core architectures to optimize dynamic frontend views and maximize responsive web database application execution pipelines."
            hd_blt.append(bullet)
            rw_list.append(f"<div class='bg-slate-950 p-4 rounded-xl border border-purple-500/20 mt-3'><p class='text-xs text-purple-400 font-bold uppercase mb-1.5'>🔧 Ready-to-use Bullet Point for {s.upper()}:</p><p class='text-sm text-slate-300 font-light'>\\\"{bullet}\\\"</p></div>")
    else:
        rw_list.append("<p class='text-sm text-green-400 font-light'>🎉 Perfect Match! No rewrite optimizations required.</p>")
    rw_str, blt_payload = "".join(rw_list), "|||".join(hd_blt)
    if not blt_payload.strip():
        blt_payload = "EMPTY_DATA"
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>AI Resume Parser & Optimizer</title><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div id="report-content" class="max-w-4xl mx-auto py-12 px-4">
            <div class="bg-slate-900/60 p-8 rounded-2xl border border-blue-500/30 shadow-2xl mb-8">
                <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
                    <h2 class="text-2xl font-bold text-white">📊 ATS Compatibility Audit Summary</h2>
                    <form action="/download-perfect-resume-doc/" method="post">
                        <input type="hidden" name="bullets" value="{blt_payload.replace('"', '&quot;')}">
                        <button type="submit" class="bg-purple-600 text-white font-bold py-2 px-5 rounded-xl text-xs uppercase shadow-md hover:bg-purple-500 transition-colors">🤖 Auto-Inject & Download Perfect Executive Resume</button>
                    </form>
                </div>
                <div class="flex items-center space-x-6 mb-8 bg-slate-950 p-5 rounded-xl">
                    <div class="text-5xl font-black text-green-400 bg-slate-900 px-6 py-4 rounded-xl">{pct}%</div>
                    <div><p class="text-md text-slate-200 font-medium">Overall ATS Compatibility Score</p></div>
                </div>
                <div class="space-y-5 mb-8">
                    <div><h3 class="text-sm font-semibold text-green-400 uppercase">✔️ Matched Keywords:</h3><div class="text-slate-300 text-sm bg-slate-950/80 p-4 rounded-xl mt-2 font-mono">{m_str}</div></div>
                    <div><h3 class="text-sm font-semibold text-red-400 uppercase">❌ Missing Keywords:</h3><div class="text-slate-300 text-sm bg-slate-950/80 p-4 rounded-xl mt-2 font-mono">{ms_str}</div></div>
                </div>
                <div class="bg-purple-950/30 p-6 rounded-2xl mt-6"><h3 class="text-md font-bold text-purple-400 mb-2">🤖 Smart AI Resume Rewriter</h3><div class="space-y-3">{rw_str}</div></div>
            </div>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/download-perfect-resume-doc/")
async def download_doc_resume(bullets: str = Form(...)):
    formatted_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>G_Sainath_Professional_Resume</title>
        <script src="https://tailwindcss.com"></script>
        <style>@media print { body { background: white; color: black; } .no-print { display: none; } }</style>
    </head>
    <body class="bg-slate-100 text-slate-900 p-6 font-sans">
        <div class="max-w-3xl mx-auto bg-white p-12 rounded-xl shadow-lg border border-slate-200">
            <div class="text-center no-print mb-8">
                <button onclick="window.print()" class="bg-blue-600 text-white font-bold px-8 py-3 rounded-lg shadow-md hover:bg-blue-700 transition-colors text-sm tracking-wide">💾 CLICK HERE TO SAVE AS PERFECT PDF</button>
                <p class="text-xs text-slate-500 mt-2">Section segmentation and formatting fixed automatically by AI Executive Suite.</p>
            </div>
            
            <div class="border-b-4 border-blue-900 pb-4 mb-6">
                <h1 class="text-3xl font-black text-slate-900 tracking-tight">G. SAINATH</h1>
                <p class="text-sm text-slate-600 font-medium mt-1">Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com</p>
            </div>
            
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase tracking-wider mb-2">CAREER OBJECTIVE</h2>
                <p class="text-sm text-slate-700 font-light leading-relaxed">Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals.</p>
            </div>

            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase tracking-wider mb-2">EDUCATION</h2>
                <div class="flex justify-between items-start text-sm">
                    <div>
                        <p class="font-bold text-slate-800">B.Tech - Computer Science and Engineering</p>
                        <p class="text-slate-600 font-light">Narayana Engineering College, Gudur</p>
                    </div>
                    <p class="font-semibold text-blue-800">CGPA: 7.8/10 (78%) | Current Year: 4-1</p>
                </div>
            </div>

            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase tracking-wider mb-2">TECHNICAL SKILLS</h2>
                <ul class="space-y-1.5 text-sm font-light text-slate-700">
                    <li><strong class="font-semibold text-slate-800">Programming Languages:</strong> C, Java</li>
                    <li><strong class="font-semibold text-slate-800">Web Technologies:</strong> HTML, CSS, JavaScript (Basics)</li>
                    <li><strong class="font-semibold text-slate-800">Database:</strong> SQL Basics, Database Fundamentals</li>
                    <li><strong class="font-semibold text-slate-800">Tools:</strong> Visual Studio Code, GitHub</li>
                    <li><strong class="font-semibold text-slate-800">Core Concepts:</strong> OOP, Programming Fundamentals, Problem Solving</li>
                </ul>
            </div>

            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase tracking-wider mb-2">PROJECT</h2>
                <div class="text-sm">
