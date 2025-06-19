# === Import Required Libraries ===
import pickle  # For loading the pre-trained model
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify  # Web framework utilities
from alibi_detect.cd import KSDrift  # KSDrift for concept/data drift detection
from src.feature_store import (
    RedisFeatureStore,
)  # Custom module to fetch data from Redis
from sklearn.preprocessing import StandardScaler  # For feature scaling
from src.logger import get_logger  # Custom logging utility
from prometheus_client import (
    start_http_server,
    Counter,
)  # For metrics monitoring via Prometheus

# === Setup Logger ===
logger = get_logger(__name__)

# === Initialize Flask App ===
app = Flask(__name__, template_folder="templates")

# === Prometheus Metrics Setup ===
prediction_count = Counter("prediction_count", "Number of prediction requests made")
drift_count = Counter("drift_count", "Number of times data drift was detected")

# === Load Trained Model ===
MODEL_PATH = "artifacts/models/random_forest_model.pkl"
with open(MODEL_PATH, "rb") as model_file:
    model = pickle.load(model_file)

# === Define Feature Columns Used by Model ===
FEATURE_NAMES = [
    "Age",
    "Fare",
    "Pclass",
    "Sex",
    "Embarked",
    "Familysize",
    "Isalone",
    "HasCabin",
    "Title",
    "Pclass_Fare",
    "Age_Fare",
]

# === Initialize Redis Feature Store and Scaler ===
feature_store = RedisFeatureStore()
scaler = StandardScaler()


# === Fit Scaler on Historical Reference Data ===
def fit_scaler_on_ref_data():
    entity_ids = feature_store.get_all_entity_ids()  # Get entity IDs from Redis
    all_features = feature_store.get_batch_features(entity_ids)  # Fetch batch features
    all_features_df = pd.DataFrame.from_dict(all_features, orient="index")[
        FEATURE_NAMES
    ]  # Convert to DataFrame
    scaler.fit(all_features_df)  # Fit the scaler on the historical data
    return scaler.transform(all_features_df)  # Return scaled data


# === Prepare Drift Detector with Historical Data ===
historical_data = fit_scaler_on_ref_data()
ksd = KSDrift(x_ref=historical_data, p_val=0.05)  # Initialize KSDrift detector


# === Home Route: Renders the Input Form UI ===
@app.route("/")
def home():
    return render_template("index.html")


# === Predict Route: Processes Form Input, Detects Drift, Returns Prediction ===
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # === Get Form Data from UI ===
        data = request.form
        Age = float(data["Age"])
        Fare = float(data["Fare"])
        Pclass = int(data["Pclass"])
        Sex = int(data["Sex"])
        Embarked = int(data["Embarked"])
        Familysize = int(data["Familysize"])
        Isalone = int(data["Isalone"])
        HasCabin = int(data["HasCabin"])
        Title = int(data["Title"])
        Pclass_Fare = float(data["Pclass_Fare"])
        Age_Fare = float(data["Age_Fare"])

        # === Create DataFrame from Input Features ===
        features = pd.DataFrame(
            [
                [
                    Age,
                    Fare,
                    Pclass,
                    Sex,
                    Embarked,
                    Familysize,
                    Isalone,
                    HasCabin,
                    Title,
                    Pclass_Fare,
                    Age_Fare,
                ]
            ],
            columns=FEATURE_NAMES,
        )

        # === Scale Features for Drift Detection ===
        features_scaled = scaler.transform(features)

        # === Detect Data Drift ===
        drift = ksd.predict(features_scaled)
        print("Drift Response : ", drift)

        drift_response = drift.get("data", {})
        is_drift = drift_response.get("is_drift", None)

        if is_drift is not None and is_drift == 1:
            print("Drift Detected....")
            logger.info("Drift Detected....")
            drift_count.inc()  # Increment Prometheus drift counter

        # === Predict Using Model ===
        prediction = model.predict(features)[0]
        prediction_count.inc()  # Increment Prometheus prediction counter

        # === Format the Prediction for Display ===
        if prediction == 1:
            result_text = "✅ The passenger is likely to <strong>Survive</strong>"
            result_class = "survived"
        else:
            result_text = "❌ The passenger is likely to <strong>Not Survive</strong>"
            result_class = "not-survived"

        return render_template(
            "index.html", prediction_text=result_text, result_class=result_class
        )

    except Exception as e:
        return jsonify({"error": str(e)})


# === Prometheus Metrics Endpoint ===
@app.route("/metrics")
def metrics():
    from prometheus_client import generate_latest
    from flask import Response

    return Response(generate_latest(), content_type="text/plain")


# === Start Flask and Prometheus Server ===
if __name__ == "__main__":
    start_http_server(8000)  # Expose metrics on port 8000
    app.run(debug=True, host="0.0.0.0", port=5000)  # Start Flask app
