import numpy as np
import plotly.graph_objects as go


def calculadora(
    Simetria, a, b, datax, datay,
    modo_beam, angle, cofb1, coefb2,
    reconstruct, A1, A2, personalizacion,
):
    """
    Red recíproca 3D (RHEED).

    personalizacion = [varillas, vectores, ewald]
    reconstruct + A1, A2 → densifica la red con puntos fraccionarios A1×A2
    """
    _ = (modo_beam, angle, cofb1, coefb2)

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

    zlim = max(xlim, ylim)
    z_arrow = (0.5 * zlim) if personalizacion[0] else (1.2 * zlim)

    if Simetria == "RECT":
        vectores = np.array([
            [dos_pi_a, 0.0, 0.0],
            [0.0, dos_pi_b, 0.0],
            [0.0, 0.0, z_arrow],
        ], dtype=float)
    elif Simetria == "CENT":
        vectores = np.array([
            [dos_pi_a, dos_pi_a, 0.0],
            [dos_pi_a, -dos_pi_a, 0.0],
            [0.0, 0.0, z_arrow],
        ], dtype=float)
    else:
        vectores = np.array([
            [dos_pi_a, (1 / np.sqrt(3)) * dos_pi_a, 0.0],
            [0.0, 2 * (1 / np.sqrt(3)) * dos_pi_a, 0.0],
            [0.0, 0.0, z_arrow],
        ], dtype=float)

    b1 = vectores[0]
    b2 = vectores[1]

    recon_nodos = []
    A1i = A2i = 1
    if reconstruct:
        A1i = max(1, int(round(float(A1) if A1 not in (None, "") else 1)))
        A2i = max(1, int(round(float(A2) if A2 not in (None, "") else 1)))

        if A1i > 1 or A2i > 1:
            for i in range(-datax, datax + 1):
                for j in range(-datay, datay + 1):
                    for p in range(A1i):
                        for q in range(A2i):
                            if p == 0 and q == 0:
                                continue
                            fi = i + p / A1i
                            fj = j + q / A2i
                            x = fi * b1[0] + fj * b2[0]
                            y = fi * b1[1] + fj * b2[1]
                            recon_nodos.append((fi, fj, float(x), float(y)))

    if personalizacion[0]:
        z_vals = 0.5 * np.linspace(-zlim, zlim, 100)
        z_range = [z_vals[0], z_vals[-1]]
    else:
        z_vals = []
        z_range = [-1.3 * zlim, 1.3 * zlim]

    hover = "(%{customdata[0]}, %{customdata[1]})<extra></extra>"

    def _varillas(lista_nodos):
        xs, ys, zs, cd = [], [], [], []
        for i, j, x, y in lista_nodos:
            for z in z_vals:
                xs.append(x); ys.append(y); zs.append(z); cd.append((i, j))
            xs.append(None); ys.append(None); zs.append(None); cd.append((None, None))
        return xs, ys, zs, cd

    xs, ys, zs, cd = _varillas(nodos)
    rxs, rys, rzs, rcd = _varillas(recon_nodos) if (personalizacion[0] and recon_nodos) else ([], [], [], [])

    px = [n[2] for n in nodos]
    py = [n[3] for n in nodos]
    pz = [0.0] * len(nodos)
    pcd = [(n[0], n[1]) for n in nodos]

    rx = [n[2] for n in recon_nodos]
    ry = [n[3] for n in recon_nodos]
    rz = [0.0] * len(recon_nodos)
    rpcd = [(n[0], n[1]) for n in recon_nodos]

    xx = np.linspace(-xlim, xlim, 40)
    yy = np.linspace(-ylim, ylim, 40)
    XX, YY = np.meshgrid(xx, yy)
    ZZ = np.zeros_like(XX)

    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=XX, y=YY, z=ZZ,
        surfacecolor=XX, colorscale="Blues", opacity=0.35,
        showscale=False, name="plano xy", hoverinfo="skip",
    ))

    if personalizacion[0]:
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs, mode="lines",
            line=dict(width=4, color="#9aa7a3"),
            customdata=cd, hovertemplate=hover, name="varillas",
        ))
        if rxs:
            fig.add_trace(go.Scatter3d(
                x=rxs, y=rys, z=rzs, mode="lines",
                line=dict(width=3, color="#e9c46a"),
                customdata=rcd, hovertemplate=hover,
                name=f"varillas recon {A1i}×{A2i}",
            ))

    fig.add_trace(go.Scatter3d(
        x=px, y=py, z=pz, mode="markers",
        marker=dict(size=5, color="#0f3d3e"),
        customdata=pcd, hovertemplate=hover, name="nodos",
    ))

    if recon_nodos:
        fig.add_trace(go.Scatter3d(
            x=rx, y=ry, z=rz, mode="markers",
            marker=dict(size=4, color="#e9c46a"),
            customdata=rpcd, hovertemplate=hover,
            name=f"recon {A1i}×{A2i}",
        ))

    if personalizacion[1]:
        nombres = ["b1", "b2", "z"]
        colores = ["#e63946", "#2a9d8f", "#457b9d"]

        for k, vec in enumerate(vectores):
            color_actual = colores[k]
            etiqueta = f"{nombres[k]} ({vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f})"
            largo = float(np.linalg.norm(vec))
            tip_size = 0.15 * largo if largo > 0 else 0.1 * zlim

            fig.add_trace(go.Scatter3d(
                x=[0, vec[0]], y=[0, vec[1]], z=[0, vec[2]],
                mode="lines", line=dict(width=6, color=color_actual),
                name=etiqueta, legendgroup=nombres[k], showlegend=True,
            ))
            fig.add_trace(go.Cone(
                x=[vec[0]], y=[vec[1]], z=[vec[2]],
                u=[vec[0]], v=[vec[1]], w=[vec[2]],
                sizemode="absolute", sizeref=tip_size, anchor="tip",
                colorscale=[[0, color_actual], [1, color_actual]],
                showscale=False, legendgroup=nombres[k],
                showlegend=False, name=etiqueta,
            ))
            fig.add_trace(go.Scatter3d(
                x=[vec[0]], y=[vec[1]], z=[vec[2]],
                mode="text", text=[etiqueta], textposition="top center",
                textfont=dict(color=color_actual, size=12),
                legendgroup=nombres[k], showlegend=False, hoverinfo="skip",
            ))

        # ejes x, y, z
        _flecha(eje_x, "x", "#264653", ...)
        _flecha(eje_y, "y", "#2a9d8f", ...)
        _flecha(eje_z, "z", "#6c757d", ...)

        if reconstruct and (A1i > 1 or A2i > 1):
            _flecha(b1 / A1i, f"b1* (=b1/{A1i})", "#f4a261", ...)
            _flecha(b2 / A2i, f"b2* (=b2/{A2i})", "#e76f51", ...)
            for nombre, vec, color in (
                (f"b1/{A1i}", b1 / A1i, "#f4a261"),
                (f"b2/{A2i}", b2 / A2i, "#e76f51"),
            ):
                etiqueta = f"{nombre} ({vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f})"
                largo = float(np.linalg.norm(vec))
                tip_size = 0.15 * largo if largo > 0 else 0.1 * zlim
                fig.add_trace(go.Scatter3d(
                    x=[0, vec[0]], y=[0, vec[1]], z=[0, vec[2]],
                    mode="lines", line=dict(width=4, color=color, dash="dash"),
                    name=etiqueta, legendgroup=nombre, showlegend=True,
                ))
                fig.add_trace(go.Cone(
                    x=[vec[0]], y=[vec[1]], z=[vec[2]],
                    u=[vec[0]], v=[vec[1]], w=[vec[2]],
                    sizemode="absolute", sizeref=tip_size, anchor="tip",
                    colorscale=[[0, color], [1, color]],
                    showscale=False, legendgroup=nombre,
                    showlegend=False, name=etiqueta,
                ))

        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode="markers+text",
            marker=dict(size=6, color="gold", line=dict(width=2, color="black")),
            text=["Origen (0, 0, 0)"], textposition="bottom center",
            name="Origen (0, 0, 0)", showlegend=True,
        ))

    # personalizacion[2] = esfera de Ewald (pendiente)

    titulo = f"Red {Simetria}"
    if reconstruct and (A1i > 1 or A2i > 1):
        titulo += f" · reconstrucción {A1i}×{A2i}"

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        scene=dict(
            xaxis=dict(range=[-xlim, xlim], title="x (Å⁻¹)"),
            yaxis=dict(range=[-ylim, ylim], title="y (Å⁻¹)"),
            zaxis=dict(range=z_range, title="z (Å⁻¹)"),
            aspectmode="data",
        ),
        uirevision="rheed",
        title=titulo,
    )
    return fig