import re
from json import JSONDecoder


class CommaStripper(JSONDecoder):
    def decode(self, s, _w=None):
        s = re.sub(r",\s*(}|\])", r"\1", s)
        return super().decode(s)


def split_json_objects(text: str):
    pattern = re.compile(r"```json\s+({.*?})\s+```", re.DOTALL)
    return pattern.findall(text)


def parse_json(text: str):
    json_objects_str = split_json_objects(text)
    json_list = []
    for json_object_str in json_objects_str:
        decoded_object = CommaStripper().decode(json_object_str)
        for key in decoded_object:
            json_list.append(decoded_object[key])
    return json_list
