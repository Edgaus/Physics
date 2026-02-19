import numpy as np
import matplotlib.pyplot as plt

# --- 1. Define Model Functions ---

def damping_func(E, Gamma, Alpha, Eg):
    """
    Frequency-dependent damping function from Eq. (11).
    Replaces constant Gamma with Gamma'(E) to fix absorption tails.
    """
    # Avoid division by zero if Gamma is 0 (though it shouldn't be)
    if Gamma == 0: return 0
    return Gamma * np.exp(-Alpha * ((E - Eg) / Gamma)**2)

def term_E0_3D(E, A, E0, Gamma, Alpha, G0_3D, A0_ex):
    """
    Calculates contributions from the Fundamental Band Gap (E0).
    Includes:
      1. Interband transition (Eq. 2)
      2. Excitonic transition (Eq. 4) - Summed to m=5 for convergence
    """
    # Calculate frequency-dependent damping
    Gam_prime = damping_func(E, Gamma, Alpha, E0)
    
    # -- Part A: Interband (One-Electron) --
    chi_0 = (E + 1j * Gam_prime) / E0
    # Eq. (2): f(chi) = chi^-2 * [2 - sqrt(1+chi) - sqrt(1-chi)]
    f_chi = (chi_0**-2) * (2 - np.sqrt(1 + chi_0) - np.sqrt(1 - chi_0))
    eps_interband = A * (E0**-1.5) * f_chi
    
    # -- Part B: Excitonic (Discrete sum) --
    eps_exciton = 0 + 0j
    # Summing first 4-5 terms is usually sufficient for convergence
    for m in range(1, 6): 
        # Eq. (4)
        denominator = E0 - (G0_3D / (m**2)) - E - 1j * Gam_prime
        eps_exciton += (A0_ex / (m**3)) * (1 / denominator)
        
    return eps_interband + eps_exciton

def term_E1_2D(E, B_1, E_1, Gamma_1, Alpha_1, G_1_2D, B_1_X):
    """
    Calculates contributions from Higher Critical Points (E1_beta).
    Includes:
      1. 2D Interband transition (Eq. 5)
      2. 2D Excitonic transition (Eq. 7)
    """
    # Frequency-dependent damping
    Gam_prime = damping_func(E, Gamma_1, Alpha_1, E_1)
    
    # -- Part A: 2D Interband --
    chi_1 = (E + 1j * Gam_prime) / E_1
    # Eq. (5): -B * chi^-2 * ln(1 - chi^2)
    eps_interband = -B_1 * (chi_1**-2) * np.log(1 - chi_1**2)
    
    # -- Part B: 2D Exciton (Wannier Type) --
    eps_exciton = 0 + 0j
    for m in range(1, 5):
        # Eq. (7)
        term_denom = (2*m - 1)**2
        numerator = B_1_X / ((2*m - 1)**3)
        denominator = E_1 - (G_1_2D / term_denom) - E - 1j * Gam_prime
        eps_exciton += numerator / denominator

    return eps_interband + eps_exciton

def total_dielectric_aln(E):
    """
    Sums all contributions using Table I parameters for AlN.
    """
    # --- TABLE I PARAMETERS FOR AlN (Djurišić & Li, 1999) ---
    # General
    Eps_inf = 1.230
    
    # E0 Critical Point (Fundamental Gap ~6.2 eV)
    A       = 5.648
    E0      = 6.222
    Gamma_0 = 0.439
    Alpha_0 = 0.465
    G0_3D   = 0.060
    A0_ex   = 0.600 # Calculated from exciton strength
    
    # E1A Critical Point
    B_1A    = 0.236
    E_1A    = 12.055
    Gamma_1A= 0.064
    Alpha_1A= 0.747
    G_1A_2D = 2.880
    B_1A_X  = 1.393

    # E1B Critical Point
    B_1B    = 0.037
    E_1B    = 8.841
    Gamma_1B= 2.045
    Alpha_1B= 0.687
    G_1B_2D = 0.980
    B_1B_X  = 1.655
    
    # E1C Critical Point
    B_1C    = 0.230
    E_1C    = 12.900
    Gamma_1C= 0.411
    Alpha_1C= 1.913
    G_1C_2D = 5.507
    B_1C_X  = 3.234

    # --- Summation ---
    eps = Eps_inf + \
          term_E0_3D(E, A, E0, Gamma_0, Alpha_0, G0_3D, A0_ex) + \
          term_E1_2D(E, B_1A, E_1A, Gamma_1A, Alpha_1A, G_1A_2D, B_1A_X) + \
          term_E1_2D(E, B_1B, E_1B, Gamma_1B, Alpha_1B, G_1B_2D, B_1B_X) + \
          term_E1_2D(E, B_1C, E_1C, Gamma_1C, Alpha_1C, G_1C_2D, B_1C_X)
          
    return eps

# --- 2. Calculate and Plot ---

# Define Energy Range (eV) covering 200 nm (6.2 eV)
E_range = np.linspace(4.0, 10.0, 500) 

# Calculate Dielectric Function
eps_complex = total_dielectric_aln(E_range)
eps_1 = eps_complex.real
eps_2 = eps_complex.imag

# Calculate Refractive Index (n) and Extinction Coefficient (k)
n = np.sqrt( (np.abs(eps_complex) + eps_1) / 2 )
k = np.sqrt( (np.abs(eps_complex) - eps_1) / 2 )

# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.set_xlabel('Photon Energy (eV)')
ax1.set_ylabel('Refractive Index (n)', color='blue')
ax1.plot(E_range, n, color='blue', label='n (Index)')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_ylim(1.5, 4.0)

ax2 = ax1.twinx()
ax2.set_ylabel('Extinction Coefficient (k)', color='red')
ax2.plot(E_range, k, color='red', linestyle='--', label='k (Extinction)')
ax2.tick_params(axis='y', labelcolor='red')
ax2.set_ylim(0, 2.0)

plt.title('Modeled Optical Constants of AlN (Djurišić & Li)')
plt.axvline(x=6.2, color='green', linestyle=':', label='200nm (6.2 eV)')
plt.show()

# Output specific value at 200 nm (6.20 eV)
E_target = 6.20
eps_target = total_dielectric_aln(E_target)
n_target = np.sqrt((np.abs(eps_target) + eps_target.real) / 2)
k_target = np.sqrt((np.abs(eps_target) - eps_target.real) / 2)

print(f"At 200 nm ({E_target} eV):")
print(f"n = {n_target:.4f}")
print(f"k = {k_target:.4f}")