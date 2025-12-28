# generate list of keywords from the document using AI agent

import logging
import os
from DocumentKeywordsGenerator_class import DocumentKeywordsGenerator


def read_document_from_file(document_name: str) -> str:
    """
    Read the document from the documents
    Args:
        document_name: The name of the document (filename with path)
    Returns:
        The document as a string
    """
    try:
        with open(f"{document_name}", "r") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error reading document from file: {e}", exc_info=True)
        raise e


def save_keywords_to_file(keywords_str: str, document_name: str) -> None:
    """
    Save the keywords to a file.
    Args:
        keywords_str: The keywords to save in JSON format (as string)
        document_name: The name of the document (filename with path)
    """
    try:
        logging.debug(f"Saving keywords to file: {document_name}")
        logging.debug(f"Keywords: {keywords_str}")
        with open(f"{document_name}", "w") as file:
            file.write(keywords_str)
    except Exception as e:
        logging.error(f"Error saving keywords to file: {e}", exc_info=True)
        raise e


def process_document(document_name: str, doc_folder: str, keywords_folder: str) -> None:
    """
    Process a document and generate keywords.
    Args:
        document_name: The name of the document (filename with path)
        doc_folder: The folder containing the documents
        keywords_folder: The folder containing the keywords
    """
    document = read_document_from_file(f"{doc_folder}/{document_name}")
    keywords_generator = DocumentKeywordsGenerator()
    keywords = keywords_generator.generate_keywords(document)
    save_keywords_to_file(keywords, f"{keywords_folder}/{document_name}.json")


if __name__ == "__main__":
    # filename = "149520415.md"
    doc_folder = "documents"
    keywords_folder = "documents_keywords"

    # process_document(filename, doc_folder, keywords_folder)

    # list all files in the doc_folder
    files = os.listdir(doc_folder)
    for file in files:
        process_document(file, doc_folder, keywords_folder)
