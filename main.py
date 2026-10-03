from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdf, io, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor

app = FastAPI()

def extract_text_from_pdf(b):
    r = pypdf.PdfReader(io.BytesIO(b))
    return "".join([p.extract_text() or "" for p in r.pages])

def fix_spelling(text):
    rep = {"experiance": "Experience", "managment": "Management", "engeneering": "Engineering", "autocad": "AutoCAD", "python": "Python", "java": "Java"}
    for p, r in rep.items(): text = re.sub(r'\b'+p+r'\b', r, text, flags=re.IGNORECASE)
    return text

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
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, 730, "G. SAINATH")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(HexColor('#475569'))
    c.drawString(54, 712, "Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com")
    c.setStrokeColor(HexColor('#cbd5e1'))
    c.line(54, 698, 558, 698)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, 675, "CAREER OBJECTIVE")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#334155'))
    obj = "Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals."
    words, curr, y = obj.split(" "), "", 655
    for w in words:
        test = curr + " " + w if curr else w
        if c.stringWidth(test, "Helvetica", 10) < 504: curr = test
        else: c.drawString(54, y, curr); y -= 15; curr = w
    c.drawString(54, y, curr); y -= 25
    c.setFont("Helvetica-Bold", 11); c.setFillColor(HexColor('#1e3a8a')); c.drawString(54, y, "EDUCATION"); y -= 18
    c.setFont("Helvetica-Bold", 10); c.setFillColor(HexColor('#1e293b')); c.drawString(54, y, "B.Tech - Computer Science and Engineering"); c.drawRightString(558, y, "CGPA: 7.8/10 (78%) | Current Year: 4-1")
    y -= 14; c.setFont("Helvetica", 10); c.setFillColor(HexColor('#475569')); c.drawString(54, y, "Narayana Engineering College, Gudur"); y -= 25
    c.setFont("Helvetica-Bold", 11); c.setFillColor(HexColor('#1e3a8a')); c.drawString(54, y, "TECHNICAL SKILLS"); y -= 18
    skills = ["Programming Languages: C, Java", "Web Technologies: HTML, CSS, JavaScript (Basics)", "Database: SQL Basics, Database Fundamentals", "Tools: Visual Studio Code, GitHub", "Core Concepts: OOP, Programming Fundamentals, Problem Solving"]
    c.setFont("Helvetica", 10); c.setFillColor(HexColor('#334155'))
    for s in skills: c.drawString(54, y, f"• {s}"); y -= 15
    y -= 15; c.setFont("Helvetica-Bold", 11); c.setFillColor(HexColor('#1e3a8a')); c.drawString(54, y, "PROJECT"); y -= 18
    c.setFont("Helvetica-Bold", 10); c.setFillColor(HexColor('#1e293b')); c.drawString(54, y, "Web Application Development Project"); c.setFont("Helvetica-Oblique", 9); c.setFillColor(HexColor('#2563eb')); c.drawRightString(558, y, "Live: https://netlify.app")
    pb = ["Developed and deployed a responsive web application.", "Designed user-friendly interfaces and layouts.", "Integrated database functionality for storing and retrieving data.", "Performed testing and debugging to improve performance and usability."]
    y -= 16; c.setFont("Helvetica", 10); c.setFillColor(HexColor('#334155'))
    for b in pb: c.drawString(54, y, f"• {b}"); y -= 15
    y -= 15; c.setFont("Helvetica-Bold", 11); c.setFillColor(HexColor('#1e3a8a')); c.drawString(54, y, "STRENGTHS"); y -= 18
    c.drawString(54, y, "• Quick Learner  • Team Player  • Communication Skills  • Problem Solving  • Adaptability  • Time Management"); y -= 25
    c.setFont("Helvetica-Bold", 11); c.setFillColor(HexColor('#1e3a8a')); c.drawString(54, y, "ACTIVITIES & INTERESTS"); y -= 18
    ints = ["Built and deployed a web application project.", "Interested in learning modern web development technologies.", "Watching Movies, Content Shooting, and Exploring New Technologies."]
    for i in ints: c.drawString(54, y, f"• {i}"); y -= 15
    if bullets.strip() and bullets != "EMPTY":
        y -= 20; c.setStrokeColor(HexColor('#3b82f6')); c.line(54, y+12, 558, y+12)
        c.setFont("Helvetica-Bold", 11); c.setFillColor(HexColor('#2563eb')); c.drawString(54, y, "AI OPTIMIZED ATS EXPERIENCE ENHANCEMENTS"); y -= 18
        c.setFont("Helvetica", 10); c.setFillColor(HexColor('#1e293b'))
        for b in bullets.split("|||"):
            if b.strip(): c.drawString(54, y, f"• {b.strip()[:92]}"); y -= 16
    c.showPage(); c.save(); buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Perfect_Sainath_Resume.pdf"})
