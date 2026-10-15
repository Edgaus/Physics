import sympy as sy
import numpy as np


# Definicion de constantes fisicas en (eV)

hbar = 6.58211957E-16 # eV/s  
c = 3E18 # A/s
m0 = 5.11E5/c**2 # eV/c^2

print(' Este programa resuelve el potencial cuantico finito bajo la aproximacion de masas finitas ')

V = input('Potencial de la barrera (meV): ' )
mass_b = input('Massa efectiva de la barrera (m0): ' )
mass_p = input('Masa efectiva del pozo: (m0): ' )
l_p = input('Espesor del pozo (Armstrong)')

# Acorde al desarrollo teorico, tenemos que v_max, el maximo numero de niveles confinados viene dado por la ecuacion 
v_max = int(  ( mass_p*V   )**(1/2)*l_p/( 2*hbar )   )

E = [ ]
for i in range (v_max):
    if i%2==0:
        lambda f(E) = (k*E/mass_p)*np.tan( k*(E**(1/2))*l_p/2 ) - kappa*np.sqrt(V-E)/mass_b