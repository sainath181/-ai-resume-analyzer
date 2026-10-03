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

def fix_spelling(text):
    rep = {"experiance": "Experience", "managment": "Management", "engeneering": "Engineering", "autocad": "AutoCAD", "python": "Python", "java": "Java"}
    for p, r in rep.items(): text = re.sub(r'\b'+p+r'\b', r, text, flags=re.IGNORECASE)
    return text

@app.get("/", response_class=HTMLResponse)
async def read_item():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI Resume Parser & Optimizer</title>
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div class="max-w-4xl mx-auto py-12 px-4">
            <header class="text-center mb-12">
                <h1 class="text-5xl font-black text-white mb-3">AI Resume Parser & Optimizer</h1>
                <p class="text-gray-400 text-lg">Fix spelling mistakes, align professional layouts, and export clean print-ready resumes instantly.</p>
            </header>
            <div class="bg-slate-900/60 p-8 rounded-2xl border border-slate-800/80 mb-8">
                <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">
                    <div>
                        <label class="block text-sm font-semibold text-slate-300 mb-2">1. Upload Candidate Resume (PDF)</label>
                        <input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-slate-400 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-blue-600 file:text-white cursor-pointer">
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-300 mb-2">2. Paste Custom Job Description (JD)</label>
                        <textarea name="jd" rows="5" required class="w-full bg-slate-950 text-white p-4 rounded-xl border border-slate-800 focus:outline-none"></textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg uppercase">Calculate Compatibility Match</button>
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
    txt = fix_spelling(extract_text_from_pdf(contents))
    
    j_w = set(re.findall(r'\b\w+\b', jd.lower()))
    r_w = set(re.findall(r'\b\w+\b', txt.lower()))
    stop = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are', 'your'}
    imp = {w for w in j_w if len(w) > 2 and w not in stop}
    match = imp.intersection(r_w)
    miss = imp.difference(r_w)
    pct = int((len(match) / len(imp)) * 100) if imp else 0
    
    m_str = ", ".join(list(match)[:10]).upper()
    ms_str = ", ".join(list(miss)[:8]).upper()
    
    allowed = {'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'aws', 'git', 'github'}
    valid_skills = [s for s in miss if s.lower() in allowed]
    
    hd_blt = []
    rw_list = []
    if valid_skills:
        for s in valid_skills[:3]:
            bullet = f"Utilized {s.upper()} core architectures to optimize dynamic frontend views and maximize responsive web database application execution pipelines."
            hd_blt.append(bullet)
            rw_list.append(f"<div class='bg-slate-950 p-4 rounded-xl border border-purple-500/20 mt-3'><p class='text-xs text-purple-400 font-bold uppercase mb-1.5'>🔧 Ready-to-use Bullet Point for {s.upper()}:</p><p class='text-sm text-slate-300 font-light'>\\\"{bullet}\\\"</p></div>")
    else:
        rw_list.append("<p class='text-sm text-green-400 font-light'>🎉 Perfect Match! No rewrite optimizations required.</p>")
        
    rw_str = "".join(rw_list)
    blt_payload = "|||".join(hd_blt) if hd_blt else "EMPTY"
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>AI Resume Parser & Optimizer</title><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div id="report-content" class="max-w-4xl mx-auto py-12 px-4">
            <div class="bg-slate-900/60 p-8 rounded-2xl border border-blue-500/30 shadow-2xl mb-8">
                <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
                    <h2 class="text-2xl font-bold text-white">📊 ATS Compatibility Audit Summary</h2>
                    <form action="/download-perfect-resume-pdf/" method="post">
                        <input type="hidden" name="bullets" value="{blt_payload.replace('"', '&quot;')}">
                        <button type="submit" class="bg-purple-600 text-white font-bold py-2 px-5 rounded-xl text-xs uppercase shadow-md hover:bg-purple-500 transition-colors">🤖 Auto-Inject & Download Perfect PDF Resume</button>
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

@app.post("/download-perfect-resume-pdf/")
async def download_pdf_resume(bullets: str = Form(...)):
    # Standard Python Canvas engine to generate zero-error pure PDF documents directly
    output_writer = pypdf.PdfWriter()
    packet = io.BytesIO()
    
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import HexColor
    
    c = canvas.Canvas(packet, pagesize=letter)
    
    # Header Design
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, 730, "G. SAINATH")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(HexColor('#475569'))
    c.drawString(54, 712, "Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com")
    
    c.setStrokeColor(HexColor('#cbd5e1'))
    c.setLineWidth(1)
    c.line(54, 698, 558, 698)
    
    # 1. Career Objective
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, 675, "CAREER OBJECTIVE")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#334155'))
    obj_text = "Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals."
    
    words = obj_text.split(" ")
    curr, y = "", 655
    for w in words:
        test = curr + " " + w if curr else w
        if c.stringWidth(test, "Helvetica", 10) < 504:
            curr = test
        else:
            c.drawString(54, y, curr)
            y -= 15
            curr = w
    c.drawString(54, y, curr)
    
    # 2. Education
    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, y, "EDUCATION")
    
    y -= 18
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(HexColor('#1e293b'))
    c.drawString(54, y, "B.Tech - Computer Science and Engineering")
    c.drawRightString(558, y, "CGPA: 7.8/10 (78%) | Current Year: 4-1")
    
    y -= 14
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#475569'))
    c.drawString(54, y, "Narayana Engineering College, Gudur")
    
    # 3. Technical Skills
    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, y, "TECHNICAL SKILLS")
    
    skills = [
        "Programming Languages: C, Java",
        "Web Technologies: HTML, CSS, JavaScript (Basics)",
        "Database: SQL Basics, Database Fundamentals",
        "Tools: Visual Studio Code, GitHub",
        "Core Concepts: OOP, Programming Fundamentals, Problem Solving"
    ]
    
    y -= 18
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#334155'))
    for s in skills:
        c.drawString(54, y, f"• {s}")
        y -= 15
        
    # 4. Project
    y -= 15
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, y, "PROJECT")
    
    y -= 18
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(HexColor('#1e293b'))
    c.drawString(54, y, "Web Application Development Project")
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(HexColor('#2563eb'))
    c.drawRightString(558, y, "Live: https://netlify.app")
    
    proj_bullets = [
