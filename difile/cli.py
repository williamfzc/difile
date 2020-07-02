from difile import Difile
import fire


class Cli(object):
    d = Difile()

    def compare_file(self, left, right):
        for each in self.d.compare_file(left, right):
            print(each)

    def compare_dir(self, left, right):
        for each_file in self.d.compare_dir(left, right):
            for each_line in each_file:
                print(each_line)

    cf = compare_file
    cd = compare_dir


def main():
    fire.Fire(Cli)
