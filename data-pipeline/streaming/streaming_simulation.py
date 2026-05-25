"""
BankFlow Data Pipeline — Streaming Simulation
──────────────────────────────────────────────
Simulates a streaming pipeline using file-based micro-batches.
For production, replace with Kafka/Redpanda consumer.

This simulation:
1. Generates transactions in small batches
2. Applies fraud scoring in near-real-time
3. Writes results to a streaming output directory
"""
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone


MERCHANT_CATEGORIES = [
    "groceries", "restaurants", "transport", "entertainment",
    "utilities", "healthcare", "shopping", "travel",
]
COUNTRIES = ["GB", "US", "FR", "DE", "JP", "NG", "BR"]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "stream_output")


def calculate_fraud_risk(amount: float, country: str, hour: int) -> tuple:
    """Calculate fraud risk score and level."""
    score = 0.0
    if amount > 500:
        score += 0.3
    elif amount > 200:
        score += 0.15
    if country != "GB":
        score += 0.3
    if hour < 6 or hour > 22:
        score += 0.2

    level = "LOW"
    if score >= 0.6:
        level = "HIGH"
    elif score >= 0.3:
        level = "MEDIUM"

    return round(score, 2), level


def generate_streaming_batch(batch_size: int = 10) -> list[dict]:
    """Generate a small batch of transactions."""
    batch = []
    for _ in range(batch_size):
        now = datetime.now(timezone.utc)
        amount = round(random.uniform(1.0, 1500.0), 2)
        country = random.choice(COUNTRIES)
        fraud_score, fraud_level = calculate_fraud_risk(
            amount, country, now.hour
        )

        txn = {
            "transaction_id": str(uuid.uuid4()),
            "account_id": str(uuid.uuid4()),
            "amount": amount,
            "currency": random.choice(["GBP", "USD", "EUR"]),
            "merchant_category": random.choice(MERCHANT_CATEGORIES),
            "timestamp": now.isoformat(),
            "country": country,
            "status": "completed",
            "fraud_score": fraud_score,
            "fraud_risk_level": fraud_level,
        }
        batch.append(txn)
    return batch


def main():
    """Run streaming simulation."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    batch_num = 0
    total_processed = 0

    print("🌊 Starting streaming simulation...")
    print(f"   Output: {OUTPUT_DIR}")
    print("   Press Ctrl+C to stop\n")

    try:
        while True:
            batch = generate_streaming_batch(batch_size=random.randint(5, 20))
            batch_num += 1
            total_processed += len(batch)

            # Write batch to file
            filename = f"batch_{batch_num:06d}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w") as f:
                json.dump(batch, f)

            # Print summary
            high_risk = sum(1 for t in batch if t["fraud_risk_level"] == "HIGH")
            print(
                f"  Batch {batch_num}: {len(batch)} txns | "
                f"🔴 High risk: {high_risk} | "
                f"Total: {total_processed:,}"
            )

            # Wait before next batch (simulate stream interval)
            time.sleep(random.uniform(1.0, 3.0))

    except KeyboardInterrupt:
        print(f"\n\n✅ Streaming stopped. Total batches: {batch_num}, Total transactions: {total_processed:,}")


if __name__ == "__main__":
    main()
