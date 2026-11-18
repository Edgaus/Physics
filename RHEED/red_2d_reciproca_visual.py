<<<<<<< HEAD
# Este es un archivo Python para poder simular patrones RHEED
# Pero primero estamos simulando como se ve una red cristalina en 2d

=======
# Este es un archivo Python para poder simular patrons RHEED
>>>>>>> faf6fb5225c615816e44899c0d61cfe0b3e1a09c
"""
Bosquejo Dash: pantalla 1:2 con margen.
Izquierda = Parámetros | Derecha = Plotly
"""

<<<<<<< HEAD
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
import numpy as np
import plotly.graph_objects as go
import redreciproca as rr

app = Dash(__name__)


# Función auxiliar para mostrar un lienzo limpio antes de la primera simulación
def figura_vacia():
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        plot_bgcolor="white",
        annotations=[
            {
                "text": (
                    "Configura los parámetros y presiona 'Actualizar Simulación'"
                ),
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16, "color": "#666"},
            }
        ],
    )
    return fig


=======
# app.py
from dash import Dash, Input, Output, dcc, html
import numpy as np
import plotly.graph_objects as go

app = Dash(__name__)

>>>>>>> faf6fb5225c615816e44899c0d61cfe0b3e1a09c
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
        # PANEL IZQUIERDO (1/3)
=======
>>>>>>> faf6fb5225c615816e44899c0d61cfe0b3e1a09c
        html.Div(
            style={
                "flex": "1",
                "border": "2px solid #111",
                "padding": "16px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "12px",
<<<<<<< HEAD
                "overflowY": "auto",
            },
            children=[
                html.H2("Parámetros RHEED", style={"margin": 0}),
                html.Label("Amplitud / Intensidad:"),
                html.H4(
                    "Configuración de Red Superficial",
                    style={"marginBottom": "4px"},
                ),
                # 1. Selector principal de red
                dcc.Dropdown(
                    id="selector-geometria",
                    options=[
                        {"label": "Hexagonal", "value": "HEX"},
                        {"label": "Rectangular / Cuadrada", "value": "RECT"},
                        {"label": "Centrada en Caras (c-rect)", "value": "CENT"},
                    ],
                    value="HEX",
                    clearable=False,
                ),
                # 2. Primera barra para registrar datos numéricos
                html.Div([
                    html.Label(
                        id="label-dato-1", children="Parámetro de red a (Å):"
                    ),
                    dcc.Input(
                        id="input-dato-1",
                        type="number",
                        value=3.0,
                        step=0.1,
                        placeholder="Ingresa un número...",
                        disabled=False,
                        style={"width": "100%", "marginTop": "4px"},
                    ),
                ]),
                # 3. Segunda barra para registrar datos numéricos
                html.Div([
                    html.Label(
                        id="label-dato-2",
                        children="Parámetro b (No requerido en Hexagonal):",
                    ),
                    dcc.Input(
                        id="input-dato-2",
                        type="number",
                        placeholder="Ingresa un número...",
                        disabled=True,
                        style={"width": "100%", "marginTop": "4px"},
                    ),
                ]),
                # Botón de ejecución
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
            ],
=======
            },
            children=[
                html.H2("Parametros", style={"margin": 0}),
                dcc.Input(id="amp", type="number", value=1.0, step=0.1),
                html.Button("Actualizar", id="go", n_clicks=0),
                dcc.Dropdown(
                id='mi-lista-desplegable',
                options=[
                        {'label': 'Ciudad de México', 'value': 'CDMX'},
                        {'label': 'Guadalajara', 'value': 'GDL'},
                        {'label': 'Monterrey', 'value': 'MTY'}
                        ],
                        value='CDMX',  # Valor seleccionado por defecto
                        clearable=False # Evita que el usuario deje el campo vacío
                        )
            ],
        ),
        html.Div(
            style={"flex": "2", "border": "3px solid #e11", "padding": "8px"},
            children=[dcc.Graph(id="plot", style={"height": "100%"})],
>>>>>>> faf6fb5225c615816e44899c0d61cfe0b3e1a09c
        ),
    ],
)

<<<<<<< HEAD

# Callback 1: Habilitar/deshabilitar barras según la red elegida
@app.callback(
    [
        Output("input-dato-1", "disabled"),
        Output("input-dato-2", "disabled"),
        Output("input-dato-2", "value"),
        Output("label-dato-1", "children"),
        Output("label-dato-2", "children"),
    ],
    Input("selector-geometria", "value"),
)
def actualizar_campos(opcion_seleccionada):
    if opcion_seleccionada == "HEX":  # Solo requiere un parámetro de red (a)
        return (
            False,
            True,
            None,
            "Parámetro de red a (Å):",
            "Parámetro b (No requerido en Hexagonal):",
        )

    elif opcion_seleccionada == "RECT":  # Requiere lados a y b
        return (
            False,
            False,
            3.0,
            "Parámetro de red a (Å):",
            "Parámetro de red b (Å):",
        )

    elif opcion_seleccionada == "CENT":  # Requiere lados a y b
        return (
            False,
            False,
            4.0,
            "Parámetro base a (Å):",
            "Parámetro base b (Å):",
        )

    return False, False, None, "Dato 1:", "Dato 2:"


# Callback 2: Actualizar gráfica solo cuando se presiona el botón
@app.callback(
    Output("plot", "figure"),
    Input("go", "n_clicks"),
    State("selector-geometria", "value"),
    State("input-dato-1", "value"),
    State("input-dato-2", "value"),
    prevent_initial_call=True,
)
def update_plot(n_clicks, geometria, dato1, dato2):
    if not n_clicks:
        raise PreventUpdate

    fig = rr.calculadora( geometria, dato1, dato2 )
    return fig


=======
@app.callback(Output("plot", "figure"), Input("amp", "value"), Input("go", "n_clicks"))
def update_plot(amp, _n):
    amp = 1.0 if amp is None else float(amp)
    x = np.linspace(0, 2 * np.pi, 200)
    fig = go.Figure(go.Scatter(x=x, y=amp * np.sin(x), mode="lines"))
    fig.update_layout(title="Espacio para Plotly", margin=dict(l=40, r=20, t=30, b=40))
    return fig

>>>>>>> faf6fb5225c615816e44899c0d61cfe0b3e1a09c
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8765)