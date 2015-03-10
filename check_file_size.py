# -*- coding: utf-8 -*-
import os
import glob
import argparse
import sys

SIZE = [ "Byte", "KB", "MB", "GB", "TB", "PB", ]

def check_file_size(root = '.'):

    size_dir = {}
    skip_files = []
    for path, dirs, files in os.walk(root, topdown=False):

        relpath = os.path.relpath(path, root)
        abspath = os.path.abspath(path)
        key = relpath
        size_dir[key] = 0

        for f in files:
            file_path = os.path.join(abspath, f)
            try:
                size_dir[key] += os.path.getsize(file_path)
            except WindowsError:
                skip_files.append(file_path)

        if key == os.path.curdir:
            for r_d in dirs:
                if not size_dir.has_key(r_d):
                    continue
                size_dir[key] += size_dir[r_d]
        else:
            for d in dirs:
                dir_key = os.path.join(key, d)
                if not size_dir.has_key(dir_key):
                    continue
                size_dir[key] += size_dir[dir_key]

    return size_dir, skip_files

def main(
        root = ".",
        max_depth = 0,
        min_size = 0,
        size_type_list = SIZE,
        outbuf = sys.stdout,
        delimiter = "\t",
        end_of_line = "\n",
        ):
    """main"""

    size_dir, skip_files = check_file_size(root)

    keys = sorted(size_dir.keys())
    for k in keys:

        # depth check
        dirs_depth = k.split(os.path.sep)
        depth = len(dirs_depth)
        if 0 < max_depth and max_depth < depth:
            continue

        # size check
        s = size_dir[k]
        if s < min_size:
            continue

        s = float(s)

        size_type = size_type_list[0]
        for s_type in size_type_list[1:]:
            if 1024 < s:
                s /= 1024
                size_type = s_type
            else:
                break
        outbuf.write(delimiter.join([k, "%.2f"%(s), size_type]) + end_of_line)

    for f in skip_files:
        outbuf.write(delimiter.join(["Skipped:", f]) + end_of_line)

def arg_parse(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
            '--help',
            action = 'help',
            help='このヘルプを表示',
            )
    parser.add_argument(
            '--input-dir-path', '-i',
            metavar='ROOT_PATH',
            default='.',
            help='ファイルサイズを調査したいディレクトリパス',
            )
    parser.add_argument(
            '--max-depth', '-d',
            metavar='N',
            type=int, default=0,
            help='表示するディレクトリの深さ'
            )
    parser.add_argument(
            '--min-size', '-s',
            metavar='N',
            type=int, default=0,
            help='表示するディレクトリの最小サイズ'
            )
    parser.add_argument(
            '--min-size-type', '-t',
            default=SIZE[0], choices=SIZE,
            help='表示するディレクトリの最小サイズの単位'
            )
    parser.add_argument(
            '--human-readble', '-h',
            action = 'store_true',
            help='単位を読み取りやすく変更'
            )
    parser.add_argument(
            '--output_file', '-o',
            type=argparse.FileType("w", 0), default='-',
            help='出力バッファ'
            )
    parser.add_argument(
            '--delimiter',
            default="\t",
            help='区切り文字'
            )
    parser.add_argument(
            '--end-of-line',
            default="\n",
            help='行末記号'
            )

    args = parser.parse_args(argv)

    size_dir = check_file_size(args.input_dir_path)

    min_size = args.min_size
    size_type = args.min_size_type
    for s_type in SIZE:
        if s_type == size_type:
            break
        min_size *= 1024

    if args.human_readble:
        size_type_list = SIZE
    else:
        size_type_list = SIZE[:1]

    outbuf = args.output_file

    return {
            'root' : args.input_dir_path,
            'max_depth' : args.max_depth,
            'min_size' : min_size,
            'size_type_list' : size_type_list,
            'outbuf' : outbuf,
            'delimiter' : args.delimiter,
            'end_of_line' : args.end_of_line,
            }

if __name__ == '__main__':

    args = arg_parse(sys.argv[1:])
    main(**args)
