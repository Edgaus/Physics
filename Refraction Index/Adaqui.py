import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import dual_annealing


# Programa para poder calcular la funcion dialectrica utilizando el modelo de Adaqui. Prueba 1 para el GaN


#Adaqui function to stablish the data 

def dialectric_function(E):


    # Params
    # Calculo para la contribucion de la funcion dialectrica de epsilon 0
    A_0 = 41.251
    E_0 = 3.550
    Gamma_0 = 0.287
    Chi_0 = (E + Gamma_0*1j)/E_0

    e_0 =  A_0* E_0**(-3/2) * Chi_0**(-2)*(  2-(1+Chi_0)^(1/2)- (1-Chi_0)**(1/2)       )

    # Calculando la contribucion de la funcion dialectrica de epsilon 0X

    m = 1
    e_0X = 0
    A_0X = 0.249
    G_0X = 0.030

    for i in range(m):
        e_0X += (A_0X/i**3)* (1/(  E_0 - (G_0X/i**2) - E-Gamma_0*1j     )) 


    # Calculando la contribucion de la funcion dialectrica de epsilon 1

    



    e_inf = 
    e_total = e_inf + e_0(E) + e_0X(E) + e_1(E) + e_1X(E)
    
    
    return e_total






# Function that defines the model annealing algorithim objective 

def objective_function(params, omega, n_expt, k_expt):
    """
    Calculates F based on Equation (13) from your image.
    """
    # Get model predictions for current parameters
    n_calc, k_calc = optical_model(omega, params)
    
    # Avoid division by zero if experimental data has 0s
    n_expt_safe = np.where(n_expt == 0, 1e-9, n_expt)
    k_expt_safe = np.where(k_expt == 0, 1e-9, k_expt)

    # Calculate Relative Error Terms (inside the absolute value bars)
    # Term 1: | n(w)/n_expt(w) - 1 |
    term_n = np.abs((n_calc / n_expt_safe) - 1)
    
    # Term 2: | k(w)/k_expt(w) - 1 |
    term_k = np.abs((k_calc / k_expt_safe) - 1)
    
    # Eq 13: Sum of (Term 1 + Term 2)^2
    # The image shows the square is outside the sum of absolute values
    F = np.sum((term_n + term_k)**2)
    
    return F
