"""Figuras de RHEED. Los cálculos están en fisica.py."""
import numpy as np
import plotly.graph_objects as go

try:
    from .fisica import (
        _flotante,
        claves_que_cortan,
        componentes_ki,
        direccion_haz,
        direccion_muestra,
        haz_incidente,
        llegan_a_pantalla,
        malla_reciproca,
        manchas_pantalla,
        radio_ewald,
        varillas_que_cortan,
    )
except ImportError:
    from fisica import (
        _flotante,
        claves_que_cortan,
        componentes_ki,
        direccion_haz,
        direccion_muestra,
        haz_incidente,
        llegan_a_pantalla,
        malla_reciproca,
        manchas_pantalla,
        radio_ewald,
        varillas_que_cortan,
    )

# Un color por familia, pensado para fondo oscuro.
COLORES = {
    "b1": "#ff4d6d",    # carmín
    "b2": "#06d6a0",    # esmeralda
    "b3": "#9d4edd",    # violeta — tercer vector hexagonal
    "bz": "#4895ef",    # azul
    "b1s": "#ffd166",   # oro — reconstrucción
    "b2s": "#f77f00",   # naranja — reconstrucción
    "k": "#c77dff",     # lila — vector de Ewald
    "esfera": "#4cc9f0",
    "varilla": "#8d99ae",          # red 1×1, fuera de la esfera
    "corte": "#ff5c33",            # red 1×1, corta la esfera
    "varilla_recon": "#e9c46a",    # reconstrucción, fuera de la esfera
    "corte_recon": "#7dffb3",      # reconstrucción, corta la esfera
}


def _activo(personalizacion, clave, default=False):
    """Lee un interruptor. Acepta dict o la lista corta antigua."""
    if isinstance(personalizacion, dict):
        return bool(personalizacion.get(clave, default))
    if not isinstance(personalizacion, (list, tuple)):
        return default
    # [varillas, vectores, ewald, leyenda]
    if len(personalizacion) <= 4:
        if clave == "varillas":
            return bool(personalizacion[0]) if personalizacion else default
        if clave in ("b1", "b2", "bz", "recon", "ejes"):
            return bool(personalizacion[1]) if len(personalizacion) > 1 else default
        if clave in ("ewald", "k_ewald"):
            return bool(personalizacion[2]) if len(personalizacion) > 2 else default
        if clave == "leyenda":
            return True if len(personalizacion) < 4 else bool(personalizacion[3])
        return default
    orden = ["varillas", "b1", "b2", "bz", "recon", "ewald", "k_ewald", "ejes", "leyenda"]
    if clave in orden and orden.index(clave) < len(personalizacion):
        return bool(personalizacion[orden.index(clave)])
    return default


