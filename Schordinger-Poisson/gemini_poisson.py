import numpy as np
import matplotlib.pyplot as plt
import finite_differencess_mod as mfd
import Poisson_differences_methods as pfd

# --- Constantes y Materiales ---
constant_x = 0.4  # Para Ga_0.6 Al_0.4 As
GaAs = {'mass': 0.067, 'eps': 13.18}
AlGaAs = {'mass': 0.067 + 0.083*constant_x, 'eps': 13.18 - 3.12*constant_x}
V0 = 0.60 * (1.247 * constant_x)  # Offset de banda de conducción (eV)

def solve_quantum_well(sheet_density_cm2, doped_width_A):
    # 1. Definir Geometría (Pozo de 100A, Barreras de 200A)
    # Estructura: AlGaAs(200) | GaAs(100) | AlGaAs(200)
    thickness = [200, 100, 200]
    dz = 0.1 # Angstroms
    
    # Crear malla
    x = np.arange(0, sum(thickness) + dz, dz)
    n = len(x)
    
    # Inicializar arreglos de la malla
    potential_well = np.zeros(n)
    mass_grid = np.zeros(n)
    dielec_grid = np.zeros(n)
    nd_grid = np.zeros(n) # Concentración volumétrica (m^-3)

    # Llenar propiedades físicas
    for i, xi in enumerate(x):
        if xi < 200 or xi > 300: # Barreras
            potential_well[i] = V0
            mass_grid[i] = AlGaAs['mass']
            dielec_grid[i] = AlGaAs['eps']
        else: # Pozo
            potential_well[i] = 0
            mass_grid[i] = GaAs['mass']
            dielec_grid[i] = GaAs['eps']

    # 2. Definir Capa Dopada (En el centro del pozo: x=250A)
    center = 250
    half_w = doped_width_A / 2
    # Convertir densidad superficial (cm^-2) a volumétrica (m^-3)
    # Nd_vol = N_sheet / width
    nd_vol_m3 = (sheet_density_cm2 * 1e4) / (doped_width_A * 1e-10)
    
    for i, xi in enumerate(x):
        if (center - half_w) <= xi <= (center + half_w):
            nd_grid[i] = nd_vol_m3

    # 3. Ciclo Autoconsistente
    phi_poisson = np.zeros(n)
    alpha = 0.05
    diff_A = np.full(n, dz)
    
    for _ in range(20):
        V_total = potential_well - phi_poisson # 1V = 1eV
        energies, functions = mfd.finite_differences_mod(V_total, mass_grid, diff_A)
        
        # Resolver Poisson para actualización
        delta_phi, _ = pfd.poisson(phi_poisson, nd_grid, dielec_grid, mass_grid, 
                                   [energies[0]], functions[:, 0:1], diff_A)
        phi_poisson += alpha * delta_phi
        
    return energies[0] # Retorna energía del estado base en meV

# --- Inciso (a): Variar densidad de 1x10^9 a 1x10^10 cm^-2 ---
densities = np.linspace(1e9, 1e10, 5)
results_a = []

print("Calculando Inciso (a)...")
for d in densities:
    e0 = solve_quantum_well(d, 10.0)
    results_a.append(e0)

# --- Inciso (b): Variar ancho de la capa (Difusión) ---
widths = [2, 10, 20, 50] # Angstroms
results_b = []

print("Calculando Inciso (b)...")
for w in widths:
    e0 = solve_quantum_well(1e10, w)
    results_b.append(e0)

# --- Gráficas y Comentarios ---
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(densities, results_a, 'o-')
plt.title("Efecto de la Densidad de Dopaje (a)")
plt.xlabel("Densidad ($cm^{-2}$)")
plt.ylabel("Energía $E_1$ (meV)")

plt.subplot(1, 2, 2)
plt.plot(widths, results_b, 's-r')
plt.title("Efecto de la Difusión (b)")
plt.xlabel("Ancho de capa dopada ($\AA$)")
plt.ylabel("Energía $E_1$ (meV)")

plt.tight_layout()
plt.show()