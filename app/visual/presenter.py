import logging
from typing import List
from app.visual.controls import Control, load_controls
from app.visual.documents import Document, load_documents
from app.visual.selected_documents import SelectedControl, load_selected_controls
import dash
from dash import callback, Input, Output, State
from app.visual.presenter_layout import update_layout


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CONTROLS_DIR = "controls"
DOCUMENTS_DIR = "documents"
SELECTED_DOCUMENTS_DIR = "selected_documents_agent"


@callback(
    Output("cytoscape-graph", "elements"),
    Input("input-keywords", "value"),
    State("cytoscape-graph", "elements"),
)
def update_elements(
    input_keywords,
    elements,
):
    if not input_keywords:
        return elements

    print(f"input_keywords: {input_keywords}. This is not implemented yet.")

    return elements


def create_elements(
    controls: List[Control],
    documents: List[Document],
    selected_controls: List[SelectedControl],
):
    elements = []
    for control in controls:
        elements.append(
            {
                "data": {
                    "id": control.id,
                    "label": f"{control.id} {control.name}",
                    "classes": "Control",
                }
            },
        )
    for document in documents:
        elements.append(
            {"data": {"id": document.id, "label": document.name}, "classes": "Document"}
        )

    for selected_control in selected_controls:
        for relevant_document_id in selected_control.relevant_document_ids:
            elements.append(
                {
                    "data": {
                        "source": selected_control.id,
                        "target": relevant_document_id,
                    }
                }
            )

    return elements


def main():
    """Main function to run the presenter."""
    logger.info("Starting the presenter...")
    logger.info(f"Controls directory: {CONTROLS_DIR}")
    logger.info(f"Selected documents directory: {SELECTED_DOCUMENTS_DIR}")
    logger.info("Presenter started successfully.")

    # Load controls
    controls = load_controls(CONTROLS_DIR)
    logger.info(f"Loaded {len(controls)} controls.")

    control = controls[0]
    logger.info(f"Control: {control.name}")
    logger.info(f"Control ID: {control.id}")

    # Load documents
    documents = load_documents(DOCUMENTS_DIR)
    logger.info(f"Loaded {len(documents)} documents.")

    document = documents[0]
    logger.info(f"Document: {document.name}")
    logger.info(f"Document ID: {document.id}")

    # Load selected documents

    # Load selected controls and map them to documents
    selected_controls = load_selected_controls(SELECTED_DOCUMENTS_DIR, documents)
    logger.info(f"Loaded {len(selected_controls)} selected controls.")
    selected_control = selected_controls[2]
    logger.info(f"Selected control: {selected_control.name}")
    logger.info(f"Selected control ID: {selected_control.id}")
    logger.info(
        f"Selected control relevant document IDs: {selected_control.relevant_document_ids}"
    )

    elements = create_elements(controls, documents, selected_controls)
    # elements = create_elements(controls, documents, selected_controls)
    # input_keywords = None
    # filtered_elements = update_elements(input_keywords, elements)

    app = dash.Dash(__name__)
    update_layout(app, elements)

    app.run_server(debug=True)


if __name__ == "__main__":
    main()
