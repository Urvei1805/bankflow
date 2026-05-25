"""
BankFlow Data Pipeline — PySpark Batch Processing
──────────────────────────────────────────────────
Reads raw JSON transactions, cleans data, calculates:
- Total spend by merchant category per account
- Fraud risk scores using rule-based logic
- Monthly aggregations using Spark window functions

Outputs:
- Parquet files for processed data
- Analytics results for PostgreSQL ingestion
"""
import os
import sys
from datetime import datetime

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


def create_spark_session() -> SparkSession:
    """Create a SparkSession for batch processing."""
    return (
        SparkSession.builder
        .appName("BankFlow-BatchPipeline")
        .master("local[*]")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def define_schema() -> StructType:
    """Define the schema for raw transaction JSON."""
    return StructType([
        StructField("transaction_id", StringType(), False),
        StructField("account_id", StringType(), False),
        StructField("amount", DoubleType(), False),
        StructField("currency", StringType(), True),
        StructField("merchant_category", StringType(), True),
        StructField("merchant_name", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("country", StringType(), True),
        StructField("status", StringType(), True),
    ])


def calculate_fraud_score(df):
    """
    Calculate fraud risk score based on rules:
    - High amount (> 500): +0.3
    - Foreign country (not GB): +0.3
    - Night-time (hour < 6 or hour > 22): +0.2
    - Failed/pending status: +0.1
    """
    df = df.withColumn(
        "hour", F.hour(F.col("parsed_timestamp"))
    )

    df = df.withColumn(
        "fraud_score",
        (
            F.when(F.col("amount") > 500, 0.3).otherwise(
                F.when(F.col("amount") > 200, 0.15).otherwise(0.0)
            )
            + F.when(F.col("country") != "GB", 0.3).otherwise(0.0)
            + F.when(
                (F.col("hour") < 6) | (F.col("hour") > 22), 0.2
            ).otherwise(0.0)
            + F.when(F.col("status").isin("failed", "pending"), 0.1).otherwise(0.0)
        ),
    )

    df = df.withColumn(
        "fraud_risk_level",
        F.when(F.col("fraud_score") >= 0.6, "HIGH")
        .when(F.col("fraud_score") >= 0.3, "MEDIUM")
        .otherwise("LOW"),
    )

    return df


def main():
    """Main batch processing pipeline."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_FILE = os.path.join(BASE_DIR, "..", "data-generator", "output", "raw_transactions.json")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🚀 Starting BankFlow Batch Pipeline...")
    spark = create_spark_session()

    # ── Step 1: Read raw transactions ─────────────────────────
    print("📖 Reading raw transactions...")
    schema = define_schema()

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("   Run the data generator first: python data-generator/generate_transactions.py")
        sys.exit(1)

    df = spark.read.json(INPUT_FILE, schema=schema, multiLine=True)
    raw_count = df.count()
    print(f"   Total raw records: {raw_count:,}")

    # ── Step 2: Clean data ────────────────────────────────────
    print("🧹 Cleaning data...")
    df = df.filter(
        F.col("transaction_id").isNotNull()
        & F.col("account_id").isNotNull()
        & F.col("amount").isNotNull()
        & (F.col("amount") > 0)
    )

    # Parse timestamp
    df = df.withColumn(
        "parsed_timestamp",
        F.to_timestamp(F.col("timestamp")),
    )
    df = df.filter(F.col("parsed_timestamp").isNotNull())

    # Fill nulls
    df = df.fillna({"currency": "GBP", "country": "GB", "status": "completed"})
    clean_count = df.count()
    print(f"   Clean records: {clean_count:,} (dropped {raw_count - clean_count:,})")

    # ── Step 3: Fraud scoring ─────────────────────────────────
    print("🔍 Calculating fraud scores...")
    df = calculate_fraud_score(df)

    fraud_summary = (
        df.groupBy("fraud_risk_level")
        .agg(F.count("*").alias("count"))
        .orderBy("fraud_risk_level")
    )
    print("   Fraud distribution:")
    fraud_summary.show()

    # ── Step 4: Spend by category per account ─────────────────
    print("📊 Calculating spend by category...")
    spend_by_category = (
        df.groupBy("account_id", "merchant_category")
        .agg(
            F.sum("amount").alias("total_spend"),
            F.count("*").alias("transaction_count"),
            F.avg("amount").alias("avg_spend"),
        )
        .orderBy("account_id", F.desc("total_spend"))
    )

    # ── Step 5: Monthly aggregations with window functions ────
    print("📅 Calculating monthly aggregations...")
    df = df.withColumn("year_month", F.date_format(F.col("parsed_timestamp"), "yyyy-MM"))

    # Window: running total per account
    account_window = Window.partitionBy("account_id").orderBy("parsed_timestamp")

    df = df.withColumn(
        "running_total", F.sum("amount").over(account_window)
    )
    df = df.withColumn(
        "txn_rank_in_account", F.row_number().over(account_window)
    )

    monthly_agg = (
        df.groupBy("account_id", "year_month")
        .agg(
            F.sum("amount").alias("monthly_total"),
            F.count("*").alias("monthly_txn_count"),
            F.avg("amount").alias("monthly_avg"),
            F.max("amount").alias("monthly_max"),
            F.min("amount").alias("monthly_min"),
            F.sum(F.when(F.col("fraud_risk_level") == "HIGH", 1).otherwise(0)).alias("high_risk_count"),
        )
        .orderBy("account_id", "year_month")
    )

    # ── Step 6: Write Parquet output ──────────────────────────
    print("💾 Writing Parquet output...")

    processed_path = os.path.join(OUTPUT_DIR, "processed_transactions")
    df.write.mode("overwrite").parquet(processed_path)
    print(f"   ✅ Processed transactions: {processed_path}")

    spend_path = os.path.join(OUTPUT_DIR, "spend_by_category")
    spend_by_category.write.mode("overwrite").parquet(spend_path)
    print(f"   ✅ Spend by category: {spend_path}")

    monthly_path = os.path.join(OUTPUT_DIR, "monthly_aggregations")
    monthly_agg.write.mode("overwrite").parquet(monthly_path)
    print(f"   ✅ Monthly aggregations: {monthly_path}")

    fraud_path = os.path.join(OUTPUT_DIR, "fraud_summary")
    fraud_summary.write.mode("overwrite").parquet(fraud_path)
    print(f"   ✅ Fraud summary: {fraud_path}")

    # ── Step 7: Write CSV summaries for easy inspection ───────
    print("📋 Writing CSV summaries...")

    global_spend = (
        df.groupBy("merchant_category")
        .agg(
            F.sum("amount").alias("total_spend"),
            F.count("*").alias("count"),
        )
        .orderBy(F.desc("total_spend"))
    )
    global_spend.coalesce(1).write.mode("overwrite").csv(
        os.path.join(OUTPUT_DIR, "global_spend_summary"), header=True
    )

    fraud_summary.coalesce(1).write.mode("overwrite").csv(
        os.path.join(OUTPUT_DIR, "fraud_summary_csv"), header=True
    )

    print("\n🎉 Batch pipeline complete!")
    print(f"   Processed {clean_count:,} transactions")
    print(f"   Output directory: {OUTPUT_DIR}")

    spark.stop()


if __name__ == "__main__":
    main()
