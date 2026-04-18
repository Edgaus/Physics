# Define the layers that define my structure
import Grid as gr
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
import finite_differencess as fd
import finite_differencess_mod as mfd

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
        'dielectric' : 13.18
        }




#structure = [ GaAs, AlGaAs, AlGaAs, GaAs ]
structure = [ AlxGa1_xAs, GaAs, AlxGa1_xAs ]

#thickness = [ 150, 200, 50, 5000]   # Thickness is in Armstrongs
thickness = [ 200, 100, 200]   # Thickness is in Armstrongs


mesh_array= [0.05,0.05,0.05]  

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


# Así

grider = gr.Grider( thickness, 'uniform',  mesh_array )

######### variable, uniform , constant
x, diff =    grider.grid_axis()
######### step or inf_sheet_Band_Edge_Potential

Band_Edge_Potential_grid =        grider.grid_propertie( Band_Edge_Potential,       'step'  )
mass_e_grid =           grider.grid_propertie( mass_e,          'step'  )
dielec_grid =           grider.grid_propertie( dielec,          'step'  )
#inf_sheet_grid =        grider.grid_propertie( propertie_array=None, type_propertie='inf_sheet_Band_Edge_Potential' )


########################## Solving Schrodinger equation
values, funct = mfd.finite_differences_mod( Band_Edge_Potential_grid , mass_e_grid , diff  )
#values, funct = fd.finite_differences( Band_Edge_Potential_grid , mass_e_grid , diff  )


########################## Print and Plot

# 1. Sort and prepare your data
idx = np.argsort(values)
energies = values[idx]       # Energies in meV (because of your *1000 in fd)
eigenvectors = funct[:, idx] # Each column is a wavefunction
psi0 = funct[:, 0]

m = 1

print( f'Los {m} niveles de energía son {energies[0:m]}')
plt.plot(x, psi0)
plt.show()