import json
import csv
from datetime import datetime, timedelta
import random

def generate_sample_csv():
    """Generate sample CSV data for testing"""
    data = []
    users = [f"user{i}" for i in range(1, 11)]
    event_types = ['transaction', 'message', 'login', 'file_access']
    
    for i in range(100):
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 168))
        data.append({
            'timestamp': timestamp.isoformat(),
            'type': random.choice(event_types),
            'user_id': random.choice(users),
            'amount': random.randint(100, 50000) if random.random() > 0.5 else '',
            'receiver': random.choice(users) if random.random() > 0.5 else '',
            'source': 'system_log'
        })
    
    with open('sample_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'user_id', 'amount', 'receiver', 'source'])
        writer.writeheader()
        writer.writerows(data)
    
    print("Generated sample_data.csv")

def generate_sample_json():
    """Generate sample JSON data for testing"""
    data = []
    users = [f"user{i}" for i in range(1, 11)]
    event_types = ['transaction', 'message', 'login', 'file_access']
    
    for i in range(100):
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 168))
        event = {
            'timestamp': timestamp.isoformat(),
            'event_type': random.choice(event_types),
            'user': random.choice(users),
            'source': 'api_log'
        }
        
        if random.random() > 0.5:
            event['amount'] = random.randint(100, 50000)
        if random.random() > 0.5:
            event['to'] = random.choice(users)
        if random.random() > 0.8:
            event['deleted'] = True
        
        data.append(event)
    
    with open('sample_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Generated sample_data.json")

if __name__ == "__main__":
    generate_sample_csv()
    generate_sample_json()
    print("\nSample data files created successfully!")
    print("Use these files to test the upload functionality.")
