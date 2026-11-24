"""Cálculos de RHEED: red recíproca, haz, esfera de Ewald y pantalla.

Este módulo no dibuja. Las figuras están en figuras.py.
"""
import numpy as np


def _flotante(valor, defecto):
    try:
        if valor in (None, ""):
            return float(defecto)
        return float(valor)
    except (TypeError, ValueError):
        return float(defecto)


def radio_ewald(keV):
    """|k| no relativista en Å⁻¹. E en keV, ℏc ≈ 1973.27 eV·Å, E0 = 511 keV."""
    try:
        E_eV = float(keV) * 1e3
    except (TypeError, ValueError):
        return 0.0
    if E_eV <= 0:
        return 0.0
    return float(np.sqrt(2 * 511e3 * E_eV) / 1973.270)


def componentes_ki(keV, theta_deg, phi_deg=None, direccion=None, b1=None, b2=None):
    """Componentes de k_i a partir de la energía y el ángulo rasante θ.

    El módulo es |k|(E). En el plano, |k_∥| = |k| cos θ.
    La normal +z apunta hacia el vacío: k_⊥ = |k| sin θ ẑ.

    La dirección paralela se da de una sola forma:
    - phi_deg: azimut φ respecto a b1. Hacen falta b1 y b2.
      k_∥ = |k_∥| (cos φ  b1/|b1| + sin φ  b2/|b2|)
    - direccion: vector A, ya en el plano.
      k_∥ = |k| cos θ  A/|A|
      No es (M b1 + N b2)/sqrt(M²+N²): eso tiene módulo |b|.

    Devuelve k_i = (k_∥x, k_∥y, k_⊥).
    """
    radio = radio_ewald(keV)
    if radio == 0.0:
        raise ValueError("La energía tiene que ser mayor que cero.")

    theta = np.deg2rad(float(theta_deg))
    k_par_mod = radio * np.cos(theta)
    k_perp = radio * np.sin(theta)

    tiene_phi = phi_deg not in (None, "")
    tiene_dir = direccion is not None
    if tiene_phi == tiene_dir:
        raise ValueError("Indica el azimut φ o la dirección paralela, no ambos ni ninguno.")

    if tiene_phi:
        if b1 is None or b2 is None:
            raise ValueError("El azimut φ se mide desde b1: hacen falta b1 y b2.")
        b1 = np.asarray(b1, dtype=float).reshape(-1)[:2]
        b2 = np.asarray(b2, dtype=float).reshape(-1)[:2]
        n1 = float(np.linalg.norm(b1))
        n2 = float(np.linalg.norm(b2))
        if n1 == 0.0 or n2 == 0.0:
            raise ValueError("b1 y b2 tienen que ser distintos de cero.")
        phi = np.deg2rad(float(phi_deg))
        k_par = k_par_mod * (np.cos(phi) * b1 / n1 + np.sin(phi) * b2 / n2)
    else:
        A = np.asarray(direccion, dtype=float).reshape(-1)[:2]
        norma_A = float(np.linalg.norm(A))
        if norma_A == 0.0:
            raise ValueError("La dirección paralela no puede ser el vector cero.")
        k_par = k_par_mod * (A / norma_A)

    return np.array([k_par[0], k_par[1], k_perp], dtype=float)


def _base_real(Simetria, a, b):
    """a1, a2 en el plano. [u v] = u a1 + v a2 es la dirección del haz."""
    if Simetria == "RECT":
        return np.array([a, 0.0]), np.array([0.0, b])
    if Simetria == "CENT":
        # a1 = (a/2)(ŷ − ẑ), a2 = (a/2)(ŷ + ẑ). x̂ es la normal,
        # así que en el plano de la figura (x, y) = (y, z) del cristal.
        return np.array([a / 2, -a / 2]), np.array([a / 2, a / 2])
    return np.array([a, 0.0]), np.array([-0.5 * a, 0.5 * a * np.sqrt(3)])


