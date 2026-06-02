# wordcount.py — Job clássico de contagem de palavras com PySpark
# Este script é executado dentro do cluster Spark via spark-submit

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, lower, col, desc

# Criar SparkSession
spark = SparkSession.builder \
    .appName("WordCount - K8s Lab") \
    .getOrCreate()

print("=" * 60)
print("🚀 WordCount — Spark on Kubernetes")
print("=" * 60)

# Dados de exemplo (em produção, seria um arquivo no S3/HDFS)
textos = [
    "Kubernetes orquestra contêineres em escala",
    "Docker empacota aplicações em contêineres portáteis",
    "Spark processa dados em larga escala com paralelismo",
    "Big Data e Kubernetes são o futuro da engenharia de dados",
    "Contêineres Docker rodam no Kubernetes com orquestração automática",
    "A ciência de dados usa Spark para processar grandes volumes",
    "Kubernetes escala automaticamente os workers do Spark",
    "Docker e Kubernetes formam a base da infraestrutura moderna",
    "Dados distribuídos são processados por Spark em clusters Kubernetes",
    "O futuro da ciência de dados é na nuvem com Kubernetes e Spark",
]

# Criar DataFrame
df = spark.createDataFrame([(t,) for t in textos], ["texto"])

# Contar palavras
resultado = (
    df.select(explode(split(lower(col("texto")), r"\s+")).alias("palavra"))
    .groupBy("palavra")
    .count()
    .orderBy(desc("count"))
)

print("\n📊 Top 15 palavras mais frequentes:")
print("-" * 40)
resultado.show(15, truncate=False)

# Estatísticas
total_palavras = resultado.agg({"count": "sum"}).collect()[0][0]
palavras_unicas = resultado.count()

print(f"\n📈 Total de palavras: {total_palavras}")
print(f"📈 Palavras únicas: {palavras_unicas}")
print("=" * 60)

spark.stop()
