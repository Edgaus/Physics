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
    # Parámetros de haz / Ewald quedan para etapas siguientes
    _ = (modo_beam, angle, cofb1, coefb2)

    dos_pi_a = 2 * np.pi / a
    dos_pi_b = 2 * np.pi / b
    nodos = []  # (i, j, x, y)  — índices de la red 1×1

    # 1) Nodos + límites
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

    # Vector z más largo si no hay varillas
    z_arrow = (0.5 * zlim) if personalizacion[0] else (1.2 * zlim)

    # Vectores recíprocos primitivos
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
    else:  # HEX
        vectores = np.array([
            [dos_pi_a, (1 / np.sqrt(3)) * dos_pi_a, 0.0],
            [0.0, 2 * (1 / np.sqrt(3)) * dos_pi_a, 0.0],
            [0.0, 0.0, z_arrow],
        ], dtype=float)

    b1 = vectores[0]
    b2 = vectores[1]

    # 1b) Reconstrucción A1×A2 → puntos fraccionarios extra
    #     posición = (i + p/A1) b1 + (j + q/A2) b2
    recon_nodos = []  # (fi, fj, x, y)
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
                                continue  # ya está en la red 1×1
                            fi = i + p / A1i
                            fj = j + q / A2i
                            x = fi * b1[0] + fj * b2[0]
                            y = fi * b1[1] + fj * b2[1]
                            recon_nodos.append((fi, fj, float(x), float(y)))

    # 2) Varillas (personalizacion[0])
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
                xs.append(x)
                ys.append(y)
                zs.append(z)
                cd.append((i, j))
            xs.append(None)
            ys.append(None)
            zs.append(None)
            cd.append((None, None))
        return xs, ys, zs, cd

    xs, ys, zs, cd = _varillas(nodos)
    rxs, rys, rzs, rcd = _varillas(recon_nodos) if (personalizacion[0] and recon_nodos) else ([], [], [], [])

    # 3) Puntos del plano xy
    px = [n[2] for n in nodos]
    py = [n[3] for n in nodos]
    pz = [0.0] * len(nodos)
    pcd = [(n[0], n[1]) for n in nodos]

    rx = [n[2] for n in recon_nodos]
    ry = [n[3] for n in recon_nodos]
    rz = [0.0] * len(recon_nodos)
    rpcd = [(n[0], n[1]) for n in recon_nodos]

    # Malla del plano semitransparente
    xx = np.linspace(-xlim, xlim, 40)
    yy = np.linspace(-ylim, ylim, 40)
    XX, YY = np.meshgrid(xx, yy)
    ZZ = np.zeros_like(XX)

    # 4) Figura
    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=XX,
        y=YY,
        z=ZZ,
        surfacecolor=XX,
        colorscale="Blues",
        opacity=0.35,
        showscale=False,
        name="plano xy",
        hoverinfo="skip",
    ))

    if personalizacion[0]:
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="lines",
            line=dict(width=4, color="#9aa7a3"),
            customdata=cd,
            hovertemplate=hover,
            name="varillas",
        ))
        if rxs:
            fig.add_trace(go.Scatter3d(
                x=rxs, y=rys, z=rzs,
                mode="lines",
                line=dict(width=3, color="#e9c46a"),
                customdata=rcd,
                hovertemplate=hover,
                name=f"varillas recon {A1i}×{A2i}",
            ))

    fig.add_trace(go.Scatter3d(
        x=px, y=py, z=pz,
        mode="markers",
        marker=dict(size=5, color="#0f3d3e"),
        customdata=pcd,
        hovertemplate=hover,
        name="nodos",
    ))

    if recon_nodos:
        fig.add_trace(go.Scatter3d(
            x=rx, y=ry, z=rz,
            mode="markers",
            marker=dict(size=4, color="#e9c46a"),
            customdata=rpcd,
            hovertemplate=hover,
            name=f"recon {A1i}×{A2i}",
        ))

    def _flecha(vec, nombre, color, width=5, tip_frac=0.15, etiqueta=None, showlegend=True):
        """Flecha 3D: línea + cono + etiqueta en la punta."""
        vec = np.asarray(vec, dtype=float)
        etiqueta = etiqueta or nombre
        largo = float(np.linalg.norm(vec))
        tip_size = tip_frac * largo if largo > 0 else 0.1 * zlim

        fig.add_trace(go.Scatter3d(
            x=[0, vec[0]], y=[0, vec[1]], z=[0, vec[2]],
            mode="lines",
            line=dict(width=width, color=color),
            name=etiqueta,
            legendgroup=nombre,
            showlegend=showlegend,
        ))
        fig.add_trace(go.Cone(
            x=[vec[0]], y=[vec[1]], z=[vec[2]],
            u=[vec[0]], v=[vec[1]], w=[vec[2]],
            sizemode="absolute",
            sizeref=tip_size,
            anchor="tip",
            colorscale=[[0, color], [1, color]],
            showscale=False,
            legendgroup=nombre,
            showlegend=False,
            name=etiqueta,
        ))
        fig.add_trace(go.Scatter3d(
            x=[vec[0]], y=[vec[1]], z=[vec[2]],
            mode="text",
            text=[nombre],
            textposition="top center",
            textfont=dict(color=color, size=12),
            legendgroup=nombre,
            showlegend=False,
            hoverinfo="skip",
        ))

    # 5a) Ejes cartesianos x, y (y z corto de referencia)
    eje_x = np.array([0.9 * xlim, 0.0, 0.0])
    eje_y = np.array([0.0, 0.9 * ylim, 0.0])
    eje_z = np.array([0.0, 0.0, 0.45 * zlim])

    _flecha(eje_x, "x", "#264653", width=3, tip_frac=0.08,
            etiqueta=f"eje x (±{xlim:.2f} Å⁻¹)")
    _flecha(eje_y, "y", "#2a9d8f", width=3, tip_frac=0.08,
            etiqueta=f"eje y (±{ylim:.2f} Å⁻¹)")
    _flecha(eje_z, "z", "#6c757d", width=2, tip_frac=0.10,
            etiqueta="eje z")

    # Líneas bidireccionales del eje (cruzan el origen)
    fig.add_trace(go.Scatter3d(
        x=[-xlim, xlim, None, 0, 0, None, 0, 0],
        y=[0, 0, None, -ylim, ylim, None, 0, 0],
        z=[0, 0, None, 0, 0, None, z_range[0], z_range[1]],
        mode="lines",
        line=dict(width=2, color="#adb5bd"),
        name="ejes cartesianos",
        hoverinfo="skip",
        showlegend=False,
    ))

    # 5b) Vectores de reconstrucción b1* = b1/A1, b2* = b2/A2
    if reconstruct and (A1i > 1 or A2i > 1):
        b1_star = b1 / A1i
        b2_star = b2 / A2i
        _flecha(
            b1_star, f"b1* (=b1/{A1i})", "#f4a261", width=5,
            etiqueta=f"b1* recon ({b1_star[0]:.2f}, {b1_star[1]:.2f}, {b1_star[2]:.2f})",
        )
        _flecha(
            b2_star, f"b2* (=b2/{A2i})", "#e76f51", width=5,
            etiqueta=f"b2* recon ({b2_star[0]:.2f}, {b2_star[1]:.2f}, {b2_star[2]:.2f})",
        )

    # 5c) Vectores primitivos b1, b2, z (personalizacion[1])
    if personalizacion[1]:
        for nombre, vec, color in (
            ("b1", vectores[0], "#e63946"),
            ("b2", vectores[1], "#1d3557"),
            ("ẑ", vectores[2], "#457b9d"),
        ):
            etiqueta = f"{nombre} ({vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f})"
            _flecha(vec, nombre, color, width=6, etiqueta=etiqueta)

        fig.add_trace(go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers+text",
            marker=dict(size=6, color="gold", line=dict(width=2, color="black")),
            text=["Origen (0, 0, 0)"],
            textposition="bottom center",
            name="Origen (0, 0, 0)",
            showlegend=True,
        ))

    # 6) personalizacion[2] = esfera de Ewald (pendiente)
    # if personalizacion[2]:
    #     ...

    titulo = f"Red {Simetria}"
    if reconstruct and (A1i > 1 or A2i > 1):
        titulo += f" · reconstrucción {A1i}×{A2i}"

    axis_style = dict(
        backgroundcolor="#1a1f26",
        gridcolor="#2d3640",
        zerolinecolor="#4a5560",
        showbackground=True,
        color="#9aa0a6",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="#0f1419",
        plot_bgcolor="#0f1419",
        font=dict(color="#e8eaed"),
        legend=dict(
            bgcolor="rgba(26,31,38,0.85)",
            bordercolor="#2d3640",
            font=dict(color="#e8eaed"),
        ),
        scene=dict(
            bgcolor="#0f1419",
            xaxis=dict(range=[-xlim, xlim], title="x (Å⁻¹)", **axis_style),
            yaxis=dict(range=[-ylim, ylim], title="y (Å⁻¹)", **axis_style),
            zaxis=dict(range=z_range, title="z (Å⁻¹)", **axis_style),
            aspectmode="data",
        ),
        uirevision="rheed",
        title=dict(text=titulo, font=dict(color="#e8eaed")),
    )
    return fig
