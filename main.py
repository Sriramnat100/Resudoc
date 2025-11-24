import os
import sys
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import List, Optional
import tempfile
from datetime import datetime

# Add scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.db_manager import DbManager
from scripts.embedder import Embedder
from scripts.pdf_reader import PDFReader
from scripts.matching_engine import MatchingEngine
from models import (
    MatchRequest, MatchResponse, CandidateResult,
    ResumeUploadResponse, BatchUploadResponse,
    ResumeListResponse, ResumeInfo,
    DeleteResponse, HealthResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Resudoc API",
    description="AI-powered resume matching system with LLM-based ranking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
db_manager = DbManager()
embedder = Embedder()
pdf_reader = PDFReader()
matching_engine = MatchingEngine(db_manager, embedder)


@app.get("/")
async def root():
    """Redirect to the frontend"""
    return RedirectResponse(url="/static/index.html")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database_connected": db_manager.conn is not None
    }


@app.post("/resumes/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    tags: str = Form(default="")  # Comma-separated tags
):
    """Upload and ingest a single resume"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Extract text
            text = pdf_reader.read_pdf(tmp_path)
            cleaned_text = pdf_reader.clean_text(text)
            
            # Generate embedding
            embedding = embedder.get_embedding(cleaned_text)
            
            # Generate deterministic ID
            resume_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, file.filename))
            
            # Store in database with tags
            db_manager.upsert_resume(resume_id, user_id, cleaned_text, filename=file.filename, tags=tag_list)
            db_manager.upsert_embedding(resume_id, user_id, embedding)
            
            return {
                "resume_id": resume_id,
                "filename": file.filename,
                "status": "success",
                "message": f"Resume uploaded and processed successfully"
            }
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.post("/resumes/upload-batch", response_model=BatchUploadResponse)
async def upload_resumes_batch(
    files: List[UploadFile] = File(...),
    user_id: str = Form(...),
    tags: str = Form(default="")  # Comma-separated tags
):
    """Upload and ingest multiple resumes"""
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    
    uploaded = []
    failed = []
    
    for file in files:
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                failed.append({
                    "filename": file.filename,
                    "error": "Only PDF files are supported"
                })
                continue
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            try:
                # Extract text
                text = pdf_reader.read_pdf(tmp_path)
                cleaned_text = pdf_reader.clean_text(text)
                
                # Generate embedding
                embedding = embedder.get_embedding(cleaned_text)
                
                # Generate deterministic ID
                resume_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, file.filename))
                
                # Store in database with tags
                db_manager.upsert_resume(resume_id, user_id, cleaned_text, filename=file.filename, tags=tag_list)
                db_manager.upsert_embedding(resume_id, user_id, embedding)
                
                uploaded.append({
                    "resume_id": resume_id,
                    "filename": file.filename,
                    "status": "success"
                })
                
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
                
        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "uploaded": uploaded,
        "failed": failed,
        "total": len(files),
        "success_count": len(uploaded),
        "failure_count": len(failed)
    }


@app.get("/resumes", response_model=ResumeListResponse)
async def list_resumes(user_id: str = Query(..., description="User ID")):
    """List all resumes for a user with their tags"""
    
    try:
        resumes = db_manager.list_resumes(user_id)
        
        return {
            "resumes": [
                {
                    "resume_id": r["id"],
                    "filename": r["filename"],
                    "created_at": r.get("created_at"),
                    "tags": r.get("tags", [])
                }
                for r in resumes
            ],
            "total": len(resumes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resumes: {str(e)}")


@app.delete("/resumes/{resume_id}", response_model=DeleteResponse)
async def delete_resume(resume_id: str):
    """Delete a resume and its embedding"""
    
    try:
        success = db_manager.delete_resume(resume_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Resume {resume_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Resume not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")


@app.get("/folders")
async def list_folders(user_id: str = Query(..., description="User ID")):
    """List all folders/tags for a user"""
    
    try:
        from models import FoldersListResponse, FolderInfo
        folders = db_manager.list_folders(user_id)
        
        return {
            "folders": folders,
            "total": len(folders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching folders: {str(e)}")


@app.post("/match", response_model=MatchResponse)
async def match_job_description(request: MatchRequest):
    """Match job description against user's resumes using LLM-based ranking"""
    
    try:
        # Run matching engine with optional tag filtering
        results = matching_engine.match_best_resume(
            user_id=request.user_id,
            jd_text=request.jd_text,
            k=request.k,
            tags=request.tags
        )
        
        # Convert to response model
        candidates = [
            CandidateResult(
                resume_id=r["resume_id"],
                filename=r["filename"],
                score=r["score"],
                reasoning=r["reasoning"],
                key_matches=r["key_matches"],
                gaps=r["gaps"]
            )
            for r in results
        ]
        
        return {
            "results": candidates,
            "total_candidates": len(candidates)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching resumes: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
