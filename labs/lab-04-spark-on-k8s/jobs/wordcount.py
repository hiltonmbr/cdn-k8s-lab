# wordcount.py — Classic word count job with PySpark
# This script runs inside the Spark cluster via spark-submit

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, lower, col, desc

# Create SparkSession
spark = SparkSession.builder \
    .appName("WordCount - K8s Lab") \
    .getOrCreate()

print("=" * 60)
print("🚀 WordCount — Spark on Kubernetes")
print("=" * 60)

# Sample data (in production, this would be a file in S3/HDFS)
textos = [
    "Kubernetes orchestrates containers at scale",
    "Docker packages applications in portable containers",
    "Spark processes data at scale with parallelism",
    "Big Data and Kubernetes are the future of data engineering",
    "Docker containers run on Kubernetes with automatic orchestration",
    "Data science uses Spark to process large volumes",
    "Kubernetes automatically scales Spark workers",
    "Docker and Kubernetes form the foundation of modern infrastructure",
    "Distributed data is processed by Spark on Kubernetes clusters",
    "The future of data science is in the cloud with Kubernetes and Spark",
]

# Create DataFrame
df = spark.createDataFrame([(t,) for t in textos], ["text"])

# Count words
resultado = (
    df.select(explode(split(lower(col("text")), r"\s+")).alias("word"))
    .groupBy("word")
    .count()
    .orderBy(desc("count"))
)

print("\n📊 Top 15 most frequent words:")
print("-" * 40)
resultado.show(15, truncate=False)

# Statistics
total_palavras = resultado.agg({"count": "sum"}).collect()[0][0]
palavras_unicas = resultado.count()

print(f"\n📈 Total words: {total_palavras}")
print(f"📈 Unique words: {palavras_unicas}")
print("=" * 60)

spark.stop()
