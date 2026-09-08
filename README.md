# Data Warehouse & OLAP Analytics Project

A Data Warehouse and OLAP Analytics project built using **Oracle, SQL, and Python**, with **ETL processes and Business Intelligence (BI) implementation** for analyzing e-commerce data.

## 📌 Project Overview

This project develops a data warehouse using the Olist e-commerce dataset. The system integrates data from multiple sources, transforms it through ETL processes, and loads it into an Oracle-based dimensional data warehouse for analytical reporting.

## 🛠️ Technologies Used

- **Oracle Database** – Data warehouse
- **SQL / PL/SQL** – Database development and analytical queries
- **Python** – ETL, data processing, and database interaction
- **Pandas** – Data transformation and analysis
- **SQLAlchemy** – Python–Oracle database connection
- **Power BI** – Business Intelligence and data visualization
- **Git & GitHub** – Version control

## 🔄 ETL Process

The ETL pipeline consists of:

1. **Extract** – Read raw Olist CSV datasets.
2. **Transform** – Clean, validate, and transform the data using Python.
3. **Load** – Load transformed data into Oracle dimension and fact tables.

## 🏗️ Data Warehouse

The warehouse follows a **Star Schema** consisting of:

- Fact tables
- Dimension tables
- Primary and foreign keys
- Surrogate keys
- Time dimension

## 📊 OLAP Analytics

Analytical SQL queries are implemented to perform:

- Aggregations
- Filtering
- Grouping
- Roll-up analysis
- Drill-down analysis
- Pivot analysis
- Sales and customer analysis

## ⚡ Physical Design & Optimization

The project also demonstrates database optimization techniques:

- **Range Partitioning** – Partitioning fact data by date/year
- **Partition Pruning** – Reducing the number of partitions scanned
- **Bitmap Indexing** – Improving queries on low-cardinality columns
- **Materialized Views** – Storing pre-aggregated data for faster analytical queries

## 📈 Business Intelligence

**Power BI** is used to create interactive dashboards and visualizations for:

- Sales performance
- Product categories
- Customer analysis
- Revenue analysis
- Geographic analysis
- Business trends

## 📁 Project Structure

```text
Datawarehouse_Olist/
│
├── data/              # Raw dataset files
├── etl/               # ETL scripts
├── sql/               # SQL and database scripts
├── docs/              # Project documentation
├── Power_BI/          # Power BI reports/dashboard
├── .env               # Database configuration (not uploaded to github)
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation summary
