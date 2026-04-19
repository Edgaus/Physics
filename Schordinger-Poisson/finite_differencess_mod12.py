import numpy as np
from scipy.linalg import eigh_tridiagonal

def finite_differences(V_total, mass_e_grid, diff, L):
    """
    V_total : en eV
    mass_e_grid : en unidades de m0 (e.g. 0.067)
    diff : en Angstroms
    L : array de normalización (longitud efectiva del nodo) en Angstroms
    """
    m = len(V_total)
    
    # Factor de conversión hbar^2 / 2*m0  en unidades de [eV * Angstroms^2]
    HBAR2_2M0 = 3.80998  
    
    diagonal = np.zeros(m)
    off_diagonal = np.zeros(m-1)
    
    # Construcción de la matriz Laplaciana 1D para la energía cinética
    for i in range(m):
        dx = diff[i]
        T_term = HBAR2_2M0 / (mass_e_grid[i] * dx**2)
        diagonal[i] = 2 * T_term + V_total[i]
        
    for i in range(m-1):
        dx_avg = (diff[i] + diff[i+1]) / 2.0
        mass_avg = (mass_e_grid[i] + mass_e_grid[i+1]) / 2.0
        off_diagonal[i] = -HBAR2_2M0 / (mass_avg * dx_avg**2)
        
    # Resolver problema de eigenvalores (condiciones de frontera rígidas asintóticas en los bordes)
    eigenvalues, eigenvectors = eigh_tridiagonal(diagonal, off_diagonal)
    
    # Normalizar funciones de onda (en unidades de 1/sqrt(Angstroms))
    for j in range(eigenvectors.shape[1]):
        # sum(|psi|^2 * L_node) = 1
        norm = np.sqrt(np.sum(eigenvectors[:, j]**2 * L))
        eigenvectors[:, j] = eigenvectors[:, j] / norm
        
    return eigenvalues, eigenvectors