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
    # if os.path.exists(f"{CODE_FOLDER}/{INPUT_FOLDER}"):
    #     shutil.rmtree(f"{CODE_FOLDER}/{INPUT_FOLDER}")
    if os.path.exists(f"{CODE_FOLDER}/{INTERMEDIATE_FOLDER}"):
        shutil.rmtree(f"{CODE_FOLDER}/{INTERMEDIATE_FOLDER}")
    if os.path.exists(f"{CODE_FOLDER}/__pycache__"):
        shutil.rmtree(f"{CODE_FOLDER}/__pycache__")

    shutil.make_archive(CODE_FOLDER, 'zip', CODE_FOLDER)
    shutil.rmtree(CODE_FOLDER)
    os.makedirs(directory)
    shutil.move(zip_file, directory)


def save_deliveries_dataframe(folder: string, df_deliveries: pd.DataFrame):
    df_deliveries.reset_index(inplace=True, drop=True)
    df_deliveries.sort_values(by=["value", "team_id", "pizza_ids_sum"], ascending=[False, True, True], inplace=True)
    df_deliveries.reset_index(inplace=True, drop=True)
    points = df_deliveries["value"].sum()
    hash = hashlib.sha1(df_deliveries.to_csv().encode()).hexdigest()
    filename = f"SOL_{hash.upper()}-{points}.pickle"
    df_deliveries.to_pickle(path=f'{folder}/{filename}')
    return filename, points


def load_deliveries(filename):
    df_deliveries = pd.read_pickle(filename)
    points = df_deliveries["value"].sum()
    return points, df_deliveries
