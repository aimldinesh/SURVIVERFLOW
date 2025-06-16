from src.logger import get_logger
from src.custom_exception import CustomException
import pandas as pd
from src.feature_store import RedisFeatureStore
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
import os
import pickle
from sklearn.metrics import accuracy_score

logger = get_logger(__name__)


class ModelTraining:
    def __init__(
        self, feature_store: RedisFeatureStore, model_save_path="artifacts/models/"
    ):
        # Initialize Redis feature store and model path
        self.feature_store = feature_store
        self.model_save_path = model_save_path
        self.model = None

        # Create directory to save model if it doesn't exist
        os.makedirs(self.model_save_path, exist_ok=True)
        logger.info("Model Training initialized...")

    def load_data_from_redis(self, entity_ids):
        """
        Load feature data from Redis using a list of entity IDs.
        """
        try:
            logger.info("Extracting data from Redis")

            data = []
            for entity_id in entity_ids:
                features = self.feature_store.get_features(entity_id)
                if features:
                    data.append(features)
                else:
                    logger.warning("Feature not found")
            return data
        except Exception as e:
            logger.error(f"Error while loading data from Redis: {e}")
            raise CustomException(str(e))

    def prepare_data(self):
        """
        Prepare training and testing data from Redis.
        """
        try:
            # Get all entity IDs from Redis
            entity_ids = self.feature_store.get_all_entity_ids()

            # Split into train and test IDs
            train_entity_ids, test_entity_ids = train_test_split(
                entity_ids, test_size=0.2, random_state=42
            )

            # Load data from Redis
            train_data = self.load_data_from_redis(train_entity_ids)
            test_data = self.load_data_from_redis(test_entity_ids)

            # Convert to DataFrame
            train_df = pd.DataFrame(train_data)
            test_df = pd.DataFrame(test_data)

            # Split into features and target
            X_train = train_df.drop("Survived", axis=1)
            logger.info(X_train.columns)
            X_test = test_df.drop("Survived", axis=1)
            y_train = train_df["Survived"]
            y_test = test_df["Survived"]

            logger.info("Preparation for Model Training completed")
            return X_train, X_test, y_train, y_test

        except Exception as e:
            logger.error(f"Error while preparing data: {e}")
            raise CustomException(str(e))

    def hyperparamter_tuning(self, X_train, y_train):
        """
        Perform hyperparameter tuning using RandomizedSearchCV.
        """
        try:
            param_distributions = {
                "n_estimators": [100, 200, 300],
                "max_depth": [10, 20, 30],
                "min_samples_split": [2, 5],
                "min_samples_leaf": [1, 2],
            }

            rf = RandomForestClassifier(random_state=42)
            random_search = RandomizedSearchCV(
                rf,
                param_distributions,
                n_iter=10,
                cv=3,
                scoring="accuracy",
                random_state=42,
            )

            random_search.fit(X_train, y_train)
            logger.info(f"Best parameters: {random_search.best_params_}")
            return random_search.best_estimator_

        except Exception as e:
            logger.error(f"Error while hyperparameter tuning: {e}")
            raise CustomException(str(e))

    def train_and_evaluate(self, X_train, y_train, X_test, y_test):
        """
        Train the model using best parameters and evaluate it.
        """
        try:
            # Get best estimator from hyperparameter tuning
            best_rf = self.hyperparamter_tuning(X_train, y_train)

            # Predict on test data
            y_pred = best_rf.predict(X_test)

            # Calculate accuracy
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"Accuracy is: {accuracy}")

            # Save the trained model
            self.save_model(best_rf)

            return accuracy

        except Exception as e:
            logger.error(f"Error while model training: {e}")
            raise CustomException(str(e))

    def save_model(self, model):
        """
        Save the trained model to a .pkl file.
        """
        try:
            model_filename = f"{self.model_save_path}random_forest_model.pkl"

            with open(model_filename, "wb") as model_file:
                pickle.dump(model, model_file)

            logger.info(f"Model saved at {model_filename}")
        except Exception as e:
            logger.error(f"Error while saving model: {e}")
            raise CustomException(str(e))

    def run(self):
        """
        Execute the full model training pipeline.
        """
        try:
            logger.info("Starting Model Training Pipeline...")
            X_train, X_test, y_train, y_test = self.prepare_data()
            accuracy = self.train_and_evaluate(X_train, y_train, X_test, y_test)
            logger.info("Model Training pipeline completed successfully.")
        except Exception as e:
            logger.error(f"Error while running model training pipeline: {e}")
            raise CustomException(str(e))


if __name__ == "__main__":
    # Instantiate feature store
    feature_store = RedisFeatureStore()

    # Create and run model training pipeline
    model_trainer = ModelTraining(feature_store)
    model_trainer.run()
