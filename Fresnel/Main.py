# Save this as main.py
import numpy as np
from Fresnel.fresnel_engine import optimize_thickness_from_extrema # Importing your custom function

# 1. Define your Experimental Data
wave = np.linspace(400e-9, 1200e-9, 200)
max_exp = np.array([4.74e-07, 6.53e-07, 1.07e-06])
min_exp = np.array([4.19e-07, 5.52e-07, 8.02e-07])

# 2. Setup your stack
n_air = np.ones_like(wave) * 1.0
n_aln = 2.1 + (0.01 / (wave * 1e6)**2)
n_gan = 1.95 + (0.02 / (wave * 1e6)**2)
n_glass = np.ones_like(wave) * 1.5
n_stack = np.vstack([n_air, n_aln, n_gan, n_glass])

# 3. Set Search Bounds and Run
d_bounds = [(100e-9, 200e-9), (200e-9, 300e-9)]
theta0 = 0

# Just call the function like you would in MATLAB
thickness_results = optimize_thickness_from_extrema(
    min_exp, max_exp, wave, n_stack, d_bounds, theta0, polarization='m'
)

print(f"Resulting thicknesses: {thickness_results}")