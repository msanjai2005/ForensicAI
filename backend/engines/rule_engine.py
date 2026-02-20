import uuid
from datetime import datetime, time
from collections import defaultdict
from database import get_connection

class RuleEngine:
    
    @staticmethod
    def run_all_rules(case_id: str):
        conn = get_connection()
        events = conn.execute(
            'SELECT * FROM unified_events WHERE case_id = ? AND is_valid = 1',
            (case_id,)
        ).fetchall()
        conn.close()
        
        events = [dict(e) for e in events]
        
        findings = []
        findings.extend(RuleEngine.midnight_activity_rule(case_id, events))
        findings.extend(RuleEngine.transaction_burst_rule(case_id, events))
        findings.extend(RuleEngine.high_value_transfer_rule(case_id, events))
        findings.extend(RuleEngine.deleted_message_rule(case_id, events))
        
        # Store findings
        conn = get_connection()
        for finding in findings:
            conn.execute(
                'INSERT INTO suspicious_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (finding['id'], finding['case_id'], finding['event_id'], 
                 finding['rule_type'], finding['severity'], finding['score_contribution'],
                 finding['description'], finding['created_at'])
            )
        conn.commit()
        conn.close()
        
        return findings
    
    @staticmethod
    def midnight_activity_rule(case_id: str, events):
        findings = []
        for event in events:
            try:
                ts = datetime.fromisoformat(event['timestamp'])
                if ts.hour >= 0 and ts.hour < 6:
                    findings.append({
                        'id': str(uuid.uuid4()),
                        'case_id': case_id,
                        'event_id': event['event_id'],
                        'rule_type': 'Midnight Activity',
                        'severity': 'high',
                        'score_contribution': 15.0,
                        'description': f"Activity detected at {ts.hour}:00 (off-hours)",
                        'created_at': datetime.now().isoformat()
                    })
            except:
                pass
        return findings
    
    @staticmethod
    def transaction_burst_rule(case_id: str, events):
        findings = []
        user_events = defaultdict(list)
        
        for event in events:
            if event['event_type'] in ['transaction', 'transfer']:
                user_events[event['user_id']].append(event)
        
        for user_id, user_txns in user_events.items():
            if len(user_txns) > 10:
                for txn in user_txns[:5]:
                    findings.append({
                        'id': str(uuid.uuid4()),
                        'case_id': case_id,
                        'event_id': txn['event_id'],
                        'rule_type': 'Transaction Burst',
                        'severity': 'critical',
                        'score_contribution': 25.0,
                        'description': f"User {user_id} made {len(user_txns)} transactions (burst detected)",
                        'created_at': datetime.now().isoformat()
                    })
        return findings
    
    @staticmethod
    def high_value_transfer_rule(case_id: str, events):
        findings = []
        threshold = 10000.0
        
        for event in events:
            if event['amount'] and event['amount'] > threshold:
                findings.append({
                    'id': str(uuid.uuid4()),
                    'case_id': case_id,
                    'event_id': event['event_id'],
                    'rule_type': 'High Value Transfer',
                    'severity': 'critical',
                    'score_contribution': 30.0,
                    'description': f"High value transfer: ₹{event['amount']:.2f}",
                    'created_at': datetime.now().isoformat()
                })
        return findings
    
    @staticmethod
    def deleted_message_rule(case_id: str, events):
        findings = []
        for event in events:
            try:
                import json
                metadata = json.loads(event['metadata']) if event['metadata'] else {}
                # Check multiple possible fields for deletion
                is_deleted = (
                    metadata.get('deleted') == True or 
                    metadata.get('is_deleted') == True or 
                    metadata.get('deleted_flag') == 1 or
                    metadata.get('deleted_flag') == '1'
                )
                
                if is_deleted:
                    findings.append({
                        'id': str(uuid.uuid4()),
                        'case_id': case_id,
                        'event_id': event['event_id'],
                        'rule_type': 'Deleted Messages',
                        'severity': 'medium',
                        'score_contribution': 10.0,
                        'description': f"{event['event_type'].title()} was deleted - potential evidence tampering",
                        'created_at': datetime.now().isoformat()
                    })
            except:
                pass
        return findings
