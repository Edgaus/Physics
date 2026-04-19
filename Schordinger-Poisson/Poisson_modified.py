import numpy as np
from scipy.linalg import solve_banded


def poisson(phi, Nd, T, Mass_confinament ,epsilon, eigen_energies, eigen_vectors, diff, L):
    vacuum_permitivity = 8.85E-12
    m0 = 9.11E-31
    qe = 1.602E-19
    hbar = 1.054E-34

    
    constant = Mass_confinament * m0 * (qe**2) / (vacuum_permitivity * np.pi * hbar**2)

    m = len(epsilon)
    number_energies = len(eigen_energies)

    # AQUÍ DEFINES diff_m (Conversión de Angstroms a Metros)
    diff_m = np.asarray(diff) * 1E-10
    Nd_m = np.asarray(Nd) * 1E6


    
 ################## Calculation of element of matrix  #####################
    
    csup = np.zeros(m-1)
    cinf = np.zeros(m-1)
    cdiag = np.zeros(m)
    term_B = np.zeros(m)
    n_x = np.zeros(m)

    for i in range(m - 1):
        # Diagonal superior (C_{i, i+1}): Conecta i con i+1
        h_left_sup = diff_m[i-1] if i > 0 else diff_m[0]
        h_right_sup = diff_m[i]
        csup[i] = (epsilon[i] + epsilon[i+1]) / (h_right_sup * (h_left_sup + h_right_sup))
        
        # Diagonal inferior (C_{i+1, i}): Conecta i+1 de vuelta con i
        h_left_inf = diff_m[i]
        h_right_inf = diff_m[i+1] if i < m - 2 else diff_m[i]
        cinf[i] = (epsilon[i] + epsilon[i+1]) / (h_left_inf * (h_left_inf + h_right_inf))

    # Diagonal principal (C_{i, i})
    # Garantiza la conservación estricta de la carga (la suma de la fila = 0)
    for i in range(1, m - 1):
        cdiag[i] = -csup[i] - cinf[i-1]

    # Condiciones de frontera de Neumann (Campo eléctrico = 0 en los bordes)
    cdiag[0] = -2 * csup[0]
    cdiag[-1] = -2 * cinf[-1]



################## Calculation A and B termns  #####################


    for k in range(number_energies):

        n_x += fermi(eigen_energies[k], T, Fermi_eneg, constant )* eigen_vectors[:, k]**2 / L 
        
        term_B +=  qe*n_x/vacuum_permitivity

    # Añadimos el a la diagonal principal

    Cij = np.diag(cdiag, k=0) + np.diag(cinf, k=-1) + np.diag(csup, k=1)

    # Calculamos N_2D integrand Nd espacialmente
    N_2D = np.sum(Nd_m * diff) 

    # Obtenemos la densidad volumétrica tridimensional real
    n_volumetrico = n_x




################## Solve for small increment of electrostatic field  #####################


   
    xi = (Cij @ phi) + qe * (Nd_m - n_volumetrico) / vacuum_permitivity
    
    # Corrección de padding exigida por scipy.linalg.solve_banded

    upper_band = np.append(0, csup)
    lower_band = np.append(cinf, 0)
    main_band= cdiag + constant * term_B

    ab = np.array([upper_band, main_band, lower_band])
    delta_phi = solve_banded((1, 1), ab, -xi)



################## Solve for small increment of electrostatic field  #####################

    with np.errstate(divide='ignore', invalid='ignore'):
        # Calculamos el error relativo nodo a nodo
        # Si phi es 0 (como en la primera iteración), asignamos 1.0 (100% de error)
        error = np.where(phi != 0, np.abs(delta_phi / phi), 1.0)
    
    return delta_phi, error
    
