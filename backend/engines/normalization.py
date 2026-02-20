import json
import csv
import uuid
from datetime import datetime
from io import StringIO
import pandas as pd
from dateutil import parser
from database import get_connection
from engines.case_management import CaseManagementEngine, CaseStatus

INVALID_THRESHOLD = 0.5  # 50% threshold

class NormalizationEngine:
    
    @staticmethod
    def parse_timestamp(ts_str):
        """Parse any timestamp format"""
        if not ts_str:
            return None
        try:
            # Try common formats
            return parser.parse(str(ts_str)).isoformat()
        except:
            # Try as unix timestamp
            try:
                return datetime.fromtimestamp(float(ts_str)).isoformat()
            except:
                return None
    
    @staticmethod
    def normalize_phone(phone):
        if not phone:
            return None
        return ''.join(filter(str.isdigit, str(phone)))
    
    @staticmethod
    def parse_csv(content: bytes):
        try:
            df = pd.read_csv(StringIO(content.decode('utf-8')))
            return df.to_dict('records')
        except:
            # Try with different encoding
            try:
                df = pd.read_csv(StringIO(content.decode('latin-1')))
                return df.to_dict('records')
            except:
                return None
    
    @staticmethod
    def parse_json(content: bytes):
        try:
            data = json.loads(content.decode('utf-8'))
            
            # Handle wrapped arrays: extract ALL arrays from nested structure
            if isinstance(data, dict):
                all_events = []
                for key, value in data.items():
                    if isinstance(value, list):
                        # Add source tag to each event
                        for item in value:
                            if isinstance(item, dict):
                                if 'source' not in item and 'source_type' not in item:
                                    item['_extracted_from'] = key
                                all_events.append(item)
                
                if all_events:
                    return all_events
                
                # If dict but no arrays found, treat as single event
                return [data]
            
            return data if isinstance(data, list) else [data]
        except:
            # Try line-delimited JSON
            try:
                lines = content.decode('utf-8').strip().split('\n')
                return [json.loads(line) for line in lines if line.strip()]
            except:
                return None
    
    @staticmethod
    def parse_txt(content: bytes):
        try:
            lines = content.decode('utf-8').strip().split('\n')
            # Try to detect if it's structured (tab/comma separated)
            if '\t' in lines[0] or ',' in lines[0]:
                # Try as CSV
                return NormalizationEngine.parse_csv(content)
            return [{'raw_line': line, 'text': line} for line in lines if line.strip()]
        except:
            return None
    
    @staticmethod
    def detect_field_type(key):
        """Detect what type of field this is"""
        key_lower = str(key).lower()
        
        # Timestamp fields
        if any(x in key_lower for x in ['time', 'date', 'timestamp', 'created', 'updated', 'at']):
            return 'timestamp'
        
        # User fields (actor_id, sender, caller, from)
        if any(x in key_lower for x in ['user', 'from', 'sender', 'actor', 'person', 'name', 'caller']):
            return 'user'
        
        # Receiver fields (target_id, receiver, callee, to)
        if any(x in key_lower for x in ['to', 'receiver', 'recipient', 'target', 'callee']):
            return 'receiver'
        
        # Amount fields
        if any(x in key_lower for x in ['amount', 'value', 'price', 'cost', 'sum', 'total']):
            return 'amount'
        
        # Type fields (event_type, source_type)
        if any(x in key_lower for x in ['type', 'event', 'action', 'activity', 'category']):
            return 'type'
        
        # Source fields (source_type, source)
        if any(x in key_lower for x in ['source']):
            return 'source'
        
        return 'metadata'
    
    @staticmethod
    def is_valid_value(value):
        """Check if value is valid (not None, NaN, empty string)"""
        if value is None:
            return False
        if isinstance(value, float):
            import math
            if math.isnan(value):
                return False
        if isinstance(value, str) and (value.strip() == '' or value.lower() in ['nan', 'null', 'none']):
            return False
        return True
    
    @staticmethod
    def normalize_event(raw_event):
        """Intelligently normalize any event structure"""
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'unknown',
            'user_id': None,
            'timestamp': None,
            'source': 'unknown',
            'amount': None,
            'receiver': None,
            'metadata': {},
            'is_valid': 1,
            'validation_errors': None
        }
        
        # Auto-detect and map fields
        for key, value in raw_event.items():
            if not NormalizationEngine.is_valid_value(value):
                continue
                
            field_type = NormalizationEngine.detect_field_type(key)
            
            if field_type == 'timestamp':
                parsed = NormalizationEngine.parse_timestamp(value)
                if parsed and not event['timestamp']:
                    event['timestamp'] = parsed
            
            elif field_type == 'user':
                if not event['user_id']:
                    event['user_id'] = str(value)
            
            elif field_type == 'receiver':
                if not event['receiver']:
                    event['receiver'] = str(value)
            
            elif field_type == 'amount':
                try:
                    if not event['amount']:
                        # Remove currency symbols and parse
                        amount_str = str(value).replace('$', '').replace(',', '').strip()
                        event['amount'] = float(amount_str)
                except:
                    pass
            
            elif field_type == 'type':
                key_lower = str(key).lower()
                # Prioritize event_type over source_type for event classification
                if 'event' in key_lower and event['event_type'] == 'unknown':
                    event['event_type'] = str(value).lower()
                elif 'source' in key_lower and event['source'] == 'unknown':
                    event['source'] = str(value).lower()
                elif event['event_type'] == 'unknown':
                    event['event_type'] = str(value).lower()
            
            elif field_type == 'source':
                if event['source'] == 'unknown':
                    event['source'] = str(value)
            
            else:
                # Store in metadata
                event['metadata'][key] = value
        
        # If no timestamp found, use current time
        if not event['timestamp']:
            event['timestamp'] = datetime.now().isoformat()
        
        # If no user found, try to extract from metadata or use event_id
        if not event['user_id']:
            # Look for any ID-like field
            for key, value in event['metadata'].items():
                if 'id' in str(key).lower() and NormalizationEngine.is_valid_value(value):
                    event['user_id'] = str(value)
                    break
            # Last resort: use a hash of event data
            if not event['user_id']:
                event['user_id'] = f"user_{abs(hash(str(raw_event)))%10000}"
        
        # Auto-detect source from event_type or metadata
        if event['source'] == 'unknown':
            # Check if event_type hints at source
            if event['event_type'] in ['message', 'chat']:
                event['source'] = 'messaging'
            elif event['event_type'] in ['call', 'voice']:
                event['source'] = 'calls'
            elif event['event_type'] in ['transaction', 'payment', 'transfer']:
                event['source'] = 'financial'
            elif event['event_type'] in ['email']:
                event['source'] = 'email'
            elif event['event_type'] in ['login', 'access']:
                event['source'] = 'system'
            
            # Check metadata for app labels
            for key, value in event['metadata'].items():
                if not NormalizationEngine.is_valid_value(value):
                    continue
                key_lower = str(key).lower()
                value_lower = str(value).lower()
                if 'whatsapp' in key_lower or 'whatsapp' in value_lower:
                    event['source'] = 'whatsapp'
                    break
                elif 'telegram' in key_lower or 'telegram' in value_lower:
                    event['source'] = 'telegram'
                    break
                elif 'signal' in key_lower or 'signal' in value_lower:
                    event['source'] = 'signal'
                    break
        
        # Validate
        errors = []
        if not event['user_id']:
            errors.append('Missing user identifier')
            event['is_valid'] = 0
        
        # Clean metadata - remove NaN values
        clean_metadata = {k: v for k, v in event['metadata'].items() 
                         if NormalizationEngine.is_valid_value(v)}
        
        event['validation_errors'] = json.dumps(errors) if errors else None
        event['metadata'] = json.dumps(clean_metadata)
        
        return event
    
    @staticmethod
    def normalize_and_store(case_id: str, filename: str, content: bytes):
        try:
            CaseManagementEngine.update_status(case_id, CaseStatus.PROCESSING)
            
            print(f"Normalizing file: {filename}, size: {len(content)} bytes")
            
            # Parse based on file type
            if filename.endswith('.csv'):
                raw_events = NormalizationEngine.parse_csv(content)
            elif filename.endswith('.json'):
                raw_events = NormalizationEngine.parse_json(content)
            elif filename.endswith('.txt'):
                raw_events = NormalizationEngine.parse_txt(content)
            else:
                CaseManagementEngine.update_status(case_id, CaseStatus.FAILED)
                return False, "Unsupported file format"
            
            if not raw_events:
                print("Failed to parse file - no events extracted")
                CaseManagementEngine.update_status(case_id, CaseStatus.FAILED)
                return False, "Failed to parse file"
            
            print(f"Parsed {len(raw_events)} raw events")
            
            # First pass: collect statistics for imputation
            user_ids = []
            receivers = []
            sources = []
            event_types = []
            
            for raw_event in raw_events:
                for key, value in raw_event.items():
                    if not NormalizationEngine.is_valid_value(value):
                        continue
                    field_type = NormalizationEngine.detect_field_type(key)
                    if field_type == 'user':
                        user_ids.append(str(value))
                    elif field_type == 'receiver':
                        receivers.append(str(value))
                    elif field_type == 'source':
                        sources.append(str(value).lower())
                    elif field_type == 'type':
                        if 'event' in str(key).lower():
                            event_types.append(str(value).lower())
                        elif 'source' in str(key).lower():
                            sources.append(str(value).lower())
            
            # Calculate most common values for imputation
            from collections import Counter
            most_common_source = Counter(sources).most_common(1)[0][0] if sources else 'unknown'
            most_common_event_type = Counter(event_types).most_common(1)[0][0] if event_types else 'unknown'
            unique_users = list(set(user_ids)) if user_ids else []
            unique_receivers = list(set(receivers)) if receivers else []
            
            print(f"Statistics: {len(unique_users)} users, {len(unique_receivers)} receivers, source={most_common_source}")
            
            # Second pass: normalize with statistical imputation
            normalized_events = []
            for i, raw_event in enumerate(raw_events):
                try:
                    normalized = NormalizationEngine.normalize_event(raw_event)
                    
                    # Statistical imputation
                    if not normalized['user_id'] or normalized['user_id'] == f"user_{abs(hash(str(raw_event)))%10000}":
                        # Use most frequent user or generate consistent ID
                        if unique_users:
                            import random
                            random.seed(i)  # Consistent random selection
                            normalized['user_id'] = random.choice(unique_users)
                        else:
                            normalized['user_id'] = f"user_{i%100:04d}"
                    
                    if not normalized['receiver'] and unique_receivers:
                        import random
                        random.seed(i + 1000)
                        normalized['receiver'] = random.choice(unique_receivers)
                    
                    if normalized['source'] == 'unknown' and most_common_source != 'unknown':
                        normalized['source'] = most_common_source
                    
                    if normalized['event_type'] == 'unknown' and most_common_event_type != 'unknown':
                        normalized['event_type'] = most_common_event_type
                    
                    normalized_events.append(normalized)
                except Exception as e:
                    print(f"Error normalizing event {i}: {e}")
                    continue
            
            if not normalized_events:
                print("No events could be normalized")
                CaseManagementEngine.update_status(case_id, CaseStatus.FAILED)
                return False, "No valid events found"
            
            print(f"Normalized {len(normalized_events)} events")
            
            # Check invalid threshold
            invalid_count = sum(1 for e in normalized_events if not e['is_valid'])
            invalid_rate = invalid_count / len(normalized_events)
            
            print(f"Invalid rate: {invalid_rate*100:.1f}% ({invalid_count}/{len(normalized_events)})")
            
            if invalid_rate > INVALID_THRESHOLD:
                CaseManagementEngine.update_status(case_id, CaseStatus.FAILED)
                return False, f"Too many invalid records: {invalid_rate*100:.1f}%"
            
            # Store in database
            conn = get_connection()
            for event in normalized_events:
                conn.execute(
                    '''INSERT INTO unified_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (event['event_id'], case_id, event['event_type'], event['user_id'],
                     event['timestamp'], event['source'], event['amount'], event['receiver'],
                     event['metadata'], event['is_valid'], event['validation_errors'])
                )
            conn.commit()
            conn.close()
            
            # Update case
            valid_count = len(normalized_events) - invalid_count
            CaseManagementEngine.update_records_count(case_id, valid_count)
            CaseManagementEngine.update_status(case_id, CaseStatus.NORMALIZED)
            
            print(f"Successfully stored {valid_count} valid events")
            return True, f"Normalized {valid_count} events ({invalid_count} invalid)"
            
        except Exception as e:
            print(f"Normalization error: {e}")
            import traceback
            traceback.print_exc()
            CaseManagementEngine.update_status(case_id, CaseStatus.FAILED)
            return False, f"Normalization failed: {str(e)}"
