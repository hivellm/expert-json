#!/usr/bin/env python3
"""
CloudEvents Collector

Generates CloudEvents examples based on CNCF spec.
CloudEvents is a standard for event data.

Target: 5k examples
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Any
import random
from datetime import datetime, timedelta
from collections import defaultdict

OUTPUT_DIR = Path("../datasets/raw/cloudevents")

# CloudEvents required fields
CLOUDEVENTS_SPEC_VERSION = "1.0"

# Common event sources
EVENT_SOURCES = [
    "https://github.com/user/repo",
    "https://api.example.com/orders",
    "https://messaging.example.com",
    "https://storage.example.com/bucket",
    "urn:event:source:custom",
    "/compute/instance/123",
    "kafka://topic/events"
]

# Common event types
EVENT_TYPES = [
    "com.github.pull_request.opened",
    "com.github.push",
    "com.example.order.created",
    "com.example.user.registered",
    "com.example.payment.processed",
    "com.example.file.uploaded",
    "com.example.email.sent",
    "io.k8s.pod.created",
    "io.k8s.deployment.scaled",
    "com.amazonaws.s3.object.created"
]

# Sample data payloads - DIVERSE structures
DATA_PAYLOADS = [
    # User events
    {"userId": "user123", "action": "created", "timestamp": "2025-11-06T12:00:00Z", "email": "user@example.com", "role": "admin"},
    {"userId": "user456", "action": "updated", "fields": ["email", "name"], "previousValues": {"email": "old@example.com"}},
    {"userId": "user789", "action": "deleted", "reason": "user_request", "timestamp": "2025-11-06T14:30:00Z"},
    
    # E-commerce events
    {"orderId": "order-456", "total": 99.99, "currency": "USD", "status": "pending", "items": [{"sku": "ABC123", "quantity": 2}]},
    {"orderId": "order-789", "status": "shipped", "trackingNumber": "1Z999AA1", "carrier": "UPS", "estimatedDelivery": "2025-11-10"},
    {"orderId": "order-101", "event": "payment_failed", "reason": "insufficient_funds", "amount": 49.99, "retryCount": 2},
    
    # File events
    {"fileName": "document.pdf", "size": 1024000, "contentType": "application/pdf", "bucket": "uploads", "path": "/documents/2025/11/"},
    {"fileName": "image.jpg", "size": 512000, "contentType": "image/jpeg", "width": 1920, "height": 1080, "metadata": {"camera": "Canon"}},
    {"fileName": "data.csv", "size": 2048000, "rows": 15000, "columns": ["id", "name", "email"], "status": "processed"},
    
    # Communication events
    {"from": "sender@example.com", "to": ["recipient1@example.com", "recipient2@example.com"], "subject": "Meeting", "hasAttachments": True},
    {"messageId": "msg123", "channel": "general", "userId": "user456", "text": "Hello team", "reactions": {"thumbsup": 5}},
    
    # Infrastructure events
    {"podName": "nginx-7d8", "namespace": "default", "status": "Running", "containers": 2, "restarts": 0, "cpu": "100m"},
    {"deploymentName": "api-v2", "replicas": {"desired": 3, "current": 3, "ready": 3}, "version": "1.2.0"},
    {"serviceName": "auth-service", "endpoint": "https://auth.example.com", "healthCheck": "passed", "latency": 45},
    
    # Code events
    {"repositoryName": "user/repo", "branch": "main", "commit": "abc123", "author": "dev@example.com", "filesChanged": 5},
    {"pullRequestId": 42, "title": "Fix bug", "state": "merged", "reviewers": ["reviewer1", "reviewer2"], "commits": 3},
    
    # Data events
    {"recordId": "rec456", "table": "users", "operation": "UPDATE", "changes": {"status": "active"}, "timestamp": "2025-11-06T15:00:00Z"},
    {"queryId": "q789", "duration": 234, "rows": 1500, "cached": False, "sql": "SELECT * FROM orders WHERE created_at > NOW()"}
]

def generate_cloudevent(variant: str = "minimal") -> Dict[str, Any]:
    """Generate a CloudEvent example"""
    event = {
        "specversion": CLOUDEVENTS_SPEC_VERSION,
        "type": random.choice(EVENT_TYPES),
        "source": random.choice(EVENT_SOURCES),
        "id": str(uuid.uuid4())
    }
    
    if variant in ["standard", "full"]:
        event["time"] = (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat() + "Z"
    
    if variant in ["full"]:
        event["datacontenttype"] = "application/json"
        event["dataschema"] = "https://example.com/schema/v1"
        event["subject"] = f"resource/{random.randint(1, 1000)}"
    
    # Add data payload
    event["data"] = random.choice(DATA_PAYLOADS).copy()
    
    return event

def generate_cloudevent_with_extensions() -> Dict[str, Any]:
    """Generate CloudEvent with custom extensions"""
    event = generate_cloudevent("full")
    
    # Add custom extensions (prefixed)
    extensions = {
        "correlationid": str(uuid.uuid4()),
        "userid": f"user{random.randint(1, 1000)}",
        "priority": random.choice(["low", "medium", "high"]),
        "region": random.choice(["us-east-1", "eu-west-1", "ap-south-1"])
    }
    
    event.update(extensions)
    return event

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_examples = []
    stats = defaultdict(int)
    
    # Generate different variants
    variants = {
        "minimal": 1500,      # Only required fields
        "standard": 2000,     # Required + time
        "full": 1000,         # All optional fields
        "with_extensions": 500  # Custom extensions
    }
    
    print("Generating CloudEvents examples...")
    
    for variant_name, count in variants.items():
        print(f"\n  Generating {count} {variant_name} events...")
        
        for i in range(count):
            try:
                if variant_name == "with_extensions":
                    event = generate_cloudevent_with_extensions()
                else:
                    event = generate_cloudevent(variant_name)
                
                all_examples.append({
                    "source": f"cloudevents/{variant_name}",
                    "format": "cloudevents",
                    "variant": variant_name,
                    "schema": {
                        "type": "object",
                        "required": ["specversion", "type", "source", "id"],
                        "properties": {
                            "specversion": {"type": "string", "const": "1.0"},
                            "type": {"type": "string"},
                            "source": {"type": "string"},
                            "id": {"type": "string"},
                            "time": {"type": "string", "format": "date-time"},
                            "datacontenttype": {"type": "string"},
                            "data": {"type": "object"}
                        }
                    },
                    "example": event,
                    "task": "generate"
                })
                stats["examples_generated"] += 1
                
            except Exception as e:
                stats["errors"] += 1
                if stats["errors"] < 10:
                    print(f"    Error: {e}")
    
    # Save all examples
    output_file = OUTPUT_DIR / "cloudevents_examples.jsonl"
    print(f"\n\nSaving {len(all_examples)} examples to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    # Save statistics
    stats_file = OUTPUT_DIR / "collection_stats.json"
    stats_data = {
        "variants": {k: v for k, v in variants.items()},
        "examples_generated": len(all_examples),
        "errors": stats["errors"]
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("CLOUDEVENTS COLLECTION SUMMARY")
    print("="*60)
    print(f"Examples generated:     {len(all_examples)}")
    print(f"Errors:                 {stats['errors']}")
    for variant, count in variants.items():
        print(f"  {variant:20s}: {count}")
    print(f"\nOutput: {output_file}")
    print(f"Stats:  {stats_file}")

if __name__ == "__main__":
    main()

