# Project Title: ETL Pipeline for Product Data with MongoDB Storage

This repository includes the data pipeline for the ETL process on a sample Amazon products dataset based on Daria's interview task.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technologies Used](#technologies-used)
3. [Initial Data Structure](#initial-data-structure)
4. [ERD Diagram](#erd-diagram)
5. [ETL Process](#etl-process)
6. [Apache Airflow Integration](#apache-airflow-integration)
7. [Setup Instructions](#setup-instructions)
8. [Usage](#usage)


## Project Overview
This project implements an ETL (Extract, Transform, Load) pipeline that processes product data from an initial SQL or Excel source, cleans the data, and stores it in a MongoDB collection. The project also utilizes Apache Airflow to monitor and manage the ETL pipelines effectively.

## Technologies Used
- **Programming Language**: Python
- **Database**: MongoDB
- **Data Processing Libraries**: Pandas
- **ETL Orchestration**: Apache Airflow
- **Database Connectivity**: PyMongo
- **Diagramming**: Draw.io for ERD

## Initial Data Structure
The initial data consists of three tables:
1. **Product Price**: Contains pricing information.
   - Columns: `product_id`, `actual_price`, `discount_price`
   
2. **Product Details**: Contains descriptive information about products.
   - Columns: `product_id`, `name`, `main_category`

3. **Sales**: Contains sales data.
   - Columns: `product_id`, `no_of_ratings`, `ratings`, `date`

## ERD Diagram
The Entity-Relationship Diagram (ERD) illustrates the relationships between the tables. You can view and edit the ERD using [Draw.io](https://app.diagrams.net/). Below is a description of the ERD structure:

1. **Product Price Table**:
   - Contains `actual_price` and `discount_price`.
   - Relationship: One-to-One with Product Details (via `product_id`).

2. **Product Details Table**:
   - Contains `name` and `main_category`.
   - Relationship: One-to-Many with Sales (via `product_id`).

3. **Sales Table**:
   - Contains `ratings`, `no_of_ratings`, and `date`.
   - Relationship: Many-to-One with Product Price and Product Details.

![ERD Diagram](./documents/Amazon%20Products%20-%20Daria.png)

## ETL Process
The ETL process consists of the following steps:

### Extract
- Read data from the initial SQL database or Excel file.

### Transform
- **Data Cleaning**:
  - Convert `actual_price` to float format with one decimal place.
  - Format the `date` column to “YYYY-MM-DD” string format.

### Load
- Store the cleaned data into a MongoDB collection named `products`.

## Apache Airflow Integration
Apache Airflow is utilized to manage and monitor the ETL pipelines. The following Python libraries are used for integration:
- `apache-airflow`
- `apache-airflow-providers-mongo`

### Airflow DAG
Create a Directed Acyclic Graph (DAG) to orchestrate the ETL process. Define tasks for extraction, transformation, and loading, and set up dependencies between them.

## Setup Instructions
Follow these steps to set up the project:

environment variables:

POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5436"
POSTGRES_USER = "daria"
POSTGRES_PASS = "daria1234"
POSTGRES_DB = "products"
MONGO_HOST = "localhost"
MONGO_PORT = "27017"
MONGO_USER = "daria"
MONGO_PASS = "daria1234"
MONGO_DB = "Amazon"
MONGO_COLLECTION = "Products"

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/PayamZohari/AmazonProductETL.git
   cd AmazonProductETL
   ```

2. **Set Up Apache Airflow**:
   - Run the following command in the root directory of the project to start Apache Airflow:
   ```bash
   docker-compose up -d
   ```
   - Access Airflow on [localhost:8080](http://localhost:8080).

3. **Set Up PostgreSQL**:
   - Navigate to the `initial_db` directory and run:
   ```bash
   docker-compose up -d
   ```
   - This will set up PostgreSQL.

4. **Load Data into PostgreSQL**:
   - Run the `create_initial_db.py` script to load data from the Excel file into PostgreSQL:
   ```bash
   python create_initial_db.py
   ```

5. **Set Up MongoDB**:
   - Go to the `final_db` directory and run:
   ```bash
   docker-compose up -d
   ```
   - This will set up MongoDB.

6. **Run the ETL Process**:
   - Finally, execute the `ETL.py` script to transfer data from PostgreSQL to MongoDB:
   ```bash
   python ETL.py
   ```

## Usage
Once the setup is complete, you can monitor and manage the ETL process through the Airflow UI. You can also modify the DAG and tasks as needed for your requirements.


