# Define the layers that define my structure
import Grid as gr
from matplotlib import pyplot as plt
import numpy as np
import finite_differencess_mod as mfd
import Poisson_modified as pm
import fermi_level_calculator as flc


# Masses are in m0 units and energy is in eV

AlGaAs = { 
        'mass_e': 0.092,
        'Bandgap' : 1.65,
        'dielectric' : 12.03
        }
GaAs = { 
        'mass_e': 0.067, 
        'Bandgap' : 1.426,
        'dielectric' : 13.18
        }
  
constant_x=0.2

AlxGa1_xAs = { 
        'mass_e': (0.067+0.083*constant_x),
        'Bandgap' : (1.426+1.247*constant_x),
        'dielectric' : 13.18-3.12*constant_x
        }

x_IN = 0.2
bowing_AlInN = 6

AlN = { 
        'mass_e': (0.4),
        'mass_hh': (3.53),
        'Bandgap' : (6.2),
        'dielectric' : 13.18-3.12*constant_x
        }

AlInN = { 
        'mass_e': ( 0.4*(1-x_IN)+x_IN*0.11  ),
        'mass_hh': ( 3.53*(1-x_IN)+x_IN*1.63  ),
        'Bandgap' : (  6.2*(1-x_IN) + x_IN -bowing_AlInN*x_IN*(1-x_IN) ),
        'dielectric' : 13.18-3.12*constant_x
        }

structure = [ AlN, AlInN, AlN] 


#Concentration donors



thickness = [250,100,250]
mesh_array = [0.1,0.1,0.1]




Band_Edge_Potential = []
mass_e = []
dielec = []
mass_hh = []

for layer in structure:
    Band_Edge_Potential.append( layer.get('Bandgap')  )
    mass_e.append( layer.get('mass_e') )
    mass_hh.append( layer.get('mass_hh') )
    dielec.append( layer.get('dielectric') )


Band_offsset = 0.7

# Convertir a array de NumPy para poder operar
#Band_Edge_Potential = np.array(Band_Edge_Potential)
#Band_Edge_Potential = (Band_Edge_Potential - Band_Edge_Potential.min()) *Band_offsset


grider = gr.Grider( thickness, 'uniform',  mesh_array )

########################## variable, uniform , constant ##########################

x, diff =    grider.grid_axis()

L = np.zeros_like(diff)
L[0] =  ( diff[0] ) 
L[-1] =  ( diff[-1] )
for i in range( 1, len(L)-1 ):
    L[i] = (0.5*( diff[i-1] + diff[i]  ))



########################## Constants ##########################

mass_e_grid =                   grider.grid_propertie( mass_e, 'step'  )
mass_hh_grid =                  grider.grid_propertie( mass_hh, 'step'  )
#Band_Edge_Potential_grid =      grider.grid_propertie( Band_Edge_Potential, 'step'  )
band_stark_c, band_stark_v =                   grider.grid_propertie( [1], 'analytical_band_profile_zeroed'  )


energies_QW_c, energies_Func_c = mfd.finite_differences( band_stark_c , mass_e_grid , diff, L )
energies_QW_v, energies_Func_v = mfd.finite_differences( -(band_stark_v + 4) , mass_hh_grid , diff, L )
    
# =====================================================================
# SECCIÓN DE ANÁLISIS DE TRANSICIONES ÓPTICAS (CORREGIDO)
# =====================================================================

