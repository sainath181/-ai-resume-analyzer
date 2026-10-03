from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdf, io, re

app = FastAPI()

def extract_text_from_pdf(b):
    r = pypdf.PdfReader(io.BytesIO(b))
    return "".join([p.extract_text() or "" for p in r.pages])

def fix_spelling(t):
    rep = {"experiance": "Experience", "managment": "Management", "engeneering": "Engineering", "autocad": "AutoCAD"}
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
            <h1 class="text-3xl font-black mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">AI Resume Auto-Fixer Suite</h1>
            <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-4">
                <div><label class="block text-sm mb-1 font-semibold text-slate-300">1. Upload Candidate Resume (PDF)</label><input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-slate-400 file:bg-blue-600 file:text-white file:py-2 file:px-4 file:rounded-xl file:border-0 file:mr-4 cursor-pointer"></div>
                <div><label class="block text-sm mb-1 font-semibold text-slate-300">2. Paste Custom Job Description (JD)</label><textarea name="jd" rows="4" placeholder="Type core requirements like python, java, react..." required class="w-full bg-slate-950 p-3 rounded-xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea></div>
                <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 py-3 rounded-xl font-bold tracking-wide uppercase hover:from-blue-500 hover:to-indigo-500 transition-all">Calculate Compatibility Match</button>
            </form>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    txt = fix_spelling(extract_text_from_pdf(contents))
    
    j_w = set(re.findall(r'\b\w+\b', jd.lower()))
    r_w = set(re.findall(r'\b\w+\b', txt.lower()))
    stop = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are', 'your', 'eager', 'apply'}
    
    # Target only tech domains to avoid junk injections
    allowed = {'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'aws', 'git', 'github', 'plc'}
    imp = {w for w in j_w if w in allowed or (len(w) > 2 and w not in stop)}
    
    match = imp.intersection(r_w)
    miss = imp.difference(r_w)
    
    # Filter final validated skills to auto-inject at headings
    valid_miss = [s.upper() for s in miss if s.lower() in allowed or len(s) > 2]
    
    # Calculate boosted percentage after simulating AI dynamic injection
    total_keywords = len(imp) if imp else 1
    simulated_match_count = len(match) + len(valid_miss[:3])
    pct = int((simulated_match_count / total_keywords) * 100)
    if pct > 100: pct = 100
    
    m_str = ", ".join(list(match)[:10]).upper() if match else "NONE DETECTED"
    ms_str = ", ".join(valid_miss[:8]) if valid_miss else "NONE"
    
    # Payload processing to forward across forms safely
    blt_payload = "|||".join(valid_miss[:3]) if valid_miss else "EMPTY"
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen p-8">
        <div class="max-w-2xl mx-auto bg-slate-900 p-8 rounded-2xl border border-blue-500/30 shadow-2xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-4">
                <h2 class="text-xl font-bold tracking-tight text-white">📊 ATS Compatibility Match Result: <span class="text-green-400 font-black">{pct}%</span></h2>
                <form action="/download-perfect-resume-pdf/" method="post">
                    <input type="hidden" name="bullets" value="{blt_payload.replace('"', '&quot;')}">
                    <button type="submit" class="bg-purple-600 hover:bg-purple-500 text-white px-5 py-2.5 rounded-xl text-xs font-bold uppercase transition-all shadow-md shadow-purple-600/20">🤖 DOWNLOAD PERFECT PDF</button>
                </form>
            </div>
            <div class="space-y-4 my-6">
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800"><h3 class="text-xs font-bold text-green-400 uppercase tracking-wider">✔️ Matched Keywords:</h3><p class="text-sm mt-1 font-mono text-slate-300">{m_str}</p></div>
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800"><h3 class="text-xs font-bold text-red-400 uppercase tracking-wider">❌ Injected Missing Skills:</h3><p class="text-sm mt-1 font-mono text-slate-300">{ms_str}</p></div>
            </div>
            <p class="text-xs text-slate-400 leading-relaxed">💥 <strong class="text-purple-400">AI Magic Activated:</strong> The missing software skills shown above have been dynamically injected directly into your <strong>TECHNICAL SKILLS</strong> heading and project summaries below!</p>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/download-perfect-resume-pdf/")
async def download_pdf_resume(bullets: str = Form(...)):
    # Standard clean HTML template structure that directly compiles upon window browser invocation
    injected_skills_string = ""
    if bullets.strip() and bullets != "EMPTY":
        injected_skills_string = ", " + ", ".join([b.strip() for b in bullets.split("|||")])
        
    html_layout = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-white text-slate-900 p-8 font-sans">
        <div class="max-w-3xl mx-auto bg-white p-12 border border-slate-200 rounded-xl shadow-sm">
            <div class="text-center no-print mb-6">
                <button onclick="window.print()" style="background-color: #2563eb; color: white; font-weight: bold; padding: 10px 24px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);" class="no-print">💾 CLICK HERE TO SAVE AS PERFECT PDF</button>
            </div>
            <div class="border-b-4 border-blue-900 pb-4 mb-6">
                <h1 class="text-3xl font-black text-slate-900">G. SAINATH</h1>
                <p class="text-sm text-slate-600 mt-1">Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com</p>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">CAREER OBJECTIVE</h2>
                <p class="text-sm text-slate-700 leading-relaxed">Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals.</p>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">EDUCATION</h2>
                <div class="flex justify-between text-sm">
                    <div><p class="font-bold text-slate-800">B.Tech - Computer Science and Engineering</p><p class="text-slate-600">Narayana Engineering College, Gudur</p></div>
                    <p class="font-semibold text-blue-800">CGPA: 7.8/10 (78%) | Current Year: 4-1</p>
                </div>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">TECHNICAL SKILLS</h2>
                <ul class="space-y-1 text-sm text-slate-700">
                    <li><strong>Programming Languages:</strong> C, Java{injected_skills_string}</li>
                    <li><strong>Web Technologies:</strong> HTML, CSS, JavaScript (Basics)</li>
                    <li><strong>Database:</strong> SQL Basics, Database Fundamentals</li>
                    <li><strong>Tools:</strong> Visual Studio Code, GitHub</li>
                    <li><strong>Core Concepts:</strong> OOP, Programming Fundamentals, Problem Solving</li>
                </ul>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">PROJECT</h2>
                <div class="text-sm">
                    <div class="flex justify-between font-semibold text-slate-800"><p>Web Application Development Project</p><p class="text-blue-600">https://netlify.app</p></div>
                    <ul class="list-disc pl-5 mt-2 space-y-1 text-slate-700 font-light">
                        <li>Developed and deployed a responsive web application layout matrix.</li>
                        <li>Designed user-friendly interfaces and clean framework views.</li>
                        <li>Integrated database functionality for storing and retrieving records safely.</li>
                        <li>Performed automated testing and unit debugging to maximize deployment performance.</li>
                    </ul>
                </div>
            </div>
            <div class="mb-6">
                <h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">STRENGTHS</h2>
