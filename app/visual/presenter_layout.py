import logging
from typing import List

from app.visual.controls import Control
from app.visual.documents import Document
from app.visual.selected_documents import SelectedControl
from dash import html, dcc
import dash_cytoscape as cyto


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTROLS_DIR = "controls"
DOCUMENTS_DIR = "documents"
SELECTED_DOCUMENTS_DIR = "selected_documents_agent"


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


DASH_STYLESHEET = [
    {
        "selector": "node",
        "style": {
            "content": "data(label)",
            "width": 20,
            "height": 20,
            "color": "#333333",
            "font-size": "12px",
            "text-outline-width": 2,
            "text-outline-color": "#ffffff",
        },
    },
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            # 'target-arrow-shape': 'triangle',
            "width": 1.5,
            "line-color": "#cccccc",
            # 'target-arrow-color': '#cccccc'
        },
    },
    {
        "selector": ".Control",
        "style": {
            "background-color": "#e74c3c",  # Soft red
            "line-color": "#c0392b",  # Darker red for edges
            "shape": "star",
        },
    },
    {
        "selector": ".Document",
        "style": {
            "background-color": "#2980b9",  # Mid blue
            "line-color": "#1f6390",  # Slightly darker blue
            "shape": "triangle",
        },
    },
]


def update_layout(app, elements):
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Table(
                        [
                            html.Tr(
                                [
                                    html.Td(
                                        "ISO 27001 Documents Mapping",
                                        style={
                                            "font-size": "30px",
                                            "font-weight": "bold",
                                        },
                                    )
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Keywords:"),
                                    dcc.Input(
                                        id="input-keywords", type="text", size="150"
                                    ),
                                ]
                            ),
                        ],
                        style={"font-size": "20px", "font-weight": "bold"},
                    ),
                ]
            ),
            cyto.Cytoscape(
                id="cytoscape-graph",
                elements=elements,
                layout={"name": "cose"},  # Force-directed layout
                style={"width": "100%", "height": "2500px"},
                stylesheet=DASH_STYLESHEET,
            ),
        ]
    )
