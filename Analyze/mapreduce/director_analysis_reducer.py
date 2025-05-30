#!/usr/bin/env python3
import sys

current_director = None
total_rating = 0.0
movie_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    director, rating_str, cnt_str = line.split('\t')
    try:
        rating = float(rating_str)
        cnt = int(cnt_str)
    except ValueError:
        continue
    
    if current_director != director:
        if current_director is not None:
            avg_rating = total_rating / movie_count
            print(f"{current_director}\t{movie_count}\t{avg_rating:.2f}")
        current_director = director
        total_rating = 0.0
        movie_count = 0
    
    total_rating += rating
    movie_count += cnt

# 处理最后一个导演
if current_director is not None:
    avg_rating = total_rating / movie_count
    print(f"{current_director}\t{movie_count}\t{avg_rating:.2f}")
