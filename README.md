# difile

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

compare files and get a line list:

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

## license

[MIT](LICENSE)
