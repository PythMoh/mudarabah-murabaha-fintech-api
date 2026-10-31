import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from fintech_database_manager import FintechDatabaseManager
from murabaha_engine import MurabahaFinancingEngine

load_dotenv()

app = FastAPI(title="Fintech Non-Interest Banking API", version="1.0.0")

DB_PASSWORD = os.getenv("DB_PASSWORD")

# --- Request Models ---
class CalculationRequest(BaseModel):
    account_id: int = Field(..., description="Registered Financing Account ID")
    gross_revenue: float = Field(..., gt=0)
    operating_expenses: float = Field(..., ge=0)
    bank_psr_ratio: float = Field(..., gt=0, lt=1, description="Bank Profit-Sharing Ratio e.g. 0.30 for 30%")

class MurabahaRequest(BaseModel):
    account_id: int = Field(..., gt=0, description="Registered Financing Account ID")
    asset_cost: float = Field(..., gt=0, description="Initial acquisition cost of the asset")
    profit_rate_annual: float = Field(..., gt=0, le=0.50, description="Annual profit markup rate (0.01 to 0.50)")
    tenure_months: int = Field(..., gt=0, le=360, description="Repayment period in months")

# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"status": "Active", "message": "Fintech Engine API Running!"}

# --- Day 4: Mudarabah Endpoint ---
@app.post("/api/v1/calculate-mudarabah")
def calculate_and_save_mudarabah(payload: CalculationRequest):
    db = FintechDatabaseManager(password=DB_PASSWORD)
    db.connect()
    
    if not db.connection or not db.connection.is_connected():
        raise HTTPException(status_code=500, detail="Database connection failure")

    insert_id = db.log_mudarabah_calculation(
        account_id=payload.account_id,
        gross_revenue=payload.gross_revenue,
        operating_expenses=payload.operating_expenses,
        bank_psr_ratio=payload.bank_psr_ratio
    )
    
    db.disconnect()

    if not insert_id:
        raise HTTPException(
            status_code=400, 
            detail="Calculation failed. Check if account_id exists in financing_accounts."
        )

    return {
        "status": "Success",
        "calculation_id": insert_id,
        "message": f"Mudarabah calculation logged successfully for account {payload.account_id}"
    }

# --- Day 8: Murabaha Endpoint ---
@app.post("/api/v1/calculate-murabaha")
def calculate_and_save_murabaha(payload: MurabahaRequest):
    db = FintechDatabaseManager(password=DB_PASSWORD)
    
    try:
        # 1. Compute Murabaha markup and amortization schedule
        engine = MurabahaFinancingEngine(
            asset_cost=payload.asset_cost,
            profit_rate_annual=payload.profit_rate_annual,
            tenure_months=payload.tenure_months
        )
        summary = engine.calculate_summary()
        schedule = engine.generate_amortization_schedule()

        # 2. Persist contract metadata and full schedule into MySQL
        contract_id = db.log_murabaha_contract(
            account_id=payload.account_id,
            asset_cost=summary["asset_cost"],
            profit_rate=payload.profit_rate_annual,
            tenure_months=summary["tenure_months"],
            total_selling_price=summary["total_selling_price"],
            monthly_installment=summary["monthly_installment"],
            schedule=schedule
        )

        db.disconnect()

        if not contract_id:
            raise HTTPException(
                status_code=400, 
                detail="Contract creation failed. Check if account_id exists in financing_accounts."
            )

        return {
            "status": "Success",
            "contract_id": contract_id,
            "message": f"Murabaha contract logged successfully for account {payload.account_id}",
            "summary": summary,
            "amortization_schedule": schedule
        }

    except ValueError as ve:
        db.disconnect()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.disconnect()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")