def direccion_haz(Simetria, a, b, modo_beam, phi_deg, u, v):
    """Dirección paralela del haz. Azimut φ desde a1, o Miller [u v]."""
    a1, a2 = _base_real(Simetria, float(a), float(a if b in (None, "") else b))
    if modo_beam == "miller":
        try:
            uu = 0.0 if u in (None, "") else float(u)
            vv = 0.0 if v in (None, "") else float(v)
        except (TypeError, ValueError):
            uu, vv = 1.0, 0.0
        return uu * a1 + vv * a2
    try:
        phi = 0.0 if phi_deg in (None, "") else float(phi_deg)
    except (TypeError, ValueError):
        phi = 0.0
    phi = np.deg2rad(phi)
    a1h = a1 / np.linalg.norm(a1)
    perpendicular = np.array([-a1h[1], a1h[0]])
    return np.cos(phi) * a1h + np.sin(phi) * perpendicular


def _rotar_plano(v, grados):
    """Gira un vector del plano un ángulo en grados, sentido antihorario."""
    ang = np.deg2rad(_flotante(grados, 0.0))
    c, s = np.cos(ang), np.sin(ang)
    v = np.asarray(v, dtype=float).reshape(-1)[:2]
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]], dtype=float)


def direccion_muestra(Simetria, a, b, modo_beam, phi_deg, u, v, rotacion_deg=0.0):
    """Dirección del haz con la muestra girada φ alrededor de la normal.

    En azimut, φ es el ángulo desde a1. En Miller, [u v] se gira esos grados.
    """
    if modo_beam == "miller":
        base = direccion_haz(Simetria, a, b, "miller", phi_deg, u, v)
        return _rotar_plano(base, rotacion_deg)
    return direccion_haz(Simetria, a, b, "azimut", rotacion_deg, u, v)


def varillas_que_cortan(k_i, b1, b2, A1=1, A2=1):
    """k_f de las varillas que cortan la esfera de Ewald.

    k_i es el vector incidente; su módulo es el radio. Componentes (x, y)
    o (x, y, z): el plano de la superficie es xy.
    b1 y b2 son los primitivos del plano. B1 = b1/A1, B2 = b2/A2.

    G_ij = i B1 + j B2
    k_f,∥ = k_i,∥ + G_ij
    Corta si |k_i|² − |k_f,∥|² ≥ 0.
    k_f,⊥ = +sqrt(...)  (sale hacia el vacío)

    Devuelve una lista de k_f, cada uno un vector (k_fx, k_fy, k_f⊥).
    """
    k_i = np.asarray(k_i, dtype=float).reshape(-1)
    if k_i.size not in (2, 3):
        raise ValueError("k_i debe tener 2 o 3 componentes.")
    radio = float(np.linalg.norm(k_i))
    if radio == 0.0:
        return []

    b1 = np.asarray(b1, dtype=float).reshape(-1)[:2]
    b2 = np.asarray(b2, dtype=float).reshape(-1)[:2]
    A1i = max(1, int(round(float(A1))))
    A2i = max(1, int(round(float(A2))))
    B1 = b1 / A1i
    B2 = b2 / A2i
    if np.linalg.norm(B1) == 0.0 or np.linalg.norm(B2) == 0.0:
        raise ValueError("b1 y b2 tienen que ser distintos de cero.")

    k_i_par = k_i[:2]
    m_max = int(np.floor(2 * radio / np.linalg.norm(B1)))
    n_max = int(np.floor(2 * radio / np.linalg.norm(B2)))
    radio2 = radio * radio
    kfs = []

    for i in range(-m_max, m_max + 1):
        for j in range(-n_max, n_max + 1):
            k_f_par = k_i_par + i * B1 + j * B2
            resto = radio2 - float(np.dot(k_f_par, k_f_par))
            # θ = 0 deja |k_∥| un ulp por encima de |k| y el haz especular
            # desaparecía (resto ≈ −1e−15).
            if resto < -1e-8 * radio2:
                continue
            k_perp = float(np.sqrt(resto)) if resto > 0.0 else 0.0
            kfs.append(np.array([k_f_par[0], k_f_par[1], k_perp], dtype=float))
    return kfs


