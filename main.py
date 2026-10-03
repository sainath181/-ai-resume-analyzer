from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdf, io, re

app = FastAPI()

def extract_text_from_pdf(b):
    r = pypdf.PdfReader(io.BytesIO(b))
    return "".join([p.extract_text() or "" for p in r.pages])

def fix_spelling(t):
    rep = {"experiance": "Experience", "managment": "Management", "engeneering": "Engineering", "autocad": "AutoCAD", "python": "Python", "java": "Java"}
    for p, r in rep.items(): t = re.sub(r'\b'+p+r'\b', r, t, flags=re.IGNORECASE)
    return t

@app.get("/", response_class=HTMLResponse)
async def read_item():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>AI Resume Parser</title><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen p-8">
        <div class="max-w-xl mx-auto bg-slate-900 p-8 rounded-2xl border border-slate-800">
            <h1 class="text-3xl font-black mb-4">AI Resume Auto-Fixer Suite</h1>
            <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-4">
                <div><label class="block text-sm mb-1">Upload Resume (PDF)</label><input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-slate-400"></div>
                <div><label class="block text-sm mb-1">Paste Job Description (JD)</label><textarea name="jd" rows="4" required class="w-full bg-slate-950 p-2 rounded border border-slate-800"></textarea></div>
                <button type="submit" class="w-full bg-blue-600 py-3 rounded font-bold">CALCULATE COMPATIBILITY</button>
            </form>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    txt = fix_spelling(extract_text_from_pdf(contents))
    j_w, r_w = set(re.findall(r'\b\w+\b', jd.lower())), set(re.findall(r'\b\w+\b', txt.lower()))
    stop = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are'}
    imp = {w for w in j_w if len(w) > 2 and w not in stop}
    match, miss = imp.intersection(r_w), imp.difference(r_w)
    pct = int((len(match) / len(imp)) * 100) if imp else 0
    allowed = {'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'aws', 'git', 'github'}
    valid = [s for s in miss if s.lower() in allowed]
    hd_blt = [f"Utilized {s.upper()} core architectures to optimize dynamic views and maximize responsive web database application execution pipelines." for s in valid[:3]]
    blt_payload = "|||".join(hd_blt) if hd_blt else "EMPTY"
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen p-8">
        <div class="max-w-2xl mx-auto bg-slate-900 p-8 rounded-2xl border border-blue-500/30">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-4">
                <h2 class="text-xl font-bold">📊 ATS Compatibility Match Result: {pct}%</h2>
                <form action="/download-perfect-resume-pdf/" method="post">
                    <input type="hidden" name="bullets" value="{blt_payload.replace('"', '&quot;')}">
                    <button type="submit" class="bg-purple-600 px-4 py-2 rounded text-xs font-bold">🤖 DOWNLOAD PERFECT PDF</button>
                </form>
            </div>
            <p class="text-sm text-gray-400">Spelling fixed. Click the button above to download the professional PDF package.</p>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/download-perfect-resume-pdf/")
async def download_pdf_resume(bullets: str = Form(...)):
    # Standard Python File stream engine to generate 100% error-free print file packages
    html_layout = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-white text-slate-900 p-8 font-sans">
        <div class="max-w-3xl mx-auto bg-white p-12 border border-slate-200 rounded-xl">
            <div class="border-b-4 border-blue-900 pb-4 mb-6">
                <h1 class="text-3xl font-black text-slate-900">G. SAINATH</h1>
                <p class="text-sm text-slate-600 mt-1">Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com</p>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2">CAREER OBJECTIVE</h2>
                <p class="text-sm text-slate-700 leading-relaxed">Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals.</p>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2">EDUCATION</h2>
                <div class="flex justify-between text-sm">
                    <div><p class="font-bold">B.Tech - Computer Science and Engineering</p><p class="text-slate-600">Narayana Engineering College, Gudur</p></div>
                    <p class="font-semibold text-blue-800">CGPA: 7.8/10 (78%) | Current Year: 4-1</p>
                </div>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2">TECHNICAL SKILLS</h2>
                <ul class="space-y-1 text-sm text-slate-700">
                    <li><strong>Programming Languages:</strong> C, Java</li>
                    <li><strong>Web Technologies:</strong> HTML, CSS, JavaScript (Basics)</li>
                    <li><strong>Database:</strong> SQL Basics, Database Fundamentals</li>
                    <li><strong>Tools:</strong> Visual Studio Code, GitHub</li>
                    <li><strong>Core Concepts:</strong> OOP, Programming Fundamentals, Problem Solving</li>
                </ul>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2">PROJECT</h2>
                <div class="text-sm">
                    <div class="flex justify-between font-semibold"><p>Web Application Development Project</p><p class="text-blue-600">https://netlify.app</p></div>
                    <ul class="list-disc pl-5 mt-2 space-y-1 text-slate-700">
                        <li>Developed and deployed a responsive web application.</li>
                        <li>Designed user-friendly interfaces and layouts.</li>
                        <li>Integrated database functionality for storing and retrieving data.</li>
                        <li>Performed testing and debugging to improve performance and usability.</li>
                    </ul>
                </div>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2">STRENGTHS</h2>
                <p class="text-sm text-slate-700">• Quick Learner • Team Player • Communication Skills • Problem Solving • Adaptability • Time Management</p>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2">ACTIVITIES & INTERESTS</h2>
                <ul class="list-disc pl-5 space-y-1 text-sm text-slate-700">
                    <li>Built and deployed a web application project.</li>
                    <li>Interested in learning modern web development technologies.</li>
                    <li>Watching Movies, Content Shooting, and Exploring New Technologies.</li>
                </ul>
            </div>
    """
    if bullets.strip() and bullets != "EMPTY":
        html_layout += """
            <div class="mt-6 border-t-2 border-slate-200 pt-4">
                <h2 class="text-sm font-bold text-purple-900 uppercase mb-2">🤖 AI Injected Technical Enhancements (ATS Optimizer)</h2>
                <ul class="list-disc pl-5 space-y-1 text-sm text-slate-800 font-medium">
        """
        for b in bullets.split("|||"):
            if b.strip(): html_layout += f"<li>{b.strip()}</li>"
        html_layout += "</ul></div>"
        
    html_layout += "</div><script>window.onload = function() { window.print(); }</script></body></html>"
    file_stream = io.BytesIO(html_layout.encode("utf-8"))
    return StreamingResponse(file_stream, media_type="text/html", headers={"Content-Disposition": "attachment; filename=Perfect_AI_Resume.html"})
