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
        opacity=0.22,
        showscale=False,
        showlegend=False,
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
        marker=dict(size=5, color="#ffffff"),
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

    def _flecha(vec, nombre, color, width=5, tip_frac=0.18, etiqueta=None,
                showlegend=True, text_size=14, con_cono=True):
        """Línea (+ cono opcional) + etiqueta. Un clic en la leyenda oculta el grupo."""
        vec = np.asarray(vec, dtype=float)
        etiqueta = etiqueta or nombre
        largo = float(np.linalg.norm(vec))
        tip_size = tip_frac * largo if largo > 0 else 0.12 * zlim
        grupo = f"flecha:{nombre}"

        fig.add_trace(go.Scatter3d(
            x=[0, vec[0]], y=[0, vec[1]], z=[0, vec[2]],
            mode="lines",
            line=dict(width=width, color=color),
            name=etiqueta,
            legendgroup=grupo,
            showlegend=showlegend,
        ))
        if con_cono:
            fig.add_trace(go.Cone(
                x=[vec[0]], y=[vec[1]], z=[vec[2]],
                u=[vec[0]], v=[vec[1]], w=[vec[2]],
                sizemode="absolute",
                sizeref=tip_size,
                anchor="tip",
                colorscale=[[0, color], [1, color]],
                showscale=False,
                legendgroup=grupo,
                showlegend=False,
                name=etiqueta,
                hoverinfo="skip",
            ))
        fig.add_trace(go.Scatter3d(
            x=[vec[0]], y=[vec[1]], z=[vec[2]],
            mode="text",
            text=[nombre],
            textposition="top center",
            textfont=dict(color=color, size=text_size, family="Arial Black, sans-serif"),
            legendgroup=grupo,
            showlegend=False,
            hoverinfo="skip",
            name=etiqueta,
        ))

    # 5) Vectores: ejes + b1/b2 + reconstrucción (solo si Configuración → Vectores)
    if personalizacion[1]:
        # 5a) Ejes x,y: solo línea + etiqueta (sin cono). z: flecha completa.
        eje_x = np.array([0.85 * xlim, 0.0, 0.0])
        eje_y = np.array([0.0, 0.85 * ylim, 0.0])
        eje_z = np.array([0.0, 0.0, 0.55 * zlim])

        _flecha(
            eje_x, "x̂", "#4cc9f0", width=7, tip_frac=0.14, text_size=16,
            etiqueta=f"eje x̂ (±{xlim:.2f} Å⁻¹)", con_cono=False,
        )
        _flecha(
            eje_y, "ŷ", "#80ed99", width=7, tip_frac=0.14, text_size=16,
            etiqueta=f"eje ŷ (±{ylim:.2f} Å⁻¹)", con_cono=False,
        )
        _flecha(
            eje_z, "ẑ", "#f8f9fa", width=6, tip_frac=0.16, text_size=16,
            etiqueta="eje ẑ", con_cono=True,
        )

        # Cruz tenue de referencia (no compite con las flechas)
        fig.add_trace(go.Scatter3d(
            x=[-xlim, xlim, None, 0, 0, None, 0, 0],
            y=[0, 0, None, -ylim, ylim, None, 0, 0],
            z=[0, 0, None, 0, 0, None, z_range[0], z_range[1]],
            mode="lines",
            line=dict(width=1, color="rgba(173,181,189,0.35)"),
            name="ejes cartesianos",
            hoverinfo="skip",
            showlegend=False,
            legendgroup="ejes-ref",
        ))

        # 5b) Vectores primitivos de la red recíproca
        for nombre, vec, color in (
            ("b₁", vectores[0], "#ff006e"),   # magenta/rojo intenso
            ("b₂", vectores[1], "#8338ec"),   # violeta
            ("b_z", vectores[2], "#3a86ff"),  # azul brillante
        ):
            etiqueta = f"{nombre} ({vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f})"
            _flecha(vec, nombre, color, width=9, tip_frac=0.20, text_size=15,
                    etiqueta=etiqueta)

        # 5c) Vectores de reconstrucción b1* = b1/A1, b2* = b2/A2
        #     Solo si hay reconstrucción activa Y "Vectores" está enabled
        if reconstruct and (A1i > 1 or A2i > 1):
            b1_star = b1 / A1i
            b2_star = b2 / A2i
            _flecha(
                b1_star, f"b₁* (=b₁/{A1i})", "#ffbe0b", width=7, tip_frac=0.22,
                text_size=14,
                etiqueta=f"b₁* recon ({b1_star[0]:.2f}, {b1_star[1]:.2f}, {b1_star[2]:.2f})",
            )
            _flecha(
                b2_star, f"b₂* (=b₂/{A2i})", "#c332be", width=7, tip_frac=0.22,
                text_size=14,
                etiqueta=f"b₂* recon ({b2_star[0]:.2f}, {b2_star[1]:.2f}, {b2_star[2]:.2f})",
            )

        fig.add_trace(go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers+text",
            marker=dict(size=8, color="#ffd60a", line=dict(width=2, color="#000")),
            text=["Origen (0, 0, 0)"],
            textposition="bottom center",
            textfont=dict(color="#ffd60a", size=12),
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
    # Sin varillas: el eje z se dibuja, pero sin números/ticks
    if personalizacion[0]:
        zaxis_kw = dict(
            range=z_range,
            title="z (Å⁻¹)",
            showticklabels=True,
            ticks="outside",
            **axis_style,
        )
    else:
        zaxis_kw = dict(
            range=z_range,
            title="z",
            showticklabels=False,
            ticks="",
            showspikes=False,
            **axis_style,
        )

    # personalizacion[3] opcional: mostrar leyenda (True por defecto)
    mostrar_leyenda = True if len(personalizacion) < 4 else bool(personalizacion[3])

    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, t=48, b=0),
        paper_bgcolor="#0f1419",
        plot_bgcolor="#0f1419",
        font=dict(color="#e8eaed"),
        showlegend=mostrar_leyenda,
        legend=dict(
            bgcolor="rgba(26,31,38,0.92)",
            bordercolor="#2d3640",
            borderwidth=1,
            font=dict(color="#e8eaed", size=11),
            itemsizing="constant",
            # Clic = ocultar/mostrar ese ítem (+ su legendgroup: cono y texto)
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            groupclick="togglegroup",
            tracegroupgap=4,
        ),
        scene=dict(
            bgcolor="#0f1419",
            xaxis=dict(range=[-xlim, xlim], title="x (Å⁻¹)", **axis_style),
            yaxis=dict(range=[-ylim, ylim], title="y (Å⁻¹)", **axis_style),
            zaxis=zaxis_kw,
            aspectmode="data",
            # Vista por defecto similar a la captura (casi cenital, ligeramente inclinada)
            camera=dict(
                eye=dict(x=0.15, y=-1.55, z=1.85),
                center=dict(x=0, y=0, z=-0.05),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        uirevision="rheed",
        title=dict(text=titulo, font=dict(color="#e8eaed", size=16)),
    )
    return fig
