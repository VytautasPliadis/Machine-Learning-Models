# Precious Metals Prediction System
![price_prediction.jpeg](img%2Fprice_prediction.jpeg)
## Project Summary
This repository houses a machine learning-based system designed to predict the price movements of precious metals 
such as gold, silver, platinum, and palladium. The system integrates data ingestion, a relational database for storage, 
and machine learning for analysis and prediction, supporting financial analysts and traders with additional data points
for decision-making.

## Features

- Data Ingestion: Fetches the latest prices for key precious metals using external APIs.
- RDBMS Integration: Includes a structured database schema suitable for machine learning and analytical purposes.
- Machine Learning Models: Features machine learning models to predict price movements using historical and real-time data.
- Automated Training Pipeline: Periodically retrains models to incorporate new data, aiming to maintain prediction relevance.
- Backup Mechanisms: Implements backups for both the machine learning models and database to ensure data safety.
- Containerization: Utilizes Docker to containerize the system components for easier deployment and isolation.
- Backend: Gets price predictions using web framework - FastAPI. 

## Repository Structure

- `collect_data.py` - Manages the data collection process.
- `config.py` - Stores configuration variables and keys.
- `main.py` - The central script for managing the workflow.
- `backup_db_models.py` - For making database and models backups.
- `src/db_api/database_manager.py` - Handles database operations.
- `src/db_api/sqlalchemy_model.py` - Defines the database schema models.
- `src/metapls_api/metals_api.py` - Facilitates fetching data from metals pricing APIs.
- `src//model/model.py` - Contains the machine learning model.
- `src/utils/logger.py` - Provides logging functionalities.
- `Dockerfile and docker-compose.yml` - For building and deploying the application as Docker containers.


## Delivery Plan

### Business Objective:

Develop machine learning models to predict the price movements of gold, silver, platinum, and palladium.

Data Requirements:
- Historical price data for each of the metals.
- Data granularity: Hourly price data.
- Two types of data storage: one for model training (last twelve hourly entries) and another for analytics
  (all available data).

### Development Plan
#### 1. Set Up an RDBMS
Choice of RDBMS: PostgreSQL due to its open-source nature.

#### 2. Database Schema Design:
- Analytics Table: Contains columns for metal names, prices, timestamps, and an ID. Table holds all available historical
  data.
- Training View: A view created from Analytics Table but limited to the last twelve hourly entries.
- 
#### 3. Data Ingestion Solution
- Choice of API: Metals-API for its comprehensive data on precious metals.
- Implementation: Develop Python scripts to fetch hourly data using the selected API and update both the training and
analytics table.

#### 4. Modify the Model Class
- Adjust the Model class to connect to the PostgreSQL database and fetch the required data for training instead of
  generating sample data.

#### 5. Machine Learning Training Pipeline
- Set up the machine learning training pipeline, which should result in multiple trained model files.

#### 6. Backups 
- Implement a backup strategy for both the database and trained model files.

#### 7. Containerization
- Component Split: Identify distinct components (data ingestion, model training, backup, etc.).
- Dockerization: Create Docker containers for each component, allowing for scalability, easy updates, and deployment.

## Getting Started
To run this project, ensure Docker is installed on your system.
Before running `docker-compose.yml`, ensure you have necessary environment variables listed in the `.env` file 
(or configure them directly in the `docker-compose.yml`).

Schedule to run a container (get a price of metals) at every hour, create a models and database backups for every 6h:
```
crontab -e
0 * * * * docker start container_name
0 */6 * * * docker exec container_name pg_dump -U {DB_USER} {DB_NAME} > .\model1\backup.sql
5 */6 * * * [path_to_file]backup_db_models.py
```

Accessing fetched data:
```
psql -U {DB_USER} -d {DB_NAME}
\d+    command to list all tables and views in the databse
select * from analytics_data;
select * from ml_train_data;
```
## Machine Learning Model Integration

In the core of this project lies the implementation of ARIMA (Autoregressive Integrated Moving Average) models for forecasting precious metals prices. ARIMA models are well-regarded for their ability to model and predict time series data with a degree of accuracy that's useful for practical applications. Here's a straightforward overview of the machine learning aspect:

- Data Handling: Dataset is prepared for the ARIMA models by either generating synthetic data with predefined characteristics or pulling historical price data from database. This process ensures that the models have access to relevant data for both training and validation purposes.
- Model Training: Each metal is represented by a unique identifier or 'ticker,' for which a distinct ARIMA model is trained. The training involves fitting the model to the historical data of each metal, aiming to capture the underlying trends and patterns in price movements.
- Saving and Loading Models: After training, models are saved to disk, making it easy to manage and reuse them without the need for retraining. This step is crucial for operational efficiency and allows for quick model deployment when needed.
- Forecasting: For predictions, the system uses the trained ARIMA models to forecast future prices for a specified number of steps ahead. The forecasts are intended to be straightforward and actionable, providing users with a set of predicted values that can aid in decision-making.
