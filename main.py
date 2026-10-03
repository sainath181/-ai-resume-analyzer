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
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div class="max-w-4xl mx-auto py-12 px-4">
            <header class="text-center mb-12">
                <div class="inline-flex bg-blue-500/10 border border-blue-500/30 px-4 py-1.5 rounded-full text-xs font-semibold text-blue-400 mb-4 tracking-wide uppercase">⚡ Production Ready AI Framework</div>
                <h1 class="text-5xl font-black text-white mb-3">AI Resume Parser & Optimizer</h1>
                <p class="text-gray-400 text-lg font-light">Scan profiles and optimize engineering resumes dynamically with AI Auto-Injector.</p>
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
                    <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold py-4 rounded-xl shadow-lg">Calculate Compatibility Match</button>
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

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    phone_match = re.search(r'\+?\d[\d -]{8,12}\d', resume_text)
    email = email_match.group(0) if email_match else "Not Extracted"
    phone = phone_match.group(0) if phone_match else "Not Extracted"

    jd_words = set(re.findall(r'\b\w+\b', jd.lower()))
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))

    stop_words = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'a', 'an', 'on', 'that', 'this', 'as', 'by', 'at', 'from', 'it', 'or', 'be', 'are', 'your', 'with'}
    important_jd_keywords = {word for word in jd_words if len(word) > 2 and word not in stop_words}

    matched_skills = important_jd_keywords.intersection(resume_words)
    missing_skills = important_jd_keywords.difference(resume_words)

    match_percentage = int((len(matched_skills) / len(important_jd_keywords)) * 100) if important_jd_keywords else 0
    matched_str = ", ".join(list(matched_skills)[:10]) if matched_skills else "None Detected"
    missing_str = ", ".join(list(missing_skills)[:8]) if missing_skills else "None"

    ai_rewrite_list = []
    injected_text_payload = ""
    if missing_skills:
        injected_text_payload += "\\n\\n--- AI OPTIMIZED ENHANCEMENTS ---\\n"
        for skill in list(missing_skills)[:3]:
            bullet = f"Leveraged {skill.upper()} technologies to optimize production configurations and streamline core backend execution pipelines."
            injected_text_payload += f"• {bullet}\\n"
            ai_rewrite_list.append(f"<div class='bg-slate-950 p-4 rounded-xl border border-purple-500/20 mt-3'><p class='text-xs text-purple-400 font-bold tracking-wide uppercase mb-1.5'>🔧 Ready-to-use Bullet Point for {skill.upper()}:</p><p class='text-sm text-slate-300 font-light leading-relaxed'>\\\"{bullet}\\\"</p></div>")
    else:
        ai_rewrite_list.append("<p class='text-sm text-green-400 font-light'>🎉 Perfect Match! No rewrite optimizations required.</p>")
    
    ai_rewrite_str = "".join(ai_rewrite_list)
    full_optimized_text = resume_text + injected_text_payload

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI Resume Parser & Optimizer</title>
        <script src="https://tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-gray-100 min-h-screen font-sans">
        <div id="report-content" class="max-w-4xl mx-auto py-12 px-4">
            <div class="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 mb-8">
                <h2 class="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">⚡ Extraction Intelligence</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-light">
                    <div><span class="text-slate-500 font-medium">Candidate Profile:</span> <span class="text-white font-semibold">Applicant Details</span></div>
                    <div><span class="text-slate-500 font-medium">Email:</span> <span class="text-slate-300">{email}</span></div>
                    <div><span class="text-slate-500 font-medium">Phone:</span> <span class="text-slate-300">{phone}</span></div>
                </div>
            </div>

            <div class="bg-slate-900/60 p-8 rounded-2xl border border-blue-500/30 shadow-2xl relative mb-8">
                <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
                    <h2 class="text-2xl font-bold text-white tracking-wide flex items-center gap-2">📊 ATS Compatibility Audit Summary</h2>
                    <button onclick="downloadTextReport()" class="bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 px-5 rounded-xl text-xs uppercase tracking-wider transition duration-200 shadow-md">
                        🤖 Auto-Inject & Download Document
                    </button>
                </div>

                <div class="flex items-center space-x-6 mb-8 bg-slate-950 p-5 rounded-xl border border-slate-800/50">
                    <div class="text-5xl font-black text-green-400 bg-slate-900 px-6 py-4 rounded-xl border border-green-500/30">{match_percentage}%</div>
                    <div>
                        <p class="text-md text-slate-200 font-medium">Overall ATS Compatibility Score</p>
                    </div>
                </div>
                
                <div class="space-y-5 mb-8">
                    <div>
                        <h3 class="text-sm font-semibold text-green-400 uppercase tracking-wider">✔️ Matched Technical Keywords:</h3>
                        <div class="text-slate-300 text-sm bg-slate-950/80 p-4 rounded-xl mt-2 border border-slate-800 font-mono tracking-wide">{matched_str}</div>
                    </div>
                    <div>
                        <h3 class="text-sm font-semibold text-red-400 uppercase tracking-wider">❌ Missing Target Keywords:</h3>
                        <div class="text-slate-300 text-sm bg-slate-950/80 p-4 rounded-xl mt-2 border border-slate-800 font-mono tracking-wide">{missing_str}</div>
                    </div>
                </div>

                <div class="bg-purple-950/30 border border-purple-500/30 p-6 rounded-2xl mt-6">
                    <h3 class="text-md font-bold text-purple-400 mb-2 flex items-center gap-2">🤖 Smart AI Resume Rewriter</h3>
                    <div class="space-y-3">
                        {ai_rewrite_str}
                    </div>
                </div>
            </div>
            <p class="text-center"><a href="/" class="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors underline underline-offset-4">← Go Back and Scan Another Profile</a></p>
        </div>

        <script>
            function downloadTextReport() {{
                const text = `{full_optimized_text.replace('\n', '\\n').replace('"', '\\"')}`;
                const blob = new Blob([text], {{ type: 'text/plain' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.setAttribute('href', url);
                a.setAttribute('download', 'Optimized_AI_Resume.txt');
                a.click();
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
