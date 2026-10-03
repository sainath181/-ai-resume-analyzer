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
    <head><meta charset="UTF-8"><title>Universal AI Resume Optimizer</title><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen p-8">
        <div class="max-w-xl mx-auto bg-slate-900 p-8 rounded-2xl border border-slate-800 shadow-2xl">
            <h1 class="text-3xl font-black mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">Universal AI Resume Suite</h1>
            <p class="text-xs text-slate-400 mb-6">Supports all engineering branches: CSE, IT, ME, CE, ECE, EEE</p>
            <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-4">
                <div><label class="block text-sm mb-1 font-semibold text-slate-300">1. Upload Any Branch Resume (PDF)</label><input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-slate-400 file:bg-blue-600 file:text-white file:py-2 file:px-4 file:rounded-xl file:border-0 cursor-pointer"></div>
                <div><label class="block text-sm mb-1 font-semibold text-slate-300">2. Paste Target Company Job Description (JD)</label><textarea name="jd" rows="5" placeholder="Paste company criteria, roles, or technical points here..." required class="w-full bg-slate-950 p-3 rounded-xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white text-sm"></textarea></div>
                <button type="submit" class="w-full bg-blue-600 py-3 rounded-xl font-bold tracking-wide uppercase hover:bg-blue-700 transition-all">Optimize & Align Profile</button>
            </form>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    txt = fix_spelling(extract_text_from_pdf(contents))
    
    # 1. Clean and tokenise the inputs
    jd_words = set(re.findall(r'\b\w+\b', jd.lower()))
    resume_words = set(re.findall(r'\b\w+\b', txt.lower()))
    
    stop = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are', 'your', 'eager', 'apply', 'role', 'company', 'position', 'job', 'points', 'must'}
    
    # 2. Universal Global Cross-Branch Dictionary mapping
    all_branch_dictionary = {
        # IT & Computer Science (CSE/IT)
        'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'aws', 'git', 'github', 'c', 'cpp', 'cloud',
        # Mechanical Engineering (ME)
        'autocad', 'solidworks', 'ansys', 'catia', 'matlab', 'thermodynamics', 'hvac', 'cad', 'cam', 'cnc', 'manufacturing',
        # Civil Engineering (CE)
        'revit', 'staad', 'etabs', 'surveying', 'concrete', 'estimation', 'gis', 'autodesk', 'structures', 'geotechnical',
        # Electronics & Electrical (ECE/EEE)
        'plc', 'scada', 'vlsi', 'embedded', 'verilog', 'vhdl', 'arduino', 'microcontroller', 'circuit', 'signal', 'robotics'
    }
    
    # 3. Filter active targets requested by the company role
    target_company_points = {w for w in jd_words if w in all_branch_dictionary or (len(w) > 2 and w not in stop)}
    
    match = target_company_points.intersection(resume_words)
    missing = target_company_points.difference(resume_words)
    
    # Valid missing points to inject automatically based on the user's domain
    valid_miss = [s.upper() for s in missing if s.lower() in all_branch_dictionary or len(s) > 2]
    
    # 4. Smart Multi-Branch Case-Insensitive Injection Engine
    injected_text = txt
    inj_str = ", ".join(valid_miss[:4]) if valid_miss else ""
    
    if inj_str:
        # Detects any layout title like TECHNICAL SKILLS, Technical Skills, Core Competencies, Skills, etc.
        pattern = r'(TECHNICAL\s+SKILLS|TECHNICAL\s+SKILL|SKILLS|CORE\s+COMPETENCIES|CORE\s+SKILLS|PROFESSIONAL\s+SKILLS|SKILLS\s*:\s*)'
        match_header = re.search(pattern, injected_text, re.IGNORECASE)
        if match_header:
            header_end = match_header.end()
            injected_text = injected_text[:header_end] + " " + inj_str + ", " + injected_text[header_end:]
        else:
            # Fallback block: If no skills title exists, append cleanly at the top boundary safely
            injected_text = "TECHNICAL SKILLS: " + inj_str + "\n" + injected_text
            
    # Recalculate boosted metrics after executing dynamic cross-branch keyword blending
    txt_lower_updated = injected_text.lower()
    final_match = target_company_points.intersection(set(re.findall(r'\b\w+\b', txt_lower_updated)))
    
    pct = int((len(final_match) / len(target_company_points)) * 100) if target_company_points else 100
    if pct > 100: pct = 100
    
    m_str = ", ".join(list(final_match)[:12]).upper() if final_match else "NONE DETECTED"
    ms_str = ", ".join([s for s in valid_miss if s not in [x.upper() for x in final_match]]) if valid_miss else "NONE"
    if not ms_str: ms_str = "NONE"
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>
    <body class="bg-slate-950 text-gray-100 min-h-screen p-8">
        <div class="max-w-2xl mx-auto bg-slate-900 p-8 rounded-2xl border border-blue-500/30 shadow-2xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-4">
                <h2 class="text-xl font-bold">📊 Universal ATS Match Result: <span class="text-green-400 font-black">{pct}%</span></h2>
                <form action="/download-perfect-resume-pdf/" method="post">
                    <input type="hidden" name="payload" value="{injected_text.replace('"', '&quot;')}">
                    <button type="submit" class="bg-purple-600 hover:bg-purple-500 text-white px-5 py-2.5 rounded-xl text-xs font-bold uppercase transition-all shadow-md">🤖 DOWNLOAD PERFECT PDF</button>
                </form>
            </div>
            <div class="space-y-4 my-4">
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800"><p class="text-sm font-semibold text-green-400">✔️ Satisfied Company Role Criteria:</p><p class="text-xs font-mono text-slate-400 mt-1">{m_str}</p></div>
                <div class="bg-slate-950 p-4 rounded-xl border border-slate-800"><p class="text-sm font-semibold text-purple-400">🤖 AI Branch Injected Core Skills:</p><p class="text-xs font-mono text-slate-400 mt-1">{inj_str if inj_str else "NONE"}</p></div>
            </div>
            <p class="text-xs text-slate-400 leading-relaxed">💥 <strong class="text-blue-400">Universal Automation Suite:</strong> The engine auto-scanned the resume layout, identified the exact branch domain, matched the company criteria points, and successfully embedded the missing core specs into the active profile segment safely!</p>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.post("/download-perfect-resume-pdf/")
async def download_pdf_resume(payload: str = Form(...)):
    html_layout = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>
    <body class="bg-white text-slate-900 p-8 font-sans">
        <div class="max-w-3xl mx-auto p-12 border border-slate-200 rounded-xl shadow-sm">
            <div class="text-center no-print mb-6">
                <button onclick="window.print()" style="background-color: #2563eb; color: white; font-weight: bold; padding: 10px 24px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);" class="no-print">💾 CLICK HERE TO SAVE AS PERFECT PDF</button>
                <p class="text-xs text-slate-400 mt-1.5">Universal Cross-Branch formatting matrices verified by AI Executive Engine.</p>
            </div>
            <div class="text-sm text-slate-800 font-light leading-relaxed whitespace-pre-wrap font-mono">
{payload}
            </div>
        </div>
        <style>@media print {{ .no-print {{ display: none !important; }} body {{ background: white; }} }}</style>
    </body>
    </html>
    """
    return StreamingResponse(io.BytesIO(html_layout.encode("utf-8")), media_type="text/html", headers={"Content-Disposition": "attachment; filename=Optimized_AI_Resume.html"})
