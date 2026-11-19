import numpy as np
import plotly.graph_objects as go

def calculadora(Simetria, a, b, datax, datay):
   

    mesh = []

    if Simetria == "RECT":
        for i in range(-datax, datax + 1):
            for j in range(-datay, datay + 1):
                mesh.append((i , j ))

    if Simetria == "CENT":
            for i in range(-datax, datax + 1):
                for j in range(-datay, datay + 1):
                    mesh.append((i + j , i - j))

    if Simetria == "HEX":
                for i in range(-datax, datax + 1):
                    for j in range(-datay, datay + 1):
                        mesh.append((i  , i*( 1/np.sqrt(3) ) + j*( 2/np.sqrt(3) ) ))
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
        xaxis=dict(range=[-datax, datax], scaleanchor="y", scaleratio=1, title="x"),
        yaxis=dict(range=[-datay, datay], title="y"),
        uirevision="rheed",
        title="Red rectangular",
    )
    return fig