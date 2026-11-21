from dash import Dash, Input, Output, State, dcc, html, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import redreciproca as rr
import numpy as np

app = Dash(__name__)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            summary {
                cursor: pointer;
                font-weight: 700;
                font-size: 18px;
                padding: 8px 0;
            }
            details {
                border-bottom: 1px solid #ccc;
                padding-bottom: 6px;
            }
        </style>
        <script>
        window.MathJax = {
          tex: {
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
          },
          svg: {fontCache: 'global'}
        };
        </script>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


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


def linea(tex):
    return html.Div(tex, style={"margin": "8px 0"})


def seccion(titulo, children, abierto=False):
    return html.Details(
        [
            html.Summary(titulo),
            html.Div(children, style={"display": "flex", "flexDirection": "column", "gap": "10px", "padding": "4px 0 10px"}),
        ],
        open=abierto,
    )


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
        dcc.Store(id="mathjax-tick"),
        html.Div(
            style={
                "flex": "1",
                "border": "2px solid #111",
                "padding": "16px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "4px",
                "overflowY": "auto",
            },
            children=[
                seccion("Cristal", [
                    html.Label("Estructura cristalina"),
                    dcc.Dropdown(
                        id="tipo-red-2d",
                        options=[
                            {"label": "Hexagonal", "value": "HEX"},
                            {"label": "Rectangular / Cuadrada", "value": "RECT"},
                            {"label": "Cuadrado Centrada en Caras", "value": "CENT"},
                        ],
                        value="HEX",
                        clearable=False,
                    ),
                    html.Label(id="label-dato-1", children="Parámetro de red a (Å):"),
                    dcc.Input(id="parametro-a", type="number", value=3.0, step=0.01, style={"width": "100%"}),
                    html.Label(id="label-dato-2", children="Parámetro b (No requerido en Hexagonal):"),
                    dcc.Input(id="parametro-b", type="number", disabled=True, style={"width": "100%"}),
                ], abierto=True),

                seccion("E-beam", [
                    dcc.Tabs(
                        id="modo-haz",
                        value="azimut",
                        children=[
                            dcc.Tab(label="Ángulo azimutal", value="azimut"),
                            dcc.Tab(label="Notación de Miller", value="miller"),
                        ],
                    ),
                    html.Div(
                        id="panel-azimut",
                        children=[
                            html.Label("Azimut φ respecto a a1 (°)"),
                            dcc.Input(id="phi", type="number", value=0, step=1, style={"width": "100%", "marginTop": "4px"}),
                        ],
                    ),
                    html.Div(
                        id="panel-miller",
                        style={"display": "none"},
                        children=[
                            html.Label("Dirección [u v] = u a1 + v a2"),
                            html.Div([
                                dcc.Input(id="miller-u", type="number", value=1, step=1, style={"width": "48%"}),
                                dcc.Input(id="miller-v", type="number", value=0, step=1, style={"width": "48%", "marginLeft": "4%"}),
                            ], style={"marginTop": "4px"}),
                        ],
                    ),
                ]),

                seccion("Configuración", [
                    html.Label([html.B("b"), html.Sub("1"), " — rango:"]),
                    dcc.Input(id="b1range", type="number", value=5, step=1, style={"width": "100%"}),
                    html.Label([html.B("b"), html.Sub("2"), " — rango:"]),
                    dcc.Input(id="b2range", type="number", value=5, step=1, style={"width": "100%"}),
                    html.Button(
                        "Actualizar Simulación",
                        id="go",
                        n_clicks=0,
                        style={"padding": "10px", "cursor": "pointer", "fontWeight": "bold"},
                    ),
                ]),

                seccion("Datos", [
                    html.Div(
                        id="info-vectores",
                        style={
                            "fontSize": "15px",
                            "lineHeight": "1.45",
                            "padding": "10px",
                            "background": "#f5f5f5",
                            "border": "1px solid #ccc",
                        },
                    ),
                ]),
            ],
        ),
        html.Div(
            style={"flex": "2", "border": "3px solid #e11", "padding": "8px"},
            children=[dcc.Graph(id="plot", figure=figura_vacia(), style={"height": "100%"})],
        ),
    ],
)


@app.callback(
    Output("panel-azimut", "style"),
    Output("panel-miller", "style"),
    Input("modo-haz", "value"),
)
def cambiar_modo_haz(modo):
    visible = {"display": "block"}
    oculto = {"display": "none"}
    if modo == "miller":
        return oculto, visible
    return visible, oculto


