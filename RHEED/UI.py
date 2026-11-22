from dash import Dash, Input, Output, ctx, dcc, html, no_update
import plotly.graph_objects as go
import numpy as np

try:
    from . import figuras as rr
except ImportError:
    import figuras as rr

app = Dash(__name__)

    # Tema oscuro compartido
DARK = {
        "bg": "#0f1419",
        "panel": "#1a1f26",
        "panel2": "#222831",
        "border": "#2d3640",
        "text": "#e8eaed",
        "muted": "#9aa0a6",
        "accent": "#2a9d8f",
        "accent_hover": "#21867a",
        "input_bg": "#12171e",
        "danger": "#e63946",
    }

INPUT_STYLE = {
        "width": "100%",
        "marginTop": "4px",
        "backgroundColor": DARK["input_bg"],
        "color": DARK["text"],
        "border": f"1px solid {DARK['border']}",
        "borderRadius": "6px",
        "padding": "8px 10px",
        "outline": "none",
        "colorScheme": "dark",
        "boxSizing": "border-box",
    }

app.index_string = f"""
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    background: {DARK["bg"]};
                    color: {DARK["text"]};
                    color-scheme: dark;
                }}
                summary {{
                    cursor: pointer;
                    font-weight: 700;
                    font-size: 18px;
                    padding: 8px 0;
                    color: {DARK["text"]};
                    list-style: none;
                }}
                summary::-webkit-details-marker {{ display: none; }}
                summary::before {{
                    content: "▸ ";
                    color: {DARK["accent"]};
                }}
                details[open] > summary::before {{ content: "▾ "; }}
                details {{
                    border-bottom: 1px solid {DARK["border"]};
                    padding-bottom: 6px;
                }}
                label {{
                    color: {DARK["muted"]};
                    font-size: 14px;
                }}
                /* Radio de estructura (evita el dropdown blanco de react-select) */
                .rheed-radio label {{
                    color: {DARK["text"]} !important;
                }}
                .rheed-radio input[type="radio"] {{
                    accent-color: {DARK["accent"]};
                }}
                .rheed-radio label:has(input:checked) {{
                    border-color: {DARK["accent"]} !important;
                    box-shadow: inset 0 0 0 1px {DARK["accent"]};
                }}
                /* Inputs numéricos + spinners */
                input[type="number"] {{
                    color-scheme: dark;
                    background-color: {DARK["input_bg"]} !important;
                    color: {DARK["text"]} !important;
                    border: 1px solid {DARK["border"]} !important;
                }}
                input[type="number"]:disabled {{
                    opacity: 0.55;
                }}
                /* Tabs */
                .tab {{
                    background-color: {DARK["panel2"]} !important;
                    color: {DARK["muted"]} !important;
                    border: 1px solid {DARK["border"]} !important;
                    border-bottom: none !important;
                }}
                .tab--selected {{
                    background-color: {DARK["panel"]} !important;
                    color: {DARK["accent"]} !important;
                    border-top: 2px solid {DARK["accent"]} !important;
                }}
                .tab-content {{
                    border: none !important;
                    padding-top: 10px;
                }}
                /* Checklist */
                input[type="checkbox"] {{
                    accent-color: {DARK["accent"]};
                }}
                /* Rotación de la muestra */
                .rheed-slider {{ margin: 4px 12px 18px; }}
                .rc-slider-rail {{ background-color: {DARK["border"]}; }}
                .rc-slider-track {{ background-color: {DARK["accent"]}; }}
                .rc-slider-handle {{
                    border-color: {DARK["accent"]};
                    background-color: {DARK["text"]};
                    opacity: 1;
                }}
                .rc-slider-mark-text {{ color: {DARK["muted"]}; }}
                .rc-slider-dot {{
                    border-color: {DARK["border"]};
                    background: {DARK["panel"]};
                }}
                .rc-slider-dot-active {{ border-color: {DARK["accent"]}; }}
                .rc-slider-tooltip-inner {{
                    background: {DARK["panel2"]};
                    color: {DARK["text"]};
                    box-shadow: none;
                }}
                /* Scrollbar */
                ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
                ::-webkit-scrollbar-track {{ background: {DARK["bg"]}; }}
                ::-webkit-scrollbar-thumb {{
                    background: {DARK["border"]};
                    border-radius: 4px;
                }}
                ::-webkit-scrollbar-thumb:hover {{ background: {DARK["muted"]}; }}
            </style>
            <script>
            window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }},
            svg: {{fontCache: 'global'}}
            }};
            </script>
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
        </head>
        <body>
            {{%app_entry%}}
            <footer>
                {{%config%}}
                {{%scripts%}}
                {{%renderer%}}
            </footer>
        </body>
    </html>
    """


