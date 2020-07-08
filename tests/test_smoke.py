from difile import Difile, LineCode, Line, LineOperator
import pathlib


difile = Difile()
workspace = pathlib.Path(__file__).parent
dir1 = workspace / "dirs" / "dir1"
dir2 = workspace / "dirs" / "dir2"
file1 = dir1 / "file1.txt"
file2 = dir2 / "file1.txt"


def test_compare_file():
    r = difile.compare_file(file1, file2, contain_all=False)
    assert len(list(r)) == 6
    r1 = difile.compare_file(file1.as_posix(), file2.as_posix())
    assert len(list(r1)) == 6

    for l1, l2 in zip(r, r1):
        assert l1.line_no == l2.line_no
        assert l1.code == l2.code


def test_compare_dir():
    r = difile.compare_dir(dir1, dir2)
    assert len(list(r)) == 8
    r1 = difile.compare_dir(dir1.as_posix(), dir2.as_posix())
    assert len(list(r1)) == 8

    for f1, f2 in zip(r, r1):
        for l1, l2 in zip(f1, f2):
            assert l1.line_no == l2.line_no
            assert l1.code == l2.code


def test_code():
    r = difile.compare_file(file1, file2)
    assert r[0].code == LineCode.REMOVE
    assert r[1].code == LineCode.ADD


def test_cli():
    import subprocess

    subprocess.check_call(
        ["difile", "compare_file", file1.as_posix(), file2.as_posix()]
    )
    subprocess.check_call(["difile", "cf", file1.as_posix(), file2.as_posix()])
    subprocess.check_call(["difile", "compare_dir", dir1.as_posix(), dir2.as_posix()])
    subprocess.check_call(["difile", "cd", dir1.as_posix(), dir2.as_posix()])


def test_contain_all():
    r = difile.compare_file(file1, file2, contain_all=True)

    for each in r:
        if each.is_(LineCode.IGNORE):
            break
    else:
        raise AssertionError


def test_string():
    with open(file1) as f:
        s1 = f.read()
    with open(file2) as f:
        s2 = f.read()
    assert difile.compare_string(s1, s2, left_path=file1, right_path=file2)
    line_list = difile.string2line("abc", LineCode.ADD)
    assert isinstance(line_list, list)
    assert isinstance(line_list[0], Line)
    assert str(line_list[0])


def test_operator():
    r = difile.compare_dir(dir1, dir2)
    r1 = LineOperator.list2dict(r)
    assert isinstance(r1, dict)

    for each in r:
        for i in each:
            assert i.file_path.as_posix() in r1
