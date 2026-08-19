# This code is to simulate RHEED, using kinematic theory
# Definir los vectores primitivos de la red cristalina en el espacio real

import numpy as np
import sympy as sp


# 1. Definimos los componentes de los vectores como símbolos
a_x, a_y, a_z = sp.symbols('a_x a_y a_z')
b_x, b_y, b_z = sp.symbols('b_x b_y b_z')

# 2. Creamos los vectores usando sp.Matrix (vectores columna 3x1)
a_real = sp.Matrix([a_x, a_y, a_z])
b_real = sp.Matrix([b_x, b_y, b_z])
z_unit = sp.Matrix([ 0,0,1 ])

V = a_real.dot(  b_real.cross( z_unit )   )

# 3. Calculamos el producto cruz ALGEBRAICO
a_recip = 2*np.pi* ( b_real.cross( z_unit ) ) / (V)
b_recip = 2*np.pi* ( z_unit.cross( a_real ) ) / (V)

# Here is comment of file:///C:/Users/edgau/Downloads/materials-14-03056.pdf, where for FCC the recomendation 
# is to a = sqrt(2)/2x*c_lattice, b = sqrt(2)/2y*c_lattice, when the beam is in the [1,1,0] direction

lambda_e = 12.3/np.sqrt( V*(1 + 1.95*10E-6) )

# Para poder obtener los puntos 












# Esto es para sustituir pero lo vamos a dejar para mas delante:
# Le decimos a lambdify que tome todas nuestras variables de entrada
# y las evalúe dentro de nuestra matriz de producto cruz

funcion_cruz_rapida = sp.lambdify(
    (a_x, a_y, a_z, b_x, b_y, b_z), # Variables de entrada
    producto_cruz_simbolico,        # La expresión a evaluar
    'numpy'                         # Motor matemático
)

resultado_array = funcion_cruz_rapida(1, 2, 3, 4, 5, 6)

# El output será: [[-3] [ 6] [-3]]
print("\nResultado usando NumPy de alto rendimiento:")
print(resultado_array)