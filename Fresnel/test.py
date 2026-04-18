import numpy as np
import matplotlib.pyplot as plt
import ComplexFresnelMatrix as cfm
import pandas as pd


lf = 900
li = 400
wave = np.linspace(li, lf, lf-li+1)


print(   wave[0], wave[-1]     )

# Define n as arrays (Dispersive)
n_air = np.ones_like(wave) * 1.0
n_aln = 2.1 + (0.01 / (wave * 1e6)**2) # Simple dispersion model example
n_glass = np.ones_like(wave) * 1.5


n_sio2 = pd.read_csv('Fresnel\Data\SiO2_n.txt',  delimiter='\t') # Assuming two columns: wavelength (nm) and n
k_sio2 = pd.read_csv('Fresnel\Data\SiO2_k.txt',  delimiter='\t') # Assuming two columns: wavelength (nm) and k

n_sio2_interp = np.interp(wave, n_sio2[:, 0], n_sio2[:, 1])
k_sio2_interp = np.interp(wave, k_sio2[:, 0], k_sio2[:, 1])      

nsio2 = n_sio2_interp - 1j * k_sio2_interp

n_si = pd.read_csv('Fresnel\Data\Si_n.txt',  delimiter='\t') # Assuming two columns: wavelength (nm) and n
k_si = pd.read_csv('Fresnel\Data\Si_k.txt',  delimiter='\t') # Assuming two columns: wavelength (nm) and k

n_si_interp = np.interp(wave, n_si[:, 0], n_si[:, 1])
k_si_interp = np.interp(wave, k_si[:, 0], k_si[:, 1])

n_si_complex = n_si_interp - 1j * k_si_interp

# Structure: [Incident, Layer1, Substrate]
structure_n = np.vstack([n_air, nsio2, n_si_complex])
thicknesses = [150] # Thickness of AlN
theta0 = np.radians(0)

result= cfm.ComplexFresnelMatrix(wave, structure_n, thicknesses, theta0, 'Mixed')



print(result.x_maxima)
print(result.y_maxima)
print(result.x_minima)
print(result.y_minima)

plt.figure(figsize=(8, 5))
plt.plot(wave, result.spectrum, label='Total Reflectance')
plt.xlabel('Wavelength (m)')
plt.ylabel('R')
plt.title('Vectorized Fresnel Matrix (Dispersive)')
plt.grid(True)
plt.show()