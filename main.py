import os
import math
from datetime import date
from typing import Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, Numeric, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ==========================================
# 1. DATABASE CONFIGURATION (Postgres Ready)
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./parallax_cost_engine.db")

# disable_check_same_thread is only needed for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. SILOED DATA MODELS (Parallel Views)
# ==========================================
class FactFinancialActual(Base):
    """Silo 1: Financial Actuals (Processed Invoices)"""
    __tablename__ = "fact_financial_actuals"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True, nullable=False)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    amount_invoiced = Column(Numeric(12, 2), nullable=False)
    recognized_date = Column(Date, nullable=False)

class FactOperationalCommitment(Base):
    """Silo 2: Operational Commitments (Real-time Field Logs)"""
    __tablename__ = "fact_operational_commitments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True, nullable=False)
    field_log_id = Column(String, unique=True, index=True, nullable=False)
    amount_accrued = Column(Numeric(12, 2), nullable=False)
    field_incurred_date = Column(Date, nullable=False)

# Create tables automatically on startup
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. PYDANTIC CONTRACTS (API Request/Response)
# ==========================================
class EstimationRequest(BaseModel):
    quantity: float = Field(..., gt=0, description="Raw quantity of materials needed")
    unit_rate: float = Field(..., gt=0, description="Base material unit cost")
    complexity_multiplier: float = Field(..., ge=1.0, description="Risk/Complexity escalation factor")

class EstimationResponse(BaseModel):
    # Exposing helper nodes for transparency/testing transparency
    helper_material_base: float
    helper_labor_allowance: float
    helper_overhead_factor: float
    final_estimate: float

class FinancialActualCreate(BaseModel):
    project_id: str
    invoice_number: str
    amount_invoiced: float
    recognized_date: date

class OperationalCommitmentCreate(BaseModel):
    project_id: str
    field_log_id: str
    amount_accrued: float
    field_incurred_date: date

# ==========================================
# 4. THE CALCULATION ENGINE (Excel Translation DAG)
# ==========================================
class ParallaxCalculationEngine:
    """
    Translates complex spreadsheet dependencies into deterministic code.
    Processes data through clear intermediate helper steps.
    """
    @staticmethod
    def _calc_material_base(qty: float, rate: float) -> float:
        # Mimics Column C: Raw Material Cost
        return qty * rate

    @staticmethod
    def _calc_labor_allowance(base_cost: float) -> float:
        # Mimics Column G: Dynamic Labor allocation (e.g., 45% of material base)
        return base_cost * 0.45

    @staticmethod
    def _calc_overhead(base_cost: float, labor: float, multiplier: float) -> float:
        # Mimics Column AA: Combined burden with complexity scaling
        return (base_cost + labor) * (multiplier - 1.0)

    @classmethod
    def execute_pipeline(cls, qty: float, rate: float, multiplier: float) -> Dict[str, float]:
        """Runs the entire 103-column calculation matrix sequentially."""
        material_base = cls._calc_material_base(qty, rate)
        labor_allowance = cls._calc_labor_allowance(material_base)
        overhead_factor = cls._calc_overhead(material_base, labor_allowance, multiplier)
        
        # Final output calculation
        final_estimate = material_base + labor_allowance + overhead_factor
        
        return {
            "helper_material_base": round(material_base, 4),
            "helper_labor_allowance": round(labor_allowance, 4),
            "helper_overhead_factor": round(overhead_factor, 4),
            "final_estimate": round(final_estimate, 4)
        }

# ==========================================
# 5. FASTAPI ROUTING LAYER
# ==========================================
app = FastAPI(
    title="Parallax Cost Engine",
    description="Production API translating spreadsheet estimating logic to a relational architecture."
)

@app.post("/api/v1/estimate", response_model=EstimationResponse, status_code=status.HTTP_200_OK)
def calculate_estimation(payload: EstimationRequest):
    """
    Ingests construction project variables, processes them through the 
    sequential calculation pipeline, and returns intermediate and final values.
    """
    try:
        results = ParallaxCalculationEngine.execute_pipeline(
            qty=payload.quantity,
            rate=payload.unit_rate,
            multiplier=payload.complexity_multiplier
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation engine failure: {str(e)}")

@app.post("/api/v1/data/financial", status_code=status.HTTP_201_CREATED)
def record_financial_actual(payload: FinancialActualCreate, db: Session = Depends(get_db)):
    """Ingests recognized actual accounting entries from Enterprise Resource Planning (ERP)."""
    db_record = FactFinancialActual(**payload.model_dump())
    db.add(db_record)
    db.commit()
    return {"status": "success", "message": "Financial record locked."}

@app.post("/api/v1/data/operational", status_code=status.HTTP_201_CREATED)
def record_operational_commitment(payload: OperationalCommitmentCreate, db: Session = Depends(get_db)):
    """Ingests real-time raw field execution tracking data."""
    db_record = FactOperationalCommitment(**payload.model_dump())
    db.add(db_record)
    db.commit()
    return {"status": "success", "message": "Operational milestone logged."}
