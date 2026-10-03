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
    valid_skills = [s for s in miss if s.lower() in allowed]
    hd_blt = []
    if valid_skills:
        for s in valid_skills[:3]:
            hd_blt.append(f"Utilized {s.upper()} core architectures to optimize dynamic frontend views and maximize responsive web database application execution pipelines.")
    blt_payload = "|||".join(hd_blt) if hd_blt else "EMPTY"
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen p-8">
        <div class="max-w-2xl mx-auto bg-slate-900 p-8 rounded-2xl border border-blue-500/30">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-4">
                <h2 class="text-xl font-bold">📊 ATS compatibility Match Result: {pct}%</h2>
                <form action="/download-perfect-resume-pdf/" method="post">
                    <input type="hidden" name="orig_text" value="{txt.replace('"', '&quot;')}">
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
async def download_pdf_resume(orig_text: str = Form(...), bullets: str = Form(...)):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, 745, "PROFESSIONAL ENGINEERING CURRICULUM VITAE")
    c.setStrokeColor(HexColor('#94a3b8'))
    c.line(54, 730, 558, 730)
    y = 705
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#334155'))
    for line in orig_text.split("\n"):
        if line.strip():
            if y < 60: c.showPage(); y = 745; c.setFont("Helvetica", 10)
            c.drawString(54, y, line.strip()[:95])
            y -= 16
    if bullets.strip() and bullets != "EMPTY":
        y -= 20
        if y < 120: c.showPage(); y = 745
        c.setStrokeColor(HexColor('#3b82f6'))
        c.line(54, y+12, 558, y+12)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(HexColor('#2563eb'))
        c.drawString(54, y, "PROFESSIONAL COMPETENCIES & TECHNICAL ENHANCEMENTS")
        y -= 22
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor('#1e293b'))
        for b in bullets.split("|||"):
            if b.strip():
                if y < 50: c.showPage(); y = 745; c.setFont("Helvetica", 10)
                c.drawString(54, y, f"• {b.strip()[:90]}")
                y -= 18
    c.showPage(); c.save(); buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Perfect_AI_Resume.pdf"})
