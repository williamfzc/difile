import pathlib
from filecmp import dircmp
import difflib
import os
import typing
import tempfile

CHARSET = "utf-8"


TypeLineCode = str
TypeResponse = typing.List["Line"]
TypePath = typing.Union[str, os.PathLike, pathlib.Path]


class LineCode(object):
    # same
    IGNORE: TypeLineCode = "  "
    # add
    ADD: TypeLineCode = "+ "
    # remove
    REMOVE: TypeLineCode = "- "
    # invalid
    UNKNOWN: TypeLineCode = "? "


class Line(object):
    def __init__(
        self, line_no: int, content: str, code: str, file_path: TypePath = None,
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
    def file2line(self, path: TypePath, code: TypeLineCode) -> TypeResponse:
        with open(path, encoding=CHARSET) as f:
            content = f.readlines()
        return self.list2line(content, code, path)

    def string2line(
        self,
        string: str,
        code: TypeLineCode,
        sep: str = os.linesep,
        path: TypePath = None,
    ) -> TypeResponse:
        return self.list2line(string.split(sep), code, path)

    def list2line(
        self, string_list: typing.List[str], code: TypeLineCode, path: TypePath = None,
    ) -> TypeResponse:
        ret = list()
        for index, each in enumerate(string_list):
            line = Line(index + 1, each, code, path)
            ret.append(line)
        return ret

    def compare_string(
        self, left: str, right: str, sep: str = os.linesep, *args, **kwargs
    ) -> TypeResponse:
        return self.compare_string_list(
            left.split(sep), right.split(sep), *args, **kwargs
        )

    def compare_string_list(
        self,
        left: typing.List[str],
        right: typing.List[str],
        left_path: TypePath,
        right_path: TypePath,
        contain_all: bool = None,
    ) -> TypeResponse:
        diff = difflib.Differ()
        result = list()
        left_line_no = right_line_no = 0
        for raw_line in diff.compare(left, right):
            code, content = raw_line[:2], raw_line[2:]
            line = Line(-1, content, code)
            if line.is_(LineCode.ADD):
                # right
                line.file_path = right_path
                right_line_no += 1
                line.line_no = right_line_no
            elif line.is_(LineCode.REMOVE):
                # left
                line.file_path = left_path
                left_line_no += 1
                line.line_no = left_line_no
            elif line.is_(LineCode.IGNORE):
                # both
                left_line_no += 1
                right_line_no += 1
                if contain_all:
                    line.file_path = left_path
                    line.line_no = left_line_no
                else:
                    # ignore this line
                    continue
            else:
                # unknown
                continue
            result.append(line)
        return result

    def compare_file(
        self, left: TypePath, right: TypePath, contain_all: bool = None,
    ) -> TypeResponse:
        with open(left, encoding=CHARSET) as f:
            left_content = f.readlines()
        with open(right, encoding=CHARSET) as f:
            right_content = f.readlines()

        return self.compare_string_list(
            left_content, right_content, left, right, contain_all
        )

    def compare_dir(
        self, left: TypePath, right: TypePath, contain_all: bool = None,
    ) -> typing.List[TypeResponse]:
        cmp_result = dircmp(left, right)
        result = list()

        def _loop(d: dircmp):
            # by default, comparison based on timeline: left: old; right: new
            # left only contains something has been removed
            # right only container something new

            # new file: every lines are ADD
            # removed file: every lines are REMOVED
            nonlocal result

            def _handle_side(cur_path: pathlib.Path, is_left: bool):
                if cur_path.is_file():
                    result.append(
                        self.file2line(
                            cur_path, LineCode.REMOVE if is_left else LineCode.ADD
                        )
                    )
                elif cur_path.is_dir():
                    # compare with empty dir
                    with tempfile.TemporaryDirectory() as empty_dir:
                        order = (
                            (cur_path, empty_dir) if is_left else (empty_dir, cur_path)
                        )
                        _loop(dircmp(*order))

            for each in d.left_only:
                path = pathlib.Path(d.left) / each
                _handle_side(path, is_left=True)

            for each in d.right_only:
                path = pathlib.Path(d.right) / each
                _handle_side(path, is_left=False)

            # both
            for each_file in d.diff_files:
                left_file_path = pathlib.Path(d.left) / each_file
                right_file_path = pathlib.Path(d.right) / each_file
                compare_result = self.compare_file(left_file_path, right_file_path, contain_all)
                if compare_result:
                    result.append(compare_result)
            # recursive
            for _, each_cmp in d.subdirs.items():
                _loop(each_cmp)

        _loop(cmp_result)
        return result


class LineOperator(object):
    """ extra operations about handling results """

    @classmethod
    def list2dict(
        cls, result_list: typing.Union[TypeResponse, typing.List[TypeResponse]]
    ):
        result_dict = dict()

        def dfs(r):
            if not r:
                return

            for each in r:
                if isinstance(each, list):
                    dfs(each)
                else:
                    each: Line
                    # hashable required
                    key = each.file_path.as_posix()
                    if key not in result_dict:
                        result_dict[key] = []
                    result_dict[key].append(each)

        dfs(result_list)
        return result_dict
