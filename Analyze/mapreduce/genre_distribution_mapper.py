#!/usr/bin/env python3
import sys

# 输入数据格式：id, movie_id, genre（例如 "24262,9144,武侠"）
for line in sys.stdin:
    # 跳过可能的标题行（如果存在）
    if line.startswith("id") or line.startswith("movie_id"):
        continue
    fields = line.strip().split(',')
    if len(fields) < 3:  # 现在检查至少有3列
        continue
    try:
        genre = fields[2].strip()  # 第3列为类型（索引2）
        if genre:
            print(f"{genre}\t1")
    except (IndexError, ValueError):
        continue

