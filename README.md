# ISO-21 Document Mapping Matching Agent

The project include:
- keywords generation for documents
- document selection for ISO 27001 controls

## Keywords Generation

- Document keyword generation using AI agents
- Batch processing of multiple documents
- JSON-based keyword storage

## Document Selection for ISO 27001 Controls

### Usage

```bash
python execute_control.py 5.7
python execute_control.py 8.15
python execute_control.py 5.1
```

## Project Structure

- `documents/` - Source documents to process
- `documents_keywords/` - Generated keyword JSON files
- `controls/` - ISO control documents
- `selected_documents/` - Selected documents for processing manually by the cursor commands
- `selected_documents_agent/` - Selected documents for processing by the agent (bedrock agent)

