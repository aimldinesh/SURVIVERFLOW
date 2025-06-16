# Import all pipeline components
from src.data_ingestion import DataIngestion
from src.data_processing import DataProcessing
from src.model_training import ModelTraining
from src.feature_store import RedisFeatureStore

# Configurations
from config.paths_config import *
from config.database_config import DB_CONFIG


if __name__ == "__main__":
    # Step 1: Ingest raw data from source (DB, API, file, etc.)
    data_ingestion = DataIngestion(DB_CONFIG, RAW_DIR)
    data_ingestion.run()

    # Step 2: Initialize Redis Feature Store
    feature_store = RedisFeatureStore()

    # Step 3: Data cleaning, feature engineering, encoding, SMOTE, and Redis storage
    data_processor = DataProcessing(TRAIN_PATH, TEST_PATH, feature_store)
    data_processor.run()

    # Step 4: Train and evaluate model using features from Redis
    model_trainer = ModelTraining(feature_store)
    model_trainer.run()