def claves_que_cortan(k_i, b1, b2, A1=1, A2=1):
    """Índices (i, j) de G = i b1/A1 + j b2/A2 que cortan la esfera."""
    k_i = np.asarray(k_i, dtype=float).reshape(-1)
    A1i = max(1, int(round(float(A1))))
    A2i = max(1, int(round(float(A2))))
    B1 = np.asarray(b1, dtype=float).reshape(-1)[:2] / A1i
    B2 = np.asarray(b2, dtype=float).reshape(-1)[:2] / A2i
    base = np.column_stack([B1, B2])
    try:
        inversa = np.linalg.inv(base)
    except np.linalg.LinAlgError:
        return set()

    claves = set()
    for k_f in varillas_que_cortan(k_i, b1, b2, A1i, A2i):
        coef = inversa @ (k_f[:2] - k_i[:2])
        claves.add((int(round(coef[0])), int(round(coef[1]))))
    return claves


def llegan_a_pantalla(kfs, L, r):
    """k_f que caen en el fósforo y su posición (Y, Z) sobre la pantalla.

    La muestra está en el origen. La pantalla es el plano x = L, un disco
    de radio r. L y r van en la misma unidad (cm en la interfaz); Y y Z
    salen en esa unidad.

    Y = L kf_y / kf_x
    Z = L kf_z / kf_x

    El punto entra si kf_x > 0, kf_z >= 0 y
    sqrt(kf_y² + kf_z²) <= (r/L) kf_x.
    Z = 0 es el borde de sombra.

    kfs es la lista que devuelve varillas_que_cortan.
    Devuelve una lista de (k_f, coordenada), con coordenada = [Y, Z].
    """
    L = float(L)
    r = float(r)
    if L <= 0.0:
        raise ValueError("La distancia a la pantalla tiene que ser mayor que cero.")
    if r < 0.0:
        raise ValueError("El radio de la pantalla no puede ser negativo.")

    llegadas = []
    for k_f in kfs:
        k_f = np.asarray(k_f, dtype=float).reshape(-1)
        if k_f.size != 3:
            raise ValueError("Cada k_f debe tener 3 componentes.")
        kx, ky, kz = (float(k_f[0]), float(k_f[1]), float(k_f[2]))
        if kx <= 0.0 or kz < 0.0:
            continue
        if np.hypot(ky, kz) > (r / L) * kx:
            continue
        coordenada = np.array([L * ky / kx, L * kz / kx], dtype=float)
        llegadas.append((k_f.copy(), coordenada))
    return llegadas


def _ejes_superficie(Simetria):
    """Índices (u, v, normal) del triedro.

    RECT y HEX: el plano recíproco es xy y la normal es z.
    CENT: el plano recíproco es yz y la normal es x.
    """
    if Simetria == "CENT":
        return (1, 2, 0)
    return (0, 1, 2)


def _a_lab(Simetria, u, v, normal=0.0):
    """Pasa componentes (u, v, normal) de la superficie al triedro x, y, z."""
    iu, iv, inn = _ejes_superficie(Simetria)
    punto = np.zeros(3)
    punto[iu] = float(u)
    punto[iv] = float(v)
    punto[inn] = float(normal)
    return punto


def _desde_lab(Simetria, vec):
    """(u, v) y la componente normal de un vector del triedro."""
    iu, iv, inn = _ejes_superficie(Simetria)
    vec = np.asarray(vec, dtype=float).reshape(-1)
    return np.array([float(vec[iu]), float(vec[iv])]), float(vec[inn])


def _primitivos_plano(Simetria, a, b):
    """b1, b2 en el plano de la superficie, en Å⁻¹.

    El par (u, v) es (x, y) salvo en la red centrada, donde es (y, z).
    """
    dos_pi_a = 2 * np.pi / float(a)
    lado_b = float(a if b in (None, "") else b)
    dos_pi_b = 2 * np.pi / lado_b
    if Simetria == "RECT":
        return np.array([dos_pi_a, 0.0]), np.array([0.0, dos_pi_b])
    if Simetria == "CENT":
        # b1 = (2π/a)(ŷ − ẑ), b2 = (2π/a)(ŷ + ẑ), en el plano (x, y) = (y, z).
        return np.array([dos_pi_a, -dos_pi_a]), np.array([dos_pi_a, dos_pi_a])
    if Simetria == "HEX":
        return (
            np.array([dos_pi_a, dos_pi_a / np.sqrt(3)]),
            np.array([-dos_pi_a, dos_pi_a / np.sqrt(3)]),
        )
    raise ValueError(f"Simetría desconocida: {Simetria}")


