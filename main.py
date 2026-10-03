from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdf, io, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

app = FastAPI()

def extract_text_from_pdf(b):
    r = pypdf.PdfReader(io.BytesIO(b))
    return "".join([p.extract_text() or "" for p in r.pages])

def fix_text(t):
    rep = {"autocad": "AutoCAD", "python": "Python", "java": "Java", "plc": "PLC Systems"}
    for p, r in rep.items(): t = re.sub(r'\b'+p+r'\b', r, t, flags=re.IGNORECASE)
    return t

@app.get("/", response_class=HTMLResponse)
async def read_item():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><title>AI Resume Parser & Optimizer</title><script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div class="max-w-4xl mx-auto py-12 px-4">
            <header class="text-center mb-12">
                <h1 class="text-5xl font-black text-white mb-3">AI Resume Parser & Optimizer</h1>
                <p class="text-gray-400 text-lg">Fix spelling mistakes, align layouts, and inject competencies into a print-ready PDF structure.</p>
            </header>
            <div class="bg-slate-900/60 p-8 rounded-2xl shadow-2xl border border-slate-800/80 mb-8">
                <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">
                    <div>
                        <label class="block text-sm font-semibold text-slate-300 mb-2">1. Upload Candidate Resume (PDF)</label>
                        <input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-slate-400 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-blue-600 file:text-white">
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-300 mb-2">2. Paste Custom Job Description (JD)</label>
                        <textarea name="jd" rows="5" placeholder="Paste target requirements here..." required class="w-full bg-slate-950 text-white p-4 rounded-xl border border-slate-800 focus:outline-none"></textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg">Calculate Compatibility Match</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    txt = fix_text(extract_text_from_pdf(contents))
    j_w, r_w = set(re.findall(r'\b\w+\b', jd.lower())), set(re.findall(r'\b\w+\b', txt.lower()))
    stop = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are', 'your'}
    imp = {w for w in j_w if len(w) > 2 and w not in stop}
    match, miss = imp.intersection(r_w), imp.difference(r_w)
    pct = int((len(match) / len(imp)) * 100) if imp else 0
    m_str, ms_str = ", ".join(list(match)[:10]).upper(), ", ".join(list(miss)[:8]).upper()
    hd_blt, rw_list = [], []
    if miss:
        for s in list(miss)[:3]:
            bullet = f"Utilized {s.upper()} methodologies and engineering layouts to optimize workflow production configurations and maximize execution safety matrices."
            hd_blt.append(bullet)
            rw_list.append(f"<div class='bg-slate-950 p-4 rounded-xl border border-purple-500/20 mt-3'><p class='text-xs text-purple-400 font-bold uppercase mb-1.5'>🔧 Bullet Point for {s.upper()}:</p><p class='text-sm text-slate-300 font-light'>\\\"{bullet}\\\"</p></div>")
    else:
        rw_list.append("<p class='text-sm text-green-400 font-light'>🎉 Perfect Match!</p>")
    rw_str, blt_payload = "".join(rw_list), "|||".join(hd_blt)
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>AI Resume Parser & Optimizer</title><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div class="max-w-4xl mx-auto py-12 px-4">
            <div class="bg-slate-900/60 p-8 rounded-2xl border border-blue-500/30 shadow-2xl mb-8">
                <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
                    <h2 class="text-2xl font-bold text-white">📊 ATS Compatibility Audit Summary</h2>
                    <form action="/download-perfect-resume/" method="post">
                        <input type="hidden" name="orig_text" value="{txt.replace('"', '&quot;')}">
                        <input type="hidden" name="bullets" value="{blt_payload.replace('"', '&quot;')}">
                        <button type="submit" class="bg-purple-600 text-white font-bold py-2 px-5 rounded-xl text-xs uppercase">🤖 Generate Perfect Resume & Download PDF</button>
                    </form>
                </div>
                <div class="flex items-center space-x-6 mb-8 bg-slate-950 p-5 rounded-xl">
                    <div class="text-5xl font-black text-green-400 bg-slate-900 px-6 py-4 rounded-xl">{pct}%</div>
                    <div><p class="text-md text-slate-200 font-medium">Overall ATS Compatibility Score</p></div>
                </div>
                <div class="space-y-5 mb-8">
                    <div><h3 class="text-sm font-semibold text-green-400 uppercase">✔️ Matched Technical Keywords:</h3><div class="text-slate-300 text-sm bg-slate-950/80 p-4 rounded-xl mt-2 font-mono">{m_str}</div></div>
                    <div><h3 class="text-sm font-semibold text-red-400 uppercase">❌ Missing Target Keywords:</h3><div class="text-slate-300 text-sm bg-slate-950/80 p-4 rounded-xl mt-2 font-mono">{ms_str}</div></div>
                </div>
                <div class="bg-purple-950/30 border border-purple-500/30 p-6 rounded-2xl">
                    <h3 class="text-md font-bold text-purple-400 mb-2">🤖 Smart AI Resume Rewriter</h3>
                    <div class="space-y-3">{rw_str}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/download-perfect-resume/")
async def download_perfect_resume(orig_text: str = Form(...), bullets: str = Form(...)):
    buffer = io.BytesIO()
    from reportlab.lib.colors import HexColor
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor('#1e3a8a'))
    c.drawString(54, 745, "PROFESSIONAL ENGINEERING CURRICULUM VITAE")
    c.setStrokeColor(HexColor('#94a3b8'))
    c.line(54, 730, 558, 730)
    y = 705
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#334155'))
    for line in orig_text.split("\n"):
        if line.strip():
            if y < 60:
                c.showPage()
                y = 745
                c.setFont("Helvetica", 10)
            c.drawString(54, y, line.strip()[:95])
            y -= 16
    if bullets.strip():
        y -= 20
        if y < 120: c.showPage(); y = 745
        c.setStrokeColor(HexColor('#3b82f6'))
        c.line(54, y+12, 558, y+12)
        c.setFont("Helvetica-Bold", 11)
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
    c.showPage()
    c.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Perfect_AI_Resume.pdf"})
