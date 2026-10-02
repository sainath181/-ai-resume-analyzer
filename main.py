from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pypdf
import io
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def extract_text_from_pdf(file_bytes):
    pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

@app.get("/", response_class=HTMLResponse)
async def read_item(request: any):
    return templates.TemplateResponse("index.html", {"request": request, "processed": False})

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(request: any, resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    resume_text = extract_text_from_pdf(contents)
    
    jd_words = set(re.findall(r'\b\w+\b', jd.lower()))
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    
    important_jd_keywords = {word for word in jd_words if len(word) > 2}
    matched_skills = important_jd_keywords.intersection(resume_words)
    
    if len(important_jd_keywords) > 0:
        match_percentage = int((len(matched_skills) / len(important_jd_keywords)) * 100)
    else:
        match_percentage = 0
        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "processed": True,
        "match_percentage": match_percentage,
        "matched_skills": ", ".join(list(matched_skills)[:8]) if matched_skills else "None Detected",
        "missing_skills": "None"
    })

@app.post("/match-job/", response_class=HTMLResponse)
async def match_job(request: any, resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    resume_text = extract_text_from_pdf(contents)
    
    jd_words = set(re.findall(r'\b\w+\b', jd.lower()))
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    
    important_jd_keywords = {word for word in jd_words if len(word) > 2}
    matched_skills = important_jd_keywords.intersection(resume_words)
    
    if len(important_jd_keywords) > 0:
        match_percentage = int((len(matched_skills) / len(important_jd_keywords)) * 100)
    else:
        match_percentage = 0
        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "processed": True,
        "match_percentage": match_percentage,
        "matched_skills": ", ".join(list(matched_skills)[:8]) if matched_skills else "None Detected",
        "missing_skills": "None"
    })
