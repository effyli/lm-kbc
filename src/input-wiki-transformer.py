import jsonlines
import json

from jsonmerge import merge

json_file = '../data/wikigpt.json'
wikigpt_json = dict()

with open(json_file) as json_data:
    data = json.load(json_data)
    for key in data.keys():
        # print(data[key])
        wikigpt_json[key] = data[key]


with jsonlines.open('../data/random_val_sample2.jsonl') as reader, jsonlines.open('../data/random_val_sample2-output.jsonl', mode='w') as writer:
     for obj in reader:
         tail = wikigpt_json[obj['Relation']]
         merged = merge(obj, tail)
         # print(merged)
         writer.write(merged)
        