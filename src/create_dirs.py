from os import mkdir
from os.path import join, isdir
from src.env import ROOT_PATH, ASSETS_PATH, QGZ_PATH, SHP_PATH


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