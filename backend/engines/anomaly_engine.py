import uuid
import json
import os
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
from database import get_connection

MODEL_VERSION = "v1.0.0"
MODEL_PATH = "models/anomaly_model.pkl"
MIN_TRAINING_SAMPLES = 100  # Minimum events needed for training

class AnomalyEngine:
    
    @staticmethod
    def extract_features(events):
        features = []
        for event in events:
            feature_vector = [
                event['amount'] if event['amount'] else 0,
                datetime.fromisoformat(event['timestamp']).hour if event['timestamp'] else 12,
                len(event['metadata']) if event['metadata'] else 0,
                1 if event['event_type'] == 'transaction' else 0,
                1 if event['event_type'] == 'message' else 0
            ]
            features.append(feature_vector)
        return np.array(features)
    
    @staticmethod
    def train_baseline_model():
        """
        Train baseline model using 5k training dataset file.
        """
        training_file = os.path.join(os.path.dirname(__file__), '..', 'training_dataset_5k.json')
        
        if not os.path.exists(training_file):
            return {
                "error": f"Training file not found: {training_file}"
            }
        
        # Load training data from file
        with open(training_file, 'r') as f:
            data = json.load(f)
            raw_events = data.get('events', [])
        
        # Convert to unified format for feature extraction
        events = []
        for raw in raw_events:
            event = {
                'amount': raw.get('amount', 0),
                'timestamp': raw.get('timestamp', datetime.now().isoformat()),
                'metadata': json.dumps(raw),
                'event_type': raw.get('source', 'message'),
            }
            events.append(event)
        
        if len(events) < MIN_TRAINING_SAMPLES:
            return {
                "error": f"Training file has only {len(events)} events. Need at least {MIN_TRAINING_SAMPLES}."
            }
        
        # Extract features
        X = AnomalyEngine.extract_features(events)
        
        # Train model
        model = IsolationForest(
            contamination=0.1, 
            random_state=42,
            n_estimators=100,
            max_samples='auto'
        )
        model.fit(X)
        
        # Save model to disk
        os.makedirs('models', exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        
        return {
            'status': 'success',
            'training_samples': len(events),
            'model_version': MODEL_VERSION,
            'model_path': MODEL_PATH,
            'message': f'Model trained on {len(events)} events from training file and saved successfully'
        }
    
    @staticmethod
    def load_or_train_model():
        """Load pre-trained model or return None if not exists"""
        if os.path.exists(MODEL_PATH):
            return joblib.load(MODEL_PATH)
        return None
    
    @staticmethod
    def run_anomaly_detection(case_id: str):
        conn = get_connection()
        events = conn.execute(
            'SELECT * FROM unified_events WHERE case_id = ? AND is_valid = 1',
            (case_id,)
        ).fetchall()
        conn.close()
        
        events = [dict(e) for e in events]
        
        if len(events) < 10:
            return {"error": "Not enough events for anomaly detection (minimum 10 required)"}
        
        # Extract features
        X = AnomalyEngine.extract_features(events)
        
        # Try to load pre-trained model
        model = AnomalyEngine.load_or_train_model()
        
        if model is None:
            # No pre-trained model, train on current case (fallback)
            model = IsolationForest(contamination=0.1, random_state=42)
            predictions = model.fit_predict(X)
            scores = model.score_samples(X)
            baseline_available = False
        else:
            # Use pre-trained model (only predict, don't retrain)
            predictions = model.predict(X)
            scores = model.score_samples(X)
            baseline_available = True
        
        # Normalize scores to 0-1
        normalized_scores = (scores - scores.min()) / (scores.max() - scores.min())
        
        # Store results
        conn = get_connection()
        for i, event in enumerate(events):
            anomaly_id = str(uuid.uuid4())
            is_anomaly = 1 if predictions[i] == -1 else 0
            anomaly_score = float(1 - normalized_scores[i])
            
            feature_snapshot = json.dumps({
                'amount': float(X[i][0]),
                'hour': int(X[i][1]),
                'metadata_size': int(X[i][2]),
                'is_transaction': int(X[i][3]),
                'is_message': int(X[i][4])
            })
            
            conn.execute(
                'INSERT INTO anomaly_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (anomaly_id, case_id, event['event_id'], anomaly_score, 
                 is_anomaly, MODEL_VERSION, feature_snapshot, datetime.now().isoformat())
            )
        
        conn.commit()
        conn.close()
        
        anomaly_count = sum(1 for p in predictions if p == -1)
        avg_score = float(np.mean(normalized_scores))
        
        return {
            'total_events': len(events),
            'anomalies_detected': anomaly_count,
            'average_score': avg_score,
            'model_version': MODEL_VERSION,
            'baseline_model_used': baseline_available
        }
