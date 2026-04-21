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

structure = [ AlxGa1_xAs, GaAs, AlxGa1_xAs] 


#Concentration donors

mesh_array= [0.1,0.1,0.1]  

thickness = [200,100,200]


Nd = [0, 2E18, 0]


Band_Edge_Potential = []
mass_e = []
dielec = []

for layer in structure:
    Band_Edge_Potential.append( layer.get('Bandgap')  )
    mass_e.append( layer.get('mass_e') )
    dielec.append( layer.get('dielectric') )


Band_offsset = 0.67

# Convertir a array de NumPy para poder operar
Band_Edge_Potential = np.array(Band_Edge_Potential)
Band_Edge_Potential = (Band_Edge_Potential - Band_Edge_Potential.min()) *Band_offsset


grider = gr.Grider( thickness, 'uniform',  mesh_array )

########################## variable, uniform , constant ##########################

x, diff =    grider.grid_axis()

L = np.zeros_like(diff)
L[0] =  np.sqrt( diff[0] ) 
L[-1] =  np.sqrt( diff[-1] )
for i in range( 1, len(L)-1 ):
    L[i] = np.sqrt(0.5*( diff[i-1] + diff[i]  ))



########################## Constants ##########################

mass_e_grid =                   grider.grid_propertie( mass_e, 'step'  )
Band_Edge_Potential_grid =      grider.grid_propertie( Band_Edge_Potential, 'step'  )
Nd_grid =                       grider.grid_propertie( Nd, 'step'  )
dielec_grid =                   grider.grid_propertie( dielec, 'step'  )

phi = np.zeros_like( Band_Edge_Potential_grid )


########################## Calculate donor sheet density once ##########################

# Donor sheet density correctly
Nd_array = np.array(Nd) * 1e6       # cm^-3 → m^-3
thickness_m = np.array(thickness) * 1e-10  # Å → m
donor_sheet_density = np.dot(Nd_array, thickness_m)  # m^-2


########################## Poisson loop ##########################

phi = np.zeros_like( Band_Edge_Potential_grid )
error_phi = np.ones_like( phi)

for i in range(1):

    # 1. Potencial Total
    V_total = Band_Edge_Potential_grid - phi    
    
    #  Schrödinger con el nuevo pozo
    energies_QW, energies_Func = mfd.finite_differences_mod( V_total , mass_e_grid , diff, L , x)
    
   
    
    print(f'Iteración {i:02d} | Energía del estado base es: {energies_QW[0]*1000:.4f} meV')

    # Fermi level calculator
    Fermi_energy, Energy_apro = flc.fermi_level_energy( 
        energies_QW, 
        V_total.max(), 
        donor_sheet_density, 
        300, 
        GaAs.get('mass_e')  
    )
    
    #################  Poisson ############# delta_phi, error_phi = pm.poisson(  )

    phi = phi
    

    

# =====================================================================
# SECCIÓN DE GRAFICACIÓN (Se ejecuta al terminar el loop)
# =====================================================================

plt.figure(figsize=(10, 6))

# 1. Graficar el Perfil de la Banda de Conducción (V_total)
plt.plot(x, V_total, x, energies_Func[:,0], 'k-', linewidth=2.5, label='Banda de Conducción ($E_c$)')

# 2. Graficar el Nivel de Fermi
plt.axhline(y=Fermi_energy, color='red', linestyle='--', linewidth=2, 
            label=f'Nivel de Fermi ({Fermi_energy*1000:.1f} meV)')

# 3. Graficar los niveles de energía confinados (antes/debajo de la barrera)
barrier_height = V_total.max()

# Factor de escala para que las funciones de onda se vean bien en la gráfica.
# Si los picos se ven muy grandes o muy pequeños, ajusta este valor.
escala_psi = 0.05 

# Iterar solo sobre las energías que tu calculadora de Fermi consideró activas
for idx, E in enumerate(Energy_apro):
    if E < barrier_height:
        # Graficar la línea horizontal del nivel de energía
        plt.axhline(y=E, color='blue', linestyle='-', alpha=0.5, 
                    label='Niveles Confinados' if idx == 0 else "")
        
        # Opcional: Graficar la probabilidad de la función de onda (|psi|^2)
        # Se eleva al cuadrado, se escala y se desplaza hacia su nivel de energía (E)
        prob_density = (energies_Func[:, idx]**2) * escala_psi + E
        plt.plot(x, prob_density, 'blue', alpha=0.7)
        
        # Etiqueta de texto para cada nivel (E0, E1, E2...)
        plt.text(x[10], E + 0.002, f'$E_{idx}$', color='blue', fontsize=12)




# Configuración visual de la gráfica
plt.xlabel('Posición (Å)', fontsize=12)
plt.ylabel('Energía (eV)', fontsize=12)
plt.title('Perfil de Bandas y Estados Confinados del Pozo Cuántico', fontsize=14)

# Prevenir que "Niveles Confinados" se repita en la leyenda
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='best')

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()