def _texto_indice(n, periodo):
    """n/periodo reducido: 2/2 → 1, 1/2 se queda en 1/2."""
    n = int(n)
    periodo = int(periodo)
    if periodo == 0:
        return str(n)
    if n % periodo == 0:
        return str(n // periodo)
    g = int(np.gcd(abs(n), abs(periodo)))
    num, den = n // g, periodo // g
    if den < 0:
        num, den = -num, -den
    return f"{num}/{den}"


def figura_pantalla(
    Simetria, a, b,
    modo_beam, angle, cofb1, coefb2, keV, theta_deg,
    reconstruct, A1, A2,
    distancia_cm=15.0, radio_cm=10.0,
    rotacion_deg=0.0,
):
    """Patrón en el fósforo: puntos que llegan, con su índice (h, k).

    (h, k) = (i/A1, j/A2) de G = i b1/A1 + j b2/A2.
    La red 1×1 y la reconstrucción van en colores distintos.
    """
    def _vacia(mensaje):
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f1419",
            plot_bgcolor="#0f1419",
            font=dict(color="#e8eaed"),
            title=dict(text="Pantalla de fósforo", font=dict(color="#e8eaed", size=16)),
            margin=dict(l=48, r=16, t=48, b=40),
            annotations=[dict(
                text=mensaje, x=0.5, y=0.5, xref="paper", yref="paper",
                showarrow=False, font=dict(color="#e8eaed", size=14),
            )],
            uirevision="pantalla",
        )
        return fig

    error, datos = manchas_pantalla(
        Simetria, a, b,
        modo_beam, angle, cofb1, coefb2, keV, theta_deg,
        reconstruct, A1, A2,
        distancia_cm, radio_cm, rotacion_deg,
    )
    if error:
        return _vacia(error)

    L, R, phi = datos["L"], datos["R"], datos["phi"]
    A1i, A2i = datos["A1i"], datos["A2i"]
    lim = 1.2 * R if R > 0 else 1.0

    def _etiquetar(filas):
        return [
            (Y, Z, f"({_texto_indice(i, A1i)}, {_texto_indice(j, A2i)})")
            for Y, Z, i, j in filas
        ]

    red = _etiquetar(datos["red"])
    recon = _etiquetar(datos["recon"])

    fig = go.Figure()
    fig.add_shape(
        type="circle", x0=-R, y0=-R, x1=R, y1=R,
        line=dict(color="#4cc9f0", width=2),
        fillcolor="rgba(76, 201, 240, 0.06)",
    )
    fig.add_shape(
        type="line", x0=-R, y0=0, x1=R, y1=0,
        line=dict(color="#9aa0a6", width=1, dash="dot"),
    )
    fig.add_annotation(
        x=0, y=-0.55 * R, text="sombra", showarrow=False,
        font=dict(color="#9aa0a6", size=12),
    )

    def _familia(puntos, color, nombre):
        if not puntos:
            return
        fig.add_trace(go.Scatter(
            x=[p[0] for p in puntos],
            y=[p[1] for p in puntos],
            mode="markers+text",
            text=[p[2] for p in puntos],
            textposition="top center",
            textfont=dict(color=color, size=12),
            marker=dict(size=11, color=color, line=dict(width=1, color="#0f1419")),
            name=nombre,
            hovertemplate="%{text}<br>Y=%{x:.2f} cm<br>Z=%{y:.2f} cm<extra>" + nombre + "</extra>",
        ))

    _familia(red, COLORES["corte"], "red 1×1")
    _familia(recon, COLORES["corte_recon"], "reconstrucción")
    if not red and not recon:
        fig.add_annotation(
            x=0, y=0.35 * R, text="Ningún haz cae en el fósforo",
            showarrow=False, font=dict(color="#e8eaed", size=14),
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f1419",
        plot_bgcolor="#0f1419",
        font=dict(color="#e8eaed"),
        title=dict(
            text=f"Pantalla de fósforo · φ = {phi:.0f}° · L = {L:.1f} cm, R = {R:.1f} cm",
            font=dict(color="#e8eaed", size=16),
        ),
        margin=dict(l=48, r=16, t=48, b=40),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(26,31,38,0.92)",
            bordercolor="#2d3640",
            borderwidth=1,
            font=dict(color="#e8eaed", size=11),
        ),
        xaxis=dict(
            title="Y (cm)", range=[-lim, lim], zeroline=False,
            gridcolor="#2d3640", color="#e8eaed",
            scaleanchor="y", scaleratio=1,
        ),
        yaxis=dict(
            title="Z (cm)", range=[-lim, lim], zeroline=False,
            gridcolor="#2d3640", color="#e8eaed",
        ),
        uirevision="pantalla",
    )
    return fig


