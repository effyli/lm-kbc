import os
import json
from tqdm import tqdm
import openai
import argparse
import logging

from retry import retry
from datetime import datetime
from prompt import REprompt
from compile_prompt import generate_prompt
from example_selection import ExampleSelection


os.environ["OPENAI_API_KEY"] = "sk-"
openai.api_key = os.environ["OPENAI_API_KEY"]


# Read jsonl file containing LM-KBC data
def read_lm_kbc_jsonl(file_path: str):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


# Get an answer from the GPT-API
@retry(tries=3, delay=5, max_delay=25)
def GPT3response(q, temperature, model="gpt-3.5-turbo", max_tokens=500):
    response = openai.ChatCompletion.create(
        # curie is factor of 10 cheaper than davinci, but correspondingly less performant
        # model="text-davinci-003",
        model=model,
        messages=[{"role": "assistant", "content": q}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    response = response.choices[0]["message"]["content"]
    # replace following codes to post_processing
    # response = response.splitlines()[0]
    # if len(response)>0:
    #     if response[0] == " ":
    #         response = response[1:]
    # print("Answer is \"" + response + "\"\n")
    # try:
    #     response = ast.literal_eval(response)
    # except:
    #     response = []
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--directory', required=True, help="Directory where you store the data")
    parser.add_argument('-f', '--file_to_prompt', required=True, help="File that contains data to prompt, can be test.jsonl or val.jsonl")
    parser.add_argument('-o', '--output_directory', required=True, help="Directory where to store the extraction")
    parser.add_argument('-t', '--temperature', default=0, help="Temperature used for GPT model")
    parser.add_argument('-l', '--use_langchain', default=False, help="Boolean value to indicate whether to use langchain or not")
    parser.add_argument('-m', '--model', default='gpt-3.5-turbo', help="The target OpenAI model to use")
    parser.add_argument('-c', '--continue_previous', default=False, help="Boolean value to indicate whether to replace or append the results")
    parser.add_argument('-r', '--last_row', default=0, help="value to indicate the latest row processed in previous run")

    args = parser.parse_args()

    # load arguments
    data_dir = args.directory
    output_dir = args.output_directory
    temperature = args.temperature
    use_langchain = args.use_langchain
    model = args.model
    print('Target model', model)
    print(use_langchain)
    continue_previous = args.continue_previous
    last_row_in_previous_run = args.last_row

    # set up loggings
    prompt_type = "langchain" if use_langchain else "manual"
    now = datetime.now()
    logging_file = "logging_prompt_{}_time_{}.log".format(prompt_type, now.strftime("%m-%d-%Y-%H:%M:%S"))
    logging.basicConfig(filename=logging_file, filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.warning('Start logging')

    # print("test-1")

    # output_file = "extraction_prompt_{}_time_{}.jsonl".format(prompt_type, now.strftime("%m-%d-%Y-%H:%M:%S"))
    output_file = "extractions.jsonl"
    output_file_path = os.path.join(output_dir, output_file)

    # load data
    train_path = os.path.join(data_dir, 'train-output.jsonl')
    train_data = read_lm_kbc_jsonl(train_path)

    # print("test0")

    prompt_template = ""
    if use_langchain:
        # use all training examples to select "shots" from
        examples = []
        for line in train_data:
            subject = line['SubjectEntity']
            relation = line['Relation']
            objects = str(line['ObjectEntities'])

            instance_dict = dict()

            instance_dict['entity_1'] = subject
            # instance_dict['relation'] = relation
            instance_dict['target_entities'] = objects

            instance_dict['wiki_label'] = line['wikidata_label']
            # instance_dict['domain'] = line['domain']
            # instance_dict['range'] = line['range']
            # instance_dict['exp'] = line['explanation']

            examples.append(instance_dict)

        # build the template
        # prompt_template = REprompt(use_langchain=use_langchain, examples=examples).template
        prompt_template = ""
        logging.warning("Prompt template created: {}".format(prompt_template))

    # load validation test
    val_file = args.file_to_prompt
    val_path = os.path.join(data_dir, val_file)
    val_data = read_lm_kbc_jsonl(val_path)
    print("length of val dataset {}".format(len(val_data)))

    logging.warning("Start prompting")
    logging.warning("Validation set size, {}".format(len(val_data)))
    # prompting the validation set
    extraction_output = []

    # clean file before prompting if not continuing from previous one
    if not continue_previous:
        open(output_file_path, 'w').close()

    # streaming save while prompting
    for i, line in tqdm(enumerate(val_data)):
        input_sbj = line['SubjectEntity']
        input_sbj_id = line['SubjectEntityID']
        input_relation = line['Relation']
        # print(line)

        wiki_relation_id = line['wikidata_id']
        wiki_relation_label = line['wikidata_label']
        wiki_relation_domain = line['domain']
        wiki_relation_range = line['range']
        wiki_relation_explanation = line['explanation']

        prompt = ""
        
        if use_langchain:
            # prompt = prompt_template.format(entity_1=input_sbj, wiki_label=wiki_relation_label)
            prompt = generate_prompt(subj=input_sbj, rel=input_relation)
            # print(prompt)
        else:
            # Set this param
            examples = ExampleSelection()
            trainingDataPath = os.path.join(data_dir,"train-output.jsonl")
            dataStatsPath = os.path.join(data_dir,"data-stats.csv")
            examples.load_data_stats(dataStatsPath)
            range_data = examples.range_data

            # get_examples(self, relationString, numberExamples, set_type, training_file, range_data):
            list_examples = examples.get_examples(input_relation, 5, 'Train', trainingDataPath, range_data)
            min_val, max_val = range_data[input_relation]['Train']
            # print(len(list_examples))
            # print(list_examples)

            prefix = """
            Imagine you are emulating Wikidata’s knowledge. 
            Your task is to predict objects based on the given subject and relation. 
            Below are some examples for your reference: """
            example_formatter_template = """
                Example:
                - Subject: (‘{}’,‘{}’)
                - Subject Type: ‘{}’
                - Object Type: ‘{}’
                - Relation: ‘{}’
                - Relation Wikidata ID: '{}'
                - Relation Label (Wikidata): ‘{}’
                - Relation Explanation (Wikidata): ‘{}’
                ==> 
                Target entities: {} 
                """
            suffix = """
            End of examples. Now, it’s your turn. Please only give correct answers.
            The answers shall not contain duplicates and the number of answers shall be between {} to {}. :
            - Given Subject: (‘{}’,‘{}’)
            - Subject Type: ‘{}’
            - Object Type: ‘{}’
            - Relation: ‘{}’
            - Relation Wikidata ID: '{}'
            - Relation Label (Wikidata): ‘{}’
            - Relation Explanation (Wikidata): ‘{}’
            ==> 
            Predicted Objects:
                """
            # The input variables are the variables that the overall prompt expects.
            input_variables=["entity_1", "wiki_label"]
            # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
            example_separator="\n"

            prompt = ""
            prompt += prefix
            prompt += example_separator
            for example in list_examples:
                prompt += example_formatter_template.format(example['SubjectEntity'],
                                                            example['SubjectEntityID'],
                                                            example['domain'],
                                                            example['range'],
                                                            example['Relation'], 
                                                            example['wikidata_id'], 
                                                            example['wikidata_label'],
                                                            example['explanation'], 
                                                            example['ObjectEntities'])
                # prompt += example_separator
            prompt += suffix.format(min_val, 
                                    max_val,
                                    input_sbj, 
                                    input_sbj_id, 
                                    wiki_relation_domain,
                                    wiki_relation_range,
                                    input_relation,
                                    wiki_relation_id,
                                    wiki_relation_label,
                                    wiki_relation_explanation)
            # print(prompt)

            # prefix = """Generate objects holding the relation with the given subject.
            #     Here are some examples: """
            # example_formatter_template = """
            #     Subject: {} => Predicate: '{}' => Object: {}
            #     """
            # suffix = """End of the examples. Now it is your turn to generate. Note that I only expect a set of string Objects as results without duplicates.
            #     Subject: {} => Predicate: '{}' => Objects: ??? """
            # # The input variables are the variables that the overall prompt expects.
            # input_variables=["entity_1", "wiki_label"]
            # # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
            # example_separator="\n"

            # prompt = ""
            # prompt += prefix
            # prompt += example_separator
            # for example in list_examples:
            #     prompt += example_formatter_template.format(example['SubjectEntity'], example['wikidata_label'], example['ObjectEntities'])
            #     # prompt += example_separator
            # prompt += suffix.format(input_sbj, wiki_relation_label)


            # prompt = f""" 
            #     Act like a knowledge engineer and can you give me the object for this subject '{input_sbj}' and relation '{wiki_relation_label}'. 
            #     Here are some examples {list_examples}. 
            #     Please give me the results as list of ObjectEntities"""
            # print(prompt)    

        # print(prompt)

        if continue_previous and i <= int(last_row_in_previous_run):
            print("skipping line-{i}")
            # do nothing
        else:
            extraction = GPT3response(prompt, temperature=temperature, model=model)
            # save in a dictionary
            line["Prediction"] = extraction
            print("[{}][{}]".format(input_sbj_id, input_sbj) + extraction)

            # Open the JSONLines file in append mode
            with open(output_file_path, 'a') as file:
                # Convert dictionary to JSON string and write to the file
                file.write(json.dumps(line) + '\n')

            extraction_output.append(line)
    logging.warning("Prompting finished")
    print(len(extraction_output))
