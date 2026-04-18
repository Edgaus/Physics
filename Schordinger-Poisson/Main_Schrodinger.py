# Define the layers that define my structure
import Grid as gr
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
import finite_differencess as fd
import finite_differencess_mod as mfd
import Poisson_differences_methods as pfd
import Poisson_modified as pm


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
  
constant_x=0.3

AlxGa1_xAs = { 
        'mass_e': (0.067+0.083*constant_x),
        'Bandgap' : (1.426+1.247*constant_x),
        'dielectric' : 13.18-3.12*constant_x
        }


structure = [ GaAs, AlGaAs, AlGaAs, GaAs ]


#Concentration donors
thickness = [ 150, 200, 50, 5000]   # Thickness is in Armstrongs
mesh_array= [0.5,0.5,0.5,0.5]  

Nd = [1E18, 1E18, 0, 0]

Band_Edge_Potential = []
mass_e = []
dielec = []

for layer in structure:
    Band_Edge_Potential.append( layer.get('Bandgap')  )
    mass_e.append( layer.get('mass_e') )
    dielec.append( layer.get('dielectric') )
     
Band_offsset = 0.6146

# Convertir a array de NumPy para poder operar
Band_Edge_Potential = np.array(Band_Edge_Potential)
Band_Edge_Potential = (Band_Edge_Potential - Band_Edge_Potential.min()) *Band_offsset


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
Band_Edge_Potential_grid =      grider.grid_propertie( Band_Edge_Potential, 'step'  )
Nd_grid =                       grider.grid_propertie( Nd, 'step'  )
dielec_grid =                   grider.grid_propertie( Nd, 'step'  )

phi = np.zeros_like( Band_Edge_Potential_grid )

########################## Solving Schrodinger equation ##########################

energ, funct = mfd.finite_differences( Band_Edge_Potential_grid , mass_e_grid , diff, L )

########################## Rename the Wavefuctions ##########################

lista_de_arreglos = []
for k in range(3):
        nuevo_vector =  (funct[:,k]/L)**2
        lista_de_arreglos.append(nuevo_vector)

# Al final, los "apilamos" todos en el axis=0
waves = np.stack(lista_de_arreglos, axis=0)

########################## Poisson mod ##########################

phi_elec, error_phi =  pm.poisson( phi, Nd_grid, dielec_grid, mass_e_grid, energ, waves   )

