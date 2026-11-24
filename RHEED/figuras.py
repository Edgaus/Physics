"""Figuras de RHEED. Los cálculos están en fisica.py."""
import numpy as np
import plotly.graph_objects as go

try:
    from .fisica import (
        _flotante,
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
    "varilla": "#ffffff",          # red 1×1, un solo blanco
    "corte": "#7dffb3",            # 1×1 dentro de la esfera, y en el fósforo
    "varilla_recon": "#ffe14a",    # reconstrucción, un solo amarillo
    "corte_recon": "#ff5c33",      # reconstrucción dentro de la esfera, y en el fósforo
}


def _cuerda_en_esfera(punto, eje, centro, radio):
    """Extremos, sobre el eje de la normal, del tramo de varilla dentro de la esfera."""
    punto = np.asarray(punto, dtype=float)
    centro = np.asarray(centro, dtype=float)
    d2 = 0.0
    for k in range(3):
        if k == eje:
            continue
        d2 += (punto[k] - centro[k]) ** 2
    resto = float(radio) * float(radio) - d2
    if resto < 1e-10:
        return None
    semi = float(np.sqrt(resto))
    return float(centro[eje] - semi), float(centro[eje] + semi)


def _punto_en_esfera(punto, centro, radio):
    """El origen, sobre la superficie, cuenta como dentro."""
    d = np.asarray(punto, dtype=float) - np.asarray(centro, dtype=float)
    limite = float(radio) * float(radio) + 1e-6
    return float(np.dot(d, d)) <= limite


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


def _zonas_desde_puntos(puntos, R):
    """Círculos de Laue a partir de los puntos, si fisica.py no los manda.

    Los de una misma fila caen a la misma distancia del origen de la pantalla.
    """
    radios = sorted(float(np.hypot(Y, Z)) for Y, Z, *_ in puntos if np.hypot(Y, Z) <= float(R) + 1e-6)
    if not radios:
        return []
    grupos = [[radios[0]]]
    for radio in radios[1:]:
        if radio - grupos[-1][-1] <= 0.2:
            grupos[-1].append(radio)
        else:
            grupos.append([radio])
    signos = str.maketrans("-0123456789", "₋₀₁₂₃₄₅₆₇₈₉")
    zonas = []
    for grupo in grupos:
        if len(grupo) < 2 and grupo[0] > 1.0:
            continue
        radio = float(np.mean(grupo))
        if radio <= 0.0:
            continue
        zonas.append({
            "etiqueta": "L" + str(len(zonas)).translate(signos),
            "radio": radio,
        })
    return zonas


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

    zonas = datos.get("zonas") or _zonas_desde_puntos(datos["red"] + datos["recon"], R)
    for indice, zona in enumerate(zonas):
        radio = float(zona["radio"])
        if radio <= 0.0:
            continue
        # Rayas amarillas sobre el semicírculo Z ≥ 0. El punteado de Plotly
        # no se ve en esta vista, así que el hueco va en las coordenadas.
        trazo, claro = 0.55, 0.38
        paso = trazo + claro
        n_trazos = max(6, int(np.pi * radio / paso))
        xs, zs = [], []
        for k in range(n_trazos):
            a0 = k * paso / radio
            if a0 >= np.pi:
                break
            a1 = min(a0 + trazo / radio, np.pi)
            aa = np.linspace(a0, a1, 8)
            xs.extend(radio * np.cos(aa))
            zs.extend(radio * np.sin(aa))
            xs.append(None)
            zs.append(None)
        if not xs:
            continue
        fig.add_trace(go.Scatter(
            x=xs,
            y=zs,
            mode="lines",
            line=dict(color="#ffe14a", width=3),
            name="zonas de Laue",
            legendgroup="laue",
            showlegend=indice == 0,
            hovertemplate=f"{zona['etiqueta']}<extra></extra>",
        ))
        marca = np.deg2rad(155.0)
        fig.add_annotation(
            x=float(radio * np.cos(marca)),
            y=float(radio * np.sin(marca)),
            text=zona["etiqueta"],
            showarrow=False,
            xanchor="right",
            yanchor="middle",
            font=dict(color="#1a1400", size=15),
            bgcolor="#ffe14a",
            borderpad=3,
        )

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


