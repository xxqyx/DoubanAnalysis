const express = require('express');
const mysql = require('mysql');
const cors = require('cors');  // 允许跨域请求
const app = express();
const port = 3000;

// MySQL连接配置
const connection = mysql.createConnection({
  host: 'localhost',  // MySQL服务器地址
  user: 'root',  // MySQL用户名
  password: 'xxqx001128',  // MySQL密码
  database: 'douban_viz'  // 数据库名称
});

// 连接MySQL数据库
connection.connect((err) => {
  if (err) {
    console.error('错误连接到数据库:', err.stack);
    return;
  }
  console.log('成功连接到数据库');
});

// 允许跨域请求
app.use(cors());

// 获取年度评分趋势数据
app.get('/yearly-rating', (req, res) => {
  connection.query('SELECT * FROM yearly_rating', (err, results) => {
    if (err) throw err;
    res.json(results);  // 返回JSON格式的数据
  });
});

// 获取导演分析数据
app.get('/director-stats', (req, res) => {
  connection.query(
	  'SELECT * FROM director_stats ORDER BY movie_count DESC', (err, results) => {
    if (err) throw err;
    res.json(results);  // 返回JSON格式的数据
  });
});

// 获取类型分布数据
app.get('/genre-count', (req, res) => {
  connection.query('SELECT * FROM genre_count ORDER BY count DESC', (err, results) => {
    if (err) throw err;
    res.json(results);  // 返回JSON格式的数据
  });
});

// 获取用户评分分布数据
app.get('/user-rating-dist', (req, res) => {
  connection.query('SELECT * FROM user_rating_dist', (err, results) => {
    if (err) throw err;
    res.json(results);  // 返回JSON格式的数据
  });
});

// 获取电影聚类结果数据
app.get('/movie-clusters', (req, res) => {
  connection.query('SELECT * FROM movie_clusters', (err, results) => {
    if (err) throw err;
    res.json(results);  // 返回JSON格式的数据
  });
});

// 获取评分预测数据
app.get('/rating-predictions', (req, res) => {
  connection.query('SELECT * FROM rating_predictions', (err, results) => {
    if (err) throw err;
    res.json(results);  // 返回JSON格式的数据
  });
});

// 启动服务器
app.listen(port, () => {
  console.log(`服务器正在运行在 http://localhost:${port}`);
});

