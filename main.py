from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import pypdf, io, re, base64

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
    ui_b64 = "PCFET0NUWVBFIGh0bWw+PGh0bWwgbGFuZz0iZW4iPjxoZWFkPjxtZXRhIGNoYXJzZXQ9IlVURi04Ij48dGl0bGU+VW5pdmVyc2FsIEFJIFJlc3VtZSBTdWl0ZTwvdGl0bGU+PHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuLnRhaWx3aW5kY3NzLmNvbSI+PC9zY3JpcHQ+PC9oZWFkPjxib2R5IGNsYXNzPSJiZy1ncmFkaWVudC10by1iciBmcm9tLXNsYXRlLTk1MCB2aWEtc2xhdGUtOTAwIHRvLWJsYWNrIHRleHQtZ3JheS0xMDAgbWluLWhzY3JlZW4gZmxleCBpdGVtcy1jZW50ZXIganVzdGlmeS1jZW50ZXIgcC00IGZvbnQtc2FucyI+PG1heC13LXhsIGNsYXNzPSJtYXgtdy14bCB3LWZ1bGwgYmctc2xhdGUtOTAwLzQwIGJhY2tkcm9wLWJsdXItMnhsIHAtOCByb3VuZGVkLTN4bCBib3JkZXIgYm9yZGVyLXNsYXRlLTgwMCBzaGFkb3ctMnhsIHJlbGF0aXZlIj48aGVhZGVyIGNsYXNzPSJ0ZXh0LWNlbnRlciBtYi04Ij48ZGl2IGNsYXNzPSJpbmxpbmUtZmxleCBpdGVtcy1jZW50ZXIgYmctYmx1ZS01MDAvMTAgYm9yZGVyIGJvcmRlci1ibHVlLTUwMC8zMCBweC00IHB5LTEuNSByb3VuZGVkLWZ1bGwgdGV4dC14cyBmb250LWJvbGQgdGV4dC1ibHVlLTQwMCBtYi00IHVwcGVyY2FzZSB0cmFja2luZy13aWRlc3QiPsatIFByZW1pdW0gQUkgRXhlY3V0aXZlIFN1aXRlPC9kaXY+PGgxIGNsYXNzPSJ0ZXh0LTR4bCBmb250LWJsYWNrIHRleHQtd2hpdGUgdHJhY2tpbmctdGlnaHQgbWItMiI+VW5pdmVyc2FsIEFJIFJlc3VtZSBTdWl0ZTwvaDE+PHAgY2xhc3M9InRleHQtc2xhdGUtNDAwIHRleHQteHMgZm9udC1saWdodCI+U3VwcG9ydHMgYWxsIHN0cmVhbXM6IENTRSwgSVQsIE1FLCBDRSwgRUNFLCBFRUU8L3A+PC9oZWFkZXI+PGZvcm0gYWN0aW9uLz0iL3VwbG9hZC1yZXN1bWUvIiBtZXRob2Q9InBvc3QiIGVuY3R5cGU9Im11bHRpcGFydC9mb3JtLWRhdGEiIGNsYXNzPSJzcGFjZS15LTYiPjxkaXYgY2xhc3M9ImJnLXNsYXRlLTk1MC82MCBwLTUgcm91bmRlZC0yeGwgYm9yZGVyIGJvcmRlci1zbGF0ZS04MDAgaG92ZXI6Ym9yZGVyLWJsdWUtNTAwLzQwIHRyYW5zaXRpb24tYWxsIj48bGFiZWwgY2xhc3M9ImJsb2NrIHRleHQteHMgZm9udC1ibGFjayB0ZXh0LXNsYXRlLTMwMCB1cHBlcmNhc2UgbWItMyI+MS4gVXBsb2FkIENhbmRpZGF0ZSBSZXN1bWUgKFBERik8L2xhYmVsPjxpbnB1dCB0eXBlPSJmaWxlIiBuYW1lPSJyZXN1bWUiIGFjY2VwdD0iLnBkZiIgcmVxdWlyZWQgY2xhc3M9ImJsb2NrIHctZnVsbCB0ZXh0LXhzIGN1cnNvci1wb2ludGVyIj48L2Rpdj48ZGl2IGNsYXNzPSJzcGFjZS15LTIiPjxsYWJlbCBjbGFzcz0iYmxvY2sgdGV4dC14cyBmb250LWJsYWNrIHRleHQtc2xhdGUtMzAwIHVwcGVyY2FzZSI+Mi4gUGFzdGUgQ3VzdG9tIEpvYiBEZXNjcmlwdGlvbiAoSkQpPC9sYWJlbD48dGV4dGFyZSBuYW1lPSJqZCIgcm93cz0iNSIgcGxhY2Vob2xkZXI9IlBhc3RlIGNvbXBhbnkgY3JpdGVyaWEgb3Iga2V5d29yZHMgbGlrZSBweXRob24sIHR5cGVzY3JpcHQsIHJlYWN0LCBub2RlLCBhdXRvY2FkIGhlcmUuLi4iIHJlcXVpcmVkIGNsYXNzPSJ3LWZ1bGwgYmctc2xhdGUtOTUwLzgwIHRleHQtc2xhdGUtMjAwIHAtNCByb3VuZGVkLTJ4bCBib3JkZXIgYm9yZGVyLXNsYXRlLTgwMCBmb2N1czpvdXRsaW5lLW5vbmUgdGV4dC1zbSBmb250LWxpZ2h0Ij48L3RleHRhcmU+PC9kaXY+PGJ1dHRvbiB0eXBlPSJzdWJtaXQiIGNsYXNzPSJ3LWZ1bGwgYmctZ3JhZGllbnQtdG8iciBmcm9tLWJsdWUtNjAwIHRvLXB1cnBsZS02MDAgdGV4dC13aGl0ZSBmb250LWV4dHJhYm9sZCBweS00IHJvdW5kZWQtMnhsIHRleHQteHMgdXBwZXJjYXNlIHRyYWNraW5nLXdpZGVzdCI+T3B0aW1pemUgUHJvZmlsZSBTdGF0ZTwvYnV0dG9uPjwvZm9ybT48L2Rpdj48L2JvZHk+PC9odG1sPg=="
    return HTMLResponse(content=base64.b64decode(ui_b64).decode("utf-8"), status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    txt = fix_spelling(extract_text_from_pdf(contents))
    j_w, r_w = set(re.findall(r'\b\w+\b', jd.lower())), set(re.findall(r'\b\w+\b', txt.lower()))
    stop = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are'}
    all_b = {'python', 'java', 'javascript', 'typescript', 'react', 'node', 'express', 'mongodb', 'docker', 'sql', 'html', 'css', 'aws', 'git', 'github', 'c', 'cpp', 'autocad', 'solidworks', 'ansys', 'revit', 'staad', 'plc', 'scada'}
    imp = {w for w in j_w if w in all_b or (len(w) > 2 and w not in stop)}
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
    inj_str = ", ".join(valid_miss[:3]) if valid_miss else ""
    pct = int(((len(match) + len(valid_miss[:3])) / len(imp)) * 100) if imp else 100
    if pct > 100: pct = 100
    m_str = ", ".join(list(match)[:10]).upper() if match else "NONE"
    
    lead_tech = inj_str if inj_str else "Modern Tech Stack"
    b1 = "Spearheaded architectural scaling components utilizing " + lead_tech + " to augment systemic performance by 35%."
    b2 = "Integrated secure dataset logic protocols and streamlined framework functions via proactive technical alignments."
    b3 = "Executed multi-platform pipeline metrics and optimized dynamic user interfaces to align with hiring roles."
    
    res_raw = f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><script src="https://tailwindcss.com"></script>
    <style>@media screen {{ .preview-box {{ display: none !important; }} }} @media print {{ .no-print {{ display: none !important; }} .preview-box {{ display: block !important; background: white !important; color: black !important; padding: 0 !important; }} body {{ background: white; }} }}</style></head>
    <body class="bg-gradient-to-br from-slate-950 via-slate-900 to-black text-gray-100 min-h-screen p-4 flex items-center justify-center font-sans">
        <div class="max-w-2xl w-full bg-slate-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800 shadow-2xl no-print">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800/80 pb-4 mb-4 gap-4">
                <div><h2 class="text-xl font-black text-white tracking-wide uppercase">📊 ATS Optimization Matrix</h2><p class="text-xs text-green-400 font-black">{pct}% Live Match 🎉</p></div>
                <button onclick="window.print()" class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest shadow-lg">🤖 DOWNLOAD PERFECT PDF</button>
            </div>
            <div class="space-y-4 mb-6">
                <div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 shadow-inner"><p class="text-xs font-black text-green-400 uppercase tracking-widest">✔️ Verified Target Matches:</p><p class="text-xs font-mono text-slate-300 mt-2 leading-relaxed">{m_str}</p></div>
                <div class="bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 shadow-inner"><p class="text-xs font-black text-purple-400 uppercase tracking-widest">🤖 AI Section-Mapped Injected Skills:</p><p class="text-xs font-mono text-slate-300 mt-2 leading-relaxed">{inj_str if inj_str else "NONE"}</p></div>
                <div class="bg-slate-950/60 p-5 rounded-2xl border border-purple-500/20 shadow-lg"><p class="text-xs font-black text-purple-400 uppercase tracking-widest">🤖 AI Bullet Point Suggester Active:</p><p class="text-[11px] font-mono text-slate-400 mt-2 italic">"Successfully auto-blended 3 pristine bullet descriptors right inside your Project domain below!"</p></div>
            </div>
        </div>
        <div class="preview-box max-w-3xl mx-auto p-12 bg-white text-slate-900 font-sans">
            <div class="border-b-4 border-blue-900 pb-4 mb-6"><h1 class="text-3xl font-black text-slate-900">G. SAINATH</h1><p class="text-sm text-slate-600 mt-1">Gudur, Andhra Pradesh | 9014882483 | gsainathroyal73212@gmail.com</p></div>
            <div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">CAREER OBJECTIVE</h2><p class="text-sm text-slate-700 leading-relaxed">Computer Science Engineering student seeking an entry-level Web Developer position. Eager to apply programming knowledge, web development fundamentals, and problem-solving skills while learning from industry professionals.</p></div>
            <div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">EDUCATION</h2><div class="flex justify-between text-sm"><div><p class="font-bold text-slate-800">B.Tech - Computer Science and Engineering</p><p class="text-slate-600">Narayana Engineering College, Gudur</p></div><p class="font-semibold text-blue-800">CGPA: 7.8/10 (78%) | Current Year: 4-1</p></div></div>
            <div class="mb-6"><h2 class="text-sm font-bold text-blue-900 uppercase mb-2 tracking-wide">TECHNICAL SKILLS</h2><ul class="space-y-1.5 text-sm text-slate-700"><li><strong>Programming Languages:</strong> C, Java{inj_lang}</li><li><strong>Web Technologies:</strong> HTML, CSS, JavaScript (Basics)</li><li><strong>Database:</strong> SQL Basics, Database Fundamentals</li><li><strong>Tools:</strong> Visual Studio Code, GitHub{inj_tools}</li><li><strong>Core Concepts:</strong> OOP, Programming Fundamentals, Problem Solving</li></ul></div>
