import platform
import os
import shutil

TARGET = "sgv"

def exec_command(command):
    if not os.system(command) == 0: exit(1)

system = platform.system().lower()

s = ';' if system == 'windows' else ':'

exec_command("python ../tests/main.py")
exec_command(f"pyinstaller -w --onefile --distpath ../dist/{system} --icon ../sgv/img/icon.ico --add-data '../sgv/style/style.qss{s}style' --add-data '../sgv/files/configs.conf{s}files' --add-data '../sgv/img/icon.ico{s}img' ../sgv/main.py")

os.remove("main.spec")

shutil.rmtree("./build/")