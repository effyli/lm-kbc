import jsonlines
import json
import argparse

from jsonmerge import merge

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # parser.add_argument('-d', '--directory', required=True, help="Directory where you store the data")
    parser.add_argument('-i', '--input_file', required=True, help="input data to be transformed")
    parser.add_argument('-o', '--output_file', required=True, help="output data location")
    parser.add_argument('-j', '--json_file', default="../data/wikigpt.json", help="output data location")

    args = parser.parse_args()

    # load arguments
    input_file = args.input_file
    output_file = args.output_file
    json_file = args.json_file

    wikigpt_json = dict()

    with open(json_file) as json_data:
        data = json.load(json_data)
        for key in data.keys():
            # print(data[key])
            wikigpt_json[key] = data[key]


    with jsonlines.open(input_file) as reader, jsonlines.open(output_file, mode='w') as writer:
        for obj in reader:
            tail = wikigpt_json[obj['Relation']]
            merged = merge(obj, tail)
            writer.write(merged)
            # print(merged)
            