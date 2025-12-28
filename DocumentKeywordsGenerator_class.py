from ai_agent_utils import initialize_agent, print_agent_usage

JSON_FORMAT = """
[
    {
        "word": "keyword1",
        "matching": 0.95
    },
    {
        "word": "keyword2",
        "matching": 0.90
    }
]
"""


class DocumentKeywordsGenerator:
    def __init__(self):
        self._agent = initialize_agent()

    def generate_keywords(self, document: str) -> str:
        """
        Generate a list of keywords from the document.

        Args:
            document: The document to generate keywords from
        Returns:
            A string of the JSON format of the keywords
        """

        result_agent = self._agent(
            f"""You are a helpful assistant that generates list of keywords from the document. Your expertise is in security and ISO 27001 compliance.
                You are given a document and you need to generate a list of keywords that are relevant to the document.    
                The list will be used to assing appriopriate controls to the document.
                The list you will return will be in JSON format.
                The JSON format will be like thi
                {JSON_FORMAT}
                The keywords should be one word keywords. THe percentage matching should be a number between 0 and 1. 
                The percentage is your serteninty how keyword matches the document.
                Return up to 50 keywords but focus on the relevant keywords to security and ISO 27001 compliance and ommit general keywords.
                Do not repeat keywords.

                Return the JSON format only, no other text.
            
            Generate a list of keywords from the following document:
            The document is:
            {document}"""
        )
        # keywords is an AgentResult object and I need it as a text
        # message is a TypedDict, so access it as a dictionary
        # Use the __str__ method which properly extracts text from content blocks
        pure_agent_response = str(result_agent).strip()
        # response is a json string but I want only content of the json without the ```json and ```
        pure_agent_response = pure_agent_response.replace("```json", "").replace(
            "```", ""
        )
        # convert the json string to a dictionary
        return pure_agent_response

    def print_agent_usage(self):
        print_agent_usage(self.agent)
