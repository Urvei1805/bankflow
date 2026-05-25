"""
BankFlow Data Pipeline — Transaction Data Generator
Generates 100,000+ mock financial transactions using Faker.
"""
import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker

fake = Faker()

# Configuration
NUM_TRANSACTIONS = 100_000
NUM_ACCOUNTS = 500
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "raw_transactions.json")

MERCHANT_CATEGORIES = [
    "groceries", "restaurants", "transport", "entertainment",
    "utilities", "healthcare", "shopping", "travel",
    "education", "subscription", "fuel", "insurance",
]

CURRENCIES = ["GBP", "USD", "EUR"]
COUNTRIES = ["GB", "US", "FR", "DE", "JP", "NG", "BR", "IN", "CN", "AU"]
STATUSES = ["completed", "completed", "completed", "pending", "failed"]

# Pre-generate account IDs
ACCOUNT_IDS = [str(uuid.uuid4()) for _ in range(NUM_ACCOUNTS)]


def generate_transaction(index: int) -> dict:
    """Generate a single mock transaction."""
    account_id = random.choice(ACCOUNT_IDS)
    amount = round(random.uniform(1.0, 2000.0), 2)
    currency = random.choice(CURRENCIES)
    country = random.choice(COUNTRIES)
    category = random.choice(MERCHANT_CATEGORIES)
    timestamp = fake.date_time_between(
        start_date="-6m", end_date="now", tzinfo=timezone.utc
    )
    status = random.choice(STATUSES)

    return {
        "transaction_id": str(uuid.uuid4()),
        "account_id": account_id,
        "amount": amount,
        "currency": currency,
        "merchant_category": category,
        "merchant_name": fake.company(),
        "timestamp": timestamp.isoformat(),
        "country": country,
        "status": status,
    }


def main():
    """Generate mock transactions and write to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"🏦 Generating {NUM_TRANSACTIONS:,} mock transactions...")
    transactions = []

    for i in range(NUM_TRANSACTIONS):
        txn = generate_transaction(i)
        transactions.append(txn)

        if (i + 1) % 10_000 == 0:
            print(f"  ✅ Generated {i + 1:,} transactions")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(transactions, f, indent=None)

    file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\n✅ Done! Generated {len(transactions):,} transactions")
    print(f"📁 Output: {OUTPUT_FILE} ({file_size:.1f} MB)")
    print(f"👥 Unique accounts: {NUM_ACCOUNTS}")


if __name__ == "__main__":
    main()