def _a_marco_pantalla(k_f, e_x, e_y):
    """k_f del cristal al marco de la pantalla: x hacia el fósforo."""
    k_f = np.asarray(k_f, dtype=float).reshape(-1)
    return np.array([
        float(np.dot(k_f[:2], e_x)),
        float(np.dot(k_f[:2], e_y)),
        float(k_f[2]),
    ])


def periodos(reconstruct, A1, A2):
    """A1, A2 enteros. Sin reconstrucción quedan en 1×1."""
    if not reconstruct:
        return 1, 1
    try:
        A1i = max(1, int(round(float(A1) if A1 not in (None, "") else 1)))
        A2i = max(1, int(round(float(A2) if A2 not in (None, "") else 1)))
    except (TypeError, ValueError):
        return 1, 1
    return A1i, A2i


def malla_reciproca(Simetria, a, b, datax, datay, reconstruct, A1, A2):
    """Nodos de la red 1×1, los de la reconstrucción y los vectores b.

    b1 y b2 van en el plano de la superficie. En hexagonal, b3 = -(b1 + b2).
    En la red centrada ese plano es yz y la normal es x. En las demás, xy y z.
    Devuelve None si la simetría no existe o la malla queda vacía.
    """
    try:
        b1_uv, b2_uv = _primitivos_plano(Simetria, a, b)
    except (ValueError, ZeroDivisionError, TypeError):
        return None

    b1 = _a_lab(Simetria, b1_uv[0], b1_uv[1])
    b2 = _a_lab(Simetria, b2_uv[0], b2_uv[1])
    b3 = -(b1 + b2) if Simetria == "HEX" else None
    ejes = _ejes_superficie(Simetria)

    dos_pi_a = 2 * np.pi / float(a)
    if Simetria == "RECT":
        xlim = datax * dos_pi_a
        ylim = datay * abs(b2[1])
    elif Simetria == "CENT":
        xlim = (datax + datay) * dos_pi_a
        ylim = (datax + datay) * dos_pi_a
    elif Simetria == "HEX":
        xlim = (datax + datay) * dos_pi_a
        ylim = (datax + datay) * dos_pi_a / np.sqrt(3)
    else:
        return None

    nodos = []
    for i in range(-int(datax), int(datax) + 1):
        for j in range(-int(datay), int(datay) + 1):
            punto = i * b1 + j * b2
            nodos.append((i, j, float(punto[0]), float(punto[1]), float(punto[2])))
    if not nodos:
        return None

    A1i, A2i = periodos(reconstruct, A1, A2)
    recon_nodos = []
    if reconstruct and (A1i > 1 or A2i > 1):
        for i in range(-int(datax), int(datax) + 1):
            for j in range(-int(datay), int(datay) + 1):
                for p in range(A1i):
                    for q in range(A2i):
                        if p == 0 and q == 0:
                            continue
                        fi = i + p / A1i
                        fj = j + q / A2i
                        punto = fi * b1 + fj * b2
                        recon_nodos.append((
                            fi, fj, float(punto[0]), float(punto[1]), float(punto[2]),
                        ))

    return {
        "nodos": nodos,
        "recon_nodos": recon_nodos,
        "b1": b1,
        "b2": b2,
        "b3": b3,
        "xlim": xlim,
        "ylim": ylim,
        "ejes": ejes,
        "A1i": A1i,
        "A2i": A2i,
    }


