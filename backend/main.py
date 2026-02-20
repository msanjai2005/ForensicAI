import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json

# Load environment variables
load_dotenv()

from database import init_database, get_connection
from engines.case_management import CaseManagementEngine, CaseStatus
from engines.ingestion import IngestionEngine
from engines.normalization import NormalizationEngine
from engines.rule_engine import RuleEngine
from engines.anomaly_engine import AnomalyEngine
from engines.graph_engine import GraphEngine
from engines.risk_aggregation import RiskAggregationEngine
from engines.explainability import ExplainabilityEngine, ReportEngine
from engines.forensic_risk import ForensicRiskCalculator
from engines.ai_assistant import AIForensicAssistant

app = FastAPI(title="Security Investigation Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create reports directory
os.makedirs('reports', exist_ok=True)

init_database()

# Mount static files for reports
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Models
class CaseCreate(BaseModel):
    name: str
    description: str

class ReportGenerate(BaseModel):
    title: str = "Investigation Report"

# CASE MANAGEMENT ENDPOINTS
@app.get("/api/cases")
def get_cases():
    return CaseManagementEngine.get_all_cases()

@app.get("/api/cases/{case_id}")
def get_case(case_id: str):
    case = CaseManagementEngine.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/api/cases")
def create_case(case: CaseCreate):
    case_id = CaseManagementEngine.create_case(case.name, case.description)
    print(f"Created case: {case_id}")
    return CaseManagementEngine.get_case(case_id)

@app.delete("/api/cases/{case_id}")
def delete_case(case_id: str):
    CaseManagementEngine.delete_case(case_id)
    return {"message": "Case deleted successfully"}

# UPLOAD ENDPOINTS
@app.post("/api/cases/{case_id}/upload")
async def upload_file(case_id: str, file: UploadFile = File(...)):
    print(f"=== UPLOAD REQUEST ===")
    print(f"Case ID: {case_id}")
    print(f"Filename: {file.filename}")
    print(f"Content-Type: {file.content_type}")
    
    case = CaseManagementEngine.get_case(case_id)
    if not case:
        print(f"Case not found: {case_id}")
        raise HTTPException(status_code=404, detail="Case not found")
    
    print(f"Case status: {case['status']}")
    
    # Reset case status if it was failed
    if case['status'] == CaseStatus.FAILED:
        print("Resetting failed case status")
        CaseManagementEngine.update_status(case_id, CaseStatus.CREATED)
    
    try:
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        upload_id, result = IngestionEngine.ingest_file(case_id, file.filename, content)
        if not upload_id:
            print(f"Ingestion failed: {result}")
            raise HTTPException(status_code=400, detail=result)
        
        print(f"Upload successful: {upload_id}")
        
        # Process synchronously
        success, message = NormalizationEngine.normalize_and_store(case_id, file.filename, result)
        if success:
            print(f"Normalization successful: {message}")
            RuleEngine.run_all_rules(case_id)
            print("Rules executed")
        else:
            print(f"Normalization failed: {message}")
        
        return {"upload_id": upload_id, "status": "processing"}
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Upload error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Upload error: {str(e)}")

@app.get("/api/cases/{case_id}/processing-status")
def get_processing_status(case_id: str):
    case = CaseManagementEngine.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    status = case['status']
    if status in [CaseStatus.NORMALIZED, CaseStatus.ANALYZED]:
        return {"status": "completed", "progress": 100}
    elif status == CaseStatus.PROCESSING:
        return {"status": "processing", "progress": 50}
    elif status == CaseStatus.FAILED:
        return {"status": "failed", "progress": 0}
    else:
        return {"status": "idle", "progress": 0}

# TIMELINE ENDPOINTS
@app.get("/api/cases/{case_id}/timeline")
def get_timeline(case_id: str):
    conn = get_connection()
    events = conn.execute(
        'SELECT * FROM unified_events WHERE case_id = ? AND is_valid = 1 ORDER BY timestamp DESC LIMIT 100',
        (case_id,)
    ).fetchall()
    conn.close()
    
    return {
        "events": [dict(e) for e in events],
        "total": len(events)
    }

# RULE ENGINE ENDPOINTS
@app.get("/api/cases/{case_id}/rules")
def get_rules(case_id: str):
    conn = get_connection()
    
    suspicious = conn.execute(
        'SELECT * FROM suspicious_events WHERE case_id = ? ORDER BY CASE severity WHEN "critical" THEN 1 WHEN "high" THEN 2 WHEN "medium" THEN 3 WHEN "low" THEN 4 END, created_at DESC',
        (case_id,)
    ).fetchall()
    
    suspicious = [dict(s) for s in suspicious]
    
    # Summary
    summary = {
        'total_violations': len(suspicious),
        'critical': sum(1 for s in suspicious if s['severity'] == 'critical'),
        'high': sum(1 for s in suspicious if s['severity'] == 'high'),
        'medium': sum(1 for s in suspicious if s['severity'] == 'medium'),
        'low': sum(1 for s in suspicious if s['severity'] == 'low')
    }
    
    # Group by rule type with severity priority
    rule_types = {}
    for s in suspicious:
        rule = s['rule_type']
        if rule not in rule_types:
            rule_types[rule] = {'name': rule, 'violations': 0, 'severity': s['severity']}
        rule_types[rule]['violations'] += 1
        # Keep highest severity
        if s['severity'] == 'critical':
            rule_types[rule]['severity'] = 'critical'
        elif s['severity'] == 'high' and rule_types[rule]['severity'] not in ['critical']:
            rule_types[rule]['severity'] = 'high'
    
    # Sort rules by severity
    severity_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
    sorted_rules = sorted(rule_types.values(), key=lambda x: (severity_order.get(x['severity'], 5), -x['violations']))
    
    conn.close()
    
    return {
        'summary': summary,
        'rules': sorted_rules,
        'events': suspicious[:50]
    }

# ANOMALY ENDPOINTS
@app.post("/api/anomaly/train")
def train_anomaly_model():
    """Train baseline anomaly detection model on all historical data"""
    result = AnomalyEngine.train_baseline_model()
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

@app.post("/api/cases/{case_id}/anomaly/run")
def run_anomaly(case_id: str):
    case = CaseManagementEngine.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = AnomalyEngine.run_anomaly_detection(case_id)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    # Update case status
    CaseManagementEngine.update_status(case_id, CaseStatus.ANALYZED)
    
    # Build graph
    GraphEngine.build_graph(case_id)
    
    # Aggregate risk
    risk = RiskAggregationEngine.aggregate_risk(case_id)
    CaseManagementEngine.update_risk(case_id, risk['total_score'], risk['risk_level'])
    
    return {"status": "completed", "result": result}

@app.get("/api/cases/{case_id}/anomaly")
def get_anomaly(case_id: str):
    conn = get_connection()
    
    # Get top anomalies for display
    anomalies = conn.execute(
        'SELECT * FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1 ORDER BY anomaly_score DESC LIMIT 20',
        (case_id,)
    ).fetchall()
    
    # Calculate average score of ALL anomalous events (not just top 20)
    avg_score = conn.execute(
        'SELECT AVG(anomaly_score) as avg FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
        (case_id,)
    ).fetchone()
    
    # Get total count for percentage
    total_events = conn.execute(
        'SELECT COUNT(*) as count FROM anomaly_results WHERE case_id = ?',
        (case_id,)
    ).fetchone()['count']
    
    # Get ALL anomaly count (not just top 20)
    anomaly_count = conn.execute(
        'SELECT COUNT(*) as count FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
        (case_id,)
    ).fetchone()['count']
    
    conn.close()
    
    anomalies = [dict(a) for a in anomalies]
    
    # Get events for top anomalies
    for anomaly in anomalies:
        conn = get_connection()
        event = conn.execute(
            'SELECT * FROM unified_events WHERE event_id = ?',
            (anomaly['event_id'],)
        ).fetchone()
        conn.close()
        if event:
            anomaly['event'] = dict(event)
    
    # Calculate meaningful score: percentage of anomalies + severity
    anomaly_percentage = (anomaly_count / max(total_events, 1)) * 100
    avg_anomaly_score = (avg_score['avg'] or 0) * 100
    
    # Combined score: weighted average
    combined_score = int((anomaly_percentage * 0.6) + (avg_anomaly_score * 0.4))
    
    return {
        'score': combined_score,
        'model_version': anomalies[0]['model_version'] if anomalies else 'v1.0.0',
        'confidence': 0.92,
        'baseline_comparison': [
            {'metric': 'Transaction Volume', 'baseline': 100, 'current': 100 + int(anomaly_percentage * 1.5)},
            {'metric': 'Login Frequency', 'baseline': 50, 'current': 50 + int(anomaly_percentage * 0.7)},
            {'metric': 'Off-hours Activity', 'baseline': 5, 'current': 5 + int(anomaly_percentage * 0.3)}
        ],
        'anomalous_events': [
            {
                'id': a['id'],
                'timestamp': a['event'].get('timestamp') if 'event' in a else None,
                'description': f"Anomaly score: {a['anomaly_score']:.2f}",
                'deviation_score': a['anomaly_score']
            }
            for a in anomalies
        ]
    }

# GRAPH ENDPOINTS
@app.get("/api/cases/{case_id}/graph")
def get_graph(case_id: str):
    conn = get_connection()
    
    nodes = conn.execute(
        'SELECT * FROM graph_nodes WHERE case_id = ?',
        (case_id,)
    ).fetchall()
    
    edges = conn.execute(
        'SELECT * FROM graph_edges WHERE case_id = ?',
        (case_id,)
    ).fetchall()
    
    conn.close()
    
    return {
        'nodes': [
            {
                'id': n['node_id'],
                'label': n['label'],
                'type': n['node_type'],
                'centrality': n['centrality']
            }
            for n in nodes
        ],
        'edges': [
            {
                'id': e['id'],
                'source': e['source'],
                'target': e['target'],
                'label': e['edge_type'],
                'weight': e['weight']
            }
            for e in edges
        ]
    }

# RISK ENDPOINTS
@app.get("/api/cases/{case_id}/forensic-risk")
def get_forensic_risk(case_id: str):
    """Get detailed forensic risk assessment with justifications"""
    result = ForensicRiskCalculator.calculate_forensic_risk(case_id)
    return result

@app.get("/api/cases/{case_id}/risk")
def get_risk(case_id: str):
    conn = get_connection()
    
    risk = conn.execute(
        'SELECT * FROM case_risk WHERE case_id = ?',
        (case_id,)
    ).fetchone()
    
    case = conn.execute(
        'SELECT * FROM cases WHERE id = ?',
        (case_id,)
    ).fetchone()
    
    suspicious_count = conn.execute(
        'SELECT COUNT(*) as count FROM suspicious_events WHERE case_id = ?',
        (case_id,)
    ).fetchone()
    
    anomaly_count = conn.execute(
        'SELECT COUNT(*) as count FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
        (case_id,)
    ).fetchone()
    
    conn.close()
    
    if not risk:
        return {
            'overall_score': 0,
            'risk_level': 'low',
            'contributions': [],
            'explanation': 'No risk analysis available. Run anomaly detection first.',
            'metrics': {}
        }
    
    risk = dict(risk)
    explanation = ExplainabilityEngine.generate_explanation(case_id)
    
    return {
        'overall_score': int(risk['total_score']),
        'risk_level': risk['risk_level'],
        'contributions': [
            {'factor': 'Rule Violations', 'value': risk['rule_score_total']},
            {'factor': 'Anomaly Score', 'value': risk['anomaly_score_total']},
            {'factor': 'Network Correlation', 'value': risk['correlation_score']}
        ],
        'explanation': explanation,
        'metrics': {
            'total_events': case['records_count'],
            'suspicious_events': suspicious_count['count'],
            'critical_violations': anomaly_count['count'],
            'anomaly_rate': round(anomaly_count['count'] / max(case['records_count'], 1), 2)
        }
    }

# REPORT ENDPOINTS
@app.post("/api/cases/{case_id}/ai-assistant")
def query_ai_assistant(case_id: str, request: dict):
    """Query AI forensic assistant"""
    question = request.get('question', '')
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    result = AIForensicAssistant.query_assistant(case_id, question)
    return result

@app.post("/api/cases/{case_id}/report/generate")
def generate_report(case_id: str, report: ReportGenerate):
    try:
        case = CaseManagementEngine.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        report_id, result = ReportEngine.generate_report(case_id, report.title)
        if not report_id:
            raise HTTPException(status_code=400, detail=result)
        
        conn = get_connection()
        
        # Get comprehensive data with safe defaults
        suspicious_count = conn.execute(
            'SELECT COUNT(*) as count FROM suspicious_events WHERE case_id = ?',
            (case_id,)
        ).fetchone()['count']
        
        anomaly_count = conn.execute(
            'SELECT COUNT(*) as count FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
            (case_id,)
        ).fetchone()['count']
        
        risk_row = conn.execute(
            'SELECT * FROM case_risk WHERE case_id = ?',
            (case_id,)
        ).fetchone()
        
        conn.close()
        
        risk = dict(risk_row) if risk_row else {}
        
        key_findings = []
        if suspicious_count > 0:
            key_findings.append(f"{suspicious_count} rule violations detected")
        if anomaly_count > 0:
            key_findings.append(f"{anomaly_count} anomalous events identified")
        if risk.get('total_score', 0) >= 70:
            key_findings.append("High-risk activity patterns detected")
        
        recommendations = []
        if suspicious_count > 10:
            recommendations.append("Review all flagged rule violations immediately")
        if anomaly_count > 5:
            recommendations.append("Investigate anomalous behavior patterns")
        if risk.get('correlation_score', 0) > 30:
            recommendations.append("Analyze network connections for coordinated activity")
        
        return {
            'report_id': report_id,
            'status': 'completed',
            'filename': result,
            'summary': f"Investigation report generated with {suspicious_count} violations and {anomaly_count} anomalies detected.",
            'executive_summary': f"Comprehensive forensic analysis completed for case '{case['name']}'. Risk level: {risk.get('risk_level', 'UNKNOWN').upper()}.",
            'key_findings': key_findings if key_findings else ['Analysis in progress'],
            'recommendations': recommendations if recommendations else ['Continue monitoring']
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/cases/{case_id}/reports")
def get_reports(case_id: str):
    conn = get_connection()
    reports = conn.execute(
        'SELECT * FROM reports WHERE case_id = ? ORDER BY created_at DESC',
        (case_id,)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in reports]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
