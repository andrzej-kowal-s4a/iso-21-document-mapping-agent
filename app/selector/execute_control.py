"""
Simple execution script for ISO 27001 controls.

This script demonstrates how to use DocumentSelector to select relevant documents
for a specific ISO control by control ID (e.g., 5.1, 8.3, 8.15).

Usage:
    python execute_control_5_7.py 5.7
    python execute_control_5_7.py 8.15
    python execute_control_5_7.py 5.1
"""

import argparse
import logging
import os
import glob
from DocumentSelector_class import DocumentSelector
from document_selector_utils import (
    get_control_name_from_path,
    save_selected_documents,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_control_file(control_id: str, controls_dir: str = "controls") -> str:
    """
    Find the control file matching the given control ID.

    Args:
        control_id: The control ID (e.g., "5.1", "8.3", "8.15", "5.2")
        controls_dir: Directory containing control files (default: "controls")

    Returns:
        Path to the control file

    Raises:
        FileNotFoundError: If no matching control file is found
        ValueError: If multiple matching files are found
    """
    # Get all markdown files in the controls directory
    pattern = os.path.join(controls_dir, "*.md")
    all_files = glob.glob(pattern)

    # Filter files that start with the exact control ID followed by a space or .md
    # This ensures "5.2" matches "5.2 Information..." but not "5.20 Addressing..."
    matching_files = []
    for file_path in all_files:
        filename = os.path.basename(file_path)
        # Check if filename starts with control_id followed by space or .md extension
        if filename.startswith(f"{control_id} ") or filename == f"{control_id}.md":
            matching_files.append(file_path)

    if not matching_files:
        raise FileNotFoundError(
            f"No control file found matching ID '{control_id}' in {controls_dir}/"
        )

    if len(matching_files) > 1:
        raise ValueError(
            f"Multiple control files found matching ID '{control_id}': {matching_files}"
        )

    control_path = matching_files[0]
    logger.info(f"Found control file: {control_path}")
    return control_path


def main():
    """Execute document selection for a specified ISO control."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Select relevant documents for an ISO 27001 control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python execute_control.py 5.7
  python execute_control.py 8.15
  python execute_control.py 5.1
        """,
    )
    parser.add_argument(
        "control_id",
        type=str,
        help="ISO 27001 control ID (e.g., 5.1, 8.3, 8.15)",
    )
    parser.add_argument(
        "--controls-dir",
        type=str,
        default="controls",
        help="Directory containing control files (default: controls)",
    )
    parser.add_argument(
        "--documents-dir",
        type=str,
        default="documents",
        help="Directory containing documents (default: documents)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="selected_documents_agent",
        help="Output directory for selected documents (default: selected_documents_agent)",
    )

    args = parser.parse_args()

    # Find the control file
    try:
        control_path = find_control_file(args.control_id, args.controls_dir)
    except (FileNotFoundError, ValueError) as e:
        logger.error(str(e))
        return 1

    # Get control name from path
    control_name = get_control_name_from_path(control_path)

    # Initialize DocumentSelector
    logger.info(f"Initializing DocumentSelector for control: {control_name}")
    logger.info(f"Control ID: {args.control_id}")
    logger.info(f"Control file: {control_path}")
    selector = DocumentSelector(documents_dir=args.documents_dir)

    # Select documents using the control path
    # The agent will read the control file and documents automatically
    logger.info("Selecting relevant documents...")
    try:
        result = selector.select_documents(
            control_path=control_path,
            control_name=control_name,
        )

        # Save the result
        output_filename = f"{control_name}.md"
        output_path = os.path.join(args.output_dir, output_filename)
        save_selected_documents(output_path, result)

        logger.info(f"Successfully completed document selection for {control_name}")
        logger.info(f"Output saved to: {output_path}")

        # Print agent usage statistics
        logger.info("\n" + "=" * 50)
        logger.info("Agent Usage Statistics:")
        logger.info("=" * 50)
        selector.print_agent_usage()

    except Exception as e:
        logger.error(f"Error during document selection: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
