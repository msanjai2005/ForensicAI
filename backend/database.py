import sqlite3
from datetime import datetime

DB_NAME = "security_investigation.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    c = conn.cursor()
    
    # Cases table
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL,
        records_count INTEGER DEFAULT 0,
        risk_score REAL DEFAULT 0,
        risk_level TEXT DEFAULT 'low',
        last_analysis_run TEXT
    )''')
    
    # Upload logs
    c.execute('''CREATE TABLE IF NOT EXISTS upload_logs (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_hash TEXT,
        file_size INTEGER,
        status TEXT NOT NULL,
        error_message TEXT,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    )''')
    
    # Unified events
    c.execute('''CREATE TABLE IF NOT EXISTS unified_events (
        event_id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        user_id TEXT,
        timestamp TEXT NOT NULL,
        source TEXT,
        amount REAL,
        receiver TEXT,
        metadata TEXT,
        is_valid INTEGER DEFAULT 1,
        validation_errors TEXT,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    )''')
    
    # Suspicious events (Rule engine output)
    c.execute('''CREATE TABLE IF NOT EXISTS suspicious_events (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        event_id TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        score_contribution REAL NOT NULL,
        description TEXT,
        detected_at TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id),
        FOREIGN KEY (event_id) REFERENCES unified_events(event_id)
    )''')
    
    # Anomaly results
    c.execute('''CREATE TABLE IF NOT EXISTS anomaly_results (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        event_id TEXT NOT NULL,
        anomaly_score REAL NOT NULL,
        is_anomaly INTEGER NOT NULL,
        model_version TEXT NOT NULL,
        feature_snapshot TEXT,
        detected_at TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id),
        FOREIGN KEY (event_id) REFERENCES unified_events(event_id)
    )''')
    
    # Graph nodes
    c.execute('''CREATE TABLE IF NOT EXISTS graph_nodes (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        node_id TEXT NOT NULL,
        node_type TEXT NOT NULL,
        label TEXT,
        centrality REAL,
        metadata TEXT,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    )''')
    
    # Graph edges
    c.execute('''CREATE TABLE IF NOT EXISTS graph_edges (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        edge_type TEXT,
        weight REAL,
        metadata TEXT,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    )''')
    
    # Case risk
    c.execute('''CREATE TABLE IF NOT EXISTS case_risk (
        case_id TEXT PRIMARY KEY,
        total_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        rule_score_total REAL,
        anomaly_score_total REAL,
        correlation_score REAL,
        computed_at TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    )''')
    
    # Reports
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT,
        file_path TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    )''')
    
    conn.commit()
    conn.close()
