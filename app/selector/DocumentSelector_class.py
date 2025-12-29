"""
Document Selector class for selecting relevant documents for ISO 27001 controls.
"""

import logging
import os
from typing import Dict, List

from app.utils.ai_agent_utils import print_agent_usage
from app.selector.document_selector_utils import (
    extract_document_metadata,
    get_control_name_from_path,
    read_control_file,
    read_all_documents,
)
from strands import Agent
from strands.models.bedrock import BedrockModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration (matching ai_agent_utils)
NOVA_2_OMNI = "global.amazon.nova-2-lite-v1:0"
CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
MODEL_NAME = CLAUDE_3_7_SONNET
AWS_REGION = "us-east-1"

OUTPUT_FORMAT = """
# Selected Documents for ISO 27001 Control [CONTROL_NAME]

## 1. [DOCUMENT_TITLE]
**Confluence URL:** [URL]

[2-3 lines explaining why this document was selected and how it relates to the ISO control]

## 2. [DOCUMENT_TITLE]
**Confluence URL:** [URL]

[2-3 lines explaining why this document was selected and how it relates to the ISO control]

[Continue for 3-8 documents total]
"""


class DocumentSelector:
    def __init__(self, documents_dir: str = "documents"):
        """
        Initialize the DocumentSelector with an AI agent.

        Args:
            documents_dir: Path to the documents directory (default: "documents")
        """
        self.documents_dir = documents_dir
        self._agent = None  # Will be initialized by initialize_agent method

    def _initialize_agent(self, control_path: str = None):
        """
        Initialize an agent with tools for reading documents from the documents directory.

        Args:
            control_path: Optional path to the control file. If provided, the agent
                         will first read the control file.

        Returns:
            Initialized Agent instance with document reading tools
        """
        try:
            logger.info("Initializing DocumentSelector Agent...")
            logger.info(f"Using model: {MODEL_NAME}")
            logger.info(f"Using AWS region: {AWS_REGION}")
            logger.info(f"Documents directory: {self.documents_dir}")

            # Create BedrockModel
            bedrock_model = BedrockModel(
                model_id=MODEL_NAME,
                region_name=AWS_REGION,
            )

            # Create tools for reading documents
            tools = [
                self._list_documents_tool,
                self._read_document_tool,
                self._read_control_tool,
            ]

            # Initialize agent with tools
            agent = Agent(
                model=bedrock_model,
                tools=tools,
            )

            logger.info("Agent initialized successfully with document reading tools")
            return agent

        except Exception as e:
            logger.error(f"Failed to initialize Agent: {str(e)}", exc_info=True)
            raise

    def _list_documents_tool(self) -> List[str]:
        """
        List all markdown files in the documents directory.

        Returns:
            List of document filenames
        """
        try:
            if not os.path.exists(self.documents_dir):
                logger.warning(f"Documents directory not found: {self.documents_dir}")
                return []

            files = [
                f
                for f in os.listdir(self.documents_dir)
                if f.endswith(".md")
                and os.path.isfile(os.path.join(self.documents_dir, f))
            ]
            logger.info(f"Listed {len(files)} documents")
            return files
        except Exception as e:
            logger.error(f"Error listing documents: {e}", exc_info=True)
            return []

    def _read_document_tool(self, filename: str) -> Dict[str, str]:
        """
        Read a document from the documents directory.

        Args:
            filename: Name of the document file to read

        Returns:
            Dictionary with document metadata: filename, content, title, url
        """
        try:
            file_path = os.path.join(self.documents_dir, filename)
            if not os.path.exists(file_path):
                logger.warning(f"Document file not found: {file_path}")
                return {
                    "filename": filename,
                    "content": "",
                    "title": filename,
                    "url": "",
                }

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            metadata = extract_document_metadata(content, filename)
            logger.info(f"Read document: {filename}")
            return metadata
        except Exception as e:
            logger.error(f"Error reading document {filename}: {e}", exc_info=True)
            return {
                "filename": filename,
                "content": "",
                "title": filename,
                "url": "",
            }

    def _read_control_tool(self, control_path: str) -> str:
        """
        Read a control file.

        Args:
            control_path: Path to the control file

        Returns:
            Control file content as string
        """
        try:
            content = read_control_file(control_path)
            logger.info(f"Read control file: {control_path}")
            return content
        except Exception as e:
            logger.error(
                f"Error reading control file {control_path}: {e}", exc_info=True
            )
            return ""

    def select_documents(
        self,
        control_content: str = None,
        control_name: str = None,
        control_path: str = None,
        documents: List[Dict[str, str]] = None,
    ) -> str:
        """
        Select the most relevant documents for an ISO 27001 control.

        Args:
            control_content: The content of the ISO control file (optional if control_path provided)
            control_name: The name of the ISO control (e.g., "5.18 Access rights")
            control_path: Path to the control file (optional if control_content provided)
            documents: List of dictionaries, each containing:
                - filename: Document filename
                - content: Full document content
                - title: Document title
                - url: Confluence URL
                (optional if agent has tools to read documents)

        Returns:
            A markdown string with selected documents in the template format

        Raises:
            ValueError: If required parameters are missing
            Exception: If agent fails to generate selection
        """
        # Initialize agent if not already initialized
        if self._agent is None:
            self._agent = self._initialize_agent(control_path)

        # Read control file if path provided
        if control_path and not control_content:
            control_content = read_control_file(control_path)
            if not control_name:
                control_name = get_control_name_from_path(control_path)

        if not control_content:
            raise ValueError("Either control_content or control_path must be provided")

        if not control_name:
            raise ValueError("control_name must be provided")

        # If documents not provided, agent will use tools to read them
        if documents is None:
            documents = read_all_documents(self.documents_dir)

        if not documents:
            raise ValueError(
                f"Documents list cannot be empty. No documents found in {self.documents_dir}"
            )

        # Prepare document summaries for the prompt
        # Include title and first 500 characters of content for context
        document_summaries = []
        for i, doc in enumerate(documents, 1):
            content_preview = doc["content"][:500] + (
                "..." if len(doc["content"]) > 500 else ""
            )
            summary = f"""
Document {i}:
Title: {doc["title"]}
Filename: {doc["filename"]}
Confluence URL: {doc["url"]}
Content Preview:
{content_preview}
---
"""
            document_summaries.append(summary)

        documents_text = "\n".join(document_summaries)

        prompt = f"""You are a helpful assistant specialized in ISO 27001 compliance and information security. Your task is to select the most relevant documents for an ISO 27001 control.

You have access to tools that can:
- List all documents in the documents directory (_list_documents_tool)
- Read full content of any document (_read_document_tool)
- Read control files (_read_control_tool)

You are given:
1. An ISO 27001 control description
2. A list of available documents with their titles, URLs, and content previews

If you need more detailed information about any document, you can use the _read_document_tool to read its full content.

Your task:
- Select 3-8 most important documents that are relevant to the ISO 27001 control
- The number of documents should be based on how many documents are actually relevant (use fewer if there are fewer relevant documents)
- Focus on documents that directly address the control requirements or support compliance with the control
- Prioritize documents that are policies, procedures, or standards related to the control topic
- Omit general documents that are not specifically relevant to this control

Output format:
The output must be in markdown format exactly matching this structure:

{OUTPUT_FORMAT}

Requirements:
- Start with the header: "# Selected Documents for ISO 27001 Control [CONTROL_NAME]"
- Make sure you have inclued [CONTROL_NAME] in the header of the file in OUTPUT_FORMAT.
- For each selected document, include:
  - A numbered heading: "## [NUMBER]. [DOCUMENT_TITLE]"
  - The Confluence URL: "**Confluence URL:** [URL]"
  - 2-3 lines explaining why this document was selected and how it relates to the ISO control
- Use the exact document titles and URLs provided
- Number the documents sequentially starting from 1
- Select between 3-8 documents (use fewer if fewer are relevant)
- Focus on relevance to ISO 27001 compliance and security

ISO Control:
{control_content}

Available Documents:
{documents_text}

Now select the 3-8 most relevant documents and provide your output in the specified markdown format. Return only the markdown content, no additional text or explanations."""

        try:
            logger.info(
                f"Calling AI agent to select documents for control: {control_name}"
            )
            result_agent = self._agent(prompt)

            # Extract text from AgentResult
            pure_agent_response = str(result_agent).strip()

            # Remove markdown code blocks if present (similar to DocumentKeywordsGenerator)
            pure_agent_response = (
                pure_agent_response.replace("```markdown", "")
                .replace("```md", "")
                .replace("```", "")
                .strip()
            )

            # Ensure the header includes the control name
            if not pure_agent_response.startswith("# Selected Documents"):
                # Try to fix if the format is slightly off
                if "Selected Documents" in pure_agent_response:
                    # Extract the relevant part
                    start_idx = pure_agent_response.find("#")
                    if start_idx >= 0:
                        pure_agent_response = pure_agent_response[start_idx:].strip()
                else:
                    # If header is missing, add it
                    pure_agent_response = (
                        f"# Selected Documents for ISO 27001 Control {control_name}\n\n"
                        + pure_agent_response
                    )

            logger.info(
                f"Successfully generated document selection for control: {control_name}"
            )
            return pure_agent_response

        except Exception as e:
            logger.error(
                f"Error selecting documents for control {control_name}: {e}",
                exc_info=True,
            )
            raise

    def print_agent_usage(self):
        """
        Print the agent usage statistics.

        Note: This method calls the agent with a dummy prompt to get usage stats.
        """
        print_agent_usage(self._agent)
