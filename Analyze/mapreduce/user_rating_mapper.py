#!/usr/bin/env python3
import sys

# 输入数据格式：id, movie_id, user_name, review_content, user_rating
for line in sys.stdin:
    # 跳过可能的标题行（如果存在）
    if line.startswith("id"):
        continue
    fields = line.strip().split(',')
    if len(fields) < 5:  # 检查字段数量是否正确
        continue
    try:
        rating_str = fields[4]  # 第5列为用户评分（索引4）
        rating = float(rating_str)
        # 过滤无效评分（假设豆瓣评分范围0~10）
        if rating < 0 or rating > 10:
            continue
        # 计算评分分箱（如4.3分归到4.0-4.5区间）
        rating_bin = int(rating * 2) / 2  # 例如：4.3 → 4.0
        print(f"{rating_bin:.1f}\t1")
    except (ValueError, IndexError):
        continue
