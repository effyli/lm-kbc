# Knowledge-centric Prompt Composition for Knowledge Base Construction from Pre-trained Language Models

This repository contains codes and instructions for the accepted system paper for the ISWC [LM-KBC challenge 2023](https://lm-kbc.github.io/challenge2023/).  
Our system's predictions ranked :trophy: **2nd** on the [leaderboard](https://codalab.lisn.upsaclay.fr/competitions/14777#results). Our team name is *thames*.

## Before started

Install the necessary prerequisites using the following command in the root directory before running the extraction pipeline. 

Make sure you are using a Python virtual environment. You can use environment management tools such as conda, venv, pyenv, etc.  

```
pip install -r requirements.txt
```


## Start extraction

To run the complete pipeline, simply run the following command:

```
cd src/
./run_pipeline.sh
```

Make sure the directories specified in the bash file exist in your local directory. 

You can also run each step in the pipeline separately. 
First modify input data with wikigpt information:

```
python input-wiki-transformer.py -i "../data/train.jsonl" -o "../data/train-output.jsonl"
```

Then run the pipeline by using the following command, you can specify which model to use:

```
python run.py -d "$data_dir" -f "$file_to_prompt" -o "$output_dir"  -m "gpt-4" -c "false"
```

Next parse the extraction file:

```
python ../result_parser.py -p "YOUR_EXTRACTION_FILE" -g "$gold_file" -o "OUTPUT_DIR"
```

In the end evaluate the final prediction and print out the performance.

```
python ../evaluate.py -p "YOUR_PREDICTION_FILE" -g "$GOLD_FILE"
```

## Authors (in alphabetical order)
- [Fajar J. Ekaputra](https://juang.id/)
- [Paul Groth](https://pgroth.com/)
- [Anthony Hughes](https://www.linkedin.com/in/anthonyyhughes/)
- [Majlinda Llugiqi](https://www.wu.ac.at/en/dpkm/team/majlinda-llugiqi/)
- [(Effy) Xue Li](https://effyli.github.io/)
- [Fina Polat](https://www.linkedin.com/in/finapolat/)


