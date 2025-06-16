import psycopg2
import pandas as pd
from src.logger import get_logger
from src.custom_exception import CustomException
import os
from sklearn.model_selection import train_test_split
import sys
from config.database_config import DB_CONFIG
from config.paths_config import *

logger = get_logger(__name__)


class DataIngestion:
    def __init__(self, db_params, output_dir):
        # Initialize DB credentials and output directory path
        self.db_params = db_params
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def connect_to_db(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            conn = psycopg2.connect(
                host=self.db_params["host"],
                port=self.db_params["port"],
                dbname=self.db_params["dbname"],
                user=self.db_params["user"],
                password=self.db_params["password"],
            )

            logger.info("Database connection established...")
            return conn
        except Exception as e:
            logger.error(f"Error while establishing connection {e}")
            raise CustomException(str(e), sys)

    def extract_data(self):
        """Extract data from PostgreSQL titanic table into a DataFrame."""
        try:
            # Connect to DB and run SQL query
            conn = self.connect_to_db()
            query = "SELECT * FROM public.titanic"
            df = pd.read_sql_query(query, conn)

            # Close DB connection
            conn.close()

            # Check if data is empty
            if df.empty:
                logger.warning("Extracted DataFrame is empty!")
                raise CustomException("No data found in the source table.")

            logger.info(f"Data extracted from DB with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error while extracting data {e}")
            raise CustomException(str(e), sys)

    def save_data(self, df):
        """Split the dataset into train and test and save them as CSV files."""
        try:
            # Perform 80-20 train-test split
            train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

            # Save the split data to CSV files
            train_df.to_csv(TRAIN_PATH, index=False)
            test_df.to_csv(TEST_PATH, index=False)

            logger.info("Data splitting and saving completed.")
        except Exception as e:
            logger.error(f"Error while saving data {e}")
            raise CustomException(str(e), sys)

    def run(self):
        """Main method to run the data ingestion pipeline end-to-end."""
        try:
            logger.info("Data Ingestion Pipeline Started...")
            df = self.extract_data()  # Step 1: Extract data from DB
            self.save_data(df)  # Step 2: Split and save as CSV
            logger.info("End of Data Ingestion Pipeline.")
        except Exception as e:
            logger.error(f"Error during Data Ingestion Pipeline {e}")
            raise CustomException(str(e), sys)


if __name__ == "__main__":
    # Run the data ingestion script directly
    data_ingestion = DataIngestion(DB_CONFIG, RAW_DIR)
    data_ingestion.run()
