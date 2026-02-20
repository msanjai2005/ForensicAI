import hashlib
import uuid
from datetime import datetime
from database import get_connection
from engines.case_management import CaseManagementEngine, CaseStatus

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

class IngestionEngine:
    
    @staticmethod
    def validate_file(filename: str, content: bytes):
        if len(content) > MAX_FILE_SIZE:
            return False, "File size exceeds 100MB limit"
        
        allowed_extensions = ['.csv', '.json', '.txt']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return False, "Invalid file type. Only CSV, JSON, TXT allowed"
        
        return True, None
    
    @staticmethod
    def compute_hash(content: bytes):
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def check_duplicate(case_id: str, file_hash: str):
        conn = get_connection()
        existing = conn.execute(
            'SELECT id FROM upload_logs WHERE case_id = ? AND file_hash = ?',
            (case_id, file_hash)
        ).fetchone()
        conn.close()
        return existing is not None
    
    @staticmethod
    def log_upload(case_id: str, filename: str, file_hash: str, file_size: int):
        upload_id = str(uuid.uuid4())
        conn = get_connection()
        conn.execute(
            'INSERT INTO upload_logs VALUES (?, ?, ?, ?, ?, ?, ?)',
            (upload_id, case_id, filename, file_hash, file_size, 
             'uploaded', datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return upload_id
    
    @staticmethod
    def ingest_file(case_id: str, filename: str, content: bytes):
        # Validate
        valid, error = IngestionEngine.validate_file(filename, content)
        if not valid:
            return None, error
        
        # Hash check
        file_hash = IngestionEngine.compute_hash(content)
        if IngestionEngine.check_duplicate(case_id, file_hash):
            return None, "Duplicate file detected"
        
        # Log upload
        upload_id = IngestionEngine.log_upload(case_id, filename, file_hash, len(content))
        
        # Update case status
        CaseManagementEngine.update_status(case_id, CaseStatus.UPLOADED)
        
        return upload_id, content
