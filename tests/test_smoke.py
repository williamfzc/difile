from difile import Difile


difile = Difile()

def test_compare_file():
    r = difile.compare_file("dirs/dir1/file1.txt", "dirs/dir2/file1.txt")
    assert len(list(r)) == 6


def test_compare_dir():
    r = difile.compare_dir("dirs/dir1", "dirs/dir2")
    assert len(list(r)) == 2
    assert len(list(r[0])) == 6
