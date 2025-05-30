# 1. 将数据导入mysql的表中
#假设所有数据文件在目录"/var/lib/mysql-files/"下
-- 导入主表
LOAD DATA INFILE '/var/lib/mysql-files/movies.csv'
INTO TABLE movies
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movie_name, year, director, screenwriter, country, language,
 release_date, rating, rating_count, synopsis, duration, image_url,
 detail_url, video_url);

-- 导入演员表
LOAD DATA INFILE '/var/lib/mysql-files/movie_actors.csv'
INTO TABLE movie_actors
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movie_id, actor);

-- 导入类型表
LOAD DATA INFILE '/var/lib/mysql-files/movie_genres.csv'
INTO TABLE movie_genres
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movie_id, genre);

-- 导入评论表
LOAD DATA INFILE '/var/lib/mysql-files/movie_reviews.csv'
INTO TABLE movie_reviews
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movie_id, user_name, review_content, user_rating);


# 2. 进行数据分析
#启动hadoop
$HADOOP_HOME/sibin/start-all.sh
#启动spark虚拟环境
source $SPARK_HOME/pyspark-env/bin/activate

echo "[$(date)] 开始运行 MapReduce 作业..."
#删除hdfs中的目录
hadoop fs -rm -r /user/hadoop/douban/output_yearly_rating
hadoop fs -rm -r /user/hadoop/douban/output_director_stats
hadoop fs -rm -r /user/hadoop/douban/output_genre_count
hadoop fs -rm -r /user/hadoop/douban/output_user_rating
hadoop fs -rm -r /user/hadoop/douban/cluster_results
hadoop fs -rm -r /user/hadoop/douban/kmeans_model
hadoop fs -rm -r /user/hadoop/douban/linear_model_rating

#运行 MapReduce - 年度评分趋势
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /usr/local/hadoop/code/mapreduce/yearly_rating_mapper.py,/usr/local/hadoop/code/mapreduce/yearly_rating_reducer.py \
  -input /user/hadoop/douban/movies/part-m-00000 \
  -output /user/hadoop/douban/output_yearly_rating \
  -mapper "python3 yearly_rating_mapper.py" \
  -reducer "python3 yearly_rating_reducer.py"

#运行 MapReduce - 导演分析
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /usr/local/hadoop/code/mapreduce/director_analysis_mapper.py,/usr/local/hadoop/code/mapreduce/director_analysis_reducer.py \
  -input /user/hadoop/douban/movies/part-m-00000 \
  -output /user/hadoop/douban/output_director_stats \
  -mapper "python3 director_analysis_mapper.py" \
  -reducer "python3 director_analysis_reducer.py"

#运行 MapReduce - 类型分布
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /usr/local/hadoop/code/mapreduce/genre_distribution_mapper.py,/usr/local/hadoop/code/mapreduce/genre_distribution_reducer.py \
  -input /user/hadoop/douban/movie_genres/part-m-00000 \
  -output /user/hadoop/douban/output_genre_count \
  -mapper "python3 genre_distribution_mapper.py" \
  -reducer "python3 genre_distribution_reducer.py"

#运行 MapReduce - 用户评分分布
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /usr/local/hadoop/code/mapreduce/user_rating_mapper.py,/usr/local/hadoop/code/mapreduce/user_rating_reducer.py \
  -input /user/hadoop/douban/movie_reviews/part-m-00000 \
  -output /user/hadoop/douban/output_user_rating \
  -mapper "python3 user_rating_mapper.py" \
  -reducer "python3 user_rating_reducer.py"

echo "[$(date)] MapReduce作业完成。"

echo "[$(date)] 开始运行 Spark 作业..."

#运行 Spark - 电影聚类
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  /usr/local/hadoop/code/spark/movie_clustering.py

#运行 Spark - 评分预测
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  /usr/local/hadoop/code/spark/rating_prediction.py

echo "[$(date)] Spark作业完成。"

echo "[$(date)] 开始从HDFS提取数据并导入MySQL..."

#清空本地output目录
rm -rf /usr/local/hadoop/code/output/*
mkdir -p /usr/local/hadoop/code/output

# 下载各分析任务结果
hadoop fs -cat /user/hadoop/douban/output_yearly_rating/part-* | \
  awk -F'\t' '{print $1 "," $2}' > ./output/yearly_rating.csv
hadoop fs -cat /user/hadoop/douban/output_director_stats/part-* | \
  awk -F'\t' '{print $1 "," $2 "," $3}' > ./output/director_stats.csv
hadoop fs -cat /user/hadoop/douban/output_genre_count/part-* | \
  awk -F'\t' '{print $1 "," $2}' > ./output/genre_count.csv
hadoop fs -cat /user/hadoop/douban/output_user_rating/part-* | \
  awk -F'\t' '{print $1 "," $2}' > ./output/user_rating_dist.csv
hadoop fs -cat /user/hadoop/douban/cluster_results/part-* | \
  awk -F'\t' '{print $1 "," $2 "," $3 "," $4}' > ./output/movie_clusters.csv
hadoop fs -cat /user/hadoop/douban/linear_model_rating/prediction_results/part-* | \
  awk -F'\t' '{print $1 "," $2 "," $3}' > ./output/rating_predictions.csv


# 3. 将分析结果导入mysql
#在导入之前，清空MySQL表的数据
mysql -u root -p douban_viz -e "TRUNCATE TABLE yearly_rating;"
mysql -u root -p douban_viz -e "TRUNCATE TABLE director_stats;"
mysql -u root -p douban_viz -e "TRUNCATE TABLE genre_count;"
mysql -u root -p douban_viz -e "TRUNCATE TABLE user_rating_dist;"
mysql -u root -p douban_viz -e "TRUNCATE TABLE movie_clusters;"
mysql -u root -p douban_viz -e "TRUNCATE TABLE rating_predictions;"

#向mysql中导入数据
mysqlimport --local --ignore-lines=0 --fields-terminated-by=',' \
  -u root -p douban_viz ./output/yearly_rating.csv
mysqlimport --local --ignore-lines=0 --fields-terminated-by=',' \
  -u root -p douban_viz ./output/director_stats.csv
mysqlimport --local --ignore-lines=0 --fields-terminated-by=',' \
  -u root -p douban_viz ./output/genre_count.csv
mysqlimport --local --ignore-lines=0 --fields-terminated-by=',' \
  -u root -p douban_viz ./output/user_rating_dist.csv
mysqlimport --local --ignore-lines=0 --fields-terminated-by=',' \
  -u root -p douban_viz ./output/movie_clusters.csv
mysqlimport --local --ignore-lines=0 --fields-terminated-by=',' \
  -u root -p douban_viz ./output/rating_predictions.csv

# 4. 可视化
node app.js		#后端数据库监听
http-server		#前端

# 5. 本地部署
chmod +x run_all.sh
crontab -e
0 2 * * * run_all.sh
