import re


class Parser:
    def __init__(self, infos):
        self.infos = infos

    def parse(self, string: str) -> str:
        for key, value in self.infos.items():
            if key in string and isinstance(value, str):
                string = string.replace('{' + key + '}', value)
        string = re.sub(r'\{.*?\}', '', string)
        return string
