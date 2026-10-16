from scipy.optimize import root_scalar
import numpy as np


# Definicion de constantes fisicas en (eV)

hbar = 6.58211957E-16 # eV/s  
c = 3E18 # A/s
m0 = 5.11E5/c**2 # eV/c^2

print(' Este programa resuelve el potencial cuantico finito bajo la aproximacion de masas finitas ')

#V = (1e-3)* float(input('Potencial de la barrera (meV): ' ))
#mass_b = m0*float(input('Massa efectiva de la barrera (m0): ' ))
#mass_p = m0*float(input('Masa efectiva del pozo: (m0): ' ))
#l_p = float(input('Espesor del pozo (Armstrong): '))

V = 130e-3
mass_b = 0.067*m0
mass_p = 0.08*m0
l_p = 100

# Acorde al desarrollo teorico, tenemos que v_max, el maximo numero de niveles confinados viene dado por la ecuacion 
v_max = int(l_p * np.sqrt(2 * mass_p * V) / (2 * hbar))
print(v_max)

kappa = np.sqrt( 2*mass_b/hbar**2  )
k = np.sqrt( 2*mass_p/hbar**2  )
lim = (np.pi / (k * l_p))**2

E = [ ]

for i in range (v_max):
    if i%2==0:
        f = lambda E: (k*np.sqrt(E)/mass_p)*np.tan( k*(E**(1/2))*l_p/2 ) - kappa*np.sqrt(V-E)/mass_b
        E.append(root_scalar(f, bracket=[(i+1E-10)*lim, (i+1-1E-20)*lim]))