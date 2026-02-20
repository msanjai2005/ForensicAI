import json
import random
from datetime import datetime, timedelta

# Generate 5000 realistic forensic records
records = []
start_date = datetime(2024, 1, 1)

# User pool
users = [f"{random.randint(1000000000, 9999999999)}" for _ in range(100)]

# Message templates
messages_normal = [
    "Hi, how are you?", "Meeting at 3pm", "Call me later", "Thanks", "OK", 
    "See you tomorrow", "Good morning", "Have a nice day", "Lunch?", "Busy now"
]

messages_suspicious = [
    "Delete this message", "Cash ready", "Meet at midnight", "Don't tell anyone",
    "Transfer the amount", "Package delivered", "Code is 1234", "Urgent deal"
]

languages = ["English", "Hinglish", "Tanglish", "Hindi", "Tamil"]

for i in range(5000):
    timestamp = start_date + timedelta(
        days=random.randint(0, 90),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    
    # 70% normal, 30% suspicious patterns
    is_suspicious = random.random() < 0.3
    
    # Event type distribution
    event_type = random.choices(
        ["message", "call", "transaction"],
        weights=[0.6, 0.3, 0.1]
    )[0]
    
    sender = random.choice(users)
    receiver = random.choice([u for u in users if u != sender])
    
    if event_type == "message":
        record = {
            "message_id": f"msg_{i}",
            "sender": sender,
            "receiver": receiver,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "message_text": random.choice(messages_suspicious if is_suspicious else messages_normal),
            "deleted_flag": 1 if (is_suspicious and random.random() < 0.4) else 0,
            "language": random.choice(languages),
            "source": "whatsapp"
        }
    
    elif event_type == "call":
        record = {
            "call_id": f"call_{i}",
            "caller": sender,
            "receiver": receiver,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": random.randint(30, 1800) if not is_suspicious else random.randint(300, 3600),
            "call_type": random.choice(["incoming", "outgoing", "missed"]),
            "source": "calls"
        }
    
    else:  # transaction
        amount = random.randint(100, 5000) if not is_suspicious else random.randint(10000, 100000)
        record = {
            "transaction_id": f"txn_{i}",
            "from_account": sender,
            "to_account": receiver,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "transaction_type": random.choice(["transfer", "payment", "withdrawal"]),
            "status": "completed",
            "source": "transactions"
        }
    
    records.append(record)

# Save as JSON
with open("training_dataset_5k.json", "w") as f:
    json.dump({"events": records}, f, indent=2)

print(f"Generated {len(records)} records")
print(f"File: training_dataset_5k.json")
