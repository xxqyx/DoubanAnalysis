from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import StringIndexer, CountVectorizer, VectorAssembler
from pyspark.ml import Pipeline
from pyspark.sql.functions import col, collect_list
from pyspark.sql import Row
from pyspark.sql.functions import round as spark_round  

# 初始化 SparkSession
spark = SparkSession.builder \
    .appName("RatingPrediction") \
    .getOrCreate()

# 1. 读取电影主表数据
schema_movies = """
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
df_movies = spark.read.csv(
    "hdfs://localhost:9000/user/hadoop/douban/movies",
    header=False,
    schema=schema_movies
).select(
    col("movie_id"),
    col("director"),
    col("rating")
).filter(
    (col("director").isNotNull()) &
    (col("rating").isNotNull()) &
    (col("rating") >= 0) &
    (col("rating") <= 10)
)

# 2. 读取电影类型表数据并聚合为列表
df_genres = spark.read.csv(
    "hdfs://localhost:9000/user/hadoop/douban/movie_genres",
    header=False,
    schema="movie_id INT, genre STRING"
).groupBy("movie_id").agg(
    collect_list("genre").alias("genres")
)

# 3. 合并电影主表和类型表
df = df_movies.join(df_genres, "movie_id", "inner")

# 4. 处理导演特征（StringIndexer）
director_indexer = StringIndexer(
    inputCol="director",
    outputCol="director_index"
)

# 5. 处理类型特征（CountVectorizer）
count_vectorizer = CountVectorizer(
    inputCol="genres",
    outputCol="genre_vector"
)

# 6. 特征组合（VectorAssembler）
assembler = VectorAssembler(
    inputCols=["director_index", "genre_vector"],
    outputCol="features"
)

# 7. 构建流水线
pipeline = Pipeline(stages=[
    director_indexer,
    count_vectorizer,
    assembler
])

# 8. 训练流水线并转换数据
model_pipeline = pipeline.fit(df)
df_transformed = model_pipeline.transform(df)

# 9. 划分训练集和测试集
train, test = df_transformed.randomSplit([0.8, 0.2], seed=42)

# 10. 训练线性回归模型
lr = LinearRegression(
    featuresCol="features",
    labelCol="rating",
    maxIter=10,
    regParam=0.3
)
model_lr = lr.fit(train)

# 11. 保存模型预测结果
predictions = model_lr.transform(test)
predictions.select("movie_id", 
                   "rating", 
                   spark_round(col("prediction"), 1).alias("prediction")) \
    .write.csv("hdfs://localhost:9000/user/hadoop/douban/linear_model_rating/prediction_results")

# 12. 保存模型评估指标到 HDFS
metrics = [
    Row(metric="R2", value=model_lr.summary.r2),
    Row(metric="RMSE", value=model_lr.summary.rootMeanSquaredError)
]
metrics_df = spark.createDataFrame(metrics)
metrics_df.write.mode("overwrite").csv("hdfs://localhost:9000/user/hadoop/douban/linear_model_rating/model_metrics")

# 13. 保存模型和特征流水线
model_lr.save("hdfs://localhost:9000/user/hadoop/douban/linear_model_rating/linear_model")
model_pipeline.save("hdfs://localhost:9000/user/hadoop/douban/linear_model_rating/lr_feature_model")


# 14. 关闭 Spark
spark.stop()