@app.callback(
    Output("info-vectores", "children"),
    Input("tipo-red-2d", "value"),
    Input("parametro-a", "value"),
    Input("parametro-b", "value"),
)
def mostrar_vectores(geometria, a, b):
    a = 3.0 if not a else float(a)
    b = a if not b else float(b)

    if geometria == "RECT":
        con_a = 2 * np.pi / a
        con_b = 2 * np.pi / b
        return [
            html.H4("Espacio real"),
            html.Div(f"Red rectangular ($a={a:.3f}\\,\\mathrm{{Å}}$, $b={b:.3f}\\,\\mathrm{{Å}}$)"),
            linea(f"$$\\mathbf{{a}}_1 = a[1,0,0] = [{a:.3f},\\,0,\\,0]\\,\\mathrm{{Å}}$$"),
            linea(f"$$\\mathbf{{a}}_2 = b[0,1,0] = [0,\\,{b:.3f},\\,0]\\,\\mathrm{{Å}}$$"),
            linea(r"$$\gamma = 90^\circ$$"),
            html.H4("Espacio recíproco"),
            linea(
                f"$$\\mathbf{{b}}_1 = \\frac{{2\\pi}}{{a}}[1,0,0] = "
                f"[{con_a:.3f},\\,0,\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
            ),
            linea(
                f"$$\\mathbf{{b}}_2 = \\frac{{2\\pi}}{{b}}[0,1,0] = "
                f"[0,\\,{con_b:.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
            ),
            linea(r"$$\gamma^* = 90^\circ$$"),
        ]

    if geometria == "HEX":
        con_a = 2 * np.pi / a
        return [
            html.H4("Espacio real"),
            html.Div(f"Red hexagonal ($a={a:.3f}\\,\\mathrm{{Å}}$)"),
            linea(f"$$\\mathbf{{a}}_1 = a[1,0,0] = [{a:.3f},\\,0,\\,0]\\,\\mathrm{{Å}}$$"),
            linea(
                f"$$\\mathbf{{a}}_2 = \\frac{{a}}{{2}}[-1,\\sqrt{{3}},0] = "
                f"[{-0.5 * a:.3f},\\,{a * np.sqrt(3) / 2:.3f},\\,0]\\,\\mathrm{{Å}}$$"
            ),
            linea(r"$$\gamma = 120^\circ$$"),
            html.H4("Espacio recíproco"),
            linea(
                f"$$\\mathbf{{b}}_1 = \\frac{{2\\pi}}{{a}}\\left[1,\\frac{{1}}{{\\sqrt{{3}}}},0\\right] = "
                f"[{con_a:.3f},\\,{con_a / np.sqrt(3):.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
            ),
            linea(
                f"$$\\mathbf{{b}}_2 = \\frac{{2\\pi}}{{a}}\\left[0,\\frac{{2}}{{\\sqrt{{3}}}},0\\right] = "
                f"[0,\\,{2 * con_a / np.sqrt(3):.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
            ),
            linea(r"$$\gamma^* = 60^\circ$$"),
        ]

    if geometria == "CENT":
        con_a = 2 * np.pi / a
        return [
            html.H4("Espacio real"),
            html.Div(f"Red cuadrada centrada ($a={a:.3f}\\,\\mathrm{{Å}}$)"),
            linea(
                f"$$\\mathbf{{a}}_1 = \\frac{{a}}{{2}}[1,1,0] = "
                f"[{a / 2:.3f},\\,{a / 2:.3f},\\,0]\\,\\mathrm{{Å}}$$"
            ),
            linea(
                f"$$\\mathbf{{a}}_2 = \\frac{{a}}{{2}}[1,-1,0] = "
                f"[{a / 2:.3f},\\,{-a / 2:.3f},\\,0]\\,\\mathrm{{Å}}$$"
            ),
            linea(r"$$\gamma = 90^\circ$$"),
            html.H4("Espacio recíproco"),
            linea(
                f"$$\\mathbf{{b}}_1 = \\frac{{2\\pi}}{{a}}[1,1,0] = "
                f"[{con_a:.3f},\\,{con_a:.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
            ),
            linea(
                f"$$\\mathbf{{b}}_2 = \\frac{{2\\pi}}{{a}}[1,-1,0] = "
                f"[{con_a:.3f},\\,{-con_a:.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
            ),
            linea(r"$$\gamma^* = 90^\circ$$"),
        ]

    return "Selecciona una estructura."


app.clientside_callback(
    """
    function () {
        setTimeout(function () {
            const el = document.getElementById("info-vectores");
            if (!el || !window.MathJax) return;
            const go = function () {
                MathJax.typesetClear([el]);
                MathJax.typesetPromise([el]);
            };
            if (MathJax.startup && MathJax.startup.promise) {
                MathJax.startup.promise.then(go);
            } else if (MathJax.typesetPromise) {
                go();
            }
        }, 50);
        return "";
    }
    """,
    Output("mathjax-tick", "data"),
    Input("info-vectores", "children"),
)


@app.callback(
    Output("parametro-a", "disabled"),
    Output("parametro-b", "disabled"),
    Output("parametro-b", "value"),
    Output("label-dato-1", "children"),
    Output("label-dato-2", "children"),
    Input("tipo-red-2d", "value"),
)
def actualizar_campos(opcion):
    if opcion == "HEX":
        return False, True, no_update, "Parámetro de red a (Å):", "Parámetro b (No requerido en Hexagonal):"
    if opcion == "RECT":
        return False, False, 3.0, "Parámetro de red a (Å):", "Parámetro de red b (Å):"
    if opcion == "CENT":
        return False, True, no_update, "Parámetro base a (Å):", "Parámetro b (No requerido en FCS):"
    return False, False, no_update, "Dato 1:", "Dato 2:"


@app.callback(
    Output("plot", "figure"),
    Input("go", "n_clicks"),
    State("tipo-red-2d", "value"),
    State("parametro-a", "value"),
    State("parametro-b", "value"),
    State("b1range", "value"),
    State("b2range", "value"),
    State("modo-haz", "value"),
    State("phi", "value"),
    State("miller-u", "value"),
    State("miller-v", "value"),
    prevent_initial_call=True,
)
def update_plot(n_clicks, geometria, dato1, dato2, b1range, b2range, modo, phi, u, v):
    if not n_clicks:
        raise PreventUpdate

    a = 3.0 if not dato1 else float(dato1)
    b = a if not dato2 else float(dato2)
    nx = 5 if not b1range else int(b1range)
    ny = 5 if not b2range else int(b2range)

    if modo == "miller":
        direccion = (0.0 if u is None else float(u), 0.0 if v is None else float(v))
    else:
        direccion = float(0 if phi is None else phi)

    return rr.calculadora(geometria, a, b, nx, ny,  modo, phi, u, v)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8765)