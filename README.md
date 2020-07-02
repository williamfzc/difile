# difile

![](https://github.com/williamfzc/difile/workflows/Python%20package/badge.svg)
[![codecov](https://codecov.io/gh/williamfzc/difile/branch/master/graph/badge.svg)](https://codecov.io/gh/williamfzc/difile)

lightweight diff-file library with difflib

## goal

- something like git-diff but without git
- programmable
- dirs and files

## installation

```bash
pip install difile
```

## usage

### command line

```bash
difile compare_file file1.txt file2.txt
difile compare_dir dir1 dir2
```

or a short name:

```bash
difile cf file1.txt file2.txt
difile cd dir1 dir2
```

### script

compare files and get a `List[Line]` object:

```python
from difile import Difile
difile = Difile()

diff_obj = difile.compare_file("dirs/dir1/file1.txt", "dirs/dir2/file1.txt")
```

and you can see what happened between files:

```python
for each in diff_obj:
    print(each.line_no, each.code, each.file_path, each.content.strip())
```

get:

```text
1 -  tests/dirs/dir1/file1.txt no
1 +  tests/dirs/dir2/file1.txt difile
2 -  tests/dirs/dir1/file1.txt this is file1
2 +  tests/dirs/dir2/file1.txt that is file1
3 -  tests/dirs/dir1/file1.txt random
3 +  tests/dirs/dir2/file1.txt
4 -  tests/dirs/dir1/file1.txt aha
```

- line 1: `no` -> `difile`
- line 2: `this is file1` -> `that is file1`
- line 3: `random` -> enter
- line 4: has been removed

of course compare dirs:

```python
from difile import Difile
difile = Difile()

diff_obj = difile.compare_dir("dirs/dir1", "dirs/dir2")
```

you will get a `List[List[Line]]` object.

## license

[MIT](LICENSE)
