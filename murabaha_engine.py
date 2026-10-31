import pandas as pd
from typing import Dict, List, Any

class MurabahaFinancingEngine:
    """
    Sharia-Compliant Murabaha (Cost-Plus) Financing Calculator.
    Computes cost markup, equal deferred installments, and amortized repayment schedules.
    """
    def __init__(self, asset_cost: float, profit_rate_annual: float, tenure_months: int):
        if asset_cost <= 0:
            raise ValueError("Asset cost must be greater than zero.")
        if profit_rate_annual <= 0 or profit_rate_annual > 0.50:
            raise ValueError("Annual profit rate must be between 0 and 0.50 (50%).")
        if tenure_months <= 0:
            raise ValueError("Tenure months must be a positive integer.")
            
        self.asset_cost = float(asset_cost)
        self.profit_rate_annual = float(profit_rate_annual)
        self.tenure_months = int(tenure_months)

    def calculate_summary(self) -> Dict[str, float]:
        tenure_years = self.tenure_months / 12.0
        total_profit = self.asset_cost * self.profit_rate_annual * tenure_years
        total_selling_price = self.asset_cost + total_profit
        monthly_installment = total_selling_price / self.tenure_months

        return {
            "asset_cost": round(self.asset_cost, 2),
            "total_profit": round(total_profit, 2),
            "total_selling_price": round(total_selling_price, 2),
            "monthly_installment": round(monthly_installment, 2),
            "tenure_months": self.tenure_months
        }

    def generate_amortization_schedule(self) -> List[Dict[str, Any]]:
        summary = self.calculate_summary()
        total_price = summary["total_selling_price"]
        monthly_payment = summary["monthly_installment"]
        
        # Monthly principal and profit components
        monthly_cost_portion = self.asset_cost / self.tenure_months
        monthly_profit_portion = summary["total_profit"] / self.tenure_months
        
        balance = total_price
        schedule = []

        for month in range(1, self.tenure_months + 1):
            balance -= monthly_payment
            # Handle minor floating point rounding adjustment on final installment
            if month == self.tenure_months:
                balance = 0.0

            schedule.append({
                "month": month,
                "installment": round(monthly_payment, 2),
                "cost_repaid": round(monthly_cost_portion, 2),
                "profit_repaid": round(monthly_profit_portion, 2),
                "remaining_balance": round(max(0.0, balance), 2)
            })

        return schedule

if __name__ == "__main__":
    # Test Run: ₦10,000,000 Asset Cost @ 12% per annum over 24 months
    engine = MurabahaFinancingEngine(asset_cost=10000000.0, profit_rate_annual=0.12, tenure_months=24)
    
    print("--- Transaction Summary ---")
    for key, value in engine.calculate_summary().items():
        print(f"{key}: {value:,}" if isinstance(value, float) else f"{key}: {value}")
        
    print("\n--- Amortization Schedule (First 5 Months) ---")
    schedule_df = pd.DataFrame(engine.generate_amortization_schedule())
    print(schedule_df.head())