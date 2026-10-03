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
    h = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Universal AI Resume Suite</title>'
        '<script src="https://tailwindcss.com"></script></head>'
        '<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-black text-gray-100 min-h-screen flex items-center justify-center p-4 font-sans">'
        '<div class="max-w-xl w-full bg-slate-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800 shadow-2xl relative">'
        '<header class="text-center mb-8">'
        '<div class="inline-flex items-center bg-blue-500/10 border border-blue-500/30 px-4 py-1.5 rounded-full text-xs font-bold text-blue-400 mb-4 uppercase tracking-widest shadow-inner">⚡ Premium AI Executive Suite</div>'
        '<h1 class="text-4xl font-black text-white tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">Universal AI Resume Suite</h1>'
        '<p class="text-slate-400 text-xs font-light tracking-wide">Supports all streams: CSE, IT, ME, CE, ECE, EEE</p></header>'
        '<form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">'
        '<div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800 hover:border-blue-500/40 transition-all duration-300 shadow-inner">'
        '<label class="block text-xs font-black text-slate-300 uppercase tracking-widest mb-3">1. Upload Candidate Resume (PDF)</label>'
        '<input type="file" name="resume" accept=".pdf" required class="block w-full text-xs text-slate-400 cursor-pointer"></div>'
        '<div class="space-y-2"><label class="block text-xs font-black text-slate-300 uppercase tracking-widest">2. Paste Custom Job Description (JD)</label>'
        '<textarea name="jd" rows="5" placeholder="Paste company criteria or keywords like python, react, node here..." required class="w-full bg-slate-950/80 text-slate-200 p-4 rounded-2xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/40 text-sm font-light shadow-inner placeholder:text-slate-700"></textarea></div>'
        '<button type="submit" class="w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white font-extrabold py-4 rounded-2xl shadow-xl tracking-widest text-xs uppercase transition-all duration-300 hover:scale-[1.01]">Optimize Profile State</button>'
        '</form></div></body></html>'
    )
    return HTMLResponse(content=h, status_code=200)

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
    pct = int(((len(match) + len(valid_miss[:3])) / len(imp)) * 100) if imp else 100
    if pct > 100: pct = 100
    m_str = ", ".join(list(match)[:10]).upper() if match else "NONE"
    blt_payload = "-".join(valid_miss[:3]) if valid_miss else "EMPTY"
    
    res = (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>'
        '<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-black text-gray-100 min-h-screen p-8 flex items-center justify-center relative overflow-hidden">'
        '<div class="max-w-2xl w-full bg-slate-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800 shadow-2xl">'
        '<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800/80 pb-6 mb-6 gap-4">'
        '<div><h2 class="text-xl font-black text-white tracking-wide uppercase">📊 ATS Optimization Matrix</h2>'
        f'<p class="text-xs text-slate-400 mt-1">Score: <span class="text-green-400 font-black">{pct}% Live Match</span> 🎉</p></div>'
        '<form action="/download-perfect-resume-pdf/" method="post" class="w-full sm:w-auto">'
        f'<input type="hidden" name="bullets" value="{blt_payload}">'
        '<button type="submit" class="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3.5 rounded-xl text-xs font-black uppercase tracking-widest shadow-lg">🤖 DOWNLOAD PERFECT PDF</button>'
        '</form></div><div class="space-y-4 mb-6">'
        f'<div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 shadow-inner"><p class="text-xs font-black text-green-400 uppercase tracking-widest">✔️ Verified Target Matches:</p><p class="text-xs font-mono text-slate-300 mt-2 leading-relaxed">{m_str}</p></div>'
        f'<div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 shadow-inner"><p class="text-xs font-black text-purple-400 uppercase tracking-widest">🤖 AI Case-Sensitive Injected Skills:</p><p class="text-xs font-mono text-slate-300 mt-2 leading-relaxed">{inj_str if inj_str else "NONE"}</p></div>'
        '</div><p class="text-[10px] text-slate-500 text-center font-light tracking-wide">💥 AI Framework Active: Auto-detected layout casing rules to protect candidate profile alignment.</p></div></body></html>'
    )
    return HTMLResponse(content=res, status_code=200)

@app.post("/download-perfect-resume-pdf/")
async def download_pdf_resume(bullets: str = Form(...)):
    inj = ""
    if bullets.strip() and bullets != "EMPTY":
        inj = ", " + ", ".join([b.strip() for b in bullets.split("-")])
    h_pdf = (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script></head>'
        '<body class="bg-white text-slate-900 p-8 font-sans"><div class="max-w-3xl mx-auto p-12 border border-slate-200 rounded-xl shadow-sm">'
        '<div class="text-center no-print mb-6"><button onclick="window.print()" class="bg-blue-600 text-white font-bold px-6 py-2 rounded shadow no-print" style="background-color:#2563eb; color:white; font-weight:bold; padding:10px 24px; border-radius:8px;">💾 CLICK HERE TO SAVE AS PERFECT PDF</button></div>'
        '<div class="border-b-4 border-blue-900 pb-4 mb-6"><h1 class="text-3xl font-black text-slate-900">G. SAINATH</h1><p class="text-sm text-slate-600 mt-1">Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com</p></div>'
        '<div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2">CAREER OBJECTIVE</h2><p class="text-sm text-slate-700 leading-relaxed">Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals.</p></div>'
        '<div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2">EDUCATION</h2><div class="flex justify-between text-sm"><div><p class="font-bold text-slate-800">B.Tech - Computer Science and Engineering</p><p class="text-slate-600">Narayana Engineering College, Gudur</p></div><p class="font-semibold text-blue-800">CGPA: 7.8/10 (78%) | Current Year: 4-1</p></div></div>'
        f'<div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2">TECHNICAL SKILLS</h2><ul class="space-y-1.5 text-sm text-slate-700"><li><strong>Programming Languages:</strong> C, Java{inj}</li><li><strong>Web Technologies:</strong> HTML, CSS, JavaScript (Basics)</li><li><strong>Database:</strong> SQL Basics, Database Fundamentals</li><li><strong>Tools:</strong> Visual Studio Code, GitHub</li><li><strong>Core Concepts:</strong> OOP, Programming Fundamentals, Problem Solving</li></ul></div>'
        '<div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2">PROJECT</h2><div class="text-sm"><div class="flex justify-between font-semibold text-slate-800"><p>Web Application Development Project</p><p class="text-blue-600">https://netlify.app</p></div><ul class="list-disc pl-5 mt-2 space-y-1.5 text-slate-700 font-light"><li>Developed and deployed a responsive web application.</li><li>Designed user-friendly interfaces and layouts.</li><li>Integrated database functionality for storing and retrieving data.</li><li>Performed testing and debugging to improve performance and usability.</li></ul></div></div>'
        '<div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2">STRENGTHS</h2><p class="text-sm text-slate-700 font-light tracking-wide">• Quick Learner &bull; Team Player &bull; Communication Skills &bull; Problem Solving &bull; Adaptability &bull; Time Management</p></div>'
