from difile import Difile, LineCode
import pathlib


difile = Difile()
dir1 = pathlib.Path("dirs/dir1")
dir2 = pathlib.Path("dirs/dir2")
file1 = dir1 / "file1.txt"
file2 = dir2 / "file1.txt"


def test_compare_file():
    r = difile.compare_file(file1, file2)
    assert len(list(r)) == 6
    r1 = difile.compare_file(file1.as_posix(), file2.as_posix())
    assert len(list(r1)) == 6

    for l1, l2 in zip(r, r1):
        assert l1.line_no == l2.line_no
        assert l1.code == l2.code


def test_compare_dir():
    r = difile.compare_dir(dir1, dir2)
    assert len(list(r)) == 2
    assert len(list(r[0])) == 6
    r1 = difile.compare_dir(dir1.as_posix(), dir2.as_posix())
    assert len(list(r1)) == 2
    assert len(list(r1[0])) == 6

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
    subprocess.check_call(["difile", "compare_file", file1.as_posix(), file2.as_posix()])
    subprocess.check_call(["difile", "cf", file1.as_posix(), file2.as_posix()])
    subprocess.check_call(["difile", "compare_dir", dir1.as_posix(), dir2.as_posix()])
    subprocess.check_call(["difile", "cd", dir1.as_posix(), dir2.as_posix()])
