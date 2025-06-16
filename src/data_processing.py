import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from src.feature_store import RedisFeatureStore
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *

logger = get_logger(__name__)


class DataProcessing:
    def __init__(
        self, train_data_path, test_data_path, feature_store: RedisFeatureStore
    ):
        # Initialize paths and feature store instance
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path

        # Placeholders for datasets and processed features
        self.data = None
        self.test_data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.X_resampled = None
        self.y_resampled = None

        self.feature_store = feature_store
        logger.info("Your Data Processing is initialized...")

    def load_data(self):
        try:
            # Load train and test data from CSV files
            self.data = pd.read_csv(self.train_data_path)
            self.test_data = pd.read_csv(self.test_data_path)
            logger.info("Successfully loaded the data")
        except Exception as e:
            logger.error(f"Error while reading data: {e}")
            raise CustomException(str(e))

    def preprocess_data(self):
        try:
            # Handle missing values
            self.data["Age"] = self.data["Age"].fillna(self.data["Age"].median())
            self.data["Embarked"] = self.data["Embarked"].fillna(
                self.data["Embarked"].mode()[0]
            )
            self.data["Fare"] = self.data["Fare"].fillna(self.data["Fare"].median())

            # Encode categorical columns
            self.data["Sex"] = self.data["Sex"].map({"male": 0, "female": 1})
            self.data["Embarked"] = self.data["Embarked"].astype("category").cat.codes

            # Feature engineering
            self.data["Familysize"] = self.data["SibSp"] + self.data["Parch"] + 1
            self.data["Isalone"] = (self.data["Familysize"] == 1).astype(int)
            self.data["HasCabin"] = self.data["Cabin"].notnull().astype(int)

            # Extract and encode title from the Name field
            self.data["Title"] = (
                self.data["Name"]
                .str.extract(" ([A-Za-z]+)\.", expand=False)
                .map({"Mr": 0, "Miss": 1, "Mrs": 2, "Master": 3, "Rare": 4})
                .fillna(4)
            )

            # Create interaction features
            self.data["Pclass_Fare"] = self.data["Pclass"] * self.data["Fare"]
            self.data["Age_Fare"] = self.data["Age"] * self.data["Fare"]

            logger.info("Data preprocessing completed.")
        except Exception as e:
            logger.error(f"Error during preprocessing: {e}")
            raise CustomException(str(e))

    def handle_imbalance_data(self):
        try:
            # Select features and target variable
            X = self.data[
                [
                    "Pclass",
                    "Sex",
                    "Age",
                    "Fare",
                    "Embarked",
                    "Familysize",
                    "Isalone",
                    "HasCabin",
                    "Title",
                    "Pclass_Fare",
                    "Age_Fare",
                ]
            ]
            y = self.data["Survived"]

            # Handle class imbalance using SMOTE
            smote = SMOTE(random_state=42)
            self.X_resampled, self.y_resampled = smote.fit_resample(X, y)

            logger.info("Handled class imbalance successfully using SMOTE.")
        except Exception as e:
            logger.error(f"Error while handling imbalanced data: {e}")
            raise CustomException(str(e))

    def store_feature_in_redis(self):
        try:
            batch_data = {}
            # Iterate through each row and prepare data for Redis
            for idx, row in self.data.iterrows():
                entity_id = row["PassengerId"]
                features = {
                    "Age": row["Age"],
                    "Fare": row["Fare"],
                    "Pclass": row["Pclass"],
                    "Sex": row["Sex"],
                    "Embarked": row["Embarked"],
                    "Familysize": row["Familysize"],
                    "Isalone": row["Isalone"],
                    "HasCabin": row["HasCabin"],
                    "Title": row["Title"],
                    "Pclass_Fare": row["Pclass_Fare"],
                    "Age_Fare": row["Age_Fare"],
                    "Survived": row["Survived"],
                }
                batch_data[entity_id] = features

            # Store batch data in Redis feature store
            self.feature_store.store_batch_features(batch_data)
            logger.info("Features have been stored in Redis Feature Store.")
        except Exception as e:
            logger.error(f"Error while storing features to Redis: {e}")
            raise CustomException(str(e))

    def retrive_feature_redis_store(self, entity_id):
        # Retrieve features of a given entity ID from Redis
        features = self.feature_store.get_features(entity_id)
        if features:
            return features
        return None

    def run(self):
        try:
            logger.info("Starting the data processing pipeline...")
            self.load_data()  # Step 1: Load the data
            self.preprocess_data()  # Step 2: Preprocess and engineer features
            self.handle_imbalance_data()  # Step 3: Handle imbalanced classes
            self.store_feature_in_redis()  # Step 4: Store processed features in Redis
            logger.info("Data processing pipeline completed successfully.")
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            raise CustomException(str(e))


if __name__ == "__main__":
    # Create Redis feature store instance
    feature_store = RedisFeatureStore()

    # Initialize and run the data processing pipeline
    data_processor = DataProcessing(TRAIN_PATH, TEST_PATH, feature_store)
    data_processor.run()

    # Retrieve and print features for a specific entity
    print(data_processor.retrive_feature_redis_store(entity_id=734))
