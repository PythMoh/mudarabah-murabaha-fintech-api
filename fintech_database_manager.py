# SQL Database Manager for Fintech Application
import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()

class FintechDatabaseManager:
    def __init__(self, host=None, user=None, password=None, database=None):
        self.host = host or os.getenv("DB_HOST", "localhost")
        self.user = user or os.getenv("DB_USER", "root")
        self.password = password or os.getenv("DB_PASSWORD")
        self.database = database or os.getenv("DB_NAME", "fintech_db")
        self.connection = None

    def connect(self):
        """Establishes connection to the MySQL database if not already connected."""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            if self.connection.is_connected():
                print(f"Successfully connected to database: {self.database}")
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def disconnect(self):
        """Closes active database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")

    def log_mudarabah_calculation(self, account_id: int, gross_revenue: float, 
                                 operating_expenses: float, bank_psr_ratio: float):
        """Calculates profit distribution and saves record directly to fintech_db."""
        conn = self.connect()
        if not conn:
            return None

        net_profit = gross_revenue - operating_expenses
        customer_psr_ratio = 1.0 - bank_psr_ratio

        if net_profit > 0:
            bank_share = net_profit * bank_psr_ratio
            customer_share = net_profit * customer_psr_ratio
        else:
            bank_share = 0.0
            customer_share = net_profit  # Capital provider bears financial loss

        query = """
            INSERT INTO mudarabah_calculations 
            (account_id, gross_revenue, operating_expenses, net_profit, 
             bank_psr_ratio, customer_psr_ratio, bank_profit_share, customer_profit_share)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            account_id, gross_revenue, operating_expenses, net_profit,
            bank_psr_ratio, customer_psr_ratio, bank_share, customer_share
        )

        cursor = conn.cursor()
        try:
            cursor.execute(query, values)
            conn.commit()
            print(f"Calculation recorded successfully! Insert ID: {cursor.lastrowid}")
            return cursor.lastrowid
        except Error as e:
            print(f"Failed to insert calculation record: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()

    def create_user(self, full_name: str, email: str, phone_number: str):
        """Creates a new user record in fintech_db."""
        conn = self.connect()
        if not conn:
            return None

        query = "INSERT INTO users (full_name, email, phone_number) VALUES (%s, %s, %s)"
        cursor = conn.cursor()
        try:
            cursor.execute(query, (full_name, email, phone_number))
            conn.commit()
            user_id = cursor.lastrowid
            print(f"User created successfully! User ID: {user_id}")
            return user_id
        except Error as e:
            print(f"Error creating user: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()

    def create_account(self, user_id: int, account_number: str, account_type: str, initial_principal: float):
        """Creates a new financing account for an existing user."""
        conn = self.connect()
        if not conn:
            return None

        query = """
            INSERT INTO financing_accounts (user_id, account_number, account_type, initial_principal)
            VALUES (%s, %s, %s, %s)
        """
        cursor = conn.cursor()
        try:
            cursor.execute(query, (user_id, account_number, account_type, initial_principal))
            conn.commit()
            account_id = cursor.lastrowid
            print(f"Account created successfully! Account ID: {account_id}")
            return account_id
        except Error as e:
            print(f"Error creating account: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()

    def log_murabaha_contract(
        self,
        account_id: int,
        asset_cost: float,
        profit_rate: float,
        tenure_months: int,
        total_selling_price: float,
        monthly_installment: float,
        schedule: list
    ) -> int:
        """Persists a Murabaha contract and its schedule in an atomic transaction."""
        conn = self.connect()
        if not conn:
            return None

        cursor = conn.cursor()
        try:
            # 1. Insert contract summary
            contract_sql = """
                INSERT INTO murabaha_contracts 
                (account_id, asset_cost, profit_rate, tenure_months, total_selling_price, monthly_installment)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(contract_sql, (
                account_id, asset_cost, profit_rate, tenure_months, total_selling_price, monthly_installment
            ))
            contract_id = cursor.lastrowid

            # 2. Batch-insert schedule entries
            schedule_sql = """
                INSERT INTO murabaha_schedules 
                (contract_id, payment_number, installment, cost_repaid, profit_repaid, remaining_balance)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            schedule_tuples = [
                (
                    contract_id,
                    row["month"],
                    row["installment"],
                    row["cost_repaid"],
                    row["profit_repaid"],
                    row["remaining_balance"]
                )
                for row in schedule
            ]
            cursor.executemany(schedule_sql, schedule_tuples)

            conn.commit()
            print(f"Murabaha contract recorded successfully! Contract ID: {contract_id}")
            return contract_id

        except Exception as e:
            conn.rollback()
            print(f"Failed to log Murabaha contract: {e}")
            return None
        finally:
            cursor.close()

    def get_murabaha_contract(self, contract_id: int) -> dict:
        """Retrieves a single Murabaha contract by ID."""
        conn = self.connect()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM murabaha_contracts WHERE contract_id = %s;"
            cursor.execute(query, (contract_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_murabaha_schedule(self, contract_id: int) -> list:
        """Retrieves full amortization schedule for a given Murabaha contract."""
        conn = self.connect()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM murabaha_schedules WHERE contract_id = %s ORDER BY payment_number ASC;"
            cursor.execute(query, (contract_id,))
            return cursor.fetchall()
        finally:
            cursor.close()


# --- Execution Test ---
if __name__ == "__main__":
    from murabaha_engine import MurabahaFinancingEngine

    db = FintechDatabaseManager()
    
    # 1. Log a Mudarabah Calculation
    db.log_mudarabah_calculation(
        account_id=1,
        gross_revenue=3500.00,
        operating_expenses=4000.00,
        bank_psr_ratio=0.30
    )

    # 2. Log a Murabaha Contract
    engine = MurabahaFinancingEngine(asset_cost=5000000.0, profit_rate_annual=0.10, tenure_months=12)
    summary = engine.calculate_summary()
    schedule = engine.generate_amortization_schedule()

    contract_id = db.log_murabaha_contract(
        account_id=1,
        asset_cost=summary["asset_cost"],
        profit_rate=engine.profit_rate_annual,
        tenure_months=summary["tenure_months"],
        total_selling_price=summary["total_selling_price"],
        monthly_installment=summary["monthly_installment"],
        schedule=schedule
    )

    db.disconnect()