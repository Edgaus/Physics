import numpy as np
from scipy.optimize import brentq

def fermi_level_energy(Energies, Barrier_height, donor_sheet_density, T, mas):

    ####  Constants Values
    kB = 8.617E-5        # eV/K
    hbar = 6.582E-16     # eV·s 
    
    # CORRECTED m0 for m^-2 (1 eV = 1.602e-19 J. m0 = 9.109e-31 kg)
    # m0 in eV·s²/m² = 9.109e-31 / 1.602e-19 = 5.686e-12
    m0 = 5.686E-12       
    
    kT = kB * T 
    m_eff = m0 * mas
    
    # 2D Density of states prefactor
    n2D = (m_eff * kT) / (np.pi * hbar**2)
    
    # Define the residual function using ALL states simultaneously
    def residual(E_F):
        n_s = 0.0
        for Ek in Energies:
            arg = (E_F - Ek) / kT
            # np.logaddexp(0, arg) safely calculates log(1 + exp(arg))
            n_s += n2D * np.logaddexp(0, arg)
            
        return n_s - donor_sheet_density

    # Safely bracket the root finding:
    # Lowest possible Fermi level: Far below the ground state (e.g., 2 eV below)
    Fermi_level_min = Energies[0] - 2.0 
    
    # Highest possible Fermi level: Slightly above the barrier (to catch heavy doping spillover)
    Fermi_level_max = Barrier_height + 0.5 

    try:
        # brentq will seamlessly find where residual == 0
        Fermi_level = brentq(residual, Fermi_level_min, Fermi_level_max)
        
        # Check if the Fermi Level is physically spilling over the barrier
        if Fermi_level >= Barrier_height:
            print("Warning: Fermi level exceeds the quantum well barrier. Electrons are spilling into 3D states.")
            
        return Fermi_level, Energies
        
    except ValueError:
        # If it still fails, it prints exactly why so you can debug your inputs
        res_min = residual(Fermi_level_min)
        res_max = residual(Fermi_level_max)
        raise ValueError(
            f"Convergence failed! The root is not bracketed.\n"
            f"Residual at min ({Fermi_level_min:.3f} eV) = {res_min:.2e}\n"
            f"Residual at max ({Fermi_level_max:.3f} eV) = {res_max:.2e}\n"
            f"Check if your donor_sheet_density ({donor_sheet_density:.2e} m^-2) is physically possible for this well."
        )