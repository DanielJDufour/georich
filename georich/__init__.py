from .api.scripts.enrich import run as enrich
from subprocess import call

def run_server():
    from os.path import dirname, realpath
    dir_path = dirname(realpath(__file__))
    call("python3 manage.py runserver", cwd=dir_path, shell=True)
