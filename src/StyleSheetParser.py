import json

with open("res/style.qss", "r") as f:
    style = f.read()

with open("res/colors.json", "r") as f:
    colors = json.load(f)

for color, value in colors.items():
    style = style.replace(color, value)


def get_style():
    return style
