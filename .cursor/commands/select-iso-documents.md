# Custom Command: Select Documents for ISO Control

To select the 5 most relevant documents for an ISO 27001 control, use this command pattern:

```
for select 3-8 most important documents from directory @documents which are relevant for ISO 27001 control. List those documents by name and url to confluence - I need only those information and 2-3 lines of information why you have selected this document from all set of available in the directory. Save output in the @selected_documents folder with the name of the control file. Output must be similar to the format in @selected_documents/template.md file. The ISO Control which you need to review is @controls/[CONTROL_NAME].md
```

Replace `[CONTROL_NAME]` with the actual control file name (e.g., `5.18 Access rights.md`).

## Workflow

1. The AI will search through documents in the `documents/` directory
2. It will analyze relevance to the specified ISO control
3. It will select the 3-8 most important documents. The number of documents is based on the ISO control.
3.1 If you have doubts about the number of documents, use less documents.
4. It will create a markdown file in `selected_documents/` folder matching the control file name
5. Each selected document will include:
   - Document name
   - Confluence URL
   - 2-3 lines explaining why it was selected