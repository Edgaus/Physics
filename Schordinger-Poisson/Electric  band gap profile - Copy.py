import numpy as np
import matplotlib.pyplot as plt

# --- Material Parameters ---
# We will model an Al_xGa_1-xN / GaN heterostructure
x = 0.30  # Aluminum mole fraction (30%)

# Bandgap calculations (at room temperature)
Eg_GaN = 3.42  # eV
Eg_AlN = 6.20  # eV
bowing_param = 1.0 # eV
# Vegard's law with bowing parameter for AlGaN bandgap
Eg_AlGaN = x * Eg_AlN + (1 - x) * Eg_GaN - bowing_param * x * (1 - x)

# Polarization constants (C/m^2)
P_sp_GaN = -0.034
P_sp_AlN = -0.090
# Linear interpolation for spontaneous polarization
P_sp_AlGaN = x * P_sp_AlN + (1 - x) * P_sp_GaN

# Piezoelectric polarization (simplified empirical approach for AlGaN on GaN)
# Strain induced by lattice mismatch creates P_pz
P_pz_AlGaN = -0.0525 * x + 0.0282 * (x**2) 
P_pz_GaN = 0.0 # Assuming GaN is relaxed (thick buffer)

# Total polarization
P_total_GaN = P_sp_GaN + P_pz_GaN
P_total_AlGaN = P_sp_AlGaN + P_pz_AlGaN

# Interface charge density (sigma = P_bottom - P_top)
# AlGaN is on top of GaN
sigma_int = P_total_GaN - P_total_AlGaN # C/m^2

# Dielectric constants (relative)
eps_GaN = 8.9
eps_AlN = 8.5
eps_AlGaN = x * eps_AlN + (1 - x) * eps_GaN
eps_0 = 8.854e-12 # Vacuum permittivity (F/m)
q = 1.602e-19 # Elementary charge (C)

# Calculate Electric Field in AlGaN (Simplified Gauss's Law assuming pinned surface state)
# E = -sigma / eps
E_field_AlGaN = -(sigma_int) / (eps_AlGaN * eps_0) # V/m
E_field_AlGaN_MVcm = E_field_AlGaN / 1e8 # Convert to MV/cm

# --- Setup the 1D Spatial Grid ---
z = np.linspace(-20, 30, 500) # Depth in nm (0 is interface)
# -20 to 0 nm: AlGaN surface layer
# 0 to 30 nm: GaN buffer

# Initialize arrays
Ec = np.zeros_like(z) # Conduction band
Ev = np.zeros_like(z) # Valence band
E_field = np.zeros_like(z) # Electric Field

# Band offsets (typically ~70% of bandgap difference goes to Conduction Band)
delta_Eg = Eg_AlGaN - Eg_GaN
delta_Ec = 0.7 * delta_Eg
delta_Ev = 0.3 * delta_Eg

# --- Calculate Profiles ---
for i, pos in enumerate(z):
    if pos < 0:
        # AlGaN Region
        # E_field causes the band to tilt: Energy = -q * E * distance
        # Note: pos is in nm, convert to m for energy calculation
        tilt = E_field_AlGaN * (pos * 1e-9) 
        Ec[i] = delta_Ec - tilt
        Ev[i] = Ec[i] - Eg_AlGaN
        E_field[i] = E_field_AlGaN_MVcm
    else:
        # GaN Region (assuming flat band for simplicity away from interface)
        # In reality, there's band bending here too (2DEG formation), but we keep it flat for the conceptual E-field step
        Ec[i] = 0 
        Ev[i] = -Eg_GaN
        E_field[i] = 0 

# --- Plotting ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

# Top Plot: Band Diagram
ax1.plot(z, Ec, color='blue', linewidth=2, label='$E_c$ (Conduction Band)')
ax1.plot(z, Ev, color='red', linewidth=2, label='$E_v$ (Valence Band)')
ax1.axvline(0, color='gray', linestyle='--', label='AlGaN/GaN Interface')
ax1.fill_between(z, Ec, Ev, where=(z<0), color='lightblue', alpha=0.3)
ax1.fill_between(z, Ec, Ev, where=(z>=0), color='lightgreen', alpha=0.3)
ax1.set_ylabel('Energy (eV)', fontsize=12)
ax1.set_title(f'Band Diagram of Al$_{{{x}}}$Ga$_{{{1-x}}}$N / GaN Heterostructure', fontsize=14)
ax1.legend()
ax1.grid(True, alpha=0.5)

# Add text for the 2DEG / Quantum Well
ax1.annotate('2DEG well', xy=(1, 0.2), xytext=(5, 1.0),
             arrowprops=dict(facecolor='black', shrink=0.05))

# Bottom Plot: Electric Field
ax2.plot(z, E_field, color='purple', linewidth=2, label='Electric Field')
ax2.axvline(0, color='gray', linestyle='--')
ax2.set_xlabel('Depth (nm)', fontsize=12)
ax2.set_ylabel('Electric Field (MV/cm)', fontsize=12)
ax2.set_title('Internal Electric Field Profile', fontsize=14)
ax2.legend()
ax2.grid(True, alpha=0.5)

plt.tight_layout()
plt.show()

print(f"Calculated Interface Charge Density: {sigma_int:.4f} C/m^2")
print(f"Calculated Electric Field in AlGaN: {E_field_AlGaN_MVcm:.2f} MV/cm")