#!/usr/bin/env python3
import sys

current_genre = None
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    genre, cnt_str = line.split('\t')
    cnt = int(cnt_str)
    
    if current_genre != genre:
        if current_genre is not None:
            print(f"{current_genre}\t{count}")
        current_genre = genre
        count = 0
    count += cnt

# 处理最后一个类型
if current_genre is not None:
    print(f"{current_genre}\t{count}")
