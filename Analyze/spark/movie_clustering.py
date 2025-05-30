from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.sql.functions import col
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler, StandardScaler

# 初始化 SparkSession
spark = SparkSession.builder \
    .appName("MovieClustering") \
    .getOrCreate()

# 1. 定义数据模式（手动指定字段类型）
schema = """
    movie_id INT,
    movie_name STRING,
    year INT,
    director STRING,
    screenwriter STRING,
    country STRING,
    language STRING,
    release_date STRING,
    rating DOUBLE,
    rating_count INT,
    synopsis STRING,
    duration INT,
    image_url STRING,
    detail_url STRING,
    video_url STRING
"""

# 2. 读取电影主表数据（强制指定 rating 和 rating_count 类型）
df = spark.read.csv(
    "hdfs://localhost:9000/user/hadoop/douban/movies",
    header=False,
    schema=schema  # 使用预定义模式
)

# 3. 选择需要的字段并过滤无效数据
df = df.select(
    col("movie_id"),
    col("rating").cast(DoubleType()),  # 显式转换为 Double
    col("rating_count").cast(IntegerType())  # 显式转换为 Int
).filter(
    (col("rating").isNotNull()) & 
    (col("rating_count").isNotNull()) & 
    (col("rating") >= 0) & 
    (col("rating") <= 10)
)

# 4. 特征工程：将 rating 和 rating_count 合并为特征向量
assembler = VectorAssembler(
    inputCols=["rating", "rating_count"],
    outputCol="raw_features"
)
df_features = assembler.transform(df)

# 5. 标准化特征
scaler = StandardScaler(
    inputCol="raw_features",
    outputCol="scaled_features",
    withStd=True,
    withMean=True
)
scaler_model = scaler.fit(df_features)
df_scaled = scaler_model.transform(df_features)

# 6. 训练 K-Means 模型
kmeans = KMeans(
    featuresCol="scaled_features",
    predictionCol="cluster",
    k=3,
    seed=42
)
model = kmeans.fit(df_scaled)

# 7. 预测聚类结果
clusters = model.transform(df_scaled)

# 8. 查看聚类结果示例
clusters.select("movie_id", "rating", "rating_count", "cluster").show(10)

# 9. 保存结果到 HDFS（仅保留基础字段）
clusters.select("movie_id", "rating", "rating_count", "cluster") \
    .write.csv("hdfs://localhost:9000/user/hadoop/douban/cluster_results")

# 10. 关闭 Spark
spark.stop()
