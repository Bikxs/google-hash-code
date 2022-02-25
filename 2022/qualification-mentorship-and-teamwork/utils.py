import hashlib
import json
import os
import shutil
import string
from typing import Dict

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
    # os.remove(f"{CODE_FOLDER}/problem_statement.pdf")
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


def save_assignments_dict(problem_prefix, folder: string, points, assignments: Dict):
    json_d = json.dumps(assignments).encode()
    hash = hashlib.sha1(json_d).hexdigest()
    filename = f"{problem_prefix}_{hash.upper()}-{points}.json"
    new_file = False
    if not os.path.exists(f'{folder}/{filename}'):
        with open(f'{folder}/{filename}', 'w') as fp:
            json.dump(assignments, fp)
        new_file = True
    return filename, points, new_file


def load_assignment(filename):
    # folder = "intermediate"
    with open(f'{filename}', 'r') as fp:
        assignments = json.load(fp)
    final_assignments = [assignment for  assignment in assignments if len(assignment[1])>=1]
    return final_assignments
