#!/usr/bin/env python3
import sys

# 输入数据格式：movie_id,movie_name,year,director,...,rating,...
for line in sys.stdin:
    # 跳过可能的标题行（如果存在）
    if line.startswith("movie_id"):
        continue
    fields = line.strip().split(',')
    if len(fields) < 14:  # 检查字段数量是否正确
        continue
    try:
        year = fields[2]        # 第3列为年份（索引2）
        rating = fields[8]      # 第9列为评分（索引8）
        if year and rating:
            # 输出格式：年份\t评分\t计数（固定为1）
            print(f"{year}\t{rating}\t1")
    except (ValueError, IndexError):
        # 忽略格式错误或缺失值的行
        continue
