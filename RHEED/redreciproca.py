import numpy as np
import plotly.graph_objects as go

def calculadora(Simetria, a, b, datax=None, datay=None):
    # Vista por defecto si aún no hay zoom
    if datax is None:
        datax = (-3 * a, 3 * a)
    if datay is None:
        datay = (-3 * b, 3 * b)

    xmin, xmax = float(datax[0]), float(datax[1])
    ymin, ymax = float(datay[0]), float(datay[1])

    mesh = []

    if Simetria == "RECT":
        # índices enteros que tocan la ventana
        nx0 = int(np.floor(xmin / a))
        nx1 = int(np.ceil(xmax / a))
        ny0 = int(np.floor(ymin / b))
        ny1 = int(np.ceil(ymax / b))

        for i in range(nx0, nx1 + 1):
            for j in range(ny0, ny1 + 1):
                mesh.append([a * i, b * j])  # punto (x, y)

    # --- Plotly ---
    if not mesh:
        return go.Figure()

    xs = [p[0] for p in mesh]
    ys = [p[1] for p in mesh]

    fig = go.Figure(go.Scatter(
        x=xs, y=ys,
        mode="markers",
        marker=dict(size=8, color="#0f3d3e"),
        name="RECT",
    ))
    fig.update_layout(
        xaxis=dict(range=[xmin, xmax], scaleanchor="y", scaleratio=1, title="x"),
        yaxis=dict(range=[ymin, ymax], title="y"),
        uirevision="rheed",
        title="Red rectangular",
    )
    return fig