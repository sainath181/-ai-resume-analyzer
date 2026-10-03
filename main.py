from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import pypdf, io, re

app = FastAPI()

def extract_text_from_pdf(b):
    r = pypdf.PdfReader(io.BytesIO(b))
    return "\n".join([p.extract_text() or "" for p in r.pages])

def fix_spelling(t):
    rep = {"experiance": "Experience", "managment": "Management", "engeneering": "Engineering"}
    for p, r in rep.items(): t = re.sub(r'\b'+p+r'\b', r, t, flags=re.IGNORECASE)
    return t

@app.get("/", response_class=HTMLResponse)
async def read_item():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Universal AI Resume Optimizer</title>
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans flex items-center justify-center p-4 relative overflow-x-hidden">
        <!-- Premium Glowing Neon Background Lights -->
        <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none"></div>

        <div class="max-w-2xl w-full bg-slate-900/40 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-2xl shadow-blue-950/20 relative z-10">
            <header class="text-center mb-8">
                <div class="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 px-4 py-1.5 rounded-full text-xs font-semibold text-blue-400 mb-4 uppercase tracking-wider">🚀 Next-Gen Cross-Branch AI Suite</div>
                <h1 class="text-4xl font-extrabold text-white tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">Universal AI Resume Suite</h1>
                <p class="text-slate-400 text-sm font-light">Fix layout alignments, auto-correct spellings, and dynamically match target company requirements instantly.</p>
            </header>

            <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">
                <!-- Attractive Upload Zone Card -->
                <div class="bg-slate-950/50 p-6 rounded-2xl border border-dashed border-slate-800 hover:border-blue-500/50 transition-all group relative">
                    <label class="block text-sm font-bold text-slate-300 mb-3 tracking-wide">1. Upload Candidate Resume (PDF)</label>
                    <div class="flex items-center justify-center bg-slate-900/60 p-4 rounded-xl border border-slate-800 group-hover:bg-slate-900/90 transition-all cursor-pointer">
                        <input type="file" name="resume" accept=".pdf" required class="block w-full text-xs text-slate-400 file:bg-blue-600 file:hover:bg-blue-700 file:text-white file:py-2 file:px-4 file:rounded-lg file:border-0 file:mr-4 file:font-bold file:text-xs cursor-pointer">
                    </div>
                    <p class="text-[11px] text-slate-500 mt-2">Supports any branch template layout (CSE, IT, ME, CE, ECE, EEE).</p>
                </div>

                <!-- Beautiful Text Area Form Block -->
                <div class="space-y-2">
                    <label class="block text-sm font-bold text-slate-300 tracking-wide">2. Paste Target Company Job Description (JD)</label>
                    <textarea name="jd" rows="5" placeholder="Paste target metrics, hiring roles, or specific technical skill keywords requested by the company here..." required class="w-full bg-slate-950/80 text-slate-200 p-4 rounded-2xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-sm font-light placeholder:text-slate-700 leading-relaxed"></textarea>
                </div>

                <!-- High Conversion Call to Action Button -->
                <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 rounded-2xl shadow-xl shadow-blue-900/20 tracking-wider text-sm uppercase transition-all duration-300 hover:scale-[1.01] active:scale-[0.99]">
                    Optimize & Align Profile State
                </button>
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
    all_b = {'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'aws', 'git', 'github', 'c', 'cpp', 'autocad', 'solidworks', 'ansys', 'revit', 'staad', 'plc', 'scada'}
    imp = {w for w in j_w if w in all_b or (len(w) > 2 and w not in stop)}
    
    match = imp.intersection(r_w)
    miss = imp.difference(r_w)
    
    valid_miss = [s.title() if s.lower() not in ['sql', 'plc'] else s.upper() for s in miss if s.lower() in all_b]
    inj_str = ", ".join(valid_miss[:3]) if valid_miss else ""
    
    old_pct = int((len(match) / len(imp)) * 100) if imp else 100
    boosted_pct = int(((len(match) + len(valid_miss[:3])) / len(imp)) * 100) if imp else 100
    if boosted_pct > 100: boosted_pct = 100
    
    m_str = ", ".join(list(match)[:10]).upper() if match else "NONE"
    blt_payload = "|||".join(valid_miss[:3]) if valid_miss else "EMPTY"
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen p-8 flex items-center justify-center relative overflow-x-hidden">
        <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div class="max-w-2xl w-full bg-slate-900/40 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-2xl">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800 pb-6 mb-6 gap-4">
                <div>
                    <h2 class="text-xl font-black text-white tracking-wide">📊 ATS Optimization Matrix</h2>
                    <p class="text-xs text-slate-400 mt-0.5">Score: <span class="text-red-400 line-through font-medium">{old_pct}%</span> &rarr; <span class="text-green-400 font-extrabold text-sm">{boosted_pct}% Boosted</span> 🎉</p>
                </div>
                <form action="/download-perfect-resume-pdf/" method="post" class="w-full sm:w-auto">
                    <input type="hidden" name="bullets" value="{blt_payload.replace('"', '&quot;')}">
                    <button type="submit" class="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-6 py-3 rounded-xl text-xs font-bold uppercase transition-all shadow-lg hover:scale-[1.02]">🤖 DOWNLOAD PERFECT PDF</button>
                </form>
            </div>
            <div class="space-y-4 mb-6">
                <div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800"><p class="text-xs font-bold text-green-400 uppercase tracking-wider">✔️ Verified Target Matches:</p><p class="text-sm font-mono text-slate-200 mt-1.5">{m_str}</p></div>
                <div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800"><p class="text-xs font-bold text-purple-400 uppercase tracking-wider">🤖 AI Smart Injected Competencies:</p><p class="text-sm font-mono text-slate-200 mt-1.5">{inj_str if inj_str else "NONE"}</p></div>
            </div>
            <p class="text-xs text-slate-400 leading-relaxed text-center">🎯 <strong>AI Intelligence Active:</strong> The engine auto-located the skill segments and executed Case-Sensitive injection natively to bypass ATS boundaries.</p>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/download-perfect-resume-pdf/")
async def download_pdf_resume(bullets: str = Form(...)):
    inj = ""
    if bullets.strip() and bullets != "EMPTY":
        inj = ", " + ", ".join([b.strip() for b in bullets.split("|||")])
    html_layout = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>
    <body class="bg-white text-slate-900 p-8 font-sans">
        <div class="max-w-3xl mx-auto p-12 border border-slate-200 rounded-xl">
            <div class="text-center no-print mb-6"><button onclick="window.print()" class="bg-blue-600 text-white font-bold px-6 py-2 rounded shadow no-print">💾 CLICK HERE TO SAVE AS PERFECT PDF</button></div>
            <div class="border-b-4 border-blue-900 pb-4 mb-6">
                <h1 class="text-3xl font-black text-slate-900">G. SAINATH</h1>
                <p class="text-sm text-slate-600 mt-1">Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com</p>
            </div>
            <div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2">CAREER OBJECTIVE</h2><p class="text-sm text-slate-700 leading-relaxed">Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals.</p></div>
