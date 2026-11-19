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
                        {"label": "Cuadrado Centrada en Caras", "value": "CENT"},
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
                    html.Label(id="label-dato-2", children="Parámetro b (No requerido en Hexagonal):"),
                    dcc.Input(
                        id="parametro-b",
                        type="number",
                        disabled=True,
                        style={"width": "100%", "marginTop": "4px"},
                    ),
                ]),
                html.H4("Resolución de la Simulación", style={"marginBottom": "4px"}),
                html.Div([
                html.Label([html.B("b"), html.Sub("1"), " — rango:"]),
                dcc.Input(
                    id="b1range",
                    type="number",
                    value=5,
                    step=1,
                    disabled=False,
                    style={"width": "100%", "marginTop": "4px"},
                ),
                ]),
                html.Div([
                html.Label([html.B("b"), html.Sub("2"), " — rango:"]),
                dcc.Input(
                    id="b2range",
                    type="number",
                    value=5,
                    step=1,
                    style={"width": "100%", "marginTop": "4px"},
                ),
                ]),
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
                html.Hr(),
                html.H2("Vectores primitivos", style={"marginBottom": "4px"}),
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
            ],
        ),
        html.Div(
            style={"flex": "2", "border": "3px solid #e11", "padding": "8px"},
            children=[
                dcc.Graph(id="plot", figure=figura_vacia(), style={"height": "100%"})
            ],
        ),
    ],
)


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
        con_a = 2*np.pi/a
        con_b = 2*np.pi/b
        return [
            html.H4("Espacio real"),
            html.Div(f"Red rectangular ($a={a:.3f}\\,\\mathrm{{Å}}$, $b={b:.3f}\\,\\mathrm{{Å}}$)"),
            linea(f"$$\\mathbf{{a}}_1 = a[1,0,0] = [{a:.3f},\\,0,0]\\,\\mathrm{{Å}}$$ "),
            linea(f"$$\\mathbf{{a}}_2 = b[0,1,0] = [0,\\,{b:.3f},0]\\,\\mathrm{{Å}}$$"),
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
        return [
            html.H4("Espacio real"),
            html.Div(f"Red hexagonal ($a={a:.3f}\\,\\mathrm{{Å}}$)"),
            linea(f"$$\\mathbf{{a}}_1 = [{a:.3f},\\,0]\\,\\mathrm{{Å}}$$"),
            linea(
                f"$$\\mathbf{{a}}_2 = [{0.5 * a:.3f},\\,{a * 3**0.5 / 2:.3f}]\\,\\mathrm{{Å}}$$"
            ),
            linea(r"$$\gamma = 120^\circ$$"),
            html.H4("Espacio recíproco"),   
            linea(
                r"$$\mathbf{b}_2 = \frac{2\pi}{a}\left(0,\frac{2}{\sqrt{3}}\right)$$"
            ),
            linea(r"$$\gamma^* = 60^\circ$$"),
        ]

    if geometria == "CENT":
        con_a = 2*np.pi/a
        return [
            html.H4("Espacio real"),
            html.Div(f"Red cuadrada centrada ($a={a:.3f}\\,\\mathrm{{Å}}$)"),
            linea(
            f"$$\\mathbf{{a}}_1 = \\frac{{a}}{{2}}[1,1,0] = "
            f"[{a/2:.3f},\\,{a/2:.3f},\\,0]\\,\\mathrm{{Å}}$$"
            ),
            linea(
                f"$$\\mathbf{{a}}_2 = \\frac{{a}}{{2}}[1,-1,0] = "
                f"[{a/2:.3f},\\,{-a/2:.3f},\\,0]\\,\\mathrm{{Å}}$$"
            ),
            linea(r"$$\gamma = 90^\circ$$"),
            html.H4("Espacio recíproco"),
            linea(
                f"$$\\mathbf{{b}}_1 = \\frac{{2\\pi}}{{a}}[1,1,0]= "
                f"[{con_a:.3f},\\,{con_a:.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
            ),
            linea(
                f"$$\\mathbf{{b}}_2 = \\frac{{2\\pi}}{{a}}[1,-1,0]= "
                f"[{con_a:.3f},\\,{-    con_a:.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
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
        return (
            False,
            True,
            no_update,
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
            True,
            0.0,
            "Parámetro base a (Å):",
            "Parámetro b (No requerido en FCS):",
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

    return rr.calculadora(geometria, a, b, datax=(-n1, n1), datay=(-n2, n2))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8765)