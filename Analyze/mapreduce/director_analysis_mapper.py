#!/usr/bin/env python3
import sys

# 输入数据格式：movie_id,movie_name,year,director,screenwriter,...,rating,...
for line in sys.stdin:
    # 跳过可能的标题行（如果存在）
    if line.startswith("movie_id"):
        continue
    fields = line.strip().split(',')
    if len(fields) < 14:  # 检查字段数量是否正确
        continue
    try:
        director = fields[3]        # 第4列为导演（索引3）
        rating = fields[8]          # 第9列为评分（索引8）
        if director and rating:      # 过滤空导演和空评分
            print(f"{director}\t{rating}\t1")
    except (ValueError, IndexError):
        # 忽略格式错误或缺失值的行
        continue
