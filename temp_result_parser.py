import json
import requests


# Disambiguation baseline
def disambiguation_baseline(item):
    try:
        # If item can be converted to an integer, return it directly
        return int(item)
    except ValueError:
        # If not, proceed with the Wikidata search
        try:
            url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={item}&language=en&format=json"
            data = requests.get(url).json()
            # Return the first id (Could upgrade this in the future)
            return data['search'][0]['id']
        except:
            return ""


if __name__ == '__main__':
    file = "extractions/extraction_prompt_langchain_time_08-08-2023-16:35:03.txt"
    results = []
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line:
                result_line = []
                if '[' in line:
                    result_str = line.split('[')[1]
                    if ']' in line:
                        result_str = line.split(']')[0]
                    result_str_list = list(result_str.split(','))
                    for obj in result_str_list:
                        result_line.append(obj.strip().strip("'").strip())
                elif line == '['']':
                    result_line = []
                else:
                    result_line = []
            results.append(result_line)
    with(open('predictions_val_100.json', 'w')) as out_f:
        json.dump(results, out_f)

    # align predicitions with validationset
    with open("data/val.jsonl", "r") as f:
        validationset = f.readlines()

    all_results = list(zip(validationset, results))

    # prep prediction for eval
    updated_predictions = []
    for x, ys in all_results:
        parsed_x = json.loads(x)
        wikidata_ids = []
        wikidata_ids = [disambiguation_baseline(y) for y in ys]
        updated_predictions.append(
            {
                "SubjectEntity": parsed_x["SubjectEntity"],
                "Relation": parsed_x["Relation"],
                "ObjectEntitiesID": wikidata_ids,
            }
        )

    # save
    with open("prediction-for-eval.jsonl", "w") as f:
        # pretty dump json
        for x in updated_predictions:
            f.write(json.dumps(x))
            f.write("\n")
