"""
This script corrects file names created according to montage with mistake.
One additional electrode was added to the montage file which does not exist,
resulting in one additional file in result folder after that electrode.

This script will rename files in folder with pattern *EXP* for subject 568.

Example:
    correct file: [A1, A2, A3, B1, B2, B3, C1, C2, ...]
    error file:   [A1, A2, A3, B1, B2, B3, B4, C1, C2, ...]

B4 is renamed to C1, C1 renamed to C2, etc.
"""

import os
import shutil
import glob
import re

SKIP_EXISTING_FILES = True


def generate_file_name(montage):
    file_name = []
    for tag, count in montage:
        file_name.extend([tag + str(i) for i in range(1, count + 1)])
    return file_name


def rename_directory(directory):
    directory_rename = directory.split('/')
    directory_rename[-2] = directory_rename[-2] + '_renamed'

    directory_rename = '/'.join(directory_rename)
    return directory_rename


def correct_file_name(file_directory, montage_correct, montage_error):

    file_name_correct = generate_file_name(montage_correct)
    file_name_error = generate_file_name(montage_error)

    sub_directories = glob.glob(file_directory + '*')
    for sub_dir in sub_directories:
        sub_dir_renamed = rename_directory(sub_dir)

        if not os.path.exists(sub_dir_renamed) and not re.search(r'\..*', sub_dir_renamed):
            os.makedirs(sub_dir_renamed)

        if re.match(r''+file_directory+'EXP*', sub_dir):
            for file_error, file_correct in zip(file_name_error, file_name_correct):
                if SKIP_EXISTING_FILES and os.path.exists(sub_dir_renamed + '/' + file_correct + '.ncs'):
                    continue

                if not os.path.exists(sub_dir + '/' + file_error + '.ncs'):
                    print(f'missing file: {sub_dir}/{file_error}.ncs')

                if file_error != file_correct:
                    print(f'rename: {file_error} to {file_correct} on dir: {sub_dir}')
                else:
                    print(f'copy: {file_error} to {file_correct} on dir: {sub_dir}')

                shutil.copyfile(f'{sub_dir} /{file_error}.ncs', f'{sub_dir_renamed}/{file_correct}.ncs')
        else:
            if os.path.isdir(sub_dir):
                shutil.copytree(sub_dir, sub_dir_renamed, dirs_exist_ok=True)
            else:
                shutil.copyfile(sub_dir, sub_dir_renamed)


if __name__ == '__main__':
    file_directory = r'/Users/xinniu/Library/CloudStorage/Box-Box/Vwani_Movie/568/'

    montage_error = [
        ['PZ', 1],
        ['RMH', 8],
        ['RA', 9],
        ['RAC', 8],
        ['ROF', 8],
        ['ROPRAI', 7],  # should be 6
        ['RpSMAa', 7],
        ['RpSMAp', 7],
        ['RMF', 8],
        ['LA', 9],
        ['LAH', 8],
        ['LAC', 9],
        ['LOF', 8],
        ['LAI', 7],
        ['LpSMA', 7],
    ]
    montage_correct = [
        ['PZ', 1],
        ['RMH', 8],
        ['RA', 9],
        ['RAC', 8],
        ['ROF', 8],
        ['ROPRAI', 6],
        ['RpSMAa', 7],
        ['RpSMAp', 7],
        ['RMF', 8],
        ['LA', 9],
        ['LAH', 8],
        ['LAC', 9],
        ['LOF', 8],
        ['LAI', 7],
        ['LpSMA', 7],
    ]

    correct_file_name(file_directory, montage_correct, montage_error)