def _cota_origen(nodos, b1, b2, Simetria, a, b):
    """Vecina más cercana al origen y texto de la separación en Å⁻¹."""
    candidatos = []
    for i, j, x, y, z in nodos:
        if i == 0 and j == 0:
            continue
        radio = float(np.linalg.norm((x, y, z)))
        if radio > 0.0:
            candidatos.append((radio, i, j, float(x), float(y), float(z)))
    if not candidatos:
        return None
    radio, i, j, x, y, z = min(candidatos, key=lambda fila: (fila[0], abs(fila[1]) + abs(fila[2])))

    a_val = float(a)
    b_val = float(a if b in (None, "") else b)
    dos_pi_a = 2.0 * np.pi / a_val
    dos_pi_b = 2.0 * np.pi / b_val
    tol = 1e-6 * max(dos_pi_a, dos_pi_b, radio)

    if Simetria == "RECT" and abs(radio - dos_pi_a) <= tol:
        texto = f"2π/a = {radio:.3f} Å⁻¹"
    elif Simetria == "RECT" and abs(radio - dos_pi_b) <= tol:
        texto = f"2π/b = {radio:.3f} Å⁻¹"
    elif Simetria == "HEX" and abs(radio - 4.0 * np.pi / (a_val * np.sqrt(3))) <= tol:
        texto = f"4π/(a√3) = {radio:.3f} Å⁻¹"
    elif Simetria == "CENT" and abs(radio - dos_pi_a * np.sqrt(2)) <= tol:
        texto = f"(2π/a)√2 = {radio:.3f} Å⁻¹"
    else:
        texto = f"|G| = {radio:.3f} Å⁻¹"
    return {
        "punto": np.array([x, y, z]),
        "radio": radio,
        "texto": texto,
        "indices": (i, j),
    }


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
      varillas, b1, b2, bz, recon, ewald, k_ewald, ejes, leyenda, separacion
    reconstruct + A1, A2 → densifica la red con puntos fraccionarios A1×A2
    """
    ver_varillas = _activo(personalizacion, "varillas")
    ver_ewald = _activo(personalizacion, "ewald")
    ver_separacion = _activo(personalizacion, "separacion", default=True)
    ver_recon = _activo(personalizacion, "recon", default=True)

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
    iu, iv, inn = malla.get("ejes", (0, 1, 2))
    A1i = malla["A1i"]
    A2i = malla["A2i"]

    # xlim, ylim son los semiejes del plano recíproco (u, v), no siempre x e y.
    ancho = [0.0, 0.0, 0.0]
    ancho[iu] = float(xlim)
    ancho[iv] = float(ylim)
    medio = max(float(xlim), float(ylim), 1e-6)
    zlim = medio
    largo_varilla = (0.5 * medio) if ver_varillas else (1.2 * medio)
    normal_vec = np.zeros(3)
    normal_vec[inn] = largo_varilla
    vectores = np.vstack([b1, b2, normal_vec])
    nombre_normal = "x̂" if inn == 0 else "b_z"

    k_vec = haz_incidente(
        Simetria, a, b, modo_beam, angle, cofb1, coefb2,
        keV, incidencia_deg, rotacion_deg,
    )
    ver_k = _activo(personalizacion, "k_ewald")
    centro_ewald = None
    k_hat = None
    if k_vec is not None and (ver_ewald or ver_k):
        k_vec = np.asarray(k_vec, dtype=float)
        norma_k = float(np.linalg.norm(k_vec))
        if norma_k > 0.0:
            k_hat = k_vec / norma_k
            centro_ewald = -k_vec
            ki = norma_k

    # 2) Varillas, paralelas a la normal. En la red centrada esa normal es x.
    t0_varilla, t1_varilla = -0.5 * zlim, 0.5 * zlim
    if ver_varillas:
        z_range = [t0_varilla, t1_varilla]
    else:
        z_range = [-1.3 * zlim, 1.3 * zlim]
    colorear_esfera = ver_ewald and centro_ewald is not None

    hover = "(%{customdata[0]}, %{customdata[1]})<extra></extra>"

    def _segmento(buf, punto, ta, tb, i, j):
        if tb - ta < 1e-8:
            return
        a = np.array(punto, dtype=float)
        b = np.array(punto, dtype=float)
        a[inn] = ta
        b[inn] = tb
        xs, ys, zs, cd = buf
        xs.extend((a[0], b[0], None))
        ys.extend((a[1], b[1], None))
        zs.extend((a[2], b[2], None))
        cd.extend(((i, j), (i, j), (None, None)))

    def _partir_varillas(lista_nodos):
        fuera = ([], [], [], [])
        dentro = ([], [], [], [])
        if not ver_varillas:
            return fuera, dentro
        for i, j, x, y, z in lista_nodos:
            punto = (x, y, z)
            cuerda = (
                _cuerda_en_esfera(punto, inn, centro_ewald, ki) if colorear_esfera else None
            )
            if cuerda is None:
                _segmento(fuera, punto, t0_varilla, t1_varilla, i, j)
                continue
            lo, hi = cuerda
            _segmento(fuera, punto, t0_varilla, min(t1_varilla, lo), i, j)
            _segmento(fuera, punto, max(t0_varilla, hi), t1_varilla, i, j)
            _segmento(dentro, punto, lo, hi, i, j)
        return fuera, dentro

    def _partir_puntos(lista_nodos):
        fuera, dentro = [], []
        for i, j, x, y, z in lista_nodos:
            punto = (i, j, x, y, z)
            if colorear_esfera and _punto_en_esfera((x, y, z), centro_ewald, ki):
                dentro.append(punto)
            else:
                fuera.append(punto)
        return fuera, dentro

    xs, ys, zs, cd = [], [], [], []
    dxs, dys, dzs, dcd = [], [], [], []
    rxs, rys, rzs, rcd = [], [], [], []
    rdxs, rdys, rdzs, rdcd = [], [], [], []
    if ver_varillas:
        (xs, ys, zs, cd), (dxs, dys, dzs, dcd) = _partir_varillas(nodos)
        if ver_recon and recon_nodos:
            (rxs, rys, rzs, rcd), (rdxs, rdys, rdzs, rdcd) = _partir_varillas(recon_nodos)
    nodos_fuera, nodos_dentro = _partir_puntos(nodos)
    if ver_recon:
        recon_fuera, recon_dentro = _partir_puntos(recon_nodos)
    else:
        recon_fuera, recon_dentro = [], []

    def _coords_puntos(lista):
        return (
            [n[2] for n in lista],
            [n[3] for n in lista],
            [n[4] for n in lista],
            [(n[0], n[1]) for n in lista],
        )

    # Malla del plano recíproco. Centrada: yz. Las demás: xy.
    if inn == 0:
        yy = np.linspace(-ancho[1], ancho[1], 40)
        zz = np.linspace(-ancho[2], ancho[2], 40)
        YY, ZZ = np.meshgrid(yy, zz)
        XX = np.zeros_like(YY)
        nombre_plano = "plano yz"
        color_plano = ZZ
    else:
        xx = np.linspace(-ancho[0], ancho[0], 40)
        yy = np.linspace(-ancho[1], ancho[1], 40)
        XX, YY = np.meshgrid(xx, yy)
        ZZ = np.zeros_like(XX)
        nombre_plano = "plano xy"
        color_plano = XX

    # 4) Figura
    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=XX,
        y=YY,
        z=ZZ,
        surfacecolor=color_plano,
        colorscale="Blues",
        opacity=0.22,
        showscale=False,
        showlegend=False,
        name=nombre_plano,
        hoverinfo="skip",
    ))

    def _trazo_varillas(vx, vy, vz, vcd, color, nombre, ancho=4):
        if not vx:
            return
        fig.add_trace(go.Scatter3d(
            x=vx, y=vy, z=vz,
            mode="lines",
            line=dict(width=ancho, color=color),
            customdata=vcd,
            hovertemplate=hover,
            name=nombre,
        ))

    if ver_varillas:
        _trazo_varillas(xs, ys, zs, cd, COLORES["varilla"], "varillas 1×1")
        _trazo_varillas(
            dxs, dys, dzs, dcd, COLORES["corte"], "varillas 1×1 dentro de la esfera", 7,
        )
        _trazo_varillas(rxs, rys, rzs, rcd, COLORES["varilla_recon"], f"varillas recon {A1i}×{A2i}")
        _trazo_varillas(
            rdxs, rdys, rdzs, rdcd, COLORES["corte_recon"],
            f"varillas recon {A1i}×{A2i} dentro de la esfera", 7,
        )

    # Cota solo desde el origen hasta su vecina más cercana.
    if ver_separacion:
        cota = _cota_origen(nodos, b1, b2, Simetria, a, b)
        if cota is not None:
            p = cota["punto"]
            radio = cota["radio"]
            direccion = p / radio
            n_hat = np.zeros(3)
            n_hat[inn] = 1.0
            lateral = np.cross(n_hat, direccion)
            norma_lat = float(np.linalg.norm(lateral))
            if norma_lat < 1e-8:
                apoyo = np.array([0.0, 1.0, 0.0]) if inn == 0 else np.array([1.0, 0.0, 0.0])
                lateral = np.cross(n_hat, apoyo)
                norma_lat = float(np.linalg.norm(lateral))
            lateral = lateral / norma_lat
            marca = 0.08 * radio
            elevacion = 0.04 * max(xlim, ylim, radio)
            a0 = elevacion * n_hat
            a1 = p + a0
            color_cota = "#ffe14a"
            fig.add_trace(go.Scatter3d(
                x=[
                    a0[0] - marca * lateral[0], a0[0] + marca * lateral[0], None,
                    a0[0], a1[0], None,
                    a1[0] - marca * lateral[0], a1[0] + marca * lateral[0],
                ],
                y=[
                    a0[1] - marca * lateral[1], a0[1] + marca * lateral[1], None,
                    a0[1], a1[1], None,
                    a1[1] - marca * lateral[1], a1[1] + marca * lateral[1],
                ],
                z=[
                    a0[2] - marca * lateral[2], a0[2] + marca * lateral[2], None,
                    a0[2], a1[2], None,
                    a1[2] - marca * lateral[2], a1[2] + marca * lateral[2],
                ],
                mode="lines",
                line=dict(width=5, color=color_cota),
                name=cota["texto"],
                legendgroup="separacion",
                showlegend=True,
                hovertemplate=cota["texto"] + "<extra></extra>",
            ))
            ancla = 0.5 * (a0 + a1) + 0.12 * radio * lateral
            fig.add_trace(go.Scatter3d(
                x=[ancla[0]], y=[ancla[1]], z=[ancla[2]],
                mode="text",
                text=[cota["texto"]],
                textposition="middle center",
                textfont=dict(color=color_cota, size=22, family="Arial Black, sans-serif"),
                legendgroup="separacion",
                showlegend=False,
                hoverinfo="skip",
                name=cota["texto"],
            ))

    def _trazo_puntos(lista, color, nombre, size):
        if not lista:
            return
        px, py, pz, pcd = _coords_puntos(lista)
        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz,
            mode="markers",
            marker=dict(size=size, color=color, line=dict(width=1, color="#0f1419")),
            customdata=pcd,
            hovertemplate=hover,
            name=nombre,
        ))

    _trazo_puntos(nodos_fuera, "#ffffff", "nodos", 5)
    _trazo_puntos(nodos_dentro, COLORES["corte"], "nodos 1×1 dentro de la esfera", 8)
    _trazo_puntos(recon_fuera, COLORES["varilla_recon"], f"recon {A1i}×{A2i}", 4)
    _trazo_puntos(
        recon_dentro, COLORES["corte_recon"], f"recon {A1i}×{A2i} dentro de la esfera", 7,
    )

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
    ver_ejes = _activo(personalizacion, "ejes")

    # 5a) Ejes cartesianos. El de la normal es el de las varillas.
    def _rango_eje(indice):
        if indice == inn:
            return float(z_range[0]), float(z_range[1])
        mitad = ancho[indice] if ancho[indice] > 0.0 else medio
        return -mitad, mitad

    rx = _rango_eje(0)
    ry = _rango_eje(1)
    rz = _rango_eje(2)

    if ver_ejes:
        eje_x = np.array([0.85 * rx[1], 0.0, 0.0])
        eje_y = np.array([0.0, 0.85 * ry[1], 0.0])
        eje_z = np.array([0.0, 0.0, 0.85 * rz[1]])
        _flecha(
            eje_x, "x̂", "#4cc9f0", width=7, tip_frac=0.14, text_size=16,
            etiqueta=f"eje x̂ (±{rx[1]:.2f} Å⁻¹)", con_cono=inn == 0,
        )
        _flecha(
            eje_y, "ŷ", "#80ed99", width=7, tip_frac=0.14, text_size=16,
            etiqueta=f"eje ŷ (±{ry[1]:.2f} Å⁻¹)", con_cono=False,
        )
        _flecha(
            eje_z, "ẑ", "#f8f9fa", width=6, tip_frac=0.16, text_size=16,
            etiqueta=f"eje ẑ (±{rz[1]:.2f} Å⁻¹)", con_cono=inn == 2,
        )
        fig.add_trace(go.Scatter3d(
            x=[rx[0], rx[1], None, 0, 0, None, 0, 0],
            y=[0, 0, None, ry[0], ry[1], None, 0, 0],
            z=[0, 0, None, 0, 0, None, rz[0], rz[1]],
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
        (ver_bz, nombre_normal, vectores[2], COLORES["bz"]),
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

    # 5d) k_i a escala real: va del centro de Ewald (−k_i) al origen.
    #     El centro está a −k_⊥ sobre la normal, no en el plano de las varillas.
    if k_hat is not None and k_vec is not None and centro_ewald is not None:
        centro_ewald = -np.asarray(k_vec, dtype=float)
        color_k = COLORES["k"]
        if ver_k:
            tip_size = max(0.08 * ki, 0.05 * float(min(xlim, ylim)))
            fig.add_trace(go.Scatter3d(
                x=[centro_ewald[0], 0],
                y=[centro_ewald[1], 0],
                z=[centro_ewald[2], 0],
                mode="lines",
                line=dict(width=8, color=color_k),
                name=f"kᵢ (|k|={ki:.2f} Å⁻¹, θ={incidencia_deg:.2f}°)",
                legendgroup="flecha:k",
                showlegend=True,
                hovertemplate=(
                    f"kᵢ = ({k_vec[0]:.3f}, {k_vec[1]:.3f}, {k_vec[2]:.3f}) Å⁻¹"
                    "<extra></extra>"
                ),
            ))
            fig.add_trace(go.Cone(
                x=[0], y=[0], z=[0],
                u=[k_hat[0]], v=[k_hat[1]], w=[k_hat[2]],
                sizemode="absolute",
                sizeref=tip_size,
                anchor="tip",
                colorscale=[[0, color_k], [1, color_k]],
                showscale=False,
                legendgroup="flecha:k",
                showlegend=False,
                hoverinfo="skip",
                name="kᵢ",
            ))
        if ver_ewald or ver_k:
            # −k_∥ es −k_i con la normal en cero. En la red centrada esa normal es x.
            k_vec = np.asarray(k_vec, dtype=float)
            paralelo = k_vec.copy()
            paralelo[inn] = 0.0
            k_par = float(np.linalg.norm(paralelo))
            k_perp = float(k_vec[inn])
            proy = centro_ewald.copy()
            proy[inn] = 0.0
            plano = "yz" if inn == 0 else "xy"
            fig.add_trace(go.Scatter3d(
                x=[centro_ewald[0]],
                y=[centro_ewald[1]],
                z=[centro_ewald[2]],
                mode="markers+text",
                marker=dict(size=9, color=color_k, symbol="diamond",
                            line=dict(width=1, color="#ffffff")),
                text=["−kᵢ (centro)"],
                textposition="top center",
                textfont=dict(color=color_k, size=13, family="Arial Black, sans-serif"),
                name=f"centro Ewald −kᵢ ({centro_ewald[0]:.2f}, {centro_ewald[1]:.2f}, {centro_ewald[2]:.2f})",
                legendgroup="centro-ewald",
                showlegend=True,
                hovertemplate=(
                    f"centro = −kᵢ<br>"
                    f"({centro_ewald[0]:.3f}, {centro_ewald[1]:.3f}, {centro_ewald[2]:.3f}) Å⁻¹<br>"
                    f"|k_∥|={k_par:.3f}, k_⊥={k_perp:.3f}"
                    "<extra></extra>"
                ),
            ))
            fig.add_trace(go.Scatter3d(
                x=[centro_ewald[0], proy[0]],
                y=[centro_ewald[1], proy[1]],
                z=[centro_ewald[2], proy[2]],
                mode="lines",
                line=dict(width=3, color=color_k, dash="dot"),
                name=f"proyección −k_∥ ({plano})",
                legendgroup="centro-ewald",
                showlegend=True,
                hovertemplate=f"proyección de −kᵢ sobre el plano {plano}<extra></extra>",
            ))
            fig.add_trace(go.Scatter3d(
                x=[proy[0]],
                y=[proy[1]],
                z=[proy[2]],
                mode="markers+text",
                marker=dict(size=6, color="#9aa0a6"),
                text=["−k_∥"],
                textposition="bottom center",
                textfont=dict(color="#9aa0a6", size=12),
                legendgroup="centro-ewald",
                showlegend=False,
                hovertemplate=(
                    f"−k_∥ = ({proy[0]:.3f}, {proy[1]:.3f}, {proy[2]:.3f})"
                    "<extra></extra>"
                ),
                name="−k_∥",
            ))

    if ver_ejes or ver_b1 or ver_b2 or ver_b3 or ver_bz or ver_recon or ver_k or ver_ewald:
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

    # 6) Esfera de Ewald: radio |k|, centro en −k_i (pasa por el origen)
    if ver_ewald and k_hat is not None and centro_ewald is not None:
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
        pts = centro_ewald + ki * n
        Xs, Ys, Zs = pts[..., 0], pts[..., 1], pts[..., 2]

        fig.add_trace(go.Surface(
            x=Xs, y=Ys, z=Zs,
            surfacecolor=np.zeros_like(Xs),
            colorscale=[[0, COLORES["esfera"]], [1, COLORES["esfera"]]],
            opacity=0.28,
            showscale=False,
            name=f"Ewald |k|={ki:.2f} Å⁻¹ · centro −kᵢ",
            showlegend=True,
            hoverinfo="skip",
            lighting=dict(ambient=0.95, diffuse=0.3, specular=0.05),
        ))

    titulo = f"Red {Simetria}"
    if reconstruct and (A1i > 1 or A2i > 1):
        titulo += f" · reconstrucción {A1i}×{A2i}"

    # Con la esfera, el eje de la normal toma el largo del plano para que
    # el casquete no se vea elíptico. En la red centrada ese eje es x.
    if ver_ewald and centro_ewald is not None:
        if inn == 0:
            rx = (-medio, medio)
        elif inn == 1:
            ry = (-medio, medio)
        else:
            rz = (-medio, medio)
    x_min, x_max = rx
    y_min, y_max = ry
    z_min, z_max = rz

    axis_style = dict(
        backgroundcolor="#1a1f26",
        gridcolor="#2d3640",
        zerolinecolor="#4a5560",
        showbackground=True,
        color="#9aa0a6",
    )
    def _kw_eje(indice, titulo, lo, hi):
        if ver_varillas or indice != inn:
            return dict(
                range=[lo, hi],
                title=f"{titulo} (Å⁻¹)",
                showticklabels=True,
                ticks="outside",
                **axis_style,
            )
        return dict(
            range=[lo, hi],
            title=titulo,
            showticklabels=False,
            ticks="",
            showspikes=False,
            **axis_style,
        )

    xaxis_kw = _kw_eje(0, "x", x_min, x_max)
    yaxis_kw = _kw_eje(1, "y", y_min, y_max)
    zaxis_kw = _kw_eje(2, "z", z_min, z_max)

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
            xaxis=xaxis_kw,
            yaxis=yaxis_kw,
            zaxis=zaxis_kw,
            aspectmode="data",
            # Vista por defecto similar a la captura (casi cenital, ligeramente inclinada)
            camera=dict(
                eye=dict(x=1.85, y=-1.55, z=0.15) if inn == 0 else dict(x=0.15, y=-1.55, z=1.85),
                center=dict(x=0, y=0, z=-0.05),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        uirevision="rheed-yz" if inn == 0 else "rheed",
        title=dict(text=titulo, font=dict(color="#e8eaed", size=16)),
        meta=dict(theta_deg=incidencia_deg, L_cm=L_cm, R_cm=R_cm),
    )
    return fig
