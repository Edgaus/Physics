<<<<<<< HEAD
=======
# Este es un archivo Python para poder simular patrones RHEED
# Pero primero estamos simulando como se ve una red cristalina en 2d

"""
Bosquejo Dash: pantalla 1:2 con margen.
Izquierda = Parámetros | Derecha = Plotly
"""

>>>>>>> 58a6bd9970451abf6b752e468177414880ea6358
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from dash import no_update
import plotly.graph_objects as go
import redreciproca as rr

app = Dash(__name__)


def figura_vacia():
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        plot_bgcolor="white",
        annotations=[{
            "text": "Configura los parámetros y presiona 'Actualizar Simulación'",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16, "color": "#666"},
        }],
    )
    return fig


app.layout = html.Div(
    style={
        "margin": "24px",
        "height": "calc(100vh - 48px)",
        "display": "flex",
        "gap": "16px",
        "boxSizing": "border-box",
        "fontFamily": "system-ui, sans-serif",
    },
    children=[
<<<<<<< HEAD
=======
        # PANEL IZQUIERDO (1/3)
>>>>>>> 58a6bd9970451abf6b752e468177414880ea6358
        html.Div(
            style={
                "flex": "1",
                "border": "2px solid #111",
                "padding": "16px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "12px",
                "overflowY": "auto",
            },
            children=[
                html.H2("Parámetros Red Dimensional", style={"margin": 0}),
                html.H4("Estructura Cristalina", style={"marginBottom": "4px"}),
                dcc.Dropdown(
                    id="tipo-red-2d",
                    options=[
                        {"label": "Hexagonal", "value": "HEX"},
                        {"label": "Rectangular / Cuadrada", "value": "RECT"},
                        {"label": "Centrada en Caras", "value": "CENT"},
                    ],
                    value="HEX",
                    clearable=False,
                ),
                html.Div([
                    html.Label(id="label-dato-1", children="Parámetro de red a (Å):"),
                    dcc.Input(
                        id="parametro-a",
                        type="number",
                        value=3.0,
                        step=0.01,
                        style={"width": "100%", "marginTop": "4px"},
                    ),
                ]),
                html.Div([
                    html.Label(
                        id="label-dato-2",
                        children="Parámetro b (No requerido en Hexagonal):",
                    ),
                    dcc.Input(
                        id="parametro-b",
                        type="number",
                        disabled=True,
                        style={"width": "100%", "marginTop": "4px"},
                    ),
                ]),
                html.H4("Resolución de la Simulación", style={"marginBottom": "4px"}),
                html.Label("Puntos / rango en b1:"),
                dcc.Input(
                    id="b1range",
                    type="number",
                    value=5,
                    step=1,
                    style={"width": "100%", "marginTop": "4px"},
                ),
                html.Label("Puntos / rango en b2:"),
                dcc.Input(
                    id="b2range",
                    type="number",
                    value=5,
                    step=1,
                    style={"width": "100%", "marginTop": "4px"},
                ),
                html.Button(
                    "Actualizar Simulación",
                    id="go",
                    n_clicks=0,
                    style={
                        "marginTop": "8px",
                        "padding": "10px",
                        "cursor": "pointer",
                        "fontWeight": "bold",
                    },
                ),
<<<<<<< HEAD
                # Debajo del botón "Actualizar Simulación":
                html.Hr(),
                html.H4("Vectores primitivos", style={"marginBottom": "4px"}),
                html.Div(
                id="info-vectores",
                style={
                    "fontSize": "14px",
                    "lineHeight": "1.45",
                    "padding": "10px",
                    "background": "#f5f5f5",
                    "border": "1px solid #ccc",
    },
),
            ],
        ),
        html.Div(
            style={"flex": "2", "border": "3px solid #e11", "padding": "8px"},
            children=[
                dcc.Graph(id="plot", figure=figura_vacia(), style={"height": "100%"})
=======
            ],
        ),
        # PANEL DERECHO (2/3)
        html.Div(
            style={"flex": "2", "border": "3px solid #e11", "padding": "8px"},
            children=[
                dcc.Graph(
                    id="plot",
                    figure=figura_vacia(),
                    style={"height": "100%"},
                )
>>>>>>> 58a6bd9970451abf6b752e468177414880ea6358
            ],
        ),
    ],
)

