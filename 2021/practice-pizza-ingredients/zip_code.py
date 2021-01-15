import os
import shutil


def zip(directory='output/code'):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    shutil.make_archive("../code", 'zip', "./")
    os.makedirs(directory)
    shutil.move("../code.zip", directory)
