import re
import json

predictions = []
bracket_pattern = r"\[(.*?)\]"

with(open('validation_results_LLM_ChatGPT.txt')) as f:
  lines = f.readlines()
  for line in lines:
    line = line.strip()
    object_str = re.search(bracket_pattern, line)
    if line == '' or\
     line.startswith('Predicate:') or\
      '???' in line or\
       line.startswith("[") or\
       object_str is None:
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

with(open('predictions.json', 'w')) as out_f:
  json.dump(predictions, out_f)