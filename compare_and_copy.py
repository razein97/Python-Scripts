import os
from pathlib import Path
import shutil


def start(dir1, dir2):
    dir1_dict = {}
    dir2_dict = {}

    dir1_files = os.listdir(dir1)
    dir2_files = os.listdir(dir2)

    for file in dir1_files:
        size = Path(dir1 + file).stat().st_size
        dir1_dict[file] = [dir1 + file, size]
    print(dir1_dict)

    for file in dir2_files:
        size = Path(dir2 + file).stat().st_size
        dir2_dict[file] = [dir2 + file, size]
    print(dir2_dict['Schedule 1-The National Food Security Act, 2013.pdf'][0])

    os.makedirs('./' + "New", exist_ok=True)

    for file in dir1_files:
        if dir1_dict[file][1] < dir2_dict[file][1]:
            shutil.copy(dir1_dict[file][0], './New/')
        elif dir2_dict[file][1] < dir1_dict[file][1]:
            shutil.copy(dir2_dict[file][0], './New/')
        else:
            shutil.copy(dir2_dict[file][0], './New/')


if __name__ == '__main__':
    # directory_1 = str(input("Enter First Directory:"))
    # directory_2 = str(input("Enter Second Directory:"))
    directory_1 = '/run/media/razein/internal_hdd/Projects/Python Projects/Scripts/Compressed/'
    directory_2 = '/run/media/razein/internal_hdd/Projects/Python Projects/Scripts/Schedules/'
    start(directory_1, directory_2)
