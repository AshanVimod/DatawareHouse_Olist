	Built an Oracle Data Warehouse using the Olist e-commerce dataset. 
	Implemented ETL/data loading from source data into fact and dimension tables. 
	Implemented CDC (Change Data Capture) using timestamp-based incremental loading. 
	Handled data quality issues, including missing product-category translations and NULL numeric values. 
	Created and used a DIM_TIME date dimension for time-based analysis. 
	Implemented OLAP operations: 
•	Slice 
•	Dice
•	Pivot  
•	Drill-down 
•	Roll-up / analytical queries 
Applied physical design techniques: 
•	Range partitioning on order date 
•	Partition pruning to improve query performance 
•	Bitmap indexing on low-cardinality review_score 
•	Materialized View for pre-aggregated daily sales by category 
	Used Oracle SQL, Python, Pandas, SQLAlchemy, and Jupyter/VS Code for implementation and analysis. 
	Used EXPLAIN PLAN to examine query execution and demonstrate performance-related database optimization.
