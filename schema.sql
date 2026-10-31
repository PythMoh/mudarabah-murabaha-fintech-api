-- Reconstructed from the INSERT/SELECT statements in fintech_database_manager.py.
-- Column types are sensible defaults. Adjust them to match your own database.
CREATE DATABASE IF NOT EXISTS fintech_db;
USE fintech_db;

CREATE TABLE users (
    user_id      INT AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(150) NOT NULL,
    email        VARCHAR(150) NOT NULL UNIQUE,
    phone_number VARCHAR(30)
);

CREATE TABLE financing_accounts (
    account_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL,
    account_number    VARCHAR(30) NOT NULL UNIQUE,
    account_type      VARCHAR(30) NOT NULL,
    initial_principal DECIMAL(18,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE mudarabah_calculations (
    calculation_id        INT AUTO_INCREMENT PRIMARY KEY,
    account_id            INT NOT NULL,
    gross_revenue         DECIMAL(18,2) NOT NULL,
    operating_expenses    DECIMAL(18,2) NOT NULL,
    net_profit            DECIMAL(18,2) NOT NULL,
    bank_psr_ratio        DECIMAL(5,4) NOT NULL,
    customer_psr_ratio    DECIMAL(5,4) NOT NULL,
    bank_profit_share     DECIMAL(18,2) NOT NULL,
    customer_profit_share DECIMAL(18,2) NOT NULL,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES financing_accounts(account_id)
);

CREATE TABLE murabaha_contracts (
    contract_id         INT AUTO_INCREMENT PRIMARY KEY,
    account_id          INT NOT NULL,
    asset_cost          DECIMAL(18,2) NOT NULL,
    profit_rate         DECIMAL(5,4) NOT NULL,
    tenure_months       INT NOT NULL,
    total_selling_price DECIMAL(18,2) NOT NULL,
    monthly_installment DECIMAL(18,2) NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES financing_accounts(account_id)
);

CREATE TABLE murabaha_schedules (
    schedule_id       INT AUTO_INCREMENT PRIMARY KEY,
    contract_id       INT NOT NULL,
    payment_number    INT NOT NULL,
    installment       DECIMAL(18,2) NOT NULL,
    cost_repaid       DECIMAL(18,2) NOT NULL,
    profit_repaid     DECIMAL(18,2) NOT NULL,
    remaining_balance DECIMAL(18,2) NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES murabaha_contracts(contract_id)
);

-- Sample data so the calculators work straight away
INSERT INTO users (full_name, email, phone_number) VALUES ('Demo User', 'demo@example.com', '0000000000');
INSERT INTO financing_accounts (user_id, account_number, account_type, initial_principal)
VALUES (1, 'ACC-0001', 'MUDARABAH', 1000000.00);
