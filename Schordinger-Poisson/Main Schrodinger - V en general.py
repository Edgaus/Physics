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
# SECCIÓN DE GRAFICACIÓN (Se ejecuta al terminar el loop)
# =====================================================================

plt.figure(figsize=(10, 6))

# 1. Extraer los datos del estado base (Ground State)
E0c = energies_QW_c[0]
EOv = -energies_QW_v[0] - 4  # Ajuste inverso del potencial para la VB

# Calcular la diferencia de energía (Transición óptica fundamental)
delta_E = E0c - EOv

# 2. Graficar el Perfil de ambas Bandas
# Asegúrate de pasar 'band_stark_c' para la CB y 'band_stark_v' para la VB
plt.plot(x, band_stark_c, 'k-', linewidth=2.5, label='Banda de Conducción ($E_c$)')
plt.plot(x, band_stark_v, 'gray', linewidth=2.5, label='Banda de Valencia ($E_v$)')

# 3. Graficar los Niveles de Energía E0c y E0v
plt.axhline(E0c, color='blue', linestyle='--', linewidth=1.5, label=f'$E_{{c0}}$ (Electrón) = {E0c:.4f} eV')
plt.axhline(EOv, color='red', linestyle='--', linewidth=1.5, label=f'$E_{{v0}}$ (Hueco) = {EOv:.4f} eV')

# 4. Señalar la diferencia de energía (Delta E) con una flecha
x_center = np.mean(x*1.4) # Posicionar la flecha en el centro del eje x
plt.annotate('', xy=(x_center, E0c), xytext=(x_center, EOv),
             arrowprops=dict(arrowstyle='<->', color='green', lw=2))

# Agregar el texto del valor de Delta E justo al lado de la flecha
plt.text(x_center + (x.max() - x.min()) * 0.02, (E0c + EOv) / 2, 
         f'= {delta_E:.4f} eV', 
         color='green', fontsize=12, va='center', fontweight='bold')

# 5. Configuraciones de la gráfica
plt.title("Perfil de Bandas, Estados Base y Transición Óptica", fontsize=14)
plt.xlabel("Posición", fontsize=12) 
plt.ylabel("Energía (eV)", fontsize=12)
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()