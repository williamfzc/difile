"""
MIT License

Copyright (c) 2020 williamfzc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__PROJECT_NAME__ = r"difile"
__AUTHOR__ = r"williamfzc"
__AUTHOR_EMAIL__ = r"fengzc@vip.qq.com"
__LICENSE__ = r"MIT"
__URL__ = r"https://github.com/williamfzc/difile"
__VERSION__ = r"0.1.0"
__DESCRIPTION__ = r"lightweight diff-file library with difflib"

import pathlib
from filecmp import dircmp
import difflib
import os
import typing
import warnings

CHARSET = "utf-8"
# same
CODE_IGNORE = "  "
# add
CODE_ADD = "+ "
# remove
CODE_REMOVE = "- "
# invalid
CODE_UNKNOWN = "? "


class Line(object):
    def __init__(
        self, line_no: int, content: str, code: str, file_path: os.PathLike = None
    ):
        self.line_no = line_no
        self.content = content
        self.code = code
        self.file_path = file_path

    def is_(self, code: str) -> bool:
        return self.code == code

    def __str__(self):
        return f"<Line{self.code}{self.file_path} line{self.line_no} {self.content.strip()}>"


class Difile(object):
    def compare_file(
        self,
        left: typing.Union[str, os.PathLike],
        right: typing.Union[str, os.PathLike],
    ):
        diff = difflib.Differ()
        result = list()
        with open(left, encoding=CHARSET) as f:
            left_content = f.readlines()
        with open(right, encoding=CHARSET) as f:
            right_content = f.readlines()

        left_line_no = right_line_no = 0
        for raw_line in diff.compare(left_content, right_content):
            code, content = raw_line[:2], raw_line[2:]
            line = Line(-1, content, code)
            if line.is_(CODE_ADD):
                # right
                line.file_path = right
                right_line_no += 1
                line.line_no = right_line_no
            elif line.is_(CODE_REMOVE):
                # left
                line.file_path = left
                left_line_no += 1
                line.line_no = left_line_no
            elif line.is_(CODE_IGNORE):
                # both
                left_line_no += 1
                right_line_no += 1
                # ignore this line
                continue
            else:
                # unknown
                warnings.warn(f"unknown line {left_line_no}/{right_line_no}: {line.content}")
                continue
            result.append(line)
        return result

    def compare_dir(
        self,
        left: typing.Union[str, os.PathLike],
        right: typing.Union[str, os.PathLike],
    ):
        cmp_result = dircmp(left, right)
        result = list()

        def _loop(d: dircmp):
            # by default, comparison based on timeline: left: old; right: new
            # left only contains something has been removed, so ignore
            # right only container something new
            for each_file in d.diff_files:
                # todo: file was removed?
                if each_file not in d.right_list:
                    continue
                # check
                left_file_path = pathlib.Path(d.left) / each_file
                right_file_path = pathlib.Path(d.right) / each_file
                if left_file_path.is_file() and right_file_path.is_file():
                    result.append(self.compare_file(left_file_path, right_file_path))
            # recursive
            for _, each_cmp in d.subdirs.items():
                _loop(each_cmp)

        _loop(cmp_result)
        return result
