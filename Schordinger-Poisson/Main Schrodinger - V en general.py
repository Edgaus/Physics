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

AlN = { 
        'mass_e': (0.4),
        'Bandgap' : (6.2),
        'dielectric' : 13.18-3.12*constant_x
        }

AlInN = { 
        'mass_e': ( 0.4*(1-x_IN)+x_IN*0.11  ),
        'Bandgap' : (   ),
        'dielectric' : 13.18-3.12*constant_x
        }



structure = [ AlN, AlInN, AlN] 


#Concentration donors



thickness = [250,100,250]
mesh_array = [0.1,0.1,0.1]




Band_Edge_Potential = []
mass_e = []
dielec = []

for layer in structure:
    Band_Edge_Potential.append( layer.get('Bandgap')  )
    mass_e.append( layer.get('mass_e') )
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
#Band_Edge_Potential_grid =      grider.grid_propertie( Band_Edge_Potential, 'step'  )
band_stark =                   grider.grid_propertie( [1], 'analytical_band_profile_zeroed'  )


energies_QW, energies_Func = mfd.finite_differences( band_stark , mass_e_grid , diff, L )
    

# =====================================================================
# SECCIÓN DE GRAFICACIÓN (Se ejecuta al terminar el loop)
# =====================================================================

plt.figure(figsize=(10, 6))

# 1. Graficar el Perfil de la Banda de Conducción
plt.plot(x, band_stark, 'k-', linewidth=2.5, label='Banda de Conducción ($E_c$)')

# 2. Extraer los datos del estado base (Ground State)
# Asumiendo que energies_QW está ordenado de menor a mayor energía
E0 = energies_QW[0]

# Extraer la función de onda correspondiente.
# (Nota: Si tu módulo mfd devuelve los eigenvectores en columnas, usa [:, 0]. 
# Si los devuelve en filas, usa [0] o [0, :])
psi_0 = energies_Func[:, 0]



# 4. Graficar el Nivel de Energía E0
plt.axhline(E0, color='red', linestyle='--', linewidth=1.5, label=f'Estado Base $E_0$ = {E0:.4f} eV')


# Configuraciones de la gráfica
plt.title("Perfil de Bandas y Estado Base", fontsize=14)
plt.xlabel("Posición", fontsize=12) 
plt.ylabel("Energía (eV)", fontsize=12)
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.show()