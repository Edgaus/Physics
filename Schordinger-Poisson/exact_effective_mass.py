import numpy as np
from scipy.optimize import brentq

def solucion(V, mw, mb, L_angstrom):
    """
    Devuelve la energía del estado fundamental (par) de un pozo cuántico finito.
    """
    hbar_c = 1973.27   # eV·Å
    m0_c2 = 511000.0   # eV

    # Primer polo de la tangente: k*L/2 = pi/2  ->  k = pi/L
    E_polo = ( (np.pi / L_angstrom) * hbar_c )**2 / (2 * mw * m0_c2)

    # Límite superior de búsqueda: no podemos pasar del polo ni de la barrera
    E_max = min(E_polo, V)

    # Pequeña tolerancia para evitar el polo exacto
    if E_max <= 1e-12:
        raise ValueError("El pozo es demasiado angosto o poco profundo, no hay estado ligado.")

    def f(E):
        if E <= 0 or E >= E_max:
            return np.inf   # para evitar evaluaciones peligrosas
        k = np.sqrt(2 * mw * E * m0_c2) / hbar_c
        kappa = np.sqrt(2 * mb * (V - E) * m0_c2) / hbar_c
        return (k / mw) * np.tan(k * L_angstrom / 2) - (kappa / mb)

    # brentq encuentra la raíz en (0, E_max) sin problemas
    eps = 1e-10
    root = brentq(f, eps, E_max - eps)
    return root

# Ejemplo
if __name__ == "__main__":
    V = 1.0       # eV
    mw = 1.0
    mb = 1.0
    L = 1.0       # Å
    E0 = solucion(V, mw, mb, L)
    print(f"Energía fundamental = {E0:.6f} eV")