def calculadora(
    Simetria, a, b, datax, datay,
    modo_beam, angle, cofb1, coefb2, keV, theta_deg,
    reconstruct, A1, A2, personalizacion,
    distancia_cm=15.0, radio_cm=10.0,
    rotacion_deg=0.0,
):
    """
    Red recíproca 3D (RHEED).

    theta_deg entra en k_i. distancia_cm y radio_cm son la geometría
    de la pantalla; todavía no se dibuja.

    personalizacion: dict o lista.
      varillas, b1, b2, bz, recon, ewald, k_ewald, ejes, leyenda
    reconstruct + A1, A2 → densifica la red con puntos fraccionarios A1×A2
    """
    ver_varillas = _activo(personalizacion, "varillas")

    ki = radio_ewald(keV)
    incidencia_deg = _flotante(theta_deg, 2.0)
    L_cm = _flotante(distancia_cm, 15.0)
    R_cm = _flotante(radio_cm, 10.0)

    malla = malla_reciproca(Simetria, a, b, datax, datay, reconstruct, A1, A2)
    if malla is None:
        return go.Figure()

    nodos = malla["nodos"]
    recon_nodos = malla["recon_nodos"]
    b1 = malla["b1"]
    b2 = malla["b2"]
    b3 = malla["b3"]
    xlim = malla["xlim"]
    ylim = malla["ylim"]
    A1i = malla["A1i"]
    A2i = malla["A2i"]

    zlim = max(xlim, ylim)
    z_arrow = (0.5 * zlim) if ver_varillas else (1.2 * zlim)
    vectores = np.vstack([b1, b2, np.array([0.0, 0.0, z_arrow])])

    k_vec = haz_incidente(
        Simetria, a, b, modo_beam, angle, cofb1, coefb2,
        keV, incidencia_deg, rotacion_deg,
    )
    A1_corte = A1i if reconstruct else 1
    A2_corte = A2i if reconstruct else 1
    cortes = claves_que_cortan(k_vec, b1, b2, A1_corte, A2_corte) if k_vec is not None else set()

    # 2) Varillas
    if ver_varillas:
        z_vals = 0.5 * np.linspace(-zlim, zlim, 100)
        z_range = [z_vals[0], z_vals[-1]]
    else:
        z_vals = []
        z_range = [-1.3 * zlim, 1.3 * zlim]

    hover = "(%{customdata[0]}, %{customdata[1]})<extra></extra>"

    def _varillas(lista_nodos, solo_corte):
        xs, ys, zs, cd = [], [], [], []
        for i, j, x, y in lista_nodos:
            clave = (int(round(float(i) * A1_corte)), int(round(float(j) * A2_corte)))
            if (clave in cortes) != solo_corte:
                continue
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

    xs, ys, zs, cd = _varillas(nodos, False)
    cxs, cys, czs, ccd = _varillas(nodos, True)
    if ver_varillas and recon_nodos:
        rxs, rys, rzs, rcd = _varillas(recon_nodos, False)
        rcx, rcy, rcz, rccd = _varillas(recon_nodos, True)
    else:
        rxs, rys, rzs, rcd = [], [], [], []
        rcx, rcy, rcz, rccd = [], [], [], []

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

    if ver_varillas:
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="lines",
            line=dict(width=4, color=COLORES["varilla"]),
            customdata=cd,
            hovertemplate=hover,
            name="varillas 1×1",
        ))
        if cxs:
            fig.add_trace(go.Scatter3d(
                x=cxs, y=cys, z=czs,
                mode="lines",
                line=dict(width=6, color=COLORES["corte"]),
                customdata=ccd,
                hovertemplate=hover,
                name="varillas 1×1 que cortan",
            ))
        if rxs:
            fig.add_trace(go.Scatter3d(
                x=rxs, y=rys, z=rzs,
                mode="lines",
                line=dict(width=3, color=COLORES["varilla_recon"]),
                customdata=rcd,
                hovertemplate=hover,
                name=f"varillas recon {A1i}×{A2i}",
            ))
        if rcx:
            fig.add_trace(go.Scatter3d(
                x=rcx, y=rcy, z=rcz,
                mode="lines",
                line=dict(width=6, color=COLORES["corte_recon"]),
                customdata=rccd,
                hovertemplate=hover,
                name=f"varillas recon {A1i}×{A2i} que cortan",
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

    ver_b1 = _activo(personalizacion, "b1")
    ver_b2 = _activo(personalizacion, "b2")
    ver_b3 = _activo(personalizacion, "b3")
    ver_bz = _activo(personalizacion, "bz")
    ver_recon = _activo(personalizacion, "recon")
    ver_ewald = _activo(personalizacion, "ewald")
    ver_k = _activo(personalizacion, "k_ewald")
    ver_ejes = _activo(personalizacion, "ejes")

    # k_i ya está en k_vec. La flecha y la esfera lo usan si su casilla está activa.
    k_hat = None
    if k_vec is not None and (ver_ewald or ver_k):
        k_hat = k_vec / np.linalg.norm(k_vec)

    # 5a) Ejes cartesianos
    if ver_ejes:
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

    # 5b) Cada vector primitivo, con su casilla y su color
    primitivos = [
        (ver_b1, "b₁", vectores[0], COLORES["b1"]),
        (ver_b2, "b₂", vectores[1], COLORES["b2"]),
        (ver_bz, "b_z", vectores[2], COLORES["bz"]),
    ]
    if b3 is not None:
        primitivos.append((ver_b3, "b₃", b3, COLORES["b3"]))
    for visible, nombre, vec, color in primitivos:
        if not visible:
            continue
        etiqueta = f"{nombre} ({vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f})"
        _flecha(vec, nombre, color, width=9, tip_frac=0.20, text_size=15, etiqueta=etiqueta)

    # 5c) Reconstrucción: una sola casilla para b₁* y b₂*
    if ver_recon and reconstruct and (A1i > 1 or A2i > 1):
        b1_star = b1 / A1i
        b2_star = b2 / A2i
        _flecha(
            b1_star, f"b₁* (=b₁/{A1i})", COLORES["b1s"], width=7, tip_frac=0.22,
            text_size=14,
            etiqueta=f"b₁* recon ({b1_star[0]:.2f}, {b1_star[1]:.2f}, {b1_star[2]:.2f})",
        )
        _flecha(
            b2_star, f"b₂* (=b₂/{A2i})", COLORES["b2s"], width=7, tip_frac=0.22,
            text_size=14,
            etiqueta=f"b₂* recon ({b2_star[0]:.2f}, {b2_star[1]:.2f}, {b2_star[2]:.2f})",
        )

    # 5d) Vector k: segmento que llega al origen (la punta es el centro de la red)
    if ver_k and k_hat is not None:
        largo_visible = 0.65 * float(min(xlim, ylim))
        inicio = -k_hat * largo_visible
        color_k = COLORES["k"]
        fig.add_trace(go.Scatter3d(
            x=[inicio[0], 0], y=[inicio[1], 0], z=[inicio[2], 0],
            mode="lines",
            line=dict(width=8, color=color_k),
            name=f"k Ewald (|k|={ki:.2f} Å⁻¹, θ={incidencia_deg:.2f}°)",
            legendgroup="flecha:k",
            showlegend=True,
        ))
        fig.add_trace(go.Cone(
            x=[0], y=[0], z=[0],
            u=[k_hat[0]], v=[k_hat[1]], w=[k_hat[2]],
            sizemode="absolute",
            sizeref=0.18 * largo_visible,
            anchor="tip",
            colorscale=[[0, color_k], [1, color_k]],
            showscale=False,
            legendgroup="flecha:k",
            showlegend=False,
            hoverinfo="skip",
            name="k Ewald",
        ))
        fig.add_trace(go.Scatter3d(
            x=[inicio[0]], y=[inicio[1]], z=[inicio[2]],
            mode="text",
            text=["k"],
            textfont=dict(color=color_k, size=16, family="Arial Black, sans-serif"),
            legendgroup="flecha:k",
            showlegend=False,
            hoverinfo="skip",
            name="k Ewald",
        ))

    if ver_ejes or ver_b1 or ver_b2 or ver_b3 or ver_bz or ver_recon or ver_k:
        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode="markers+text",
            marker=dict(size=8, color="#ffd60a", line=dict(width=2, color="#000")),
            text=["Origen (0, 0, 0)"],
            textposition="bottom center",
            textfont=dict(color="#ffd60a", size=12),
            name="Origen (0, 0, 0)",
            showlegend=True,
        ))

    # 6) Esfera de Ewald: radio |k|, centro en −k (pasa por el origen)
    if ver_ewald and k_hat is not None:
        aux = np.array([0.0, 0.0, 1.0]) if abs(k_hat[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        e1 = np.cross(k_hat, aux)
        e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(k_hat, e1)

        radio_corte = float(np.hypot(xlim, ylim))
        if radio_corte >= 2 * ki:
            beta_max = np.pi
        else:
            cos_max = 1.0 - 0.5 * (radio_corte / ki) ** 2
            beta_max = float(np.arccos(np.clip(cos_max, -1.0, 1.0)))

        betas = np.linspace(0, min(np.pi, beta_max * 1.15), 36)
        alfas = np.linspace(0, 2 * np.pi, 72)
        B, A = np.meshgrid(betas, alfas, indexing="ij")
        n = (
            np.cos(B)[..., None] * k_hat
            + np.sin(B)[..., None] * (np.cos(A)[..., None] * e1 + np.sin(A)[..., None] * e2)
        )
        centro = -ki * k_hat
        pts = centro + ki * n
        Xs, Ys, Zs = pts[..., 0], pts[..., 1], pts[..., 2]

        fig.add_trace(go.Surface(
            x=Xs, y=Ys, z=Zs,
            surfacecolor=np.zeros_like(Xs),
            colorscale=[[0, COLORES["esfera"]], [1, COLORES["esfera"]]],
            opacity=0.28,
            showscale=False,
            name=f"Ewald |k|={ki:.2f} Å⁻¹",
            showlegend=True,
            hoverinfo="skip",
            lighting=dict(ambient=0.95, diffuse=0.3, specular=0.05),
        ))

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
    if ver_varillas:
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

    mostrar_leyenda = _activo(personalizacion, "leyenda", default=True)

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
        meta=dict(theta_deg=incidencia_deg, L_cm=L_cm, R_cm=R_cm),
    )
    return fig
