import numpy as np
import plotly.graph_objects as go


def calculadora(Simetria, a, b, datax, datay):
    dos_pi_a = 2 * np.pi / a
    dos_pi_b = 2 * np.pi / b
    nodos = []  # (i, j, x, y)

    if Simetria == "RECT":
        for i in range(-datax, datax + 1):
            for j in range(-datay, datay + 1):
                nodos.append((i, j, i * dos_pi_a, j * dos_pi_b))
        xlim = datax * dos_pi_a
        ylim = datay * dos_pi_b

    elif Simetria == "CENT":
        for i in range(-datax, datax + 1):
            for j in range(-datay, datay + 1):
                nodos.append((i, j, (i + j) * dos_pi_a, (i - j) * dos_pi_a))
        xlim = (datax + datay) * dos_pi_a
        ylim = (datax + datay) * dos_pi_a

    elif Simetria == "HEX":
        for i in range(-datax, datax + 1):
            for j in range(-datay, datay + 1):
                nodos.append((
                    i, j,
                    i * dos_pi_a,
                    dos_pi_a * (i / np.sqrt(3) + j * 2 / np.sqrt(3)),
                ))
        xlim = datax * dos_pi_a
        ylim = dos_pi_a * (datax / np.sqrt(3) + datay * 2 / np.sqrt(3))

    else:
        return go.Figure()

    if not nodos:
        return go.Figure()

    z_vals = 0.5*   np.linspace(-max(xlim, ylim), max(xlim, ylim), 100)
    hover = "(%{customdata[0]}, %{customdata[1]})<extra></extra>"

    # Varillas
    xs, ys, zs, cd = [], [], [], []
    for i, j, x, y in nodos:
        for z in z_vals:
            xs.append(x)
            ys.append(y)
            zs.append(z)
            cd.append((i, j))
        xs.append(None)
        ys.append(None)
        zs.append(None)
        cd.append((None, None))

    # Puntos del plano xy
    px = [n[2] for n in nodos]
    py = [n[3] for n in nodos]
    pz = [0.0] * len(nodos)
    pcd = [(n[0], n[1]) for n in nodos]

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="lines",
        line=dict(width=4, color="#9aa7a3"),
        customdata=cd,
        hovertemplate=hover,
        name="varillas",
    ))
    fig.add_trace(go.Scatter3d(
        x=px, y=py, z=pz,
        mode="markers",
        marker=dict(size=5, color="#0f3d3e"),
        customdata=pcd,
        hovertemplate=hover,
        name="plano xy",
    ))
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-xlim, xlim], title="x (Å⁻¹)"),
            yaxis=dict(range=[-ylim, ylim], title="y (Å⁻¹)"),
            zaxis=dict(range=[z_vals[0], z_vals[-1]], title="z (Å⁻¹)"),
            aspectmode="data",
        ),
        uirevision="rheed",
        title=f"Red {Simetria}",
    )
    return fig