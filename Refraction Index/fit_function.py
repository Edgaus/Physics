import numpy as np
import pandas as pd
from scipy.optimize import dual_annealing
from numpy.lib.scimath import sqrt as csqrt

def model_n(E, params):
    # Unpack all 20 variables
    (A_0, alpha_0, Gamma_0, A_0X, G_0X, 
     beta_1x, beta_2x, beta_3x, Gamma_11X, Gamma_12X, Gamma_13X, 
     alpha_1X, alpha_2X, alpha_3X, beta_1X1, beta_1X2, beta_1X3, 
     G_1X1, G_1X2, G_1X3) = params

    E_0 = 3.550 # GaN Bandgap
    eps = 1e-12 # Even smaller buffer
    
    # epsilon 0
    # Guard against division by zero in the exponent
    G0_safe = Gamma_0 if Gamma_0 > 0 else 1e-6
    Gamma_0_mod = G0_safe * np.exp(-alpha_0 * (((E - E_0) / G0_safe)**2))
    Chi_0 = (E + Gamma_0_mod * 1j) / E_0
    e_0 = A_0 * (E_0**(-1.5)) * (Chi_0**(-2)) * (2 - csqrt(1 + Chi_0 + eps*1j) - csqrt(1 - Chi_0 + eps*1j))

    # epsilon 0X 
    e_0X = 0
    for i in range(1, 21):
        denom = E_0 - (G_0X / i**2) - E - G0_safe * 1j
        e_0X += (A_0X / i**3) * (1 / (denom + eps*1j)) 

    # epsilon 1
    beta_1 = [beta_1x, beta_2x, beta_3x]
    Gamma_1 = [Gamma_11X, Gamma_12X, Gamma_13X]
    E_1 = [6.010, 8.182, 8.761] 
    alpha_1 = [alpha_1X, alpha_2X, alpha_3X]
    
    e_1 = 0
    for j in range(3):
        G1_safe = Gamma_1[j] if Gamma_1[j] > 0 else 1e-6
        G1m = G1_safe * np.exp(-alpha_1[j] * (((E - E_1[j]) / G1_safe)**2))
        shi_1 = (E + G1m * 1j) / E_1[j] 
        # Add buffer inside log to prevent log(0)
        e_1 += (beta_1[j] * (shi_1**(-2)) * np.log(1 - shi_1**2 + eps*1j))

    # epsilon 1X
    beta_1X = [beta_1X1, beta_1X2, beta_1X3]
    G_1X = [G_1X1, G_1X2, G_1X3]
    e_1X = 0
    for l in range(3):
        for k in range(1, 21):
            G1l_safe = Gamma_1[l] if Gamma_1[l] > 0 else 1e-6
            denom1x = E_1[l] - (G_1X[l] / (2*k-1)**2) - E - G1l_safe * 1j
            e_1X += (beta_1X[l] / (2*k-1)**3) * (1 / (denom1x + eps*1j))  

    e_inf = 0.426
    e_total = e_inf + e_0 + e_0X - e_1 + e_1X
    
    e1 = np.real(e_total)
    e2 = np.imag(e_total)
    # Ensure e2 is not exactly zero to prevent n/k explosion
    e2 = np.where(np.abs(e2) < eps, eps, e2)

    mag = csqrt(e1**2 + e2**2)
    n_index = np.real(csqrt((mag + e1) / 2))
    k_coef = np.real(csqrt((mag - e1) / 2))

    return n_index, k_coef

def objective_function(params, omega, n_expt, k_expt):
    try:
        n_p, k_p = model_n(omega, params)
        if np.any(np.isnan(n_p)) or np.any(np.isinf(n_p)):
            return 1e18
        
        # Weighted error (optional but helpful)
        error = np.sum(( (n_p - n_expt)/n_expt )**2 + ( (k_p - k_expt)/(k_expt + 0.1) )**2)
        return error
    except:
        return 1e18

# --- LOAD DATA ---
# (Using the alignment code from previous steps)
# ... [Your data loading and interpolation code here] ...

# --- NEW BOUNDS & INITIAL GUESS (x0) ---
# We center x0 on the GaN values from Table 1 to ensure a successful start
x0 = [41.251, 1.241, 0.287, 0.249, 0.030, 0.778, 0.103, 0.920, 0.743, 0.428, 0.440, 0.240, 0.011, 0.005, 2.042, 1.024, 1.997, 0.0003, 0.356, 1.962]

# Ensure bounds strictly avoid 0 for damping/broadening
bounds = [
    (30, 50), (0.1, 5), (0.01, 1),    # A0, alpha0, Gamma0
    (0.01, 1), (0.001, 0.1),         # A0X, G0X
    (0.1, 2), (0.01, 1), (0.1, 2),   # beta1
    (0.1, 2), (0.1, 2), (0.1, 2),    # Gamma1
    (0.001, 5), (0.001, 5), (0.001, 5), # alpha1
    (0.1, 5), (0.1, 5), (0.1, 5),    # beta1X
    (1e-5, 0.1), (0.1, 1), (0.5, 3)  # G1X
]

print("Starting dual annealing with x0 safety...")
result = dual_annealing(
    objective_function, 
    bounds=bounds, 
    x0=x0, # THIS IS THE KEY: Start from a known valid point
    args=(en_n, n_dat, k_dat), 
    maxiter=500
)

print("\nSuccess:", result.success)
print("Best Fit:", result.x)