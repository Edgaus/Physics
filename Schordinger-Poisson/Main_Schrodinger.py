# Define the layers that define my structure
import Grid as gr
from matplotlib import pyplot as plt
import numpy as np
import finite_differencess_mod as mfd
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
L[0] =  ( diff[0] ) 
L[-1] =  ( diff[-1] )
for i in range( 1, len(L)-1 ):
    L[i] = (0.5*( diff[i-1] + diff[i]  ))

L_matrix = np.diag(1/L)

########################## Constants ##########################

mass_e_grid =                   grider.grid_propertie( mass_e, 'step'  )
Band_Edge_Potential_grid =      grider.grid_propertie( Band_Edge_Potential, 'step'  )
Nd_grid =                       grider.grid_propertie( Nd, 'step'  )
dielec_grid =                   grider.grid_propertie( dielec, 'step'  )

phi = np.zeros_like( Band_Edge_Potential_grid )


########################## Poisson mod ##########################

i=0
phi = np.zeros_like( Band_Edge_Potential_grid )
error_phi = np.ones_like( phi)
m=1

while (np.min(error_phi)>1E-8) and (i<10): 

    # 1. Potencial Total
    V_total = Band_Edge_Potential_grid - phi    
    
    #  Schrödinger con el nuevo pozo
    values, funct = mfd.finite_differences( V_total , mass_e_grid , diff, L )

    norm_eigen = L_matrix * funct

    print(f'Iteración {i:02d} | Energía del estado base es: {values[0]:.4f} meV')

    
    # Poisson
    delta_phi, error_phi = pm.poisson( phi, Nd_grid, dielec_grid, mass_e_grid, values[0:m], funct[:,0:m], diff, L )
    
    print( np.min(error_phi) )
    
    phi = phi + ( delta_phi)
    i +=1

if i == 10:
    print('No convergió')
