from datetime import datetime
from database import get_connection

class ForensicRiskCalculator:
    
    # Forensic significance weights
    WEIGHTS = {
        'midnight_activity': 2,
        'high_value_transfer': 4,
        'transaction_burst': 3,
        'deleted_messages': 2,
        'behavioral_chain': 5,
        'statistical_anomaly': 4,
        'cross_case_match': 6,
        'network_correlation': 3
    }
    
    @staticmethod
    def calculate_forensic_risk(case_id: str):
        """
        Advanced forensic risk scoring with explainable justifications
        """
        conn = get_connection()
        
        total_score = 0
        justifications = []
        
        # 1. RULE-BASED DETECTIONS (Category 2)
        rules = conn.execute(
            'SELECT rule_type, COUNT(*) as count, severity FROM suspicious_events WHERE case_id = ? GROUP BY rule_type',
            (case_id,)
        ).fetchall()
        
        for rule in rules:
            rule_type = rule['rule_type'].lower().replace(' ', '_')
            count = rule['count']
            weight = ForensicRiskCalculator.WEIGHTS.get(rule_type, 1)
            # Use logarithmic scaling for count to prevent explosion
            import math
            score = weight * math.log(count + 1, 2)  # Log base 2
            total_score += score
            
            justifications.append({
                'category': 'Rule Detection',
                'type': rule['rule_type'],
                'description': f"{rule['rule_type']} detected {count} times",
                'score': score,
                'severity': rule['severity']
            })
        
        # 2. CORRELATION INTELLIGENCE (Category 3)
        # Check for behavioral chains (connected suspicious events)
        correlations = conn.execute(
            '''
            SELECT COUNT(*) as chain_count FROM (
                SELECT e1.event_id, COUNT(DISTINCT e2.event_id) as linked
                FROM suspicious_events e1
                JOIN suspicious_events e2 ON e1.event_id = e2.event_id 
                WHERE e1.case_id = ? AND e2.case_id = ?
                AND e1.id != e2.id
                GROUP BY e1.event_id
                HAVING COUNT(DISTINCT e2.event_id) > 1
            )
            ''',
            (case_id, case_id)
        ).fetchone()
        
        if correlations['chain_count'] > 0:
            import math
            score = ForensicRiskCalculator.WEIGHTS['behavioral_chain'] * math.log(correlations['chain_count'] + 1, 2)
            total_score += score
            justifications.append({
                'category': 'Correlation',
                'type': 'Behavioral Chain',
                'description': f"Found {correlations['chain_count']} linked suspicious event sequences",
                'score': score,
                'severity': 'high'
            })
        
        # 3. STATISTICAL ANOMALIES (Category 4)
        anomalies = conn.execute(
            'SELECT COUNT(*) as count, AVG(anomaly_score) as avg_score FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
            (case_id,)
        ).fetchone()
        
        if anomalies['count'] > 0:
            import math
            score = ForensicRiskCalculator.WEIGHTS['statistical_anomaly'] * math.log(anomalies['count'] + 1, 2)
            total_score += score
            avg_score_display = anomalies['avg_score'] if anomalies['avg_score'] else 0
            justifications.append({
                'category': 'Anomaly Detection',
                'type': 'Statistical Deviation',
                'description': f"{anomalies['count']} events show statistical deviation from baseline (avg score: {avg_score_display:.2f})",
                'score': score,
                'severity': 'medium'
            })
        
        # 4. NETWORK CORRELATION (Graph Analysis)
        high_centrality = conn.execute(
            'SELECT COUNT(*) as count FROM graph_nodes WHERE case_id = ? AND centrality > 0.7',
            (case_id,)
        ).fetchone()
        
        if high_centrality['count'] > 0:
            import math
            score = ForensicRiskCalculator.WEIGHTS['network_correlation'] * math.log(high_centrality['count'] + 1, 2)
            total_score += score
            justifications.append({
                'category': 'Network Analysis',
                'type': 'High Centrality Nodes',
                'description': f"{high_centrality['count']} entities with high network centrality (key players)",
                'score': score,
                'severity': 'high'
            })
        
        conn.close()
        
        # Normalize to 0-100 scale using sigmoid function
        # Sigmoid prevents scores from ever reaching 100
        import math
        # Sigmoid: 1 / (1 + e^(-x))
        # Scale and shift: (1 / (1 + e^(-(x-30)/10))) * 100
        sigmoid_score = (1 / (1 + math.exp(-(total_score - 30) / 10))) * 100
        final_score_100 = round(sigmoid_score, 1)
        
        # Determine severity
        if final_score_100 >= 80:
            severity = "CRITICAL"
        elif final_score_100 >= 50:
            severity = "HIGH"
        elif final_score_100 >= 30:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        return {
            'risk_score': round(final_score_100 / 10, 2),
            'risk_score_100': round(final_score_100, 1),
            'severity': severity,
            'total_points': round(total_score, 2),
            'justifications': justifications,
            'summary': f"Risk assessment based on {len(justifications)} forensic indicators"
        }
