import hashlib
import os
import shutil
import string

import pandas as pd

INPUT_FOLDER = 'input'
CODE_FOLDER = "code"
INTERMEDIATE_FOLDER = 'intermediate'
OUTPUT_FOLDER = 'output'


def make_code_zip(directory='output'):
    zip_file = f"{CODE_FOLDER}.zip"
    if os.path.exists(directory):
        shutil.rmtree(directory)
    if os.path.exists(CODE_FOLDER):
        shutil.rmtree(CODE_FOLDER)
    if os.path.exists(zip_file):
        os.remove(zip_file)
    shutil.copytree("./", CODE_FOLDER)
    os.remove(f"{CODE_FOLDER}/problem_statement.pdf")
    if os.path.exists(f"{CODE_FOLDER}/{INPUT_FOLDER}"):
        shutil.rmtree(f"{CODE_FOLDER}/{INPUT_FOLDER}")
    if os.path.exists(f"{CODE_FOLDER}/{INTERMEDIATE_FOLDER}"):
        shutil.rmtree(f"{CODE_FOLDER}/{INTERMEDIATE_FOLDER}")
    if os.path.exists(f"{CODE_FOLDER}/__pycache__"):
        shutil.rmtree(f"{CODE_FOLDER}/__pycache__")

    shutil.make_archive(CODE_FOLDER, 'zip', CODE_FOLDER)
    shutil.rmtree(CODE_FOLDER)
    os.makedirs(directory)
    shutil.move(zip_file, directory)


def save_schedules_dataframe(problem_prefix, folder: string, points, df_schedules: pd.DataFrame):
    df_schedules.sort_values(by=["intersection_id"], ascending=[True], inplace=True)
    csv = df_schedules.to_csv().encode()
    hash = hashlib.sha1(csv).hexdigest()
    filename = f"{problem_prefix}_{hash.upper()}-{points}.pickle"
    new_file = False
    if not os.path.exists(f'{folder}/{filename}'):
        df_schedules.to_pickle(path=f'{folder}/{filename}')
        new_file = True
    return filename, points, new_file



def load_schedules(filename):
    df_schedules = pd.read_pickle(filename)
    return df_schedules
