"""
Utility functions for document selection operations.
"""

import logging
import os
import re
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_control_file(control_path: str) -> str:
    """
    Read the control file content.

    Args:
        control_path: Path to the control file

    Returns:
        The control file content as a string

    Raises:
        FileNotFoundError: If the control file doesn't exist
        IOError: If there's an error reading the file
    """
    try:
        if not os.path.exists(control_path):
            raise FileNotFoundError(f"Control file not found: {control_path}")
        with open(control_path, "r", encoding="utf-8") as file:
            content = file.read()
        logger.info(f"Successfully read control file: {control_path}")
        return content
    except Exception as e:
        logger.error(f"Error reading control file {control_path}: {e}", exc_info=True)
        raise


def extract_document_metadata(document_content: str, filename: str) -> Dict[str, str]:
    """
    Extract metadata (title and URL) from a document.

    Args:
        document_content: The full content of the document
        filename: The filename of the document

    Returns:
        Dictionary with keys: filename, content, title, url
    """
    title = ""
    url = ""

    # Extract title from first line starting with #
    lines = document_content.split("\n")
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("# "):
            title = line_stripped[2:].strip()  # Remove "# " prefix
            break
        elif line_stripped.startswith("#"):
            title = line_stripped[1:].strip()  # Remove "#" prefix
            break

    # Extract URL from **Source URL:** line
    url_pattern = r"\*\*Source URL:\*\*\s*(https?://[^\s]+)"
    url_match = re.search(url_pattern, document_content)
    if url_match:
        url = url_match.group(1).strip()

    # If title is still empty, use filename without extension as fallback
    if not title:
        title = os.path.splitext(filename)[0]

    return {
        "filename": filename,
        "content": document_content,
        "title": title,
        "url": url,
    }


def read_all_documents(documents_dir: str) -> List[Dict[str, str]]:
    """
    Read all documents from the documents directory and extract metadata.

    Args:
        documents_dir: Path to the documents directory

    Returns:
        List of dictionaries, each containing document metadata:
        - filename: Document filename
        - content: Full document content
        - title: Document title
        - url: Confluence URL

    Raises:
        FileNotFoundError: If the documents directory doesn't exist
        IOError: If there's an error reading files
    """
    documents = []

    try:
        if not os.path.exists(documents_dir):
            raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

        if not os.path.isdir(documents_dir):
            raise ValueError(f"Path is not a directory: {documents_dir}")

        # Get all .md files in the directory
        files = [
            f
            for f in os.listdir(documents_dir)
            if f.endswith(".md") and os.path.isfile(os.path.join(documents_dir, f))
        ]

        if not files:
            logger.warning(f"No markdown files found in {documents_dir}")
            return documents

        logger.info(f"Found {len(files)} documents to process")

        for filename in files:
            file_path = os.path.join(documents_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                metadata = extract_document_metadata(content, filename)
                documents.append(metadata)
            except Exception as e:
                logger.warning(
                    f"Error reading document {filename}: {e}. Skipping.",
                    exc_info=True,
                )
                continue

        logger.info(f"Successfully processed {len(documents)} documents")
        return documents

    except Exception as e:
        logger.error(
            f"Error reading documents from {documents_dir}: {e}", exc_info=True
        )
        raise


def save_selected_documents(output_path: str, content: str) -> None:
    """
    Save the selected documents markdown output to a file.

    Args:
        output_path: Path where the output file should be saved
        content: The markdown content to save

    Raises:
        IOError: If there's an error writing the file
    """
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info(f"Successfully saved selected documents to: {output_path}")
    except Exception as e:
        logger.error(
            f"Error saving selected documents to {output_path}: {e}", exc_info=True
        )
        raise


def get_control_name_from_path(control_path: str) -> str:
    """
    Extract the control name from the control file path.

    Args:
        control_path: Path to the control file (e.g., "controls/5.18 Access rights.md")

    Returns:
        The control name (e.g., "5.18 Access rights")
    """
    filename = os.path.basename(control_path)
    # Remove .md extension
    control_name = os.path.splitext(filename)[0]
    return control_name