<<<<<<< HEAD
=======

# Callback 1: Habilitar/deshabilitar barras según la red elegida
>>>>>>> 58a6bd9970451abf6b752e468177414880ea6358
@app.callback(
    Output("info-vectores", "children"),
    Input("tipo-red-2d", "value"),
    Input("parametro-a", "value"),
    Input("parametro-b", "value"),
)


def mostrar_vectores(geometria, a, b):
    a = 3.0 if not a else float(a)
    b = a if not b else float(b)
    if geometria == "HEX":
        return [
            html.Div([html.B("Red hexagonal"), f" (a = {a} Å)"]),
            html.Div([
                html.B("a"), html.Sub("1"),
                f" = ({a:.3f},  0) Å",
            ]),
            html.Div([
                html.B("a"), html.Sub("2"),
                f" = ({0.5*a:.3f},  {a * 3**0.5 / 2:.3f}) Å",
            ]),
            html.Div("γ = 120°"),
        ]
    if geometria == "RECT":
        return [
            html.Div([html.B("Red rectangular"), f" (a = {a} Å, b = {b} Å)"]),
            html.Div([html.B("a"), html.Sub("1"), f" = ({a:.3f},  0) Å"]),
            html.Div([html.B("a"), html.Sub("2"), f" = (0,  {b:.3f}) Å"]),
            html.Div("γ = 90°"),
        ]
    if geometria == "CENT":
        return [
            html.Div([html.B("Red centrada"), f" (a = {a} Å, b = {b} Å)"]),
            html.Div([html.B("a"), html.Sub("1"), f" = ({a:.3f},  0) Å"]),
            html.Div([html.B("a"), html.Sub("2"), f" = (0,  {b:.3f}) Å"]),
            html.Div("Nodo extra en el centro: (a/2, b/2)"),
            html.Div("γ = 90°"),
        ]
    return "Selecciona una estructura."









@app.callback(
    Output("parametro-a", "disabled"),
    Output("parametro-b", "disabled"),
    Output("parametro-b", "value"),
    Output("label-dato-1", "children"),
    Output("label-dato-2", "children"),
    Input("tipo-red-2d", "value"),  # DEBE ser el mismo id del Dropdown
)
def actualizar_campos(opcion):
    if opcion == "HEX":
        return (
            False,
            True,
            no_update,  # no pongas None
            "Parámetro de red a (Å):",
            "Parámetro b (No requerido en Hexagonal):",
        )
    if opcion == "RECT":
        return (
            False,
            False,
            3.0,
            "Parámetro de red a (Å):",
            "Parámetro de red b (Å):",
        )
    if opcion == "CENT":
        return (
            False,
            False,
            4.0,
            "Parámetro base a (Å):",
            "Parámetro base b (Å):",
        )
    return False, False, no_update, "Dato 1:", "Dato 2:"


@app.callback(
    Output("plot", "figure"),
    Input("go", "n_clicks"),
    State("tipo-red-2d", "value"),
    State("parametro-a", "value"),
    State("parametro-b", "value"),
    State("b1range", "value"),
    State("b2range", "value"),
    prevent_initial_call=True,
)
def update_plot(n_clicks, geometria, dato1, dato2, b1range, b2range):
    if not n_clicks:
        raise PreventUpdate

    a = 1.0 if not dato1 else float(dato1)
    b = a if not dato2 else float(dato2)
    n1 = 5 if not b1range else int(b1range)
    n2 = 5 if not b2range else int(b2range)

    # Aquí luego: rr.calculadora(geometria, a, b, datax=(-n1, n1), datay=(-n2, n2))
    fig = rr.calculadora(geometria, a, b, datax=(-n1, n1), datay=(-n2, n2))
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8765)