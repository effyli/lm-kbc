import re
import json
from baseline import disambiguation_baseline

predictions = []
bracket_pattern = r"\[(.*?)\]"

# parse predictions
with open("validation_results_LLM_ChatGPT.txt") as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        object_str = re.search(bracket_pattern, line)
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

# store predictions
with open("predictions.json", "w") as out_f:
    json.dump(predictions, out_f)

# align predicitions with validationset
with open("data/val.jsonl", "r") as f:
    validationset = f.readlines()

all_results = list(zip(validationset, predictions))

# prep prediction for eval
updated_predictions = []
for x, ys in all_results[0:100]:
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

