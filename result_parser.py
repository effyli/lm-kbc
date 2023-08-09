import re
import os
import argparse
import json
from baseline import disambiguation_baseline
from src.wikidata_utils import load_wikidata_cache, update_wikidata_cache, wikidata_id_sort

BRACKET_PATTERN = r"\[(.*?)\]"


def parse_predictions() -> list:
    ###
    # Parse predictions from the saved file containing the results of the validation set
    ###
    predictions = []
    with open("validation_results_LLM_ChatGPT.txt") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            object_str = re.search(BRACKET_PATTERN, line)
            # ignore specific lines without
            if (
                line == ""
                or line.startswith("Predicate:")
                or "???" in line
                or line.startswith("[")
                or object_str is None
            ):
                # print('Skipping empty line')
                continue

            object_pattern = r"\[(.*?)\]"
            object_str = re.search(object_pattern, line)
            target = object_str.group(1)
            object_list = [lang.strip("' ") for lang in target.split(",")]
            # print('Targert line:', line)
            # print('Parsed regex', target)
            predictions.append(object_list)

    print(len(predictions))
    return predictions


# Read jsonl file containing LM-KBC data
def read_jsonl(file_path: str):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def parse_predictions_recent_format(file: str) -> list:
    data = read_jsonl(file)
    results = []

    for line in data:
        prediction = line["Prediction"]
        result_line = []
        if prediction:
            if '[' in prediction:
                result_str = prediction.split('[')[1]
                if ']' in result_str:
                    result_str = result_str.split(']')[0]
                result_str_list = list(result_str.split(','))
                for obj in result_str_list:
                    p_obj = obj.strip().strip("'").strip()
                    if p_obj not in result_line:
                        result_line.append(p_obj)
            results.append(result_line)
        else:
            results.append(result_line)
    print(results)
    print(len(results))
    return results


def store_predictions(predictions: list, pred_file: str = "predictions.json") -> None:
    # store predictions
    with open(pred_file, "w") as out_f:
        json.dump(predictions, out_f)


def align_pedictions_with_validation(predictions: list, original_file: str):
    # align predicitions with validationset
    with open(original_file, "r") as f:
        validationset = f.readlines()

    all_results = list(zip(validationset, predictions))
    # print(all_results)

    # prep prediction for eval
    updated_predictions = []
    for x, ys in all_results:
        parsed_x = json.loads(x)
        wikidata_ids = []
        wikidata_cache = load_wikidata_cache() 
               
        for y in ys:
            if parsed_x["Relation"] in [ "PersonHasNumberOfChildren" , "SeriesHasNumberOfEpisodes" ]:
                wikidata_ids.append(y)
            elif y in wikidata_cache:
                wikidata_ids.append(str(wikidata_cache[y]))
            else:   
                dismabiguated_wikidata_id = disambiguation_baseline(y)
                update_wikidata_cache(dismabiguated_wikidata_id, y)
                wikidata_ids.append(str(dismabiguated_wikidata_id))
        wikidata_ids = sorted(wikidata_ids, key=lambda x: wikidata_id_sort(x))
        updated_predictions.append(
            {
                "SubjectEntity": parsed_x["SubjectEntity"],
                "Relation": parsed_x["Relation"],
                "ObjectEntitiesString": ys,
                "ObjectEntitiesID": wikidata_ids,
            }
        )
    return updated_predictions


def save_predictions_for_eval(updated_predictions: list, out_file: str) -> None:
    # save
    with open(out_file, "w") as f:
        # pretty dump json
        for x in updated_predictions:
            f.write(json.dumps(x))
            f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--prediction_file', required=True, help="File that contains the predictions, in a jsonl format")
    parser.add_argument('-g', '--original_input_file', required=True, help="The original input file")
    parser.add_argument('-o', '--output_directory', required=True, help="Directory where to store parsed result")

    args = parser.parse_args()
    extraction_file = args.prediction_file
    original_file = args.original_input_file
    output_directory = args.output_directory
    # extraction_file = "extractions/extraction_prompt_langchain_time_08-09-2023-11:54:15.jsonl"

    # predictions = parse_predictions()
    # TODO merge two different formats
    predictions = parse_predictions_recent_format(extraction_file)
    store_predictions(predictions)
    updated_predictions = align_pedictions_with_validation(predictions, original_file)
    output_file_path = os.path.join(output_directory, "prediction-for-eval.jsonl")
    save_predictions_for_eval(updated_predictions, output_file_path)
