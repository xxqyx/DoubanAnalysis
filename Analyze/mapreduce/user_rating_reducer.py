#!/usr/bin/env python3
import sys

current_bin = None
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    rating_bin, cnt_str = line.split('\t')
    cnt = int(cnt_str)
    
    if current_bin != rating_bin:
        if current_bin is not None:
            print(f"{current_bin}\t{count}")
        current_bin = rating_bin
        count = 0
    count += cnt

# 处理最后一个分箱
if current_bin is not None:
    print(f"{current_bin}\t{count}")
