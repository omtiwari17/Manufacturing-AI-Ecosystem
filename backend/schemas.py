from pydantic import BaseModel, Field, HttpUrl, field_validator # <-- Added field_validator here
from typing import List, Optional, Dict, Any, Union

class Evidence(BaseModel):
    type: str = "web"
    url: HttpUrl
    notes: str
    captured_at: Optional[str] = None

    @field_validator('url', mode='before')
    @classmethod
    def ensure_scheme(cls, v):
        if isinstance(v, str) and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v

class Contact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

class RawSupplier(BaseModel):
    supplier_name: str
    website: Optional[HttpUrl] = None

    @field_validator('website', mode='before')
    @classmethod
    def ensure_website_scheme(cls, v):
        if isinstance(v, str) and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v
    
    locations: List[str] = []
    capabilities: List[str] = []
    materials: List[str] = []
    certifications: List[str] = []
    lead_time_weeks: Optional[int] = None
    min_order_qty: Optional[int] = None
    contact: Contact = Field(default_factory=Contact)
    evidence: List[Evidence] = Field(default_factory=list)
    raw_notes: Optional[str] = None

class RawSupplierDataset(BaseModel):
    artifact_version: str = "1.0"
    run_id: str
    query: Dict[str, Any]
    suppliers: List[RawSupplier]
    research_notes: Union[Dict[str, Any], str] = Field(default_factory=dict)

class FinalSupplier(BaseModel):
    supplier_id: str
    supplier_name: str
    fit_score: float
    strengths: List[str] = []
    gaps: List[str] = []
    risk_flags: List[str] = []
    recommended_next_questions: List[str] = []
    evidence_count: int = 0

class FinalSuppliers(BaseModel):
    artifact_version: str = "1.0"
    run_id: str
    ranking_method: Dict[str, Any]
    suppliers: List[FinalSupplier]
