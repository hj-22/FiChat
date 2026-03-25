-- 1. 제공기관
CREATE TABLE provider_info (
    id VARCHAR(20) PRIMARY KEY,
    provider_name VARCHAR(100) NOT NULL
);

-- 2. 상품 마스터
CREATE TABLE product_info (
    id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    provider_id VARCHAR(20),
    category ENUM('GUARANTEED', 'NON_GUARANTEED'),
    FOREIGN KEY (provider_id) REFERENCES provider_info(id)
);

-- 3. 보장형 상세
CREATE TABLE product_fixed (
    product_id VARCHAR(20) PRIMARY KEY,
    maturity INT,
    interest_rate DECIMAL(5, 2),
    FOREIGN KEY (product_id) REFERENCES product_info(id)
);

-- 4. 비보장형 상세
CREATE TABLE product_variable (
    product_id VARCHAR(20) PRIMARY KEY,
    risk_level VARCHAR(20),
    launch_date DATE,
    total_net_worth BIGINT,
    return_1y DECIMAL(10, 3),
    expense_ratio DECIMAL(5, 3),
    FOREIGN KEY (product_id) REFERENCES product_info(id)
);

-- 5. 사업자 및 매핑
CREATE TABLE operator_info (
    id VARCHAR(20) PRIMARY KEY,
    operator_name VARCHAR(100) NOT NULL
);

CREATE TABLE product_mapping (
    product_id VARCHAR(20),
    operator_id VARCHAR(20),
    subscriber_type VARCHAR(20),
    PRIMARY KEY (product_id, operator_id, subscriber_type),
    FOREIGN KEY (product_id) REFERENCES product_info(id),
    FOREIGN KEY (operator_id) REFERENCES operator_info(id)
);