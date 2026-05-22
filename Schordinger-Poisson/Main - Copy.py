import numpy as np
from finite_differencess import finite_differences

# Parameters
pot_val = 0.23
width_well = 56
width_barrier = 12 * 56
mass_well = 0.067
mass_barrier = 0.092

mesh_well = 4
mesh_barrier = 4

# Create grid points
x_left = np.arange(-(width_well + width_barrier)/2, -width_well/2 + mesh_barrier, mesh_barrier)
x_center = np.arange(-width_well/2, width_well/2 + mesh_well, mesh_well)
x_right = np.arange(width_well/2, (width_well + width_barrier)/2 + mesh_barrier, mesh_barrier)

x = np.unique(np.concatenate([x_left, x_center, x_right]))
h = np.diff(x)

# Initialize Arrays
# Adjusting sizes to match the grid intervals (h)
num_intervals = len(h)
masses = np.ones(num_intervals) * mass_barrier
potential = np.ones(num_intervals) * pot_val

# Define the well region based on index logic from original code
# Note: In Python, we ensure we slice correctly relative to the center
well_mask = (x[:-1] >= -width_well/2) & (x[:-1] <= width_well/2)
masses[well_mask] = mass_well
potential[well_mask] = 0

# Solve
eigenvalues, eigenfunctions = finite_differences(potential, masses, h)

# Sort results
idx = np.argsort(eigenvalues)
energies = eigenvalues[idx]
eigen_vectors = eigenfunctions[:, idx]

print("Lowest Energy States (meV):")
print(energies[0:2])