def pantalla_inicial():
        """Patrón de la pantalla con los mismos datos de arranque que la red."""
        return rr.figura_pantalla(
            "CENT", 3.0, 3.0,
            "azimut", 0.0, 1, 0, 0.1, 2.0,
            True, 2, 4,
            15.0, 10.0,
        )


def figura_inicial():
        """Vista por defecto: CENT + reconstrucción 2×4 + varillas + vectores + leyenda."""
        return rr.calculadora(
            "CENT", 3.0, 3.0, 1, 1,
            "azimut", 0.0, 1, 0, 0.1, 2.0,
            True, 2, 4, 
            {
                "varillas": True,
                "b1": True,
                "b2": True,
                "b3": True,
                "bz": True,
                "recon": True,
                "ewald": False,
                "k_ewald": False,
                "ejes": True,
                "leyenda": True,
            },
        )


def linea(tex):
        return html.Div(tex, style={"margin": "8px 0", "color": DARK["text"]})


def seccion(titulo, children, abierto=False):
        return html.Details(
            [
                html.Summary(titulo),
                html.Div(
                    children,
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "10px",
                        "padding": "4px 0 10px",
                    },
                ),
            ],
            open=abierto,
        )


app.layout = html.Div(
        style={
            "margin": "0",
            "padding": "24px",
            "height": "100vh",
            "display": "flex",
            "gap": "16px",
            "boxSizing": "border-box",
            "fontFamily": "system-ui, sans-serif",
            "backgroundColor": DARK["bg"],
            "color": DARK["text"],
        },
        children=[
            dcc.Store(id="mathjax-tick"),
            html.Div(
                style={
                    "flex": "1",
                    "border": f"1px solid {DARK['border']}",
                    "borderRadius": "10px",
                    "padding": "16px",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "4px",
                    "overflowY": "auto",
                    "backgroundColor": DARK["panel"],
                    "boxShadow": "0 8px 24px rgba(0,0,0,0.35)",
                },
                children=[
                    html.H2(
                        "RHEED · Red recíproca",
                        style={"margin": "0 0 8px", "color": DARK["text"], "fontSize": "22px"},
                    ),
                    seccion("Cristal", [
                        html.Label("Estructura cristalina"),
                        dcc.RadioItems(
                            id="tipo-red-2d",
                            options=[
                                {"label": "Hexagonal", "value": "HEX"},
                                {"label": "Rectangular / Cuadrada", "value": "RECT"},
                                {"label": "Centrada en caras", "value": "CENT"},
                            ],
                            value="CENT",
                            className="rheed-radio",
                            inputStyle={"marginRight": "8px", "accentColor": DARK["accent"]},
                            labelStyle={
                                "display": "block",
                                "padding": "8px 10px",
                                "marginBottom": "6px",
                                "backgroundColor": DARK["input_bg"],
                                "border": f"1px solid {DARK['border']}",
                                "borderRadius": "6px",
                                "color": DARK["text"],
                                "cursor": "pointer",
                            },
                            style={"marginTop": "4px"},
                        ),
                        html.Label(id="label-dato-1", children="Parámetro de red a (Å):"),
                        dcc.Input(
                            id="parametro-a", type="number", debounce=True, value=3.0, step=0.01,
                            style=INPUT_STYLE,
                        ),
                        html.Label(id="label-dato-2", children="Parámetro b (No requerido en Hexagonal):"),
                        dcc.Input(
                            id="parametro-b", type="number", debounce=True, disabled=True,
                            style=INPUT_STYLE,
                        ),
                    ], abierto=False),

                    seccion("E-beam", [
                        html.Label(id="keV_title", children="Energía del haz de electrones (keV):"),
                            dcc.Input(
                            id="keV", type="number", debounce=True, value=0.1, step=0.1,
                            style=INPUT_STYLE,
                            ),
                        html.Label("Ángulo rasante θ (°):"),
                        dcc.Input(
                            id="theta", type="number", debounce=True, value=2.0, step=0.1,
                            style=INPUT_STYLE,
                        ),
                        dcc.Tabs(
                            id="modo-haz",
                            value="azimut",
                            children=[
                                dcc.Tab(
                                    label="Ángulo azimutal",
                                    value="azimut",
                                    style={
                                        "backgroundColor": DARK["panel2"],
                                        "color": DARK["muted"],
                                        "border": f"1px solid {DARK['border']}",
                                    },
                                    selected_style={
                                        "backgroundColor": DARK["panel"],
                                        "color": DARK["accent"],
                                        "border": f"1px solid {DARK['border']}",
                                        "borderTop": f"2px solid {DARK['accent']}",
                                    },
                                ),
                                dcc.Tab(
                                    label="Notación de Miller",
                                    value="miller",
                                    style={
                                        "backgroundColor": DARK["panel2"],
                                        "color": DARK["muted"],
                                        "border": f"1px solid {DARK['border']}",
                                    },
                                    selected_style={
                                        "backgroundColor": DARK["panel"],
                                        "color": DARK["accent"],
                                        "border": f"1px solid {DARK['border']}",
                                        "borderTop": f"2px solid {DARK['accent']}",
                                    },
                                ),
                            ],
                            colors={
                                "border": DARK["border"],
                                "primary": DARK["accent"],
                                "background": DARK["panel2"],
                            },
                        ),
                        html.Div(
                            id="panel-azimut",
                            children=[
                                html.Label("Azimut φ respecto a a1 (°)"),
                                dcc.Input(
                                    id="phi", type="number", debounce=True, value=0, step=1,
                                    style=INPUT_STYLE,
                                ),
                            ],
                        ),
                        html.Div(
                            id="panel-miller",
                            style={"display": "none"},
                            children=[
                                html.Label("Dirección [u v] = u a1 + v a2"),
                                html.Div([
                                    dcc.Input(
                                        id="miller-u", type="number", debounce=True, value=1, step=1,
                                        style={**INPUT_STYLE, "width": "48%"},
                                    ),
                                    dcc.Input(
                                        id="miller-v", type="number", debounce=True, value=0, step=1,
                                        style={**INPUT_STYLE, "width": "48%", "marginLeft": "4%"},
                                    ),
                                ], style={"marginTop": "4px"}),
                            ],
                        ),
                    ]),

                    seccion("Pantalla de fósforo", [
                        html.Label("Distancia muestra–pantalla (cm):"),
                        dcc.Input(
                            id="distancia-pantalla", type="number", debounce=True, value=15.0, step=0.1, min=0,
                            style=INPUT_STYLE,
                        ),
                        html.Label("Radio de la pantalla (cm):"),
                        dcc.Input(
                            id="radio-pantalla", type="number", debounce=True, value=10.0, step=0.1, min=0,
                            style=INPUT_STYLE,
                        ),
                    ]),

                    seccion("Reconstrucción", [
                        dcc.Checklist(
                            id="modo-reconstructed",
                            options=[{"label": " Agregar reconstrucción A1 × A2", "value": "on"}],
                            value=["on"],
                            style={"color": DARK["text"]},
                            inputStyle={"marginRight": "6px"},
                            labelStyle={"color": DARK["text"]},
                        ),
                        html.Div(
                            id="panel-reconstruccion",
                            style={"display": "block"},
                            children=[
                                html.Label("Órdenes A1, A2 (celda A1×A2)"),
                                html.Div([
                                    dcc.Input(
                                        id="A1", type="number", debounce=True, value=2, step=1,
                                        style={**INPUT_STYLE, "width": "48%"},
                                    ),
                                    dcc.Input(
                                        id="A2", type="number", debounce=True, value=4, step=1,
                                        style={**INPUT_STYLE, "width": "48%", "marginLeft": "4%"},
                                    ),
                                ]),
                            ],
                        ),
                    ], abierto=False),

                    seccion("Configuración", [
                        html.Label([html.B("b"), html.Sub("1"), " — rango:"]),
                        dcc.Input(
                            id="b1range", type="number", debounce=True, value=1, step=1,
                            style=INPUT_STYLE,
                        ),
                        html.Label([html.B("b"), html.Sub("2"), " — rango:"]),
                        dcc.Input(
                            id="b2range", type="number", debounce=True, value=1, step=1,
                            style=INPUT_STYLE,
                        ),
                        html.Label("Visualización"),
                        dcc.Checklist(
                            id="opciones-visual",
                            options=[
                                {"label": " Varillas", "value": "varillas"},
                                {"label": " Ejes x, y, z", "value": "ejes"},
                                {"label": " b₁", "value": "b1"},
                                {"label": " b₂", "value": "b2"},
                                {"label": " b₃ (hexagonal)", "value": "b3"},
                                {"label": " b_z", "value": "bz"},
                                {"label": " Vectores de reconstrucción", "value": "recon"},
                                {"label": " Esfera de Ewald", "value": "ewald"},
                                {"label": " Vector k de Ewald", "value": "k_ewald"},
                                {"label": " Mostrar leyenda", "value": "leyenda"},
                            ],
                            value=["varillas", "ejes", "b1", "b2", "b3", "bz", "recon", "leyenda"],
                            style={"color": DARK["text"]},
                            inputStyle={"marginRight": "6px"},
                            labelStyle={"display": "block", "color": DARK["text"], "marginBottom": "4px"},
                        ),
                    ], abierto=False),

                    seccion("Datos", [
                        html.Div(
                            id="info-vectores",
                            style={
                                "fontSize": "15px",
                                "lineHeight": "1.45",
                                "padding": "10px",
                                "background": DARK["panel2"],
                                "border": f"1px solid {DARK['border']}",
                                "borderRadius": "8px",
                                "color": DARK["text"],
                            },
                        ),
                    ]),
                ],
            ),
            html.Div(
                style={
                    "flex": "2",
                    "minWidth": 0,
                    "minHeight": 0,
                    "border": f"1px solid {DARK['border']}",
                    "borderRadius": "10px",
                    "padding": "8px",
                    "backgroundColor": DARK["panel"],
                    "boxShadow": "0 8px 24px rgba(0,0,0,0.35)",
                },
                children=[
                    dcc.Tabs(
                        id="vista",
                        value="reciproco",
                        children=[
                            dcc.Tab(
                                label="Espacio recíproco",
                                value="reciproco",
                                style={
                                    "backgroundColor": DARK["panel2"],
                                    "color": DARK["muted"],
                                    "border": f"1px solid {DARK['border']}",
                                },
                                selected_style={
                                    "backgroundColor": DARK["panel"],
                                    "color": DARK["accent"],
                                    "border": f"1px solid {DARK['border']}",
                                    "borderTop": f"2px solid {DARK['accent']}",
                                },
                                children=[
                                    dcc.Graph(
                                        id="plot",
                                        figure=figura_inicial(),
                                        style={"height": "calc(100vh - 130px)", "width": "100%"},
                                        config={
                                            "responsive": True,
                                            "displaylogo": False,
                                            "scrollZoom": True,
                                            "modeBarButtonsToAdd": ["resetCameraDefault3d"],
                                        },
                                    ),
                                ],
                            ),
                            dcc.Tab(
                                label="Pantalla de fósforo",
                                value="pantalla",
                                style={
                                    "backgroundColor": DARK["panel2"],
                                    "color": DARK["muted"],
                                    "border": f"1px solid {DARK['border']}",
                                },
                                selected_style={
                                    "backgroundColor": DARK["panel"],
                                    "color": DARK["accent"],
                                    "border": f"1px solid {DARK['border']}",
                                    "borderTop": f"2px solid {DARK['accent']}",
                                },
                                children=[
                                    html.Div(
                                        [
                                            html.Span(
                                                "Rotación de la muestra",
                                                style={"color": DARK["muted"], "fontSize": "14px"},
                                            ),
                                            html.Span(
                                                id="angulo-muestra",
                                                children="φ = 0°",
                                                style={
                                                    "color": DARK["accent"],
                                                    "fontWeight": "700",
                                                    "fontSize": "16px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "alignItems": "baseline",
                                            "padding": "8px 8px 0",
                                        },
                                    ),
                                    dcc.Slider(
                                        id="rotacion-muestra",
                                        min=-180,
                                        max=180,
                                        step=1,
                                        value=0,
                                        marks={
                                            -180: "-180°",
                                            -90: "-90°",
                                            0: "0°",
                                            90: "90°",
                                            180: "180°",
                                        },
                                        tooltip={"placement": "bottom", "always_visible": False},
                                        className="rheed-slider",
                                    ),
                                    dcc.Graph(
                                        id="pantalla",
                                        figure=pantalla_inicial(),
                                        style={"height": "calc(100vh - 230px)", "width": "100%"},
                                        config={
                                            "responsive": True,
                                            "displaylogo": False,
                                            "scrollZoom": True,
                                        },
                                    ),
                                ],
                            ),
                        ],
                        colors={
                            "border": DARK["border"],
                            "primary": DARK["accent"],
                            "background": DARK["panel2"],
                        },
                    ),
                ],
            ),
        ],
    )


@app.callback(
        Output("panel-reconstruccion", "style"),
        Input("modo-reconstructed", "value"),
    )
def mostrar_reconstruccion(opciones):
        if opciones and "on" in opciones:
            return {"display": "block"}
        return {"display": "none"}


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
                html.H4("Espacio real", style={"color": DARK["accent"], "margin": "0 0 6px"}),
                html.Div(f"Red rectangular ($a={a:.3f}\\,\\mathrm{{Å}}$, $b={b:.3f}\\,\\mathrm{{Å}}$)"),
                linea(f"$$\\mathbf{{a}}_1 = a[1,0,0] = [{a:.3f},\\,0,\\,0]\\,\\mathrm{{Å}}$$"),
                linea(f"$$\\mathbf{{a}}_2 = b[0,1,0] = [0,\\,{b:.3f},\\,0]\\,\\mathrm{{Å}}$$"),
                linea(r"$$\gamma = 90^\circ$$"),
                html.H4("Espacio recíproco", style={"color": DARK["accent"], "margin": "12px 0 6px"}),
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
            bmod = 2 * con_a / np.sqrt(3)
            return [
                html.H4("Espacio real", style={"color": DARK["accent"], "margin": "0 0 6px"}),
                html.Div(f"Red hexagonal, tres vectores de superficie ($a={a:.3f}\\,\\mathrm{{Å}}$)"),
                linea(f"$$\\mathbf{{a}}_1 = a[1,0,0] = [{a:.3f},\\,0,\\,0]\\,\\mathrm{{Å}}$$"),
                linea(
                    f"$$\\mathbf{{a}}_2 = a\\left[-\\frac{{1}}{{2}},\\frac{{\\sqrt{{3}}}}{{2}},0\\right] = "
                    f"[{-0.5 * a:.3f},\\,{a * np.sqrt(3) / 2:.3f},\\,0]\\,\\mathrm{{Å}}$$"
                ),
                linea(
                    f"$$\\mathbf{{a}}_3 = a\\left[-\\frac{{1}}{{2}},-\\frac{{\\sqrt{{3}}}}{{2}},0\\right] = "
                    f"[{-0.5 * a:.3f},\\,{-a * np.sqrt(3) / 2:.3f},\\,0]\\,\\mathrm{{Å}}$$"
                ),
                linea(r"$$\mathbf{a}_1+\mathbf{a}_2+\mathbf{a}_3=0,\quad \gamma=120^\circ$$"),
                html.H4("Espacio recíproco", style={"color": DARK["accent"], "margin": "12px 0 6px"}),
                linea(
                    f"$$\\mathbf{{b}}_1 = \\frac{{2\\pi}}{{a}}\\left[1,\\frac{{1}}{{\\sqrt{{3}}}},0\\right] = "
                    f"[{con_a:.3f},\\,{con_a / np.sqrt(3):.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
                ),
                linea(
                    f"$$\\mathbf{{b}}_2 = \\frac{{2\\pi}}{{a}}\\left[-1,\\frac{{1}}{{\\sqrt{{3}}}},0\\right] = "
                    f"[{-con_a:.3f},\\,{con_a / np.sqrt(3):.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
                ),
                linea(
                    f"$$\\mathbf{{b}}_3 = \\frac{{2\\pi}}{{a}}\\left[0,-\\frac{{2}}{{\\sqrt{{3}}}},0\\right] = "
                    f"[0,\\,{-bmod:.3f},\\,0]\\,\\mathrm{{Å}}^{{-1}}$$"
                ),
                linea(
                    f"$$\\mathbf{{b}}_1+\\mathbf{{b}}_2+\\mathbf{{b}}_3=0,"
                    f"\\quad |\\mathbf{{b}}|={bmod:.3f}\\,\\mathrm{{Å}}^{{-1}},\\quad 120^\\circ$$"
                ),
            ]

        if geometria == "CENT":
            con_a = 2 * np.pi / a
            return [
                html.H4("Espacio real", style={"color": DARK["accent"], "margin": "0 0 6px"}),
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
                html.H4("Espacio recíproco", style={"color": DARK["accent"], "margin": "12px 0 6px"}),
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


def _angulo(phi, rotacion, arrastre):
        """El control que se acaba de mover manda: el slider o el campo φ."""
        prop = ctx.triggered[0]["prop_id"] if ctx.triggered else ""
        if prop.endswith("drag_value") and arrastre is not None:
            return float(arrastre)
        if prop == "phi.value":
            return 0.0 if phi is None else float(phi)
        if rotacion is not None:
            return float(rotacion)
        return 0.0 if phi is None else float(phi)


@app.callback(
        Output("plot", "figure"),
        Output("pantalla", "figure"),
        Output("angulo-muestra", "children"),
        Input("tipo-red-2d", "value"),
        Input("parametro-a", "value"),
        Input("parametro-b", "value"),
        Input("b1range", "value"),
        Input("b2range", "value"),
        Input("modo-haz", "value"),
        Input("phi", "value"),
        Input("rotacion-muestra", "value"),
        Input("rotacion-muestra", "drag_value"),
        Input("miller-u", "value"),
        Input("miller-v", "value"),
        Input("keV", "value"),
        Input("theta", "value"),
        Input("distancia-pantalla", "value"),
        Input("radio-pantalla", "value"),
        Input("modo-reconstructed", "value"),
        Input("A1", "value"),
        Input("A2", "value"),
        Input("opciones-visual", "value"),
        prevent_initial_call=True,
    )
def update_plot(
        geometria, dato1, dato2, b1range, b2range,
        modo, phi, rotacion, arrastre, u, v, keV, theta, distancia, radio,
        reconstructed, A1, A2, opciones_visual,
    ):
        angulo = _angulo(phi, rotacion, arrastre)
        a = 3.0 if not dato1 else float(dato1)
        b = a if not dato2 else float(dato2)
        nx = 3 if not b1range else int(b1range)
        ny = 3 if not b2range else int(b2range)

        usar_reconstruccion = bool(reconstructed) and "on" in reconstructed
        coef_1 = 0.0 if A1 is None else float(A1)
        coef_2 = 0.0 if A2 is None else float(A2)

        opciones = opciones_visual or []
        flags = {
            "varillas": "varillas" in opciones,
            "ejes": "ejes" in opciones,
            "b1": "b1" in opciones,
            "b2": "b2" in opciones,
            "b3": "b3" in opciones,
            "bz": "bz" in opciones,
            "recon": "recon" in opciones,
            "ewald": "ewald" in opciones,
            "k_ewald": "k_ewald" in opciones,
            "leyenda": "leyenda" in opciones,
        }

        red = rr.calculadora(
            geometria, a, b, nx, ny,
            modo, phi, u, v, keV, theta,
            usar_reconstruccion, coef_1, coef_2,
            flags,
            distancia, radio,
            angulo,
        )
        pantalla = rr.figura_pantalla(
            geometria, a, b,
            modo, phi, u, v, keV, theta,
            usar_reconstruccion, coef_1, coef_2,
            distancia, radio,
            angulo,
        )
        return red, pantalla, f"φ = {angulo:.0f}°"


@app.callback(
        Output("phi", "value"),
        Output("rotacion-muestra", "value"),
        Input("phi", "value"),
        Input("rotacion-muestra", "value"),
        prevent_initial_call=True,
    )
def sincronizar_angulo(phi, rotacion):
        """El campo φ y el slider quedan en el mismo ángulo, sin ciclo."""
        prop = ctx.triggered[0]["prop_id"] if ctx.triggered else ""
        if prop == "phi.value" and phi != rotacion:
            return no_update, phi
        if prop == "rotacion-muestra.value" and rotacion != phi:
            return rotacion, no_update
        return no_update, no_update


if __name__ == "__main__":
        app.run(debug=True, host="127.0.0.1", port=8765)
