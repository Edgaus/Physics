# Define the layers that define my structure
import Grid as gr
import numpy as np
import finite_differencess as mfd
import quantum_plotter as qp

# Masses are in m0 units and energy is in eV

c_InN = { 
        'mass_e': 0.07,
        'Bandgap' : 0.7,
        }
c_GaN = { 
        'mass_e': 0.15, 
        'Bandgap' : 3.2,
        }

h_AlN = {
        'mass_e': 0.3,
        'Bandgap': 6.2
        }

h_GaN = {
        'mass_e':0.20 ,
        'Bandgap': 3.42
        }



indium_x=1

c_InGaN = { 
        'mass_e': (     c_InN['mass_e']*indium_x + c_GaN['mass_e']*(1-indium_x) ),
        'Bandgap': (     c_InN['Bandgap']*indium_x + c_GaN['Bandgap']*(1-indium_x) ),
        }



x_Al = 0.1

AlGaAs = {
        'mass_e': 0.067 + 0.083*x_Al,
        'mass_hh': 0.62 + 0.14*x_Al,
        'Bandgap': 1.426 + 1.247*x_Al,
        }

GaAs = {
        'mass_e': 0.067,
        'mass_hh': 0.62,
        'Bandgap': 1.426
        }



structure = [ AlGaAs, GaAs, AlGaAs] 


#Concentration donors

mesh_array= [0.1,0.1,0.1]  

thickness = [50, 10, 50]  # El espesor lo tengo en armstrongs 


Band_Edge_Potential = []
mass_e = []

for layer in structure:
    Band_Edge_Potential.append( layer.get('Bandgap')  )
    mass_e.append( layer.get('mass_e') )


Band_offsset = 0.7

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

   
energies_QW, energies_Func = mfd.finite_differences( Band_Edge_Potential_grid , mass_e_grid , diff, L )
print(energies_QW[0])

# ... (At the end of your cubic-InGaN.py script) ...

analyzer = qp.QuantumAnalyzer(x_grid=x, 
                              potential=Band_Edge_Potential_grid, 
                              energies=energies_QW, 
                              wavefunctions=energies_Func)

# Plot the raw wavefunctions (crossing the 0 axis)
#analyzer.plot_wavefunctions(scale_factor=0.2, show_probability=False)