def calculate_optical_transitions(E_c, E_v, Psi_c, Psi_v, diff_array, num_states=3, E_exciton_eV=0.035):
    print(f"\n--- Análisis de Transiciones Ópticas ---")
    print(f"(Asumiendo energía de ligadura del excitón = {E_exciton_eV*1000} meV)\n")
    
    print(f"{'Transición':<12} | {'Energía (eV)':<15} | {'Intensidad Relativa (|Overlap|^2)':<35}")
    print("-" * 65)

    for i in range(num_states):
        for j in range(num_states):
            
            # 1. Energía de Transición
            energia_transicion = E_c[i] - E_v[j] - E_exciton_eV
            
            # 2. Extraer funciones de onda
            psi_e = Psi_c[:, i]
            psi_h = Psi_v[:, j]
            
            # Asegurar que las funciones de onda estén normalizadas (sum(|psi|^2 * dx) = 1)
            norm_e = np.sqrt(np.sum(np.abs(psi_e)**2 * diff_array))
            norm_h = np.sqrt(np.sum(np.abs(psi_h)**2 * diff_array))
            psi_e_norm = psi_e / norm_e
            psi_h_norm = psi_h / norm_h
            
            # 3. Integral de Solapamiento (Overlap) con las funciones normalizadas
            overlap = np.sum(psi_e_norm * psi_h_norm * diff_array)
            intensidad = np.abs(overlap)**2
            
            # Quitamos el condicional para que imprima ABSOLUTAMENTE TODO
            etiqueta = f"e{i+1} - h{j+1}"
            
            # Si la intensidad es muy baja, lo indicamos visualmente
            if intensidad < 0.0001:
                print(f"{etiqueta:<12} | {energia_transicion:<15.4f} | {intensidad:<15.2e} (Casi prohibida por QCSE)")
            else:
                print(f"{etiqueta:<12} | {energia_transicion:<15.4f} | {intensidad:<15.4f}")

# Ejecución (asegúrate de que esta parte siga igual en tu código)
niveles_energia_v_absolutos = -energies_QW_v - 4 

calculate_optical_transitions(
    E_c = energies_QW_c, 
    E_v = niveles_energia_v_absolutos, 
    Psi_c = energies_Func_c, 
    Psi_v = energies_Func_v, 
    diff_array = diff,
    num_states = 3,
    E_exciton_eV = 0.035
)














    
# =====================================================================
# SECCIÓN DE GRAFICACIÓN (Actualizada para incluir funciones de onda)
# =====================================================================

plt.figure(figsize=(10, 7))

# 1. Extraer los datos del estado base
E0c = energies_QW_c[0]
E0v = -energies_QW_v[0] - 4 

# 2. Extraer y Normalizar funciones de onda (Ground State)
# Tomamos la columna 0. Multiplicamos por un factor (ej. 0.5) para que la amplitud se vea bien en la escala de eV
psi_c0 = energies_Func_c[:, 0]
psi_v0 = energies_Func_v[:, 0]

# Normalización rápida para visualización: sum(|psi|^2 * dx) = 1
norm_c = np.sqrt(np.trapz(np.abs(psi_c0)**2, x))
norm_v = np.sqrt(np.trapz(np.abs(psi_v0)**2, x))

psi_c0_plot = (psi_c0 / norm_c) * 0.3  # El 0.3 es un factor de escala visual
psi_v0_plot = (psi_v0 / norm_v) * 0.3

# Nota la 'r' antes de las comillas en el label
plt.plot(x, E0c + psi_c0_plot, 'blue', linewidth=1.5, label=r'$\psi_{e0}$ (Estado base)')
plt.fill_between(x, E0c, E0c + psi_c0_plot, color='blue', alpha=0.2)

plt.plot(x, E0v - psi_v0_plot, 'red', linewidth=1.5, label=r'$\psi_{h0}$ (Estado base)')
plt.fill_between(x, E0v, E0v - psi_v0_plot, color='red', alpha=0.2)

# 4. Graficar Funciones de Onda desplazadas a su nivel de energía
# Graficamos E_nivel + Psi para que "floten" en su nivel
plt.plot(x, E0c + psi_c0_plot, 'blue', linewidth=1.5, label='$\psi_{e0}$ (Estado base)')
plt.fill_between(x, E0c, E0c + psi_c0_plot, color='blue', alpha=0.2) # Relleno opcional

plt.plot(x, E0v - psi_v0_plot, 'red', linewidth=1.5, label='$\psi_{h0}$ (Estado base)')
plt.fill_between(x, E0v, E0v - psi_v0_plot, color='red', alpha=0.2)

# 5. Líneas de niveles de energía
plt.axhline(E0c, color='blue', linestyle='--', alpha=0.5)
plt.axhline(E0v, color='red', linestyle='--', alpha=0.5)

# 6. Etiquetas y formato
plt.title("Estructura de Bandas y Funciones de Onda del Estado Base", fontsize=14)
plt.xlabel("Posición (nm o unidades de grid)", fontsize=12)
plt.ylabel("Energía (eV)", fontsize=12)
plt.legend(loc='upper right', fontsize='small', ncol=2)
plt.grid(True, alpha=0.2)
plt.tight_layout()

plt.show()