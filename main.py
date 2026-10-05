@app.post("/download-pdf")
async def download_pdf(
    resume_data: str = Form(...)
):

    try:
        corrected_text = base64.b64decode(
            resume_data
        ).decode("utf-8")

    except Exception:
        return HTMLResponse(
            "<h2>Could not generate the resume.</h2>",
            status_code=400
        )

    # Remove empty bullet lines
    cleaned_lines = []

    for line in corrected_text.splitlines():

        stripped = line.strip()

        # Remove lines containing only bullets
        if stripped in ["•", "●", "▪", "-", "*"]:
            continue

        cleaned_lines.append(line)

    corrected_text = "\n".join(cleaned_lines)

    pdf_buffer = create_pdf(corrected_text)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename=\"Corrected_Resume.pdf\""
        }
    )
