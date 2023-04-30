from jsonfinder import jsonfinder


def parse_json(text):
    res_jsonfinder = jsonfinder(text)
    res_json = []
    for res in res_jsonfinder:
        if res[2]:
            res_json.append(res[2])
    return res_json
