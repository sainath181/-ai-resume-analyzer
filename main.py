from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import pypdf
import io
import re

app = FastAPI()

def extract_text_from_pdf(file_bytes):
    pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

@app.get("/", response_class=HTMLResponse)
async def read_item():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Resume Parser & Optimizer</title>
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-gray-100 min-h-screen font-sans">
        <div class="max-w-4xl mx-auto py-10 px-4">
            <header class="text-center mb-10">
                <h1 class="text-4xl font-extrabold text-blue-500 mb-2">⚡ AI Resume Parser & Optimizer</h1>
                <p class="text-gray-400">Scan Resumes Against Any Job Description Dynamically</p>
            </header>
            <div class="bg-gray-800 p-6 rounded-lg shadow-xl mb-8">
                <h2 class="text-xl font-bold text-blue-400 mb-4">🎯 ATS Optimization Engine</h2>
                <form action="/upload-resume/" method="post" enctype="multipart/form-data" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">1. Upload Resume (PDF)</label>
                        <input type="file" name="resume" accept=".pdf" required class="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">2. Paste Job Description (JD)</label>
                        <textarea name="jd" rows="4" placeholder="Paste target job description here..." required class="w-full bg-gray-700 text-white p-3 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
                    </div>
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-md transition duration-200">Calculate Compatibility Match</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/upload-resume/", response_class=HTMLResponse)
async def upload_resume(resume: UploadFile = File(...), jd: str = Form(...)):
    contents = await resume.read()
    resume_text = extract_text_from_pdf(contents)
    jd_words = set(re.findall(r'\b\w+\b', jd.lower()))
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    important_jd_keywords = {word for word in jd_words if len(word) > 2}
    matched_skills = important_jd_keywords.intersection(resume_words)
    missing_skills = important_jd_keywords.difference(resume_words)
    match_percentage = int((len(matched_skills) / len(important_jd_keywords)) * 100) if important_jd_keywords else 0
    matched_str = ", ".join(list(matched_skills)[:8]) if matched_skills else "None Detected"
    missing_str = ", ".join(list(missing_skills)[:6]) if missing_skills else "None"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI Resume Parser & Optimizer</title>
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-gray-100 min-h-screen font-sans">
        <div class="max-w-4xl mx-auto py-10 px-4">
            <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-blue-500/30 mb-8">
                <h2 class="text-2xl font-bold text-blue-400 mb-4">📊 ATS Compatibility Audit Summary</h2>
                <div class="flex items-center space-x-4 mb-6">
                    <div class="text-5xl font-black text-green-400 bg-gray-950 p-4 rounded-full border border-green-500/40">{match_percentage}%</div>
                    <div><p class="text-gray-400">Real-Time Match Score Percentage</p></div>
                </div>
                <div class="space-y-4">
                    <div><h3 class="text-md font-bold text-green-400">✔️ Matched Technical Keywords:</h3><p class="text-gray-300 text-sm bg-gray-700/50 p-3 rounded-md mt-1">{matched_str}</p></div>
                    <div><h3 class="text-md font-bold text-red-400">❌ Missing Target Keywords:</h3><p class="text-gray-300 text-sm bg-gray-700/50 p-3 rounded-md mt-1">{missing_str}</p></div>
                </div>
            </div>
            <p class="text-center"><a href="/" class="text-blue-400 underline"><- Go Back and Scan Again</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

