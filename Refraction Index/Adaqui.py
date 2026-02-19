import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# Programa para poder calcular la funcion dialectrica utilizando el modelo de Adaqui. Prueba 1 para el GaN

def e_0(E):
    value = A*E0^(-3/2) 
    return value



def dialectric_function(E):

    e_inf = 0.426

    e_total = e_inf + e_0(E) + e_0X(E) + e_1(E) + e_1X(E)
    return e_total
