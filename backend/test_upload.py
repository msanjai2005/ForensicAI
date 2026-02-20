from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/cases")
def get_cases():
    return [
        {
            "id": "test-case-123",
            "name": "Test Case",
            "description": "Test",
            "created_at": "2024-01-01T00:00:00",
            "status": "CREATED",
            "records_count": 0,
            "risk_score": 0,
            "risk_level": "low",
            "last_analysis_run": None
        }
    ]

@app.post("/api/cases/{case_id}/upload")
async def upload_file(case_id: str, file: UploadFile = File(...)):
    print(f"=== UPLOAD REQUEST ===")
    print(f"Case ID: {case_id}")
    print(f"Filename: {file.filename}")
    print(f"Content-Type: {file.content_type}")
    
    try:
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        print(f"First 100 chars: {content[:100]}")
        
        return {
            "upload_id": "test-upload-123",
            "status": "completed",
            "message": f"Successfully uploaded {file.filename}"
        }
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/cases/{case_id}/processing-status")
def get_status(case_id: str):
    return {"status": "completed", "progress": 100}

if __name__ == "__main__":
    print("Starting minimal test server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
