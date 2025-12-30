from pathlib import Path
from typing import List, Set
import re

from documents import load_documents, Document


class SelectedControl:
    """Model representing a selected control with its relevant documents."""

    def __init__(self, id: str, name: str, relevant_document_ids: List[str]):
        """
        Initialize a SelectedControl object.

        Args:
            id: The control ID (e.g., "5.1", "8.2")
            name: The control name
            relevant_document_ids: List of document IDs relevant to this control
        """
        self.id = id
        self.name = name
        self.relevant_document_ids = relevant_document_ids

    def __repr__(self):
        return f"SelectedControl(id='{self.id}', name='{self.name}', documents={len(self.relevant_document_ids)})"


def extract_document_ids_from_content(
    content: str, available_document_ids: Set[str]
) -> List[str]:
    """
    Extract document IDs from Confluence URLs in the content.

    Args:
        content: The content string to search for document IDs
        available_document_ids: Set of available document IDs to filter against

    Returns:
        List of unique document IDs found in the content that exist in available documents
    """
    # Pattern to match /pages/{id} in Confluence URLs
    pattern = re.compile(r"/pages/(\d+)")

    # Find all matches in the content
    matches = pattern.findall(content)

    # Convert to set to remove duplicates, then filter to only include available IDs
    found_ids = set(matches)
    relevant_ids = [doc_id for doc_id in found_ids if doc_id in available_document_ids]

    # Sort for consistency
    relevant_ids.sort(key=lambda x: int(x))

    return relevant_ids


def load_selected_controls(
    selected_documents_dir: str, documents: List[Document]
) -> List[SelectedControl]:
    """
    Load selected controls from the specified directory and map them to relevant documents.

    Args:
        selected_documents_dir: Path to the directory containing selected control files
        documents: List of available Document objects

    Returns:
        List of SelectedControl objects with mapped document IDs
    """
    selected_controls = []
    selected_documents_path = Path(selected_documents_dir)

    if not selected_documents_path.exists():
        raise FileNotFoundError(
            f"Selected documents directory not found: {selected_documents_dir}"
        )

    # Create a set of available document IDs for fast lookup
    available_document_ids = {doc.id for doc in documents}

    # Pattern to match filenames starting with a control ID (e.g., "5.1", "8.2")
    # Format: {number}.{number} {rest of name}.md
    pattern = re.compile(r"^(\d+\.\d+)\s+(.+?)\.md$")

    # Iterate through all .md files in the directory
    for file_path in selected_documents_path.glob("*.md"):
        filename = file_path.name

        # Skip template.md file
        if filename.lower() == "template.md":
            continue

        match = pattern.match(filename)

        if match:
            control_id = match.group(1)
            control_name = match.group(2)

            # Read the file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract document IDs from the content
                relevant_document_ids = extract_document_ids_from_content(
                    content, available_document_ids
                )

                selected_control = SelectedControl(
                    id=control_id,
                    name=control_name,
                    relevant_document_ids=relevant_document_ids,
                )
                selected_controls.append(selected_control)
            except Exception as e:
                print(f"Warning: Could not read file {filename}: {e}")
        else:
            # Only warn if it's not template.md (already skipped)
            if filename.lower() != "template.md":
                print(
                    f"Warning: Filename '{filename}' does not match expected pattern (ID Name.md)"
                )

    # Sort controls by ID for consistency
    selected_controls.sort(
        key=lambda x: (float(x.id.split(".")[0]), float(x.id.split(".")[1]))
    )

    return selected_controls
