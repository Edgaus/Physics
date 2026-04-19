import numpy as np
from scipy.optimize import brentq

########## Constants
kB = 8.617E-5        # eV/K
m0 = 5.686e-16       # eV·s²/m²
hbar = 6.582E-16     # eV·s 


def fermi_level_energy(Energies, Barrier_height, donor_sheet_density, T, mas):
    
    kT = kB * T 
    m_eff = m0 * mas
    
    n2D = (m_eff * kT) / (np.pi * hbar**2)
    
    number_states = 1
    number_energy = len(Energies)
    Fermi_level_min = Energies[0] - 10 * kT
    Fermi_level_max = Barrier_height
    Fermi_level = 0
    
    donor_n_target = donor_sheet_density  # Now passed directly in m^-2
    
    while number_states <= number_energy:
        E_active = Energies[:number_states]
        
        def residual(E_F):
            n_s = 0.0
            for Ek in E_active:
                arg = (E_F - Ek) / kT
                arg_clipped = np.clip(arg, -100, 100)
                n_s += n2D * np.log(1.0 + np.exp(arg_clipped))
            return n_s - donor_n_target
        
        try:
            Fermi_level = brentq(residual, Fermi_level_min, Fermi_level_max)
        except ValueError:
            number_states += 1
            continue
        
        # Check spillover
        if Fermi_level >= Fermi_level_max - kT:
            return Fermi_level, E_active
        
        # Check if we need next state
        if number_states < len(Energies):
            if Fermi_level > Energies[number_states]:
                number_states += 1
                continue
        
        # Converged
        return Fermi_level, E_active
    
    return Fermi_level, Energies