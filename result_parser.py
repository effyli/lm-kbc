import re
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

def parse_predictions_recent_format() -> list:
    file = "src/extractions/extraction_prompt_langchain_time_08-08-2023-16:35:03.txt"
    results = []
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line:
                result_line = []
                if '[' in line:
                    result_str = line.split('[')[1]
                    if ']' in result_str:
                        result_str = result_str.split(']')[0]
                    result_str_list = list(result_str.split(','))
                    for obj in result_str_list:
                        result_line.append(obj.strip().strip("'").strip())
                elif line == '['']':
                    result_line = []
                else:
                    result_line = []
            results.append(result_line)
    print(len(results))
    return results


def store_predictions(predictions: list) -> None:
    # store predictions
    with open("predictions.json", "w") as out_f:
        json.dump(predictions, out_f)


def align_pedictions_with_validation(predictions: list):
    # align predicitions with validationset
    with open("data/random_val_sample2.jsonl", "r") as f:
        validationset = f.readlines()

    all_results = list(zip(validationset, predictions))
    # print(all_results)

    # prep prediction for eval
    updated_predictions = []
    for x, ys in all_results[:400]:
        parsed_x = json.loads(x)
        wikidata_ids = []
        wikidata_cache = load_wikidata_cache() 
               
        for y in ys:
            if parsed_x["Relation"] == ( "PersonHasNumberOfChildren" or "SeriesHasNumberOfEpisodes" ):
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
                "ObjectEntitiesID": wikidata_ids,
            }
        )
    return updated_predictions


def save_predictions_for_eval(updated_predictions: list) -> None:
    # save
    with open("prediction-for-eval.jsonl", "w") as f:
        # pretty dump json
        for x in updated_predictions:
            f.write(json.dumps(x))
            f.write("\n")


if __name__ == "__main__":
    # predictions = parse_predictions()
    # TODO merge two different formats
    predictions = parse_predictions_recent_format()
    store_predictions(predictions)
    updated_predictions = align_pedictions_with_validation(predictions)
    save_predictions_for_eval(updated_predictions)
