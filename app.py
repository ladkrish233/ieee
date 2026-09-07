from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uuid

from main import generate_paper
from formatter import build_ieee_docx

app=FastAPI()

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

class GenerateRequest(BaseModel):
    topic: str
    total_word_target: int = 3000

class GenerateResponse(BaseModel):
    file_id: str
    filename: str

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    # Run the full agent pipeline
    paper_draft = await generate_paper(request.topic, request.total_word_target)

    # Build the docx
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.docx"
    output_path = os.path.join(GENERATED_DIR, filename)
    build_ieee_docx(paper_draft, output_path)

    return GenerateResponse(file_id=file_id, filename=filename)


@app.get("/download/{file_id}")
def download(file_id: str):
    filename = f"{file_id}.docx"
    filepath = os.path.join(GENERATED_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="ieee_paper.docx",
    )