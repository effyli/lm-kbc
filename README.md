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

## TODO list for the paper revision

Code review
- [x] Update README with instructions. [Effy]
- [x] Put the final prediction file in the root directory. [Effy]

Paper review
- [X] “Semantic Similarity Selector: It is unclear how this exactly was done and which model was used for the semantic similarity computation.”
- [x] “It would be helpful to refer to Fig. 1, while describing the methodology.”
- [x] “You mention hyperparameter tuning in the Figure, but never mention that again in text. Is this not done in the end?”
- [ ] “An ablation study for the Wikidata context would be interesting. Does this actually improve the results?”
- [x] “Why are the numbers for the 0-shot results identical to the other results for GPT-4? Maybe wrong results in the table?” [Anthony]
- [ ] “”““In our experiments, we observe that both demonstrated examples and additional knowledge of the entities play a crucial role in enhancing a model’s understanding and generation.” -I actually do not see this in the experiments. Would be helpful to connect this conclusion to the actual results.”“”
- [x] "You could mention in abstract and/or intro that this submission scored 2nd best in track 2" [Effy]
- [x] "Abstract: Suggested citation format for the challenge (instead of footnote): @article{lmkbc2023, title={LM-KBC: Knowledge base construction from pre-trained language models, Semantic Web Challenge @ ISWC}, author={Singhania, Sneha and Kalo, Jan-Christoph and Razniewski, Simon and Pan, Jeff Z.}, journal={CEUR-WS}, url={https://lm-kbc.github.io/challenge2023/}, year={2023} }"
- [x] "Abstract: "background KB" confused me initially, e.g., whether a new background KB is constructed. Perhaps more specific would be "constraints and descriptions of the relations"?"
- [x] "Last paragraph of Section 1: Odd tense change within first 2 sentences."
- [x] "Related work: "As one of their ablations, they also ..." (and following sentence) - not well comprehensible, maybe expand?"
- [x] "3.1 "wikidata identifies" -> "Wikidata identifiers"" [Effy]
- [x] "Figure 1 is nice. What would be even greater though, would be a walk-through with concrete examples."
- [ ] "4.1 third paragraph: An illustration of an example prompt, with highlight for the different conceptual parts, would much improve readibility."
- [ ] "4.2.2 last two sentences: I don't understand well - what does the number of relation matter for variation? Isn't variation inside on relation enough (e.g., very different object set sizes, and values)?"
- [ ] "4.3: I found the title slightly confusing (expecting something more general than happened). It seems what really happens is that more information on the properties is provided (and not on the subject, as the AT&T example made me at first believe)."
- [x] ""it's" - style (2x in paper)" [Effy]
- [ ] ""the prompt is available in Github" - I'd suggest to add it to the paper to make it more self-contained"
- [x] ""by finding related information to the given subject" - should it be "...given relation"?"
- [ ] "What is the significance of 4.4? How much performance does it add?"
- [ ] "Section 6: "The findings for our study shed light on how ..." - without numbers reporting the significance of post-processing, so far no light is shed on that part. Table 1 would also benefit from a baseline (e.g., the examples from the provided baselines?)"
- [ ] "2nd paragraph: It seems the authors wanted to provide context also for entities, not just relations, but time prevented them from doing so? Would be helpful to say whether anything was tested in that direction."
- [ ] "2nd paragraph: As this is put forward, why do more relevant examples actually help, compared with random examples (do they?)?"
- [ ] "3rd paragraph: How big an issue is that?"
- [ ] "Last paragraph: How big an issue is that in this challenge?"
- [x] "Section 7: "...when asked about specific relations" - could not understand this point."



## Authors (in alphabetical order)
- [Fajar J. Ekaputra](https://juang.id/)
- [Paul Groth](https://pgroth.com/)
- [Anthony Hughes](https://www.linkedin.com/in/anthonyyhughes/)
- [Majlinda Llugiqi](https://www.wu.ac.at/en/dpkm/team/majlinda-llugiqi/)
- [(Effy) Xue Li](https://effyli.github.io/)
- [Fina Polat](https://www.linkedin.com/in/finapolat/)


