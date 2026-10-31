# Sharia-Compliant Fintech API: Mudarabah & Murabaha Calculators

A FastAPI + MySQL backend for non-interest (Islamic) finance calculations, with Streamlit and NiceGUI front ends. It calculates and stores **Mudarabah** profit-sharing results and generates **Murabaha** cost-plus financing contracts with a full repayment schedule.

## Features
- **Mudarabah profit sharing:** takes gross revenue, operating expenses and the bank's profit-sharing ratio, then splits net profit between bank and customer. Losses are borne by the capital provider. Each calculation is saved to MySQL.
- **Murabaha cost-plus financing:** computes total profit markup, total selling price and equal monthly installments, then builds an amortization schedule (installment, cost repaid, profit repaid, remaining balance).
- **Persistence:** contracts and every schedule row are written to MySQL in a single flow, with accounts and users in relational tables.
- **Validated REST API:** request models are validated with Pydantic (ratio limits, a maximum 50% annual profit rate, tenure up to 360 months).
- **Three UIs:** a Streamlit Mudarabah calculator, a Streamlit Murabaha portal with CSV export of the schedule, and a NiceGUI dashboard with both tools in tabs.

## API endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/api/v1/calculate-mudarabah` | Calculate and save a profit-sharing record |
| POST | `/api/v1/calculate-murabaha` | Generate and save a Murabaha contract and schedule |

Interactive API docs are available at `http://127.0.0.1:8000/docs` once the server runs.

## Tech stack
Python · FastAPI · Pydantic · MySQL (mysql-connector-python) · pandas · Streamlit · NiceGUI · matplotlib

## Project structure
| File | Role |
|---|---|
| `main.py` | FastAPI app and endpoints |
| `fintech_database_manager.py` | MySQL access layer (users, accounts, calculations, contracts, schedules) |
| `murabaha_engine.py` | Murabaha pricing and amortization logic |
| `Profit_sharing_calculator.py` | Streamlit UI for Mudarabah |
| `murabaha_dashboard.py` | Streamlit UI for Murabaha |
| `nicegui_dashboard.py` | NiceGUI dashboard for both |
| `schema.sql` | Database tables and a demo account |

## Setup
1. Install dependencies:
   ```bash
   git clone https://github.com/<your-username>/mudarabah-murabaha-fintech-api.git
   cd mudarabah-murabaha-fintech-api
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Create the database: `mysql -u root -p < schema.sql`
3. Copy `.env.example` to `.env` and enter your MySQL password.
4. Run the API:
   ```bash
   uvicorn main:app --reload
   ```
5. In a second terminal, start a UI:
   ```bash
   streamlit run Profit_sharing_calculator.py   # Mudarabah
   streamlit run murabaha_dashboard.py          # Murabaha
   python nicegui_dashboard.py                  # both, on port 8501
   ```

## Example request
```bash
curl -X POST http://127.0.0.1:8000/api/v1/calculate-murabaha \
  -H "Content-Type: application/json" \
  -d '{"account_id": 1, "asset_cost": 5000000, "profit_rate_annual": 0.10, "tenure_months": 12}'
```

## Notes
- The Murabaha markup is a flat cost-plus profit (`cost × annual rate × years`) spread over equal installments.
- Educational/portfolio project. It is not a certified Sharia-compliance or banking product.
