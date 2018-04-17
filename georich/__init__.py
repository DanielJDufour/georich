from .api.scripts.enrich import run as enrich
from subprocess import call

def run_server():
    #from django.core.management import execute_from_command_line
    #import os
    #import sys
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "georich.core.settings")
    #execute_from_command_line(["manage.py", "runserver"])
    from os.path import dirname, realpath
    dir_path = dirname(realpath(__file__))
    print("dir_path", dir_path)
    call("python3 manage.py runserver", cwd=dir_path, shell=True)
