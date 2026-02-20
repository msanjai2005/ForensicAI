import json
import random
from datetime import datetime, timedelta

def generate_normal_data(num_events=500):
    """Generate normal user behavioral data"""
    events = []
    users = [f"user_{i}" for i in range(1, 11)]
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_events):
        user = random.choice(users)
        event_type = random.choice(['message', 'call', 'transaction', 'login'])
        
        # Normal hours: 8 AM - 10 PM
        hour = random.randint(8, 22)
        timestamp = start_date + timedelta(days=random.randint(0, 30), hours=hour, minutes=random.randint(0, 59))
        
        event = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "user": user,
            "source": random.choice(['whatsapp', 'calls', 'app']),
            "to": random.choice(users)
        }
        
        # Normal amounts: $10 - $500
        if event_type == 'transaction':
            event['amount'] = round(random.uniform(10, 500), 2)
        
        # Normal message behavior
        if event_type == 'message':
            event['message_text'] = random.choice([
                'Hello', 'How are you?', 'Meeting at 3pm', 'Thanks', 'See you tomorrow'
            ])
            event['deleted'] = False  # Normal users don't delete messages
        
        events.append(event)
    
    return {"events": events, "description": "Normal user behavioral data", "total_events": len(events)}

def generate_suspicious_data(num_events=500):
    """Generate suspicious user behavioral data"""
    events = []
    suspicious_users = [f"suspect_{i}" for i in range(1, 6)]
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_events):
        user = random.choice(suspicious_users)
        event_type = random.choice(['message', 'transaction', 'login', 'call'])
        
        # Suspicious patterns
        is_midnight = random.random() < 0.4  # 40% midnight activity
        is_burst = random.random() < 0.3  # 30% burst activity
        is_high_value = random.random() < 0.25  # 25% high value
        is_deleted = random.random() < 0.35  # 35% deleted messages
        
        # Midnight activity (12 AM - 6 AM)
        if is_midnight:
            hour = random.randint(0, 5)
        else:
            hour = random.randint(6, 23)
        
        timestamp = start_date + timedelta(days=random.randint(0, 30), hours=hour, minutes=random.randint(0, 59))
        
        event = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "user": user,
            "source": random.choice(['whatsapp', 'calls', 'transactions']),
            "to": random.choice(suspicious_users)
        }
        
        # High value transfers
        if event_type == 'transaction':
            if is_high_value:
                event['amount'] = round(random.uniform(10000, 50000), 2)  # Suspicious amounts
            else:
                event['amount'] = round(random.uniform(100, 2000), 2)
        
        # Deleted messages (evidence tampering)
        if event_type == 'message':
            event['message_text'] = random.choice([
                'Delete this', 'Don\'t tell anyone', 'Meet at midnight', 'Transfer complete', 'Destroy evidence'
            ])
            event['deleted'] = is_deleted
        
        # Transaction bursts - add multiple rapid transactions
        if is_burst and event_type == 'transaction':
            for j in range(random.randint(10, 20)):
                burst_event = event.copy()
                burst_event['timestamp'] = (timestamp + timedelta(seconds=j*30)).isoformat()
                burst_event['amount'] = round(random.uniform(500, 2000), 2)
                events.append(burst_event)
        
        events.append(event)
    
    return {"events": events, "description": "Suspicious user behavioral data with multiple red flags", "total_events": len(events)}

# Generate datasets
print("Generating normal user data...")
normal_data = generate_normal_data(500)
with open('normal_data.json', 'w') as f:
    json.dump(normal_data, f, indent=2)
print(f"[OK] Generated normal_data.json with {normal_data['total_events']} events")

print("\nGenerating suspicious user data...")
suspicious_data = generate_suspicious_data(500)
with open('suspicious_data.json', 'w') as f:
    json.dump(suspicious_data, f, indent=2)
print(f"[OK] Generated suspicious_data.json with {suspicious_data['total_events']} events")

print("\n" + "="*60)
print("DATASET SUMMARY")
print("="*60)
print(f"\nNormal Data:")
print(f"  - Events: {normal_data['total_events']}")
print(f"  - Characteristics: Business hours (8AM-10PM), normal amounts ($10-$500)")
print(f"  - No deleted messages, no midnight activity, no bursts")

print(f"\nSuspicious Data:")
print(f"  - Events: {suspicious_data['total_events']}")
print(f"  - Red Flags:")
print(f"    * 40% midnight activity (12AM-6AM)")
print(f"    * 25% high-value transfers ($10K-$50K)")
print(f"    * 35% deleted messages")
print(f"    * 30% transaction bursts (10-20 rapid transactions)")
print(f"  - Suspicious message content")

print("\n[OK] Datasets ready for upload to the system!")
