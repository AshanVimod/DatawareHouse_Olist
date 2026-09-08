-- =========================================================
-- OLIST DATA WAREHOUSE - STAR SCHEMA DDL (ORACLE VERSION)
-- Part A deliverable
--
-- Run this connected as the olist_dwh schema user.
-- =========================================================

-- Drop tables if re-running (fact first, since it has FKs to dims)
-- Oracle doesn't support "DROP TABLE IF EXISTS" directly before 23c,
-- so we wrap each drop in a PL/SQL block that ignores "table not found".
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE FACT_ORDERS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE DIM_CUSTOMER';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE DIM_PRODUCT';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE DIM_SELLER';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE DIM_TIME';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

-- =========================================================
-- DIM_CUSTOMER
-- =========================================================
CREATE TABLE DIM_CUSTOMER (
    customer_key         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id           VARCHAR2(50) NOT NULL,
    customer_unique_id     VARCHAR2(50),
    customer_city          VARCHAR2(100),
    customer_state         VARCHAR2(2),
    customer_zip_prefix     VARCHAR2(10)
);

-- =========================================================
-- DIM_PRODUCT
-- =========================================================
CREATE TABLE DIM_PRODUCT (
    product_key           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id             VARCHAR2(50) NOT NULL,
    category_english        VARCHAR2(100),
    category_portuguese     VARCHAR2(100),
    product_weight_g         NUMBER(10,2),
    product_length_cm        NUMBER(10,2),
    product_height_cm        NUMBER(10,2),
    product_width_cm         NUMBER(10,2)
);

-- =========================================================
-- DIM_SELLER (includes SCD Type 2 columns for A2.1)
-- Oracle has no native BOOLEAN, so is_current uses NUMBER(1)
-- with a CHECK constraint restricting it to 0/1.
-- =========================================================
CREATE TABLE DIM_SELLER (
    seller_key            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    seller_id               VARCHAR2(50) NOT NULL,
    seller_city              VARCHAR2(100),
    seller_state             VARCHAR2(2),
    seller_zip_prefix        VARCHAR2(10),
    effective_date            DATE NOT NULL,
    end_date                   DATE,
    is_current                  NUMBER(1) DEFAULT 1 CHECK (is_current IN (0,1))
);

-- =========================================================
-- DIM_TIME (8+ extra analytical columns beyond the date)
-- =========================================================
CREATE TABLE DIM_TIME (
    time_key               NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_date                DATE NOT NULL,
    year                      NUMBER(4),
    quarter                   VARCHAR2(2),
    month                      NUMBER(2),
    month_name                 VARCHAR2(15),
    week_of_year                NUMBER(2),
    day_of_month                 NUMBER(2),
    day_name                      VARCHAR2(15),
    is_weekend                     NUMBER(1) CHECK (is_weekend IN (0,1)),
    is_holiday                      NUMBER(1) DEFAULT 0 CHECK (is_holiday IN (0,1))
);

-- =========================================================
-- FACT_ORDERS
-- Grain: one row = one product line item within one order
-- =========================================================
CREATE TABLE FACT_ORDERS (
    fact_key              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id                VARCHAR2(50) NOT NULL,
    order_item_id             NUMBER,

    customer_key              NUMBER NOT NULL REFERENCES DIM_CUSTOMER(customer_key),
    product_key                NUMBER NOT NULL REFERENCES DIM_PRODUCT(product_key),
    seller_key                  NUMBER NOT NULL REFERENCES DIM_SELLER(seller_key),
    time_key                     NUMBER NOT NULL REFERENCES DIM_TIME(time_key),

    -- measures
    price                         NUMBER(10,2),  -- additive
    freight_value                  NUMBER(10,2),  -- additive
    payment_value                   NUMBER(10,2),  -- additive
    review_score                     NUMBER(3,2),  -- non-additive (avoid summing)
    delivery_days                     NUMBER          -- semi-additive
);

-- Helpful indexes for join performance
CREATE INDEX idx_fact_customer ON FACT_ORDERS(customer_key);
CREATE INDEX idx_fact_product ON FACT_ORDERS(product_key);
CREATE INDEX idx_fact_seller ON FACT_ORDERS(seller_key);
CREATE INDEX idx_fact_time ON FACT_ORDERS(time_key);
