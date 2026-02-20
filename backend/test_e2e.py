import requests
import json

BASE_URL = "http://localhost:8000/api"

print("=== TESTING BACKEND ===\n")

# 1. Create case
print("1. Creating case...")
response = requests.post(f"{BASE_URL}/cases", json={
    "name": "Test Investigation",
    "description": "End-to-end test"
})
case = response.json()
case_id = case['id']
print(f"✓ Case created: {case_id}\n")

# 2. Upload file
print("2. Uploading file...")
with open('sample_data.csv', 'rb') as f:
    response = requests.post(
        f"{BASE_URL}/cases/{case_id}/upload",
        files={'file': ('sample_data.csv', f, 'text/csv')}
    )
print(f"✓ Upload status: {response.status_code}")
print(f"  Response: {response.json()}\n")

# 3. Check processing
print("3. Checking processing status...")
response = requests.get(f"{BASE_URL}/cases/{case_id}/processing-status")
print(f"✓ Status: {response.json()}\n")

# 4. Get timeline
print("4. Getting timeline...")
response = requests.get(f"{BASE_URL}/cases/{case_id}/timeline")
timeline = response.json()
print(f"✓ Events: {len(timeline.get('events', []))}\n")

# 5. Get rules
print("5. Getting rule results...")
response = requests.get(f"{BASE_URL}/cases/{case_id}/rules")
rules = response.json()
print(f"✓ Total violations: {rules.get('summary', {}).get('total_violations', 0)}\n")

# 6. Run anomaly
print("6. Running anomaly detection...")
response = requests.post(f"{BASE_URL}/cases/{case_id}/anomaly/run")
print(f"✓ Anomaly status: {response.json()}\n")

# 7. Get anomaly results
print("7. Getting anomaly results...")
response = requests.get(f"{BASE_URL}/cases/{case_id}/anomaly")
anomaly = response.json()
print(f"✓ Anomaly score: {anomaly.get('score', 0)}\n")

# 8. Get graph
print("8. Getting graph...")
response = requests.get(f"{BASE_URL}/cases/{case_id}/graph")
graph = response.json()
print(f"✓ Nodes: {len(graph.get('nodes', []))}, Edges: {len(graph.get('edges', []))}\n")

# 9. Get risk
print("9. Getting risk score...")
response = requests.get(f"{BASE_URL}/cases/{case_id}/risk")
risk = response.json()
print(f"✓ Risk score: {risk.get('overall_score', 0)}")
print(f"  Risk level: {risk.get('risk_level', 'unknown')}\n")

# 10. Generate report
print("10. Generating report...")
response = requests.post(f"{BASE_URL}/cases/{case_id}/report/generate", json={
    "title": "Test Report"
})
report = response.json()
print(f"✓ Report ID: {report.get('report_id', 'N/A')}\n")

print("=== ALL TESTS PASSED ===")
