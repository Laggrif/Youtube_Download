import json
from src.Directory import application_path
from os.path import join

with open(join(application_path, "res", "style.qss"), "r") as f:
    style = f.read()

with open(join(application_path, "res", "colors.json"), "r") as f:
    colors = json.load(f)

for color, value in colors.items():
    style = style.replace(color, value)


def get_style():
    return style
