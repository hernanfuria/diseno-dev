from os.path import join
from os import getcwd

# PATHS
ROOT_PATH = getcwd()

ASSETS_PATH = join(ROOT_PATH, 'assets')
QGZ_PATH = join(ASSETS_PATH, 'QGZ')
SHP_PATH = join(ASSETS_PATH, 'SHP')

VENVS_PATH = join(ROOT_PATH, 'venvs')

# PARAMETERS
LOGGER_CLIO = True  # logger cli output enabled
