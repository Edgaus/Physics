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
         f'$\Delta E$ = {delta_E:.4f} eV', 
         color='green', fontsize=12, va='center', fontweight='bold')

# 5. Configuraciones de la gráfica
plt.title("Perfil de Bandas, Estados Base y Transición Óptica", fontsize=14)
plt.xlabel("Posición", fontsize=12) 
plt.ylabel("Energía (eV)", fontsize=12)
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()