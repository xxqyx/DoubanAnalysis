#!/usr/bin/env python3
import sys

current_year = None
total_rating = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    year, rating_str, cnt_str = line.split('\t')
    try:
        rating = float(rating_str)
        cnt = int(cnt_str)
    except ValueError:
        continue
    
    if current_year != year:
        if current_year is not None:
            avg_rating = total_rating / count
            print(f"{current_year}\t{avg_rating:.2f}")
        current_year = year
        total_rating = 0.0
        count = 0
    
    total_rating += rating
    count += cnt

# 处理最后一个年份
if current_year is not None:
    avg_rating = total_rating / count
    print(f"{current_year}\t{avg_rating:.2f}")
