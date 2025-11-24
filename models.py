from pydantic import BaseModel, Field
from typing import List, Optional

class MatchRequest(BaseModel):
    """Request model for job description matching"""
    user_id: str = Field(..., description="User ID to match resumes for")
    jd_text: str = Field(..., description="Job description text")
    k: int = Field(default=5, ge=1, le=20, description="Number of top candidates to return")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags to filter by (e.g., ['SWE', 'Python'])")

class CandidateResult(BaseModel):
    """Single candidate result"""
    resume_id: str
    filename: str
    score: float = Field(..., ge=0, le=100, description="Match score out of 100")
    reasoning: str
    key_matches: List[str]
    gaps: List[str]

class MatchResponse(BaseModel):
    """Response model for job description matching"""
    results: List[CandidateResult]
    total_candidates: int

class ResumeUploadResponse(BaseModel):
    """Response model for resume upload"""
    resume_id: str
    filename: str
    status: str
    message: Optional[str] = None

class BatchUploadResponse(BaseModel):
    """Response model for batch resume upload"""
    uploaded: List[ResumeUploadResponse]
    failed: List[dict]
    total: int
    success_count: int
    failure_count: int

class ResumeInfo(BaseModel):
    """Resume information"""
    resume_id: str
    filename: str
    created_at: Optional[str] = None
    tags: List[str] = []

class ResumeListResponse(BaseModel):
    """Response model for listing resumes"""
    resumes: List[ResumeInfo]
    total: int

class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    status: str
    message: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database_connected: bool

class FolderInfo(BaseModel):
    """Folder/tag information"""
    name: str
    count: int

class FoldersListResponse(BaseModel):
    """Response model for listing folders"""
    folders: List[FolderInfo]
    total: int

