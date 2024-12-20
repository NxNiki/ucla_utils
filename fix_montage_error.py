"""
This script corrects file names created according to montage with mistake.
One additional electrode was added to the montage file which does not exist,
resulting in one additional file in result folder after that electrode.

This script will rename files in folder with pattern *EXP* for subject 568.

Example:
    correct file: [A1, A2, A3, B1, B2, B3, C1, C2, ...]
    error file:   [A1, A2, A3, B1, B2, B3, B4, C1, C2, ...]

B4 is renamed to C1, C1 renamed to C2, etc.

This is outdated, see: https://github.com/NxNiki/nwbPipeline/tree/main/tools
"""

import os
import shutil
import glob
import re
import logging
import datetime

SKIP_EXISTING_FILES = True


def generate_file_name(montage):
    file_name = []
    for tag, count in montage:
        if count > 1:
            file_name.extend([tag + str(i) for i in range(1, count + 1)])
        else:
            file_name.extend([tag])
    return file_name


def rename_directory(directory):
    directory_rename = directory.split('/')
    directory_rename[-2] = directory_rename[-2] + '_renamed'

    directory_rename = '/'.join(directory_rename)
    return directory_rename


def correct_file_name(file_directory, montage_correct, montage_error):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    logging.basicConfig(
        filename=f'log_fix_montage_error_{current_datetime}.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    file_name_correct = generate_file_name(montage_correct)
    file_name_error = generate_file_name(montage_error)

    sub_directories = glob.glob(file_directory + '*')
    for sub_dir in sub_directories:
        sub_dir_renamed = rename_directory(sub_dir)

        # create directory if not exists and not a file (end with .xxx).
        if not os.path.exists(sub_dir_renamed) and not re.search(r'\..*', sub_dir_renamed):
            os.makedirs(sub_dir_renamed)

        if re.match(r''+file_directory+'EXP*', sub_dir):
            for file_error, file_correct in zip(file_name_error, file_name_correct):
                # skip file if already copied:
                if SKIP_EXISTING_FILES and os.path.exists(f'{sub_dir_renamed}/{file_correct}.ncs'):
                    continue

                file_error_full_path = glob.glob(f'{sub_dir}/{file_error}*')
                # skip if file does not exist in source:
                if len(file_error_full_path) == 0:
                    logging.info(f'missing file: {sub_dir}/{file_error}.ncs')
                    continue

                if len(file_error_full_path) > 1:
                    logging.warning(
                        f'multiple files found with pattern: {sub_dir}/{file_error}. '
                        f'Only first one is copied'
                    )
                file_error_full_path = file_error_full_path[0]
                try:
                    shutil.copyfile(file_error_full_path, f'{sub_dir_renamed}/{file_correct}.ncs')
                    if file_error != file_correct:
                        logging.info(
                            f'rename: {file_error_full_path} to '
                            f'{sub_dir_renamed}/{file_correct}.ncs on dir: {sub_dir}'
                        )
                    else:
                        logging.info(
                            f'copy: {file_error_full_path} to '
                            f'{sub_dir_renamed}/{file_correct}.ncs on dir: {sub_dir}'
                        )
                except OSError as e:
                    print(f'Error copying {file_error_full_path}: {e}')
                    logging.error(f'Error copying {file_error_full_path}: {e}')
        else:
            try:
                if os.path.isdir(sub_dir):
                    shutil.copytree(sub_dir, sub_dir_renamed, dirs_exist_ok=True)
                    logging.info(f'copy directory: {sub_dir} to {sub_dir_renamed}')
                else:
                    shutil.copyfile(sub_dir, sub_dir_renamed)
                    logging.info(f'copy file: {sub_dir} to {sub_dir_renamed}')
            except OSError as e:
                print(f'Error copying {sub_dir}: {e}')
                logging.error(f'Error copying {sub_dir}: {e}')


if __name__ == '__main__':
    file_directory = r'/Users/xinniu/Library/CloudStorage/Box-Box/Vwani_Movie/568/'
    
    # Putting 'PZ' at top so that files for this channel is not renamed.
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

