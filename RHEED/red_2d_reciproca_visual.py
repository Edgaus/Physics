# Este es un archivo Python para poder simular patrons RHEED
"""
Bosquejo Dash: pantalla 1:2 con margen.
Izquierda = Parámetros | Derecha = Plotly
"""

# app.py
from dash import Dash, Input, Output, dcc, html
import numpy as np
import plotly.graph_objects as go

app = Dash(__name__)

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
        html.Div(
            style={
                "flex": "1",
                "border": "2px solid #111",
                "padding": "16px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "12px",
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
        ),
    ],
)

@app.callback(Output("plot", "figure"), Input("amp", "value"), Input("go", "n_clicks"))
def update_plot(amp, _n):
    amp = 1.0 if amp is None else float(amp)
    x = np.linspace(0, 2 * np.pi, 200)
    fig = go.Figure(go.Scatter(x=x, y=amp * np.sin(x), mode="lines"))
    fig.update_layout(title="Espacio para Plotly", margin=dict(l=40, r=20, t=30, b=40))
    return fig

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8765)