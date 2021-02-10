import os
import shutil

CODE_FOLDER = "../code"


def make_code_zip(directory='output'):
    zip_file=f"{CODE_FOLDER}.zip"
    if os.path.exists(directory):
        shutil.rmtree(directory)
    if os.path.exists(CODE_FOLDER):
        shutil.rmtree(CODE_FOLDER)
    if os.path.exists(zip_file):
        os.remove(zip_file)
    shutil.copytree("./", CODE_FOLDER)
    os.remove(f"{CODE_FOLDER}/problem_statement.pdf")
    shutil.make_archive(CODE_FOLDER, 'zip', "./")
    shutil.rmtree(CODE_FOLDER)
    os.makedirs(directory)
    shutil.move(zip_file, directory)
