from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import pypdf, io, re

app = FastAPI()

def extract_text_from_pdf(b):
    r = pypdf.PdfReader(io.BytesIO(b))
    return "\n".join([p.extract_text() or "" for p in r.pages])

@app.get("/", response_class=HTMLResponse)
async def read_item():
    h = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI Resume Suite</title><script src="https://tailwindcss.com"></script></head><body class="bg-slate-950 text-gray-100 min-h-screen flex items-center justify-center p-4"><div class="max-w-xl w-full bg-slate-900/60 p-8 rounded-3xl border border-slate-800 shadow-2xl"><h1 class="text-3xl font-black text-white text-center mb-6">Universal AI Resume Suite</h1><form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6"><div><label class="block text-xs font-bold text-slate-300 uppercase mb-2">1. Upload Resume (PDF)</label><input type="file" name="resume" accept=".pdf" required class="block w-full text-xs text-slate-400"></div><div><label class="block text-xs font-bold text-slate-300 uppercase mb-2">2. Paste Job Description (JD)</label><textarea name="jd" rows="5" placeholder="Paste company criteria here..." required class="w-full bg-slate-950 text-slate-200 p-4 rounded-xl border border-slate-800 text-sm"></textarea></div><button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl tracking-wider text-xs uppercase transition-all">Optimize Profile State</button></form></div></body></html>'''
    return HTMLResponse(content=h, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    txt = extract_text_from_pdf(contents)
    j_w, r_w = set(re.findall(r'\b\w+\b', jd.lower())), set(re.findall(r'\b\w+\b', txt.lower()))
    all_b = {'python', 'java', 'javascript', 'typescript', 'react', 'node', 'express', 'mongodb', 'docker', 'sql', 'html', 'css', 'aws', 'git', 'github', 'c', 'cpp', 'autocad', 'solidworks', 'ansys', 'revit', 'staad', 'plc', 'scada'}
    imp = {w for w in j_w if w in all_b}
    match = imp.intersection(r_w)
    miss = imp.difference(r_w)
    valid_miss = [s.title() if s.lower() not in ['sql', 'plc'] else s.upper() for s in miss if s.lower() in all_b]
    
    languages_list, tools_list = [], []
    design_tools = {'autocad', 'solidworks', 'ansys', 'revit', 'staad', 'scada', 'plc', 'docker'}
    for s in valid_miss[:3]:
        if s.lower() in design_tools: tools_list.append(s)
        else: languages_list.append(s)
            
    inj_lang = ", " + ", ".join(languages_list) if languages_list else ""
    inj_tools = ", " + ", ".join(tools_list) if tools_list else ""
    inj_str = ", ".join(valid_miss[:3]) if valid_miss else "NONE"
    pct = int(((len(match) + len(valid_miss[:3])) / len(imp)) * 100) if imp else 100
    m_str = ", ".join(list(match)[:10]).upper() if match else "NONE"
    
    cse_skills = ", ".join(languages_list) if languages_list else "Modern Software Architectures"
    b1 = "Spearheaded architectural scaling components utilizing " + cse_skills + " to augment systemic performance by 35%."
    b2 = "Integrated secure database dataset parameters and streamlined API server routes natively within production bounds."
    b3 = "Executed multi-platform pipeline metrics and optimized responsive front-end user dashboards to align with targets."
    
    res = '<!DOCTYPE html><html><head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script><style>@media screen { .preview { display: none !important; } } @media print { .no-p { display: none !important; } .preview { display: block !important; background: white !important; color: black !important; padding: 0 !important; } body { background: white; } }</style></head><body class="bg-slate-950 text-gray-100 min-h-screen p-4 flex flex-col items-center justify-center font-sans"><div class="max-w-2xl w-full bg-slate-900/60 p-8 rounded-3xl border border-slate-800 shadow-2xl no-p"><div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-4"><div><h2 class="text-xl font-black text-white tracking-wide uppercase">ATS Optimization Matrix</h2><p class="text-xs text-green-400 font-black">' + str(pct) + '% Live Match</p></div><button onclick="window.print()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-xs font-bold uppercase tracking-widest shadow-lg">DOWNLOAD PERFECT PDF</button></div><div class="space-y-4"><div class="bg-slate-950 p-4 rounded-xl border border-slate-800"><p class="text-xs font-bold text-green-400 uppercase tracking-widest">Verified Target Matches:</p><p class="text-xs font-mono text-slate-300 mt-1">' + m_str + '</p></div><div class="bg-slate-950 p-4 rounded-xl border border-slate-800"><p class="text-xs font-bold text-purple-400 uppercase tracking-widest">AI Section-Mapped Injected Skills:</p><p class="text-xs font-mono text-slate-300 mt-1">' + inj_str + '</p></div></div></div><div class="preview max-w-3xl mx-auto p-12 bg-white text-slate-900 font-sans"><div class="border-b-4 border-blue-900 pb-2 mb-4"><h1 class="text-2xl font-black text-slate-900">G. SAINATH</h1><p class="text-xs text-slate-600">Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com</p></div><div class="mb-4"><h2 class="text-xs font-bold text-blue-900 uppercase mb-1">CAREER OBJECTIVE</h2><p class="text-xs text-slate-700 leading-relaxed">Computer Science Engineering student seeking an entry-level Web Developer position.</p></div><div class="mb-4"><h2 class="text-xs font-bold text-blue-900 uppercase mb-1">EDUCATION</h2><div class="flex justify-between text-xs"><div><p class="font-bold text-slate-800">B.Tech - Computer Science and Engineering</p><p class="text-slate-600">Narayana Engineering College, Gudur</p></div><p class="font-semibold text-blue-800">CGPA: 7.8/10</p></div></div><div class="mb-4"><h2 class="text-xs font-bold text-blue-900 uppercase mb-1">TECHNICAL SKILLS</h2><ul class="space-y-1 text-xs text-slate-700"><li><strong>Programming Languages:</strong> C, Java' + inj_lang + '</li><li><strong>Web Technologies:</strong> HTML, CSS, JavaScript (Basics)</li><li><strong>Tools:</strong> VS Code, GitHub' + inj_tools + '</li></ul></div><div class="mb-4"><h2 class="text-xs font-bold text-blue-900 uppercase mb-1">PROJECT</h2><div class="text-xs"><p class="font-semibold text-slate-800">Web Application Development Project</p><ul class="list-disc pl-5 mt-1 space-y-1 text-slate-700"><li>Developed and deployed a responsive web application.</li><li>' + b1 + '</li><li>' + b2 + '</li><li>' + b3 + '</li></ul></div></div></div></body></html>'
    return HTMLResponse(content=res, status_code=200)
