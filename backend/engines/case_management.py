from datetime import datetime
import uuid
from database import get_connection

class CaseStatus:
    CREATED = "CREATED"
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    NORMALIZED = "NORMALIZED"
    ANALYZED = "ANALYZED"
    REPORTED = "REPORTED"
    FAILED = "FAILED"

class CaseManagementEngine:
    
    @staticmethod
    def create_case(name: str, description: str):
        case_id = str(uuid.uuid4())
        conn = get_connection()
        conn.execute(
            'INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (case_id, name, description, datetime.now().isoformat(), 
             CaseStatus.CREATED, 0, 0.0, 'low', None)
        )
        conn.commit()
        conn.close()
        return case_id
    
    @staticmethod
    def get_case(case_id: str):
        conn = get_connection()
        case = conn.execute('SELECT * FROM cases WHERE id = ?', (case_id,)).fetchone()
        conn.close()
        return dict(case) if case else None
    
    @staticmethod
    def get_all_cases():
        conn = get_connection()
        cases = conn.execute('SELECT * FROM cases ORDER BY created_at DESC').fetchall()
        conn.close()
        return [dict(case) for case in cases]
    
    @staticmethod
    def update_status(case_id: str, status: str):
        conn = get_connection()
        conn.execute('UPDATE cases SET status = ? WHERE id = ?', (status, case_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def update_records_count(case_id: str, count: int):
        conn = get_connection()
        conn.execute('UPDATE cases SET records_count = ? WHERE id = ?', (count, case_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def update_risk(case_id: str, score: float, level: str):
        conn = get_connection()
        conn.execute(
            'UPDATE cases SET risk_score = ?, risk_level = ?, last_analysis_run = ? WHERE id = ?',
            (score, level, datetime.now().isoformat(), case_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_case(case_id: str):
        conn = get_connection()
        conn.execute('DELETE FROM cases WHERE id = ?', (case_id,))
        conn.execute('DELETE FROM unified_events WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM suspicious_events WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM anomaly_results WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM graph_nodes WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM graph_edges WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM case_risk WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM reports WHERE case_id = ?', (case_id,))
        conn.execute('DELETE FROM upload_logs WHERE case_id = ?', (case_id,))
        conn.commit()
        conn.close()
