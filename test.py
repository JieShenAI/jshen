from src.jshen.io.obj import dict2json, json2dict
import json

s = """
{
    "name": "唐",
    "age": 18
}
"""

print(json2dict(s))
print(dict2json(json2dict(s), 'test.json'))
