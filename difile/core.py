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
    ) -> typing.List[Line]:
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
                warnings.warn(
                    f"unknown line {left_line_no}/{right_line_no}: {line.content}"
                )
                continue
            result.append(line)
        return result

    def compare_dir(
        self,
        left: typing.Union[str, os.PathLike],
        right: typing.Union[str, os.PathLike],
    ) -> typing.List[typing.List[Line]]:
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
