# Security Investigation Platform - Backend

Professional backend with 8 modular engines for forensic investigation.

## Architecture

### 8 Engines

1. **Case Management Engine** - Lifecycle & state machine
2. **Raw Data Ingestion Engine** - File validation & logging
3. **Normalization & Validation Engine** - Unified schema conversion
4. **Rule-Based Suspicion Engine** - Deterministic detection
5. **Statistical Anomaly Engine** - ML-based anomaly detection
6. **Correlation & Graph Engine** - Network analysis
7. **Risk Aggregation Engine** - Multi-factor risk scoring
8. **Explainability & Reporting Engine** - PDF reports

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server

```bash
python main.py
```

Server runs on `http://localhost:8000`

### 3. API Documentation

Visit `http://localhost:8000/docs` for interactive API docs

## Database Schema

- **cases** - Case metadata & status
- **upload_logs** - File ingestion audit
- **unified_events** - Normalized event data
- **suspicious_events** - Rule engine findings
- **anomaly_results** - ML anomaly scores
- **graph_nodes** - Network nodes
- **graph_edges** - Network connections
- **case_risk** - Aggregated risk scores
- **reports** - Generated reports

## Case Status Flow

```
CREATED → UPLOADED → PROCESSING → NORMALIZED → ANALYZED → REPORTED
                                              ↓
                                           FAILED
```

## Risk Formula

```
risk_score = (rule_scores × 0.4) + (anomaly_score × 0.4) + (graph_risk × 0.2)
```

## API Endpoints

- `POST /api/cases` - Create case
- `GET /api/cases` - List cases
- `GET /api/cases/{id}` - Get case
- `DELETE /api/cases/{id}` - Delete case
- `POST /api/cases/{id}/upload` - Upload file
- `GET /api/cases/{id}/processing-status` - Check status
- `GET /api/cases/{id}/timeline` - Get events
- `GET /api/cases/{id}/rules` - Get rule findings
- `POST /api/cases/{id}/anomaly/run` - Run ML analysis
- `GET /api/cases/{id}/anomaly` - Get anomaly results
- `GET /api/cases/{id}/graph` - Get network graph
- `GET /api/cases/{id}/risk` - Get risk score
- `POST /api/cases/{id}/report/generate` - Generate PDF
- `GET /api/cases/{id}/reports` - List reports

## File Format Support

- CSV
- JSON
- TXT

## Rules Implemented

1. **Midnight Activity** - Events 00:00-06:00
2. **Transaction Burst** - >10 transactions per user
3. **High Value Transfer** - Amount >$10,000
4. **Deleted Messages** - Metadata flag detection

## ML Model

- **Algorithm**: IsolationForest
- **Features**: Amount, Hour, Metadata size, Event type
- **Contamination**: 10%
- **Version**: v1.0.0
