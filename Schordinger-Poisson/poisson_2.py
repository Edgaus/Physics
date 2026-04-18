import numpy as np
from scipy.linalg import solve_banded

def solve_harrison_poisson(Nd_grid, dielec_grid, funct, diff, alpha=0.1, V_old=None):
    """
    Encapsula toda la lógica de Harrison para ser llamado desde el Main.
    
    Argumentos:
    Nd_grid    : Densidad de donores del Main (m^-3)
    dielec_grid: Constante dieléctrica del Main
    funct      : Eigenvectores del solver de Schrödinger (columna 0 es el base)
    diff       : Paso de malla en Angstroms
    alpha      : Factor de mezcla (mixing)
    V_old      : El inf_sheet_grid actual (para el mezclado)
    """
    
    # --- 1. Configuración de Constantes y Unidades ---
    epsilon_0 = 8.854187e-12
    qe = 1.602176e-19
    m = len(dielec_grid)
    dz = diff[0] * 1e-10  # Conversión Angstroms -> Metros
    
    if V_old is None:
        V_old = np.zeros(m)

    # --- 2. Cálculo de la densidad de carga (Neutralidad) ---
    # Calculamos n_s (densidad superficial) integrando Nd
    n_s = np.sum(Nd_grid * dz)
    
    # Calculamos n(z) volumétrico: n_s * |psi(z)|^2 / dz
    # (El /dz es necesario porque la sumatoria de funct**2 es 1, no la integral)
    psi_squared = funct[:, 0]**2
    n_vol = n_s * (psi_squared / dz)

    # --- 3. Construcción de la Matriz de Harrison (Eq. 3.80) ---
    # epsilon en puntos medios i + 1/2
    eps_mid = (dielec_grid[:-1] + dielec_grid[1:]) / 2
    
    # Coeficientes a, b, c
    # Nota: Usamos la permitividad relativa multiplicada por epsilon_0
    a = np.zeros(m)
    b = np.zeros(m)
    c = np.zeros(m)
    
    # Llenado de coeficientes para nodos internos
    # a_i es el término de V_{i-1}, c_i es el de V_{i+1}
    a[1:] = (eps_mid * epsilon_0) / (dz**2)
    c[:-1] = (eps_mid * epsilon_0) / (dz**2)
    b = -(a + c) # La suma de la fila debe ser cero (conservación)

    # --- 4. Lado derecho (Vector rho) ---
    # rho_i = -q * (Nd - n) 
    rho = -(qe * (Nd_grid - n_vol))

    # --- 5. Resolver el sistema AV = rho usando solve_banded ---
    # Estructura para solve_banded: [diagonal superior, diagonal principal, diagonal inferior]
    diag_sup = np.append(0, c[:-1])
    diag_main = b
    diag_inf = np.append(a[1:], 0)
    
    # Ajuste de bordes (Condiciones Dirichlet V=0)
    diag_main[0] = 1.0
    diag_sup[1] = 0.0
    rho[0] = 0.0
    
    diag_main[-1] = 1.0
    diag_inf[-1] = 0.0
    rho[-1] = 0.0

    ab = np.array([diag_sup, diag_main, diag_inf])
    V_solution = solve_banded((1, 1), ab, rho)

    # --- 6. Mezcla Lineal (Mixing) para estabilidad ---
    V_updated = (1 - alpha) * V_old + alpha * V_solution

    return V_updated