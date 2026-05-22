import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_fitted_data(E):
    # --- 1. Epsilon 0 contribution ---
    A_0 = 31.575
    E_0 = 6.277
    Gamma_0 = 0.308
    alpha_0 = 10.770
    
    # Clamped at 1e-4 to prevent absolute zero damping and fix the 13 eV step
    Gamma_0_mod = np.maximum(Gamma_0 * np.exp(-alpha_0 * (((E - E_0) / Gamma_0)**2)), 1e-4)
    Chi_0 = (E + Gamma_0_mod * 1j) / E_0
    e_0 = A_0 * (E_0**(-3/2)) * (Chi_0**(-2)) * (2 - ((1 + Chi_0)**(1/2)) - (1 - Chi_0)**(1/2))

    # --- 2. Epsilon 0X contribution ---
    m = 5
    e_0X = 0
    A_0X = 0.401
    
    # G_0X is explicitly forced to be non-zero
    G_0X = 0.010

    for i in range(m):
        e_0X = e_0X + (A_0X / (i + 1)**3) * (1 / (E_0 - (G_0X / (i + 1)**2) - E - Gamma_0 * 1j))

    # --- 3. Parameters for Epsilon 1 and 1X ---
    # First two elements forced to be non-zero (0.050)
    beta_1 = [0.050, 0.050, 0.194]
    E_1 = [8.995, 9.351, 13.221]
    Gamma_1 = [0.667, 0.111, 0.810]
    
    # Fixed requested parameters
    alpha_1 = [2.436, 1.734, 0.749]  
    
    beta_1X = [0.474, 0.040, 1.667]
    G_1X = [0.023, 1.726, 5.695]

    e_1 = 0
    e_1X = 0
    n_idx = 5
    
    # --- 4. Loop for 1 and 1X contributions ---
    for l in range(3):
        # Clamped at 1e-4 to prevent the phase-flip step change
        Gamma_1_mod_cont = np.maximum(Gamma_1[l] * np.exp(-alpha_1[l] * (((E - E_1[l]) / Gamma_1[l])**2)), 1e-4)
        shi_1 = (E + Gamma_1_mod_cont * 1j) / E_1[l]
        e_1 = e_1 + (beta_1[l] * (shi_1**(-2)) * np.log(1 - shi_1**2))
        
        # Excitonic transitions use Standard Lorentzian constant damping
        Gamma_1_mod_exc = Gamma_1[l]
        
        for k in range(n_idx):
            denom = E_1[l] - (G_1X[l] / ((2 * (k + 1) - 1)**2)) - E - Gamma_1_mod_exc * 1j
            e_1X = e_1X + (beta_1X[l] / ((2 * (k + 1) - 1)**3)) * (1 / denom)

    # --- 5. Total Dielectric Function ---
    e_inf = 1.196
    e_total = e_inf + e_0 + e_0X - e_1 + e_1X
    
    e12_1 = e_total.real
    e12_2 = e_total.imag

    n_index = np.sqrt((np.sqrt(e12_1**2 + e12_2**2) + e12_1) / 2)
    k_coef = np.sqrt((np.sqrt(e12_1**2 + e12_2**2) - e12_1) / 2)

    return n_index, k_coef

# ==========================================
# Run Simulation & Export
# ==========================================

# Generate the energy array out to the expanded 20 eV bound
Energy_array = np.linspace(3.0, 20.0, 400)

# Calculate n and k
n_simulated, k_simulated = generate_fitted_data(Energy_array)

# Structure the data into a Pandas DataFrame
export_df = pd.DataFrame({
    'Energy (eV)': Energy_array,
    'n (Simulated)': n_simulated,
    'k (Simulated)': k_simulated
})

# Export to CSV
filename = 'AlN_Fitted_With_Damping.csv'
export_df.to_csv(filename, index=False)
print(f"Success! Data has been saved to '{filename}'.")

# ==========================================
# Plotting
# ==========================================

# Load your experimental files
n_exp = pd.read_csv(r'Refraction Index\AlN_index.txt', sep='\t')
k_exp = pd.read_csv(r'Refraction Index\AlN_extintion.txt', sep='\t')

# Clean column headers
n_exp.columns = n_exp.columns.str.strip()
k_exp.columns = k_exp.columns.str.strip()

n_PAMBE = pd.read_csv(r'Refraction Index\AlN Film_n.txt', sep='\t')
k_PAMBE = pd.read_csv(r'Refraction Index\AlN Film_k.txt', sep='\t')

plt.figure(figsize=(9, 6))
plt.plot(Energy_array, n_simulated, 'b-', label='Simulated n', linewidth=2)
plt.plot(Energy_array, k_simulated, 'r-', label='Simulated k', linewidth=2)
plt.plot(n_exp['Energy'], n_exp['Index_refraction'], 'bo', label='Experimental n')
plt.plot(k_exp['Energy'], k_exp['Extintion_coefficent'], 'ro', label='Experimental k')
plt.plot(n_PAMBE['Energy'], n_PAMBE['n'], 'go', label='n-AlN/Si(111) PAMBE')
plt.plot(k_PAMBE['Energy'], k_PAMBE['k'], 'yo', label='AlN/Si(111) PAMBE')
plt.xlabel('Energy (eV)')
plt.ylabel('Optical Constants (n, k)')
plt.legend()
plt.show()