import json

def load_from_json(json_file):
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def formated_response(object):
    return json.dumps(object), 200, {'Content-Type': 'application/json; charset:  utf-8'}







