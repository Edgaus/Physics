from scipy.optimize import root_scalar
import numpy as np


# Definicion de constantes fisicas en (eV)

hbar = 6.58211957E-16 # eV*s  
c = 3E18 # A/s
m0 = 5.11E5/c**2 # eV/c^2

print(' Este programa resuelve el potencial cuantico finito bajo la aproximacion de masas finitas ')

#V = (1e-3)* float(input('Potencial de la barrera (meV): ' ))
#mass_b = m0*float(input('Massa efectiva de la barrera (m0): ' ))
#mass_p = m0*float(input('Masa efectiva del pozo: (m0): ' ))
#l_p = float(input('Espesor del pozo (Armstrong): '))

V = 670e-3
mass_eff = 0.067*m0
l_p = 100
a = 0.5 * l_p

# Acorde al desarrollo teorico, tenemos que v_max, el maximo numero de niveles confinados viene dado por la ecuacion 
v_max = 1 + int(      np.sqrt(              ( 2 * mass_eff * V *l_p**2 )/((np.pi*hbar)**2)        )      ) 
print('La cantidad de niveles confinados es: ', v_max)

k = np.sqrt( 2*mass_eff/hbar**2  )
lim = ((np.pi*hbar)**2 )/( 2*mass_eff*l_p**2 )


# pares (estado base):  k tan(ξ) = κ
f_par = lambda E: np.sqrt(E) * np.tan(k * l_p * np.sqrt(E) / 2) - np.sqrt(V - E)

# impares:  -k cot(ξ) = κ
f_impar = lambda E: (
    -np.sqrt(E) / np.tan(k * l_p * np.sqrt(E) / 2) - np.sqrt(V - E)
)

alpha_par = lambda E: 1.0 / np.cos(k * l_p * np.sqrt(E) / 2)
alpha_impar = lambda E: 1.0 / np.sin(k * l_p * np.sqrt(E) / 2)


P_II_par = lambda k_n: l_p / 2 + np.sin(2 * k_n * a) / (2 * k_n)
P_II_impar = lambda k_n: l_p / 2 - np.sin(2 * k_n * a) / (2 * k_n)


Energias = []
P_barreras = []


for i in range( v_max):
    if i == 0:
        Emin = 1e-10
        Emax = min(0.999 * lim, 0.999 * V)
    else:
        Emin = ((1*i) ** 2) * lim + 1e-10
        Emax = min(0.999 * (((1*i+1)) ** 2) * lim, 0.999 * V)

    if Emin >= V:
        break
    if (i % 2 == 0):
        f = f_par
        alpha = alpha_par
        P_II = P_II_par
    else:
        f = f_impar
        alpha = alpha_impar
        P_II = P_II_impar

    Energias.append(root_scalar(f, bracket=[Emin, Emax]).root)


    k_n = k * np.sqrt(Energias[i])
    kappa_n = k * np.sqrt(V - Energias[i])
    P_I = 1.0 / kappa_n

    B2 = 1.0 / (P_I + alpha(Energias[i]) ** 2 * P_II(k_n))
    P_barreras.append(B2 * P_I)


print("Niveles (meV):", [e * 1e3 for e in Energias])
print("P_barrera:", P_barreras)



    
