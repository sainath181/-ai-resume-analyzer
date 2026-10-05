from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
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
        '<h1 class="text-4xl font-black text-white tracking-tight mb-2">Universal AI Resume Suite</h1>'
        '<p class="text-slate-400 text-xs font-light tracking-wide">Supports all Streams & Degrees: B.Tech, M.Tech, MBA, MCA, Pharmacy, Pharm.D</p></header>'
        '<form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-6">'
        '<div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800 hover:border-blue-500/40 transition-all duration-300 shadow-inner">'
        '<label class="block text-xs font-black text-slate-300 uppercase tracking-widest mb-3">1. Upload Candidate Resume (PDF)</label>'
        '<input type="file" name="resume" accept=".pdf" required class="block w-full text-xs text-slate-400 cursor-pointer"></div>'
        '<div class="space-y-2"><label class="block text-xs font-black text-slate-300 uppercase tracking-widest">2. Paste Custom Job Description (JD)</label>'
        '<textarea name="jd" rows="5" placeholder="Paste company criteria or keywords like python, typescript, react, autocad, marketing, finance, pharmacy, clinical, drug analytics here..." required class="w-full bg-slate-950/80 text-slate-200 p-4 rounded-2xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/40 text-sm font-light shadow-inner placeholder:text-slate-700"></textarea></div>'
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
    
    # 🎯 Universal Multi-Degree Smart Cross-Mapping Keyword Matrix
    all_b = {
        'python', 'java', 'javascript', 'typescript', 'react', 'node', 'express', 'mongodb', 'docker', 'sql', 'html', 'css', 'aws', 'git', 'github', 'c', 'cpp', 
        'autocad', 'solidworks', 'ansys', 'revit', 'staad', 'plc', 'scada',
        'marketing', 'finance', 'hr', 'sales', 'management', 'business', 'accounting', 'analytics', 'strategy',
        'pharmacy', 'clinical', 'drug', 'pharmacology', 'formulation', 'hplc', 'validation', 'medical', 'pharma'
    }
    
    imp = {w for w in j_w if w in all_b or (len(w) > 2 and w not in stop)}
    match = imp.intersection(r_w)
    miss = imp.difference(r_w)
    valid_miss = [s.title() if s.lower() not in ['sql', 'plc', 'hr', 'hplc'] else s.upper() for s in miss if s.lower() in all_b]
    
    languages_list, tools_list = [], []
    design_tools = {'autocad', 'solidworks', 'ansys', 'revit', 'staad', 'scada', 'plc', 'docker', 'hplc'}
    for s in valid_miss[:3]:
        if s.lower() in design_tools: tools_list.append(s)
        else: languages_list.append(s)
            
    inj_lang = ", " + ", ".join(languages_list) if languages_list else ""
    inj_tools = ", " + ", ".join(tools_list) if tools_list else ""
    inj_str = ", ".join(valid_miss[:3]) if valid_miss else "NONE"
    pct = int(((len(match) + len(valid_miss[:3])) / len(imp)) * 100) if imp else 100
    if pct > 100: pct = 100
    m_str = ", ".join(list(match)[:10]).upper() if match else "NONE"
    
    # 🧠 Universal Multi-Degree Branch Suggestion Filter Engine Matrix
    branch_injected_skills = ", ".join(valid_miss[:3]) if valid_miss else "Professional Industry Core Standards"
    
    is_eee = any(x in jd.lower() for x in ['plc', 'scada', 'electrical', 'embedded'])
    is_mech = any(x in jd.lower() for x in ['autocad', 'solidworks', 'ansys', 'revit', 'staad', 'mechanical'])
    is_mba = any(x in jd.lower() for x in ['marketing', 'finance', 'hr', 'sales', 'management', 'business', 'accounting', 'strategy'])
    is_pharma = any(x in jd.lower() for x in ['pharmacy', 'clinical', 'drug', 'pharmacology', 'formulation', 'hplc', 'validation', 'medical', 'pharma'])
    
    if is_eee:
        b1 = "Optimized electrical automated logic systems using " + branch_injected_skills + " to augment grid efficiency by 35%."
        b2 = "Integrated secure circuit dataset control parameters and streamlined distribution hardware production bounds."
        b3 = "Executed voltage signal pipeline hardware metrics and calibrated responsive automation controls natively."
    elif is_mech:
        b1 = "Spearheaded industrial CAD structural models and component designs utilizing " + branch_injected_skills + " to boost efficiency by 35%."
        b2 = "Integrated stress validation dataset parameters and streamlined geometric assembly functions under tight production tolerances."
        b3 = "Executed mechanical pipeline blueprint metrics and optimized component testing workflows to align with engineering targets."
    elif is_mba:
        b1 = "Spearheaded corporate market scaling strategies and business development initiatives utilizing " + branch_injected_skills + " to augment revenue growth by 35%."
        b2 = "Integrated financial dataset parameters and streamlined operational risk assessment metrics natively within enterprise bounds."
        b3 = "Executed multi-channel campaign analytics and optimized resource management workflows to align with strategic business roles."
    elif is_pharma:
        b1 = "Spearheaded advanced clinical drug analysis and formulation protocols utilizing " + branch_injected_skills + " to augment lab validation metrics by 35%."
        b2 = "Integrated secure pharmacological safety datasets and streamlined HPLC laboratory analysis metrics under strict regulatory standards."
        b3 = "Executed precise chemical purity pipeline workflows and optimized medical research operations to align with pharma criteria."
    else:
        b1 = "Spearheaded architectural scaling components utilizing " + branch_injected_skills + " to augment systemic performance by 35%."
        b2 = "Integrated secure database dataset parameters and streamlined server/system components natively within production bounds."
        b3 = "Executed multi-platform pipeline metrics and optimized responsive user dashboards to align with targets."

    # 🎯 Micro-Concatenation Stream: Immune to white screens and line-cutting compilation errors forever!
    res = '<!DOCTYPE html><html><head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script>'
    res += '<style>@media screen { .resume-preview { display: none !important; } } @media print { .no-print { display: none !important; } .resume-preview { display: block !important; background: white !important; color: black !important; padding: 0 !important; } body { background: white; } }</style></head>'
    res += '<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-black text-gray-100 min-h-screen p-4 flex items-center justify-center font-sans">'
    res += '<div class="max-w-2xl w-full bg-slate-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800 shadow-2xl no-print">'
    res += '<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800/80 pb-4 mb-4 gap-4">'
    res += '<div><h2 class="text-xl font-black text-white tracking-wide uppercase">📊 ATS Optimization Matrix</h2>'
    res += '<p class="text-xs text-green-400 font-black">' + str(pct) + '% Live Match 🎉</p></div>'
    res += '<button onclick="window.print()" class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3.5 rounded-xl text-xs font-black uppercase tracking-widest shadow-lg">🤖 DOWNLOAD PERFECT PDF</button></div>'
    res += '<div class="space-y-4 mb-6"><div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 shadow-inner"><p class="text-xs font-black text-green-400 uppercase tracking-widest">✔️ Verified Target Matches:</p><p class="text-xs font-mono text-slate-300 mt-2 leading-relaxed">' + m_str + '</p></div>'
    res += '<div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 shadow-inner"><p class="text-xs font-black text-purple-400 uppercase tracking-widest">🤖 AI Section-Mapped Injected Skills:</p><p class="text-xs font-mono text-slate-300 mt-2 leading-relaxed">' + inj_str + '</p></div></div></div>'
