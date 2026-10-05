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
    ui_b64 = "PCFET0NUWVBFIGh0bWw+PGh0bWwgbGFuZz0iZW4iPjxoZWFkPjxtZXRhIGNoYXJzZXQ9IlVURi04Ij48dGl0bGU+VW5pdmVyc2FsIEFJIFJlc3VtZSBTdWl0ZTwvdGl0bGU+PHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuLnRhaWx3aW5kY3NzLmNvbSI+PC9zY3JpcHQ+PC9oZWFkPjxib2R5IGNsYXNzPSJiZy1ncmFkaWVudC10by1iciBmcm9tLXNsYXRlLTk1MCB2aWEtc2xhdGUtOTAwIHRvLWJsYWNrIHRleHQtZ3JheS0xMDAgbWluLWhzY3JlZW4gZmxleCBpdGVtcy1jZW50ZXIganVzdGlmeS1jZW50ZXIgcC00IGZvbnQtc2FucyI+PG1heC13LXhsIGNsYXNzPSJtYXgtdy14bCB3LWZ1bGwgYmctc2xhdGUtOTAwLzQwIGJhY2tkcm9wLWJsdXItMnhsIHAtOCByb3VuZGVkLTN4bCBib3JkZXIgYm9yZGVyLXNsYXRlLTgwMCBzaGFkb3ctMnhsIHJlbGF0aXZlIj48aGVhZGVyIGNsYXNzPSJ0ZXh0LWNlbnRlciBtYi04Ij48ZGl2IGNsYXNzPSJpbmxpbmUtZmxleCBpdGVtcy1jZW50ZXIgYmctYmx1ZS01MDAvMTAgYm9yZGVyIGJvcmRlci1ibHVlLTUwMC8zMCBweC00IHB5LTEuNSByb3VuZGVkLWZ1bGwgdGV4dC14cyBmb250LWJvbGQgdGV4dC1ibHVlLTQwMCBtYi00IHVwcGVyY2FzZSB0cmFja2luZy13aWRlc3QiPsatIFByZW1pdW0gQUkgRXhlY3V0aXZlIFN1aXRlPC9kaXY+PGgxIGNsYXNzPSJ0ZXh0LTR4bCBmb250LWJsYWNrIHRleHQtd2hpdGUgdHJhY2tpbmctdGlnaHQgbWItMiI+VW5pdmVyc2FsIEFJIFJlc3VtZSBTdWl0ZTwvaDE+PHAgY2xhc3M9InRleHQtc2xhdGUtNDAwIHRleHQteHMgZm9udC1saWdodCI+U3VwcG9ydHMgYWxsIHN0cmVhbXM6IENTRSwgSVQsIE1FLCBDRSwgRUNFLCBFRUU8L3A+PC9oZWFkZXI+PGZvcm0gYWN0aW9uPSIvdXBsb2FkLXJlc3VtZS8iIG1ldGhvZD0icG9zdCIgZW5jdHlwZT0ibXVsdGlwYXJ0L2Zvcm0tZGF0YSIgY2xhc3M9InNwYWNlLXktNiI+PGRpdiIGNsYXNzPSJiZy1ncmFkaWVudC10by1iciBmcm9tLXNsYXRlLTk1MCB2aWEtc2xhdGUtOTAwIHRvLWJsYWNrIHAtNSByb3VuZGVkLTJ4bCBib3JkZXIgYm9yZGVyLXNsYXRlLTgwMCBob3Zlcjpib3JkZXItYmx1ZS01MDAvNDAgdHJhbnNpdGlvbi1hbGwiPjxsYWJlbCBjbGFzcz0iYmxvY2sgdGV4dC14cyBmb250LWJvbGQgdGV4dC1zbGF0ZS0zMDAgdXBwZXJjYXNlIG1iLTMiPjEuVXBsb2FkIENhbmRpZGF0ZSBSZXN1bWUgKFBERik8L2xhYmVsPjxpbnB1dCB0eXBlPSJmaWxlIiBuYW1lPSJyZXN1bWUiIGFjY2VwdD0iLnBkZiIgcmVxdWlyZWQgY2xhc3M9ImJsb2NrIHctZnVsbCB0ZXh0LXhzIGN1cnNvci1wb2ludGVyIj48L2Rpdj48ZGl2IGNsYXNzPSJzcGFjZS15LTIiPjxsYWJlbCBjbGFzcz0iYmxvY2sgdGV4dC14cyBmb250LWJvbGQgdGV4dC1zbGF0ZS0zMDAgdXBwZXJjYXNlIj4yLiBQYXN0ZSBDdXN0b20gSm9iIERlc2NyaXB0aW9uIChKRCk8L2xhYmVsPjx0ZXh0YXJlIG5hbWU9ImpkIiByb3dzPSI1IiBwbGFjZWhvbGRlcj0iUGFzdGUgY29tcGFueSBjcml0ZXJpYSBvciBrZXl3b3JkcyBsaWtlIHB5dGhvbiwgdHlwZXNjcmlwdCwgcmVhY3QsIG5vZGUsIGF1dG9jYWQgaGVyZS4uLiIgcmVxdWlyZWQgY2xhc3M9InctZnVsbCBiZy1zbGF0ZS05NTAvODAgdGV4dC1zbGF0ZS0yMDAgcC00IHJvdW5kZWQtMnhsIGJvcmRlciJ4Ym9yZGVyLXNsYXRlLTgwMCBmb2N1czpvdXRsaW5lLW5vbmUgdGV4dC1zbSBmb250LWxpZ2h0Ij48L3RleHRhcmU+PC9kaXY+PGJ1dHRvbiB0eXBlPSJzdWJtaXQiIGNsYXNzPSJ3LWZ1bGwgYmctZ3JhZGllbnQtdG8iciBmcm9tLWJsdWUtNjAwIHRvLXB1cnBsZS02MDAgdGV4dC13aGl0ZSBmb250LWV4dHJhYm9sZCBweS00IHJvdW5kZWQtMnhsIHRleHQteHMgdXBwZXJjYXNlIHRyYWNraW5nLXdpZGVzdCI+T3B0aW1pemUgUHJvZmlsZSBTdGF0ZTwvYnV0dG9uPjwvZm9ybT48L2Rpdj48L2JvZHk+PC9odG1sPg=="
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
    inj_str = ", ".join(valid_miss[:3]) if valid_miss else "NONE"
    pct = int(((len(match) + len(valid_miss[:3])) / len(imp)) * 100) if imp else 100
    if pct > 100: pct = 100
    m_str = ", ".join(list(match)[:10]).upper() if match else "NONE"
    
    lead_tech = inj_str if inj_str else "Modern Tech Stack"
    b1 = "Spearheaded architectural scaling components utilizing " + lead_tech + " to augment systemic performance by 35%."
    b2 = "Integrated secure dataset logic protocols and streamlined framework functions via proactive technical alignments."
    b3 = "Executed multi-platform pipeline metrics and optimized dynamic user interfaces to align with hiring roles."
    
    # 🎯 Complete Base64 Secure Result Output Strategy: 0% white screen, 0% github line cuts!
