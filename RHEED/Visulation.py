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

Volt = 10000 # Volts

lambda_e = 12.3/np.sqrt( Volt*(1 + 1.95*10E-6) )

# Para poder obtener los puntos que se verán en la pantalla RHEED, es necesario hacer lo siguiente. 
# Obtener la magnitud del vector k incidente, el cual es 2 pi /lambda

ki = 2*np.pi/lambda_e

# Ahora, sabemos que los vectores difractados kf, deben cumplir, al se colisiones elasticas, se debe cumplir la conservacion de energia.
# Así: |ki| = |kf|. Mientras que la condicion de Laue, para interferencia constructiva el vector kf-ki debe ser un vector de la red recriproca.
# Y en general dicho vector se puede escribir como kf = h*a_recip + k*b_recip. Esto quiere decir que se debe cumplir la siguiente relacion:

# kf = g_{hk} + lambda_k

# ki^2 = ki^2 + lambda_k^2 + g_{hk}^2 + (2ki . lambda_k) - (2ki . g_{hk} ) - (2lambda_k . g_{hk} )    
# Ahora tenemos que lambda_k . g_{hk} = 0 ya que por construccion estos vectores son normales. 
# Mientras que ki . lambda_k debería ser 0, pero no ya que en realidad ki no es realmente paralelo a la superficie del material.
# Hay un angulo phi.    


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