def haz_incidente(
    Simetria, a, b, modo_beam, angle, u, v, keV, theta_deg, rotacion_deg=0.0,
):
    """k_i, o None si no hay energía o la dirección en el plano es nula."""
    if radio_ewald(keV) <= 0.0:
        return None
    direccion = direccion_muestra(
        Simetria, a, b, modo_beam, angle, u, v, rotacion_deg,
    )
    if float(np.linalg.norm(direccion)) == 0.0:
        return None
    k_superficie = componentes_ki(keV, _flotante(theta_deg, 2.0), direccion=direccion)
    return _a_lab(Simetria, k_superficie[0], k_superficie[1], k_superficie[2])


def _paso_laue(alpha, beta):
    """Paso de G·ê entre zonas de Laue de la red 1×1, en Å⁻¹."""
    alpha, beta = abs(float(alpha)), abs(float(beta))
    if alpha < 1e-8 and beta < 1e-8:
        return 0.0
    if alpha < 1e-8:
        return beta
    if beta < 1e-8:
        return alpha
    for _ in range(48):
        alpha, beta = beta, alpha % beta
        if beta < 1e-5 * max(alpha, 1e-8):
            return float(alpha)
    return float(alpha)


def _subindice(n):
    signos = str.maketrans("-0123456789", "₋₀₁₂₃₄₅₆₇₈₉")
    return str(int(n)).translate(signos)


def etiqueta_laue(Gx, paso):
    """L₀, L₁, L₁/₂… según −Gₓ / paso."""
    if paso <= 0.0:
        return "L₀"
    razon = -float(Gx) / float(paso)
    for den in range(1, 13):
        num = int(round(razon * den))
        if abs(razon - num / den) < 0.06:
            g = int(np.gcd(abs(num), den))
            num, den = num // g, den // g
            if den == 1:
                return "L" + _subindice(num)
            return "L" + _subindice(num) + "/" + _subindice(den)
    return "L" + _subindice(int(round(razon)))


def zonas_laue(manchas, e_x, b1, b2, k_i, L, R, A1=1, A2=1):
    """Arcos de Laue de los puntos que llegan a la pantalla.

    Gₓ = G · ê, con ê el azimut del haz. En el fósforo cada Gₓ fijo
    cumple Y² + Z² = L² (|k|² / k_fx² − 1), k_fx = |k_∥| + Gₓ.
    L₀ es la zona del haz especular (Gₓ = 0) si ese arco cabe en el disco.
    manchas: (Y, Z, i, j), índices en la base b1/A1, b2/A2.
    """
    k_i = np.asarray(k_i, dtype=float).reshape(-1)
    e_x = np.asarray(e_x, dtype=float).reshape(-1)[:2]
    k_par = float(np.linalg.norm(k_i[:2]))
    k_mod = float(np.linalg.norm(k_i))
    if k_par <= 0.0 or k_mod <= 0.0 or L <= 0.0:
        return []
    A1i = max(1, int(round(float(A1))))
    A2i = max(1, int(round(float(A2))))
    B1 = np.asarray(b1, dtype=float).reshape(-1)[:2] / A1i
    B2 = np.asarray(b2, dtype=float).reshape(-1)[:2] / A2i
    paso = _paso_laue(float(np.dot(B1 * A1i, e_x)), float(np.dot(B2 * A2i, e_x)))
    if paso <= 0.0:
        return []

    escala = min(float(np.linalg.norm(B1 * A1i)), float(np.linalg.norm(B2 * A2i)))
    # En un azimut sin fila clara el mcd de las proyecciones se hace diminuto.
    paso_util = paso if paso >= 0.05 * max(escala, 1e-8) else 0.0
    tolerancia = 0.02 * paso if paso_util else 1e-4

    vistos = {}
    for _Y, _Z, i, j in manchas:
        G = i * B1 + j * B2
        Gx = float(np.dot(G, e_x))
        clave = int(round(Gx / tolerancia))
        grupo = vistos.setdefault(clave, {"gx": [], "n": 0})
        grupo["gx"].append(Gx)
        grupo["n"] += 1
    if not any(abs(float(np.mean(g["gx"]))) < tolerancia for g in vistos.values()):
        vistos["especular"] = {"gx": [0.0], "n": 0}

    crudos = []
    for grupo in vistos.values():
        Gx = float(np.mean(grupo["gx"]))
        # Una fila de Laue tiene varios puntos. L₀ se conserva aunque solo esté el especular.
        if grupo["n"] < 2 and abs(Gx) > tolerancia:
            continue
        k_fx = k_par + Gx
        if k_fx <= 1e-8 or abs(k_fx) >= k_mod:
            continue
        radio = float(L * np.sqrt((k_mod / k_fx) ** 2 - 1.0))
        if radio <= 0.0 or radio > float(R) + 1e-6:
            continue
        crudos.append((Gx, radio))

    if not paso_util and crudos:
        orden = sorted(crudos, key=lambda par: -par[0])
        i0 = int(np.argmin([abs(Gx) for Gx, _radio in orden]))
        return [
            {"etiqueta": "L" + _subindice(i - i0), "radio": radio, "Gx": Gx}
            for i, (Gx, radio) in enumerate(orden)
        ]

    zonas = [
        {"etiqueta": etiqueta_laue(Gx, paso), "radio": radio, "Gx": Gx}
        for Gx, radio in crudos
    ]
    zonas.sort(key=lambda z: z["radio"])
    return zonas


