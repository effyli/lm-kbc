from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain import PromptTemplate, FewShotPromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain import LLMChain


class REprompt:
    def __init__(self, use_langchain=True, examples=None):
        self.use_langchain = use_langchain

        if self.use_langchain:
            self.template = self.generate_langchain_template(examples)

    def generate_langchain_template(self, examples):
        # calling the embeddings
        openai_embeddings = OpenAIEmbeddings()

        # We use the `PromptTemplate` class for this.
        example_formatter_template = """
            Subject: {entity_1} => Predicate: {relation} => Object: {target_entities}
            """
        example_prompt = PromptTemplate(
            input_variables=["entity_1", "relation", "target_entities"],
            template=example_formatter_template,
        )
        # test_prompt1 = example_prompt.format(entity_1='Siemens-Schuckert', relation='CompanyHasParentOrganisation',
        #                                      target_entities='Siemens')
        # print(test_prompt1)

        example_selector = SemanticSimilarityExampleSelector.from_examples(
            # This is the list of examples available to select from.
            examples,
            # This is the embedding class used to produce embeddings which are used to measure semantic similarity.
            openai_embeddings,
            # This is the VectorStore class that is used to store the embeddings and do a similarity search over.
            Chroma,
            # This is the number of examples to produce.
            k=2
        )

        few_shot_prompt_template = FewShotPromptTemplate(
            # These are the examples we want to insert into the prompt.
            example_selector=example_selector,
            # This is how we want to format the examples when we insert them into the prompt.
            example_prompt=example_prompt,
            # The prefix is some text that goes before the examples in the prompt.
            # Usually, this consists of intructions.
            prefix="""Generate objects holding the relation with the given subject.
                Here are some examples: """,
            # The suffix is some text that goes after the examples in the prompt.
            # Usually, this is where the user input will go
            suffix="""End of the examples. Now it is your turn to generate.
                Subject: {entity_1} => Predicate: {relation} => Objects: ??? """,
            # The input variables are the variables that the overall prompt expects.
            input_variables=["entity_1", "relation"],
            # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
            example_separator="\n",
        )
        return few_shot_prompt_template

