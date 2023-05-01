import json
import re


def split_json_objects(text: str):
    pattern = re.compile(r"```json\s+({.*?})\s+```", re.DOTALL)
    return pattern.findall(text)


def parse_json(text: str):
    json_objects_str = split_json_objects(text)
    json_list = [json.loads(json_object_str) for json_object_str in json_objects_str]

    return json_list
