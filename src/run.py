import os
import json
from tqdm import tqdm
import openai
import argparse
import logging

from retry import retry
from datetime import datetime
from prompt import REprompt
from example-selection import ExampleSelection

# os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
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
        #model="text-davinci-003",
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
    parser.add_argument('-o', '--output_directory', required=True, help="Directory where to store the extraction")
    parser.add_argument('-t', '--temperature', default=0, help="Temperature used for GPT model")
    parser.add_argument('-l', '--use_langchain', action='store_true', help="Boolean value to indicate whether to use langchain or not")

    args = parser.parse_args()

    # load arguments
    data_dir = args.directory
    output_dir = args.output_directory
    temperature = args.temperature
    use_langchain = args.use_langchain

    # set up loggings
    prompt_type = "langchain" if use_langchain else "manual"
    now = datetime.now()
    logging_file = "logging_prompt_{}_time_{}.log".format(prompt_type, now.strftime("%m-%d-%Y-%H:%M:%S"))
    logging.basicConfig(filename=logging_file, filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.warning('Start logging')
    
    # print("test-1")

    # output_file = "extraction_prompt_{}_time_{}.txt".format(prompt_type, now.strftime("%m-%d-%Y-%H:%M:%S"))
    output_file = "extraction_prompt_langchain_time_08-08-2023-16:35:03.txt"
    output_file_path = os.path.join(output_dir, output_file)

    # load data
    train_path = os.path.join(data_dir, 'train-output.jsonl')
    train_data = read_lm_kbc_jsonl(train_path)
    
    # print("test0")

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
            prompt_template = REprompt(use_langchain=use_langchain, examples=examples).template
    else:
        prompt_template = "custom"

    logging.warning("Prompt template created: {}".format(prompt_template))

    # load validation test
    val_path = os.path.join(data_dir, 'random_val_sample2-output.jsonl')
    val_data = read_lm_kbc_jsonl(val_path)

    logging.warning("Start prompting")
    logging.warning("Validation set size, {}".format(len(val_data)))
    logging_data_level = 10
    # prompting the validation set
    extraction_output = []

    # print("test1")

    # streaming save while prompting
    for i, line in tqdm(enumerate(val_data)):
        print("{} samples processed, {} left. {} % processed".format(i, len(val_data) - i, (i/(len(val_data) - i)) * 100))
        if i % logging_data_level == 0:
            logging.warning("{} samples prompt, {} left".format(i, len(val_data) - i))
        
        input_sbj = line['SubjectEntity']
        input_relation = line['Relation']
        # print(line)
        
        wiki_relation_label = line['wikidata_label']
        # wiki_relation_domain = line['domain']
        # wiki_relation_range = line['range']
        # wiki_relation_explanation = line['explanation']


        if use_langchain:
            prompt = prompt_template.format(entity_1=input_sbj, wiki_label=wiki_relation_label)
        else:
            # Set this param
            working_dir = "/path/to/working_directory"
            examples = ExampleSelection(working_dir)

            examples.load_data_stats(working_dir + "/data/data-stats.csv")

            list_examples = examples.get_examples(working_dir = working_dir, relation = input_relation, numberExamples = 5, fileName = 'Train')
            prompt = f""" Act like a knowledge engineer and can you give me the object for this subject {input_sbj} and relation {input_relation}. Here are some examples {list_examples}. Please give me the results in the same format as the examples"""

        # print(prompt)


        extraction = GPT3response(prompt, temperature=temperature)
        print(extraction)
        with open(output_file_path, 'a') as f:
            f.write(extraction)
            f.write("\n")

        extraction_output.append(extraction)
    logging.warning("Prompting finished")











