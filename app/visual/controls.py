from pathlib import Path
from typing import List, Optional
import re


class Control:
    """Model representing a control document."""

    def __init__(self, id: str, name: str, content: str):
        """
        Initialize a Control object.

        Args:
            id: The control ID (e.g., "5.1", "8.2")
            name: The control name (remaining part of filename)
            content: The full content of the control document
        """
        self.id = id
        self.name = name
        self.content = content

    def __repr__(self):
        return f"Control(id='{self.id}', name='{self.name}')"


def load_controls(controls_dir: str) -> List[Control]:
    """
    Load all control files from the specified directory.

    Files are expected to be named in the format: "{id} {name}.md"
    where id is a pattern like "5.1", "8.2", etc.

    Args:
        controls_dir: Path to the directory containing control files

    Returns:
        List of Control objects
    """
    controls = []
    controls_path = Path(controls_dir)

    if not controls_path.exists():
        raise FileNotFoundError(f"Controls directory not found: {controls_dir}")

    # Pattern to match filenames starting with a control ID (e.g., "5.1", "8.2")
    # Format: {number}.{number} {rest of name}.md
    pattern = re.compile(r"^(\d+\.\d+)\s+(.+?)\.md$")

    # Iterate through all .md files in the directory
    for file_path in controls_path.glob("*.md"):
        filename = file_path.name
        match = pattern.match(filename)

        if match:
            control_id = match.group(1)
            control_name = match.group(2)

            # Read the file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                control = Control(id=control_id, name=control_name, content=content)
                controls.append(control)
            except Exception as e:
                print(f"Warning: Could not read file {filename}: {e}")
        else:
            print(
                f"Warning: Filename '{filename}' does not match expected pattern (ID Name.md)"
            )

    # Sort controls by ID for consistency
    controls.sort(key=lambda x: (float(x.id.split(".")[0]), float(x.id.split(".")[1])))

    return controls


def get_control_by_id(controls: List[Control], control_id: str) -> Optional[Control]:
    """
    Get a control by its ID.

    Args:
        controls: List of Control objects
        control_id: The ID to search for (e.g., "5.1", "8.2")

    Returns:
        Control object if found, None otherwise
    """
    for control in controls:
        if control.id == control_id:
            return control
    return None