def manchas_pantalla(
    Simetria, a, b,
    modo_beam, angle, u, v, keV, theta_deg,
    reconstruct, A1, A2,
    distancia_cm=15.0, radio_cm=10.0,
    rotacion_deg=0.0,
):
    """Puntos (Y, Z, i, j) que caen en el fósforo.

    Devuelve (mensaje, None) si el cálculo no se puede hacer, o
    (None, datos). datos separa la red 1×1 de la reconstrucción.
    """
    L = _flotante(distancia_cm, 15.0)
    R = _flotante(radio_cm, 10.0)
    phi = _flotante(rotacion_deg, 0.0)
    if L <= 0.0 or R < 0.0:
        return "La distancia y el radio de la pantalla tienen que ser válidos.", None

    try:
        k_i = haz_incidente(
            Simetria, a, b, modo_beam, angle, u, v, keV, theta_deg, phi,
        )
    except (ValueError, ZeroDivisionError) as exc:
        return str(exc), None
    if k_i is None:
        if radio_ewald(keV) <= 0.0:
            return "La energía tiene que ser mayor que cero.", None
        return "La dirección del haz no puede ser cero.", None
    try:
        b1, b2 = _primitivos_plano(Simetria, a, b)
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        return str(exc), None

    # La pantalla sigue en el marco de la superficie: (u, v) en el plano y
    # la tercera componente a lo largo de la normal. En la red centrada el
    # laboratorio tiene ese plano en yz.
    k_par, k_normal = _desde_lab(Simetria, k_i)
    if float(np.linalg.norm(k_par)) == 0.0:
        return "El haz no tiene componente paralela hacia la pantalla.", None
    k_superficie = np.array([k_par[0], k_par[1], k_normal])

    A1i, A2i = periodos(reconstruct, A1, A2)
    e_x = k_par / np.linalg.norm(k_par)
    e_y = np.array([-e_x[1], e_x[0]])
    try:
        inversa = np.linalg.inv(np.column_stack([b1 / A1i, b2 / A2i]))
    except np.linalg.LinAlgError:
        return "b1 y b2 no forman una base.", None

    red, recon = [], []
    for k_f in varillas_que_cortan(k_superficie, b1, b2, A1i, A2i):
        llegadas = llegan_a_pantalla([_a_marco_pantalla(k_f, e_x, e_y)], L, R)
        if not llegadas:
            continue
        _, (Y, Z) = llegadas[0]
        coef = inversa @ (np.asarray(k_f, dtype=float)[:2] - k_par)
        i = int(round(float(coef[0])))
        j = int(round(float(coef[1])))
        destino = recon if (i % A1i != 0) or (j % A2i != 0) else red
        destino.append((float(Y), float(Z), i, j))

    return None, {
        "phi": phi,
        "L": L,
        "R": R,
        "A1i": A1i,
        "A2i": A2i,
        "red": red,
        "recon": recon,
        "zonas": zonas_laue(red + recon, e_x, b1, b2, k_superficie, L, R, A1i, A2i),
    }
