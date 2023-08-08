import random
import json

class ExampleSelection:
    def __init__(self, working_dir):
        self.working_dir = working_dir
        self.range_data = None

    def parse_range_data(self, dataset):
        lines = dataset.strip().split("\n")
        headers = lines[0].split(";")
        range_data = {}
        for line in lines[1:]:
            parts = line.split(";")
            relation = parts[0]
            range_data[relation] = {}
            for i, header in enumerate(headers[1:]):
                min_val, max_val = map(int, parts[i+1][1:-1].split(", "))
                range_data[relation][header] = (min_val, max_val)
        return range_data

    def get_relation_examples(relationString, numberExamples, jsonlFile, set_type, range_data):
        examples = []
        min_val, max_val = range_data[relationString][set_type]

        # Containers to keep track of seen examples and possible examples for each size
        seen_examples = set()
        possible_examples = {i: [] for i in range(min_val, max_val + 1)}

        with open(jsonlFile, 'r') as f:
            for line in f:
                data = json.loads(line.strip())
                # print(data["Relation"])
                if data["Relation"] == relationString and len(data["ObjectEntities"]) in range(min_val, max_val + 1):
                    possible_examples[len(data["ObjectEntities"])].append(data)

        # Select one example with minimum objects
        if possible_examples[min_val]:
            min_example = random.choice(possible_examples[min_val])
            examples.append(min_example)
            seen_examples.add(str(min_example))

        # Select one example with maximum objects
        if possible_examples[max_val]:
            max_example = random.choice(possible_examples[max_val])
            examples.append(max_example)
            seen_examples.add(str(max_example))

        # For the remaining examples
        remaining = numberExamples - len(examples)
        # all_sizes = list(range(min_val, max_val + 1))

        # Flatten all examples from the dictionary into a single list
        all_examples = [example for sublist in possible_examples.values() for example in sublist]

        while remaining > 0 and all_examples:
            chosen_example = random.choice(all_examples)

            # If the chosen example hasn't been seen before, add it to 'examples'
            if str(chosen_example) not in seen_examples:
                examples.append(chosen_example)
                seen_examples.add(str(chosen_example))
                remaining -= 1

            # Remove the chosen example from all_examples to prevent choosing it again
            all_examples.remove(chosen_example)

        return examples

    def load_data_stats(self, file_path):
        with open(file_path, 'r') as file:
            dataset = file.read()
        self.range_data = self.parse_range_data(dataset)

    def display_examples(self, relationString, numberExamples, set_type):
        jsonlFile = self.working_dir + "/data/val.jsonl"
        examples = self.get_relation_examples(relationString, numberExamples, jsonlFile, set_type)
        for item in examples:
            print(item)


# Usage:
working_dir = "YOUR_WORKING_DIRECTORY_PATH"
data = ExampleSelection(working_dir)
data.load_data_stats(working_dir + "/data/data-stats.csv")
data.display_examples("CompanyHasParentOrganisation", 5, "Val")
