from datetime import datetime
from database import get_connection

RULE_WEIGHT = 0.4
ANOMALY_WEIGHT = 0.4
GRAPH_WEIGHT = 0.2

class RiskAggregationEngine:
    
    @staticmethod
    def calculate_risk_level(score):
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def aggregate_risk(case_id: str):
        conn = get_connection()
        
        # Get rule scores - normalize to 0-100
        rule_results = conn.execute(
            'SELECT COUNT(*) as count, SUM(score_contribution) as total FROM suspicious_events WHERE case_id = ?',
            (case_id,)
        ).fetchone()
        rule_count = rule_results['count'] if rule_results['count'] else 0
        rule_score_raw = rule_results['total'] if rule_results['total'] else 0
        # Normalize: cap at 100 based on severity
        rule_score = min(rule_score_raw / 10, 100) if rule_count > 0 else 0
        
        # Get anomaly scores
        anomaly_results = conn.execute(
            'SELECT AVG(anomaly_score) as avg FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
            (case_id,)
        ).fetchone()
        anomaly_score = (anomaly_results['avg'] * 100) if anomaly_results['avg'] else 0
        
        # Get graph risk (based on centrality)
        graph_results = conn.execute(
            'SELECT AVG(centrality) as avg FROM graph_nodes WHERE case_id = ?',
            (case_id,)
        ).fetchone()
        graph_score = (graph_results['avg'] * 100) if graph_results['avg'] else 0
        
        # Calculate total risk
        total_score = (
            rule_score * RULE_WEIGHT +
            anomaly_score * ANOMALY_WEIGHT +
            graph_score * GRAPH_WEIGHT
        )
        
        # Cap at 100
        total_score = min(total_score, 100)
        
        risk_level = RiskAggregationEngine.calculate_risk_level(total_score)
        
        # Store risk
        conn.execute('DELETE FROM case_risk WHERE case_id = ?', (case_id,))
        conn.execute(
            'INSERT INTO case_risk VALUES (?, ?, ?, ?, ?, ?, ?)',
            (case_id, total_score, risk_level, rule_score, anomaly_score, 
             graph_score, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        return {
            'total_score': total_score,
            'risk_level': risk_level,
            'rule_score': rule_score,
            'anomaly_score': anomaly_score,
            'graph_score': graph_score
        }
