# 🚀 SurvivorFlow – End-to-End MLOps Pipeline for Survival Prediction

SurvivorFlow is a production-grade MLOps project that predicts Titanic passenger survival using a fully automated ML pipeline integrated with monitoring, drift detection, a feature store, and deployment on Render with Redis and Prometheus.

---

## 📌 Key Features

- ✅ Data Ingestion from GCP → PostgreSQL via Airflow
- 🔧 ETL Pipeline with custom DAGs
- 🧠 Model Training using Scikit-learn
- ⚙️ Feature Store built with Redis (Docker/Upstash)
- 📊 Drift Detection via Alibi-Detect (KSDrift)
- 📈 Real-time Monitoring using Prometheus + Grafana
- 🌐 Flask App for Live Predictions
- 🚀 Deployed on Render with Redis integration

---

## 🗂️ Project Structure

```
SURVIVERFLOW-main
├── app.py                      # Main Flask app
├── Dockerfile
├── README.md
├── .astro/                     # Astro & Airflow configs
├── dags/                       # Airflow DAGs
│   └── extract_data_from_gcp.py
├── src/                        # Core Python modules
│   ├── data_ingestion.py
│   ├── data_processing.py
│   ├── model_trainer.py
│   ├── feature_store.py
│   └── logger.py
├── pipeline/                   # Training pipeline script
├── artifacts/                  # Saved model + raw data
│   ├── models/random_forest_model.pkl
├── config/                     # Config paths and DB settings
├── notebook/                   # Jupyter testing
├── prometheus.yml              # Prometheus config
├── render.yml                  # Render deployment config
├── requirements.txt
└── setup.py
```

---

## 🔄 End-to-End Pipeline Overview

### 1️⃣ **Data Engineering**
- Raw CSV uploaded to **GCP Bucket**
- **Airflow DAG** extracts → transforms → loads into **PostgreSQL**
- Verified in **Jupyter notebook**

### 2️⃣ **Feature Store (Redis)**
- Built Redis-based store for batch + real-time
- Integrated with both local Redis (Docker) and Upstash (Render cloud Redis)

### 3️⃣ **Model Training**
- Preprocessed data using `StandardScaler`
- Trained **Random Forest Classifier**
- Features: Age, Fare, Pclass, Title, etc.
- Saved model to `artifacts/models/`

### 4️⃣ **Flask App + Inference**
- User inputs handled via `Flask`
- Features scaled → Drift checked → Prediction made
- Result shown on `/` route with styling

### 5️⃣ **Drift Detection**
- Implemented **KSDrift (Alibi-Detect)**
- Compares live data to historical reference
- Triggers **Prometheus counter** if drift is detected

### 6️⃣ **Monitoring with Prometheus + Grafana**
- Exposes `/metrics` endpoint
- Tracks:
  - Prediction count
  - Drift count
- Grafana dashboard can be linked

### 7️⃣ **Deployment on Render**
- Dockerized using custom `Dockerfile`
- App hosted on [🌐 https://surviverflow-1.onrender.com](https://surviverflow-1.onrender.com)
- Uses `.env` for secrets like `REDIS_URL`

---

## ⚙️ Tech Stack

| Layer          | Tools Used                              |
|----------------|------------------------------------------|
| Data Storage   | GCP Bucket, PostgreSQL                   |
| Orchestration  | Airflow (Astro CLI)                      |
| Model Training | Scikit-learn, Pandas, Numpy              |
| Feature Store  | Redis (Docker + Upstash)                 |
| Drift Detect   | Alibi-Detect (KSDrift)                   |
| Monitoring     | Prometheus + Grafana                     |
| App Layer      | Flask, HTML                              |
| Deployment     | Render, Docker                           |

---

## 🔧 How to Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/aimldinesh/MLOPS-SURVIVERFLOW-PROJECT.git
   cd MLOPS-SURVIVERFLOW-PROJECT
   ```

2. Create `.env` file:
   ```
   REDIS_URL=your_upstash_redis_url
   ```

3. Run locally (Flask only):
   ```bash
   python app.py
   ```

4. OR use Docker:
   ```bash
   docker build -t survivorflow-app .
   docker run -p 5000:5000 survivorflow-app
   ```

---

## 🌍 Deployment (Render)

> Render setup with Docker + Redis service

- Redis connected via `REDIS_URL` from Upstash
- `render.yml` configured with:
```yaml
services:
  - type: web
    name: survivorflow-app
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: REDIS_URL
        sync: false  # Set manually in Render dashboard
```

---

## 📈 Monitoring Metrics

| Metric            | Description                        |
|-------------------|------------------------------------|
| `prediction_count`| Number of predictions made         |
| `drift_count`     | Number of drift detections         |

Access at `/metrics` endpoint.

---

## ✅ Live App

👉 [https://surviverflow-1.onrender.com](https://surviverflow-1.onrender.com)

---
### 🖼️ Live Prediction Interface

Below is a glimpse of the live prediction form from the deployed SurvivorFlow application:

#### ✅ Prediction Result: **Likely to Survive**
![Prediction Positive](https://raw.githubusercontent.com/aimldinesh/SURVIVERFLOW/main/Images/Prediction_output/Survive.PNG)

#### ❌ Prediction Result: **Likely to Not Survive**
![Prediction Negative](https://raw.githubusercontent.com/aimldinesh/SURVIVERFLOW/main/Images/Prediction_output/Not_Survive.PNG)

---
### 📊 Grafana Dashboard – Drift Monitoring

Visual representation of real-time drift monitoring using Grafana and Prometheus:

![Grafana Drift Dashboard](https://raw.githubusercontent.com/aimldinesh/SURVIVERFLOW/main/Images/Grafana/grafana_drift_count.PNG)
![Grafana Drift Dashboard](https://github.com/aimldinesh/SURVIVERFLOW/blob/main/Images/Grafana/grafana_prediction_count.PNG)
![Grafana Drift Dashboard](https://github.com/aimldinesh/SURVIVERFLOW/blob/main/Images/Grafana/grafana_drift_count_graph_2.PNG)
![Grafana Drift Dashboard](https://github.com/aimldinesh/SURVIVERFLOW/blob/main/Images/Grafana/grafana_prediction_count_graph_2.PNG)

---

## 📣 Acknowledgements

- Titanic dataset (Kaggle)
- Render, Upstash, Alibi-Detect
- OpenAI/ChatGPT guidance for MLOps setup

---

## 📌 TODO (Optional Enhancements)

- Add CI/CD with GitHub Actions
- Add model versioning with DVC or MLflow
- Schedule retraining pipeline
