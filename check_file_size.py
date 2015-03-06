# -*- coding: utf-8 -*-
import os
import glob

root = r'.'

size_dir = {}
for path, dirs, files in os.walk(root, topdown=False):

    relpath = os.path.relpath(path, root)
    key = relpath
    size_dir[key] = 0

    for f in files:
        size_dir[key] += os.path.getsize(os.path.join(path, f))
    if key == os.path.curdir:
        for r_d in dirs:
            size_dir[key] += size_dir[r_d]
    else:
        for d in dirs:
            dir_key = os.path.join(key, d)
            size_dir[key] += size_dir[dir_key]


SIZE = [ "Byte", "KB", "MB", "GB" ]
MAX_DEPTH = 1

keys = sorted(size_dir.keys())
for k in keys:
    dirs_depth = k.split(os.path.sep)
    depth = len(dirs_depth)
    if MAX_DEPTH < depth:
        continue
    s = float(size_dir[k])
    for siz in SIZE:
        if 1024 < s:
            s /= 1024
        else:
            print k, "%.2f"%(s), siz
            break


