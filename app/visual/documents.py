from pathlib import Path
from typing import List, Optional
import re


class Document:
    """Model representing a document."""

    def __init__(self, id: str, name: str, content: str):
        """
        Initialize a Document object.

        Args:
            id: The document ID (e.g., "1205665906", "170098836")
            name: The document name (extracted from first heading)
            content: The full content of the document
        """
        self.id = id
        self.name = name
        self.content = content

    def __repr__(self):
        return f"Document(id='{self.id}', name='{self.name}')"


def load_documents(documents_dir: str) -> List[Document]:
    """
    Load all document files from the specified directory.

    Files are expected to be named with numeric IDs: "{id}.md"
    The document name is extracted from the first line of the file (markdown heading).

    Args:
        documents_dir: Path to the directory containing document files

    Returns:
        List of Document objects
    """
    documents = []
    documents_path = Path(documents_dir)

    if not documents_path.exists():
        raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

    # Pattern to match filenames with numeric IDs (e.g., "1205665906.md")
    pattern = re.compile(r"^(\d+)\.md$")

    # Iterate through all .md files in the directory
    for file_path in documents_path.glob("*.md"):
        filename = file_path.name
        match = pattern.match(filename)

        if match:
            document_id = match.group(1)

            # Read the file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract document name from the first line
                # The first line should be a markdown heading starting with #
                lines = content.split("\n")
                document_name = ""
                if lines:
                    first_line = lines[0].strip()
                    if first_line.startswith("#"):
                        # Remove the # and any leading/trailing whitespace
                        document_name = first_line.lstrip("#").strip()
                    else:
                        # If first line doesn't start with #, use it as-is
                        document_name = first_line

                # If no name found, use the document ID as fallback
                if not document_name:
                    document_name = document_id

                document = Document(id=document_id, name=document_name, content=content)
                documents.append(document)
            except Exception as e:
                print(f"Warning: Could not read file {filename}: {e}")
        else:
            print(
                f"Warning: Filename '{filename}' does not match expected pattern (numeric ID.md)"
            )

    # Sort documents by ID (as integer) for consistency
    documents.sort(key=lambda x: int(x.id))

    return documents


def get_document_by_id(
    documents: List[Document], document_id: str
) -> Optional[Document]:
    """
    Get a document by its ID.

    Args:
        documents: List of Document objects
        document_id: The ID to search for (e.g., "1205665906", "170098836")

    Returns:
        Document object if found, None otherwise
    """
    for document in documents:
        if document.id == document_id:
            return document
    return None
