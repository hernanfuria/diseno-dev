from os import mkdir
from os.path import join, isdir
from src.env import ASSETS_PATH, QGZ_PATH, SHP_PATH, VENVS_PATH


def create_dirs():
    if not isdir(ASSETS_PATH):
        mkdir(ASSETS_PATH)
        print(f"{ASSETS_PATH} \033[32mcreated\033[0m")

    if not isdir(QGZ_PATH):
        mkdir(QGZ_PATH)
        print(f"{QGZ_PATH} \033[32mcreated\033[0m")

    if not isdir(SHP_PATH):
        mkdir(SHP_PATH)
        print(f"{SHP_PATH} \033[32mcreated\033[0m")

    if not isdir(VENVS_PATH):
        mkdir(VENVS_PATH)
        print(f"{VENVS_PATH} \033[32mcreated\033[0m")