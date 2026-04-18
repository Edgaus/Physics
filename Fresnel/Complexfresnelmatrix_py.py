import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import pchip_interpolate
from scipy.optimize import minimize_scalar
import os




def der_functi(sample, limit_1, limit_2):
    """
    Extracts experimental peaks and valleys from data within a specific wavelength range.
    Applies targeted smoothing to noisier regions.
    """
    # 1. Load the data
    file_name = f'Fresnel/Experimental/{sample}.txt'
    data = np.loadtxt(file_name)
    x_full = data[:, 0]
    y_raw_full = data[:, 1]

    # --- NEW: Crop the data to the region of interest (225 - 390 nm) ---
    # We use boolean masking in NumPy to filter the arrays
    region_idx = (x_full >= limit_1) & (x_full <= limit_2)
    x = x_full[region_idx]
    y_raw = y_raw_full[region_idx]

    # 2. Split the data at X = 300
    # np.argmax on a boolean array returns the index of the first True value
    split_idx = np.argmax(x >= 300)
    
    y_part1 = y_raw[:split_idx]
    y_part2 = y_raw[split_idx:]

    # 3. Apply heavy smoothing ONLY to the noisy part (>300)
    window_size = 25
    # uniform_filter1d replicates Octave's movmean behavior well, preserving array length
    y_part2_smooth = uniform_filter1d(y_part2, size=window_size)

    # 4. Recombine
    y_combined = np.concatenate((y_part1, y_part2_smooth))

    # 5. Safe Shift and Thresholds
    y_offset = np.min(y_combined)
    y_shifted = y_combined - y_offset + 1

    # Slightly stricter thresholds to ensure exactly 2 peaks
    min_h = 0.01   # Ignore tiny ripples
    min_dist = 60  # 60 points = 15 nm minimum separation

    # 6. Find Peaks and Valleys
    max_idx, _ = find_peaks(y_shifted, height=min_h, distance=min_dist)
    
    flipped_y = -y_shifted + np.max(y_shifted)
    min_idx, _ = find_peaks(flipped_y, height=min_h, distance=min_dist)

    x_max = x[max_idx]
    x_min = x[min_idx]

    # Optional: Uncomment these lines to visually verify it only found 2 of each!
    # plt.figure(99)
    # plt.clf()
    # plt.plot(x, y_combined, 'k-')
    # plt.plot(x_max, y_combined[max_idx], 'r^', markersize=10)
    # plt.plot(x_min, y_combined[min_idx], 'bv', markersize=10)
    # plt.show()

    return x_max, x_min


def complex_fresnel_matrix(wave, n, thickness, theta0, polar):
    # Convert inputs to numpy arrays
    n = np.asarray(n, dtype=complex)
    
    # Force thickness to be at least a 1D array so it can always be indexed
    thickness = np.atleast_1d(thickness).astype(float)
    # Initialize 2x2 identity matrices
    M_P = np.eye(2, dtype=complex)
    M_S = np.eye(2, dtype=complex)
    
    # Python is 0-indexed. 
    # Octave's `2:length(n)-1` becomes `range(1, len(n) - 1)`
    for m in range(1, len(n) - 1):
        
        # Snell's law to find the angle in the current layer
        theta_j = np.arcsin((n[0] / n[m]) * np.sin(theta0))
        
        # Phase thickness
        # Octave's `m-1` index maps directly since our loop starts at 1
        beta = (2 * np.pi / wave) * thickness[m-1] * n[m] * np.cos(theta_j)
        
        # Characteristic matrix for P-polarization
        Mp = np.array([
            [np.cos(beta), 1j * np.cos(theta_j) * np.sin(beta) / n[m]],
            [1j * n[m] * np.sin(beta) / np.cos(theta_j), np.cos(beta)]
        ], dtype=complex)
        
        # Use '@' for matrix multiplication in Python
        M_P = M_P @ Mp
        
        # Characteristic matrix for S-polarization
        Ms = np.array([
            [np.cos(beta), 1j * np.sin(beta) / (n[m] * np.cos(theta_j))],
            [1j * n[m] * np.sin(beta) * np.cos(theta_j), np.cos(beta)]
        ], dtype=complex)
        
        M_S = M_S @ Ms

    # Angle in the final substrate (n[-1] gets the last element in Python)
    theta_j_1 = np.arcsin((n[0] / n[-1]) * np.sin(theta0))

    # Construct P-polarization assembly matrices
    P_in = np.array([[1, np.cos(theta0)], [1, -np.cos(theta0)]], dtype=complex)
    P_out = np.array([[np.cos(theta_j_1), 0], [n[-1], 0]], dtype=complex)
    A_P = (1 / (2 * np.cos(theta0))) * P_in @ M_P @ P_out

    # Construct S-polarization assembly matrices
    S_in = np.array([[np.cos(theta0), 1], [np.cos(theta0), -1]], dtype=complex)
    S_out = np.array([[1, 0], [np.cos(theta_j_1) * n[-1], 0]], dtype=complex)
    A_S = (1 / (2 * np.cos(theta0))) * S_in @ M_S @ S_out

    # Reflection coefficients
    # Octave's A_P(2,1) and A_P(1,1) correspond to Python's A_P[1, 0] and A_P[0, 0]
    r_P = A_P[1, 0] / A_P[0, 0]
    r_S = A_S[1, 0] / A_S[0, 0]

    # Calculate final Reflectance R
    R = 0
    if polar == 's':
        R = np.abs(r_S)**2
    elif polar == 'p':
        R = np.abs(r_P)**2
    elif polar == 'm':
        R = 0.5 * (np.abs(r_P)**2 + np.abs(r_S)**2)
    else:
        raise ValueError("Invalid polarization. Choose 's', 'p', or 'm'.")

    return R.real # Optional: .real strips the ~0j imaginary residual to return a float














def target_function__peaks(thick, n_aln, n_si, lambda_nm, exp_x_max, exp_x_min):
    """
    Evaluates the error between simulated and experimental reflectance peaks.
    Requires complex_fresnel_matrix to be defined in the same scope.
    """
    # --- A. Generate Simulated Curve ---
    R = np.zeros(len(lambda_nm))
    
    # Iterate through each wavelength to calculate Reflectance
    for m in range(len(lambda_nm)):
        n_structure = [1.0, n_aln[m], n_si[m]]
        # Using the complex_fresnel_matrix function defined earlier
        R[m] = complex_fresnel_matrix(lambda_nm[m], n_structure, thick, np.deg2rad(45), 'm')
        
    R_opt = R

    # --- B. Find Peaks in Simulated Curve dynamically ---
    y_offset = np.min(R)
    y_shifted = R - y_offset + 1

    # Thresholds for simulated data
    min_h = 0.005
    min_dist = 40  # Note: SciPy distance is in indices/samples, matching Octave's default

    # Find Maxima
    # scipy's find_peaks returns a tuple: (indices, properties_dict)
    sim_max_idx, _ = find_peaks(y_shifted, height=min_h, distance=min_dist)

    # Find Minima (by flipping the curve upside down)
    flipped_y = -y_shifted + np.max(y_shifted)
    sim_min_idx, _ = find_peaks(flipped_y, height=min_h, distance=min_dist)

    # Map indices back to wavelength values
    sim_x_max = lambda_nm[sim_max_idx]
    sim_x_min = lambda_nm[sim_min_idx]

    # --- C. Apply User's Custom Formula Error ---
    total_error = 0.0

    # Safety Catch: if simulation flatlines
    if len(sim_x_max) == 0 or len(sim_x_min) == 0:
        total_error = 1e6
        return total_error, R_opt

    # Compare Maxima
    for exp_val in exp_x_max:
        # np.argmin finds the index of the minimum value in the array
        closest_idx = np.argmin(np.abs(sim_x_max - exp_val))
        matched_sim_x = sim_x_max[closest_idx]
        total_error += (abs(matched_sim_x / exp_val - 1))**2

    # Compare Minima
    for exp_val in exp_x_min:
        closest_idx = np.argmin(np.abs(sim_x_min - exp_val))
        matched_sim_x = sim_x_min[closest_idx]
        total_error += (abs(matched_sim_x / exp_val - 1))**2

    # --- D. Apply Mismatch Penalty ---
    # If the thickness guess creates 5 peaks but the experiment only has 3,
    # we MUST punish it so it doesn't choose that thickness.
    if len(sim_x_max) != len(exp_x_max) or len(sim_x_min) != len(exp_x_min):
        total_error += 10  # Massive penalty

    return total_error, R_opt



























# --- SETUP ---
sample = 'm672'
# Using forward slashes or os.path is safer across different operating systems in Python
file_name = f'Fresnel/Experimental/{sample}.txt'
limit_1 = 215
limit_2 = 390

# Load Raw Data
# np.loadtxt is the standard way to load numerical text files in Python
data = np.loadtxt(file_name)
x_full = data[:, 0] # 0-indexed in Python
y_full = data[:, 1]

# --- 1. GET EXPERIMENTAL PEAKS ---
print('Extracting Experimental Peaks...')
# NOTE: You must define or import `der_functi` in Python
x_max_exp, x_min_exp = der_functi(sample, limit_1, limit_2)

print('Experimental Maxima found at:\n', np.array(x_max_exp).T)
print('Experimental Minima found at:\n', np.array(x_min_exp).T)

# --- 2. LOAD OPTICAL CONSTANTS ---
index_refrac_aln = np.loadtxt('Fresnel/Data/AlN_n2.txt')
Wavelength_index_aln = index_refrac_aln[:, 0]
aln_index = index_refrac_aln[:, 1]

extintion_coeff = np.loadtxt('Fresnel/Data/AlN_k2.txt')
Wavelength_extin_aln = extintion_coeff[:, 0]
aln_extin = extintion_coeff[:, 1]

index_refrac_si = np.loadtxt('Fresnel/Data/Si_n2.txt')
Wavelength_index_si = index_refrac_si[:, 0]
si_index = index_refrac_si[:, 1]

extintion_coeff_si = np.loadtxt('Fresnel/Data/Si_k2.txt')
Wavelength_extin_si = extintion_coeff_si[:, 0]
si_extin = extintion_coeff_si[:, 1]

# Interpolate onto standard wavelength grid
lambda_nm = np.linspace(limit_1, limit_2, 750)  # [nm]

# Scipy's pchip_interpolate is the equivalent to Octave's interp1(..., 'pchip')
n_aln = (pchip_interpolate(Wavelength_index_aln, aln_index, lambda_nm) - 
         1j * pchip_interpolate(Wavelength_extin_aln, aln_extin, lambda_nm))

n_si = (pchip_interpolate(Wavelength_index_si, si_index, lambda_nm) - 
        1j * pchip_interpolate(Wavelength_extin_si, si_extin, lambda_nm))

# --- 3. RUN OPTIMIZATION ---
min_thickness = 150
max_thickness = 230

print('Starting Peak-Matching Optimization...')

# We wrap target_function__peaks_peaks in a lambda that only returns the first output (the error metric)
# because minimize_scalar expects a single float value to minimize.
# NOTE: You must define or import `target_function__peaks` in Python
res = minimize_scalar(
    lambda t: target_function__peaks(t, n_aln, n_si, lambda_nm, x_max_exp, x_min_exp)[0],
    bounds=(min_thickness, max_thickness),
    method='bounded',
    options={'xatol': 1e-9, 'disp': 3} # disp: 3 is similar to 'Display': 'iter'
)

best_thickness = res.x
final_error = res.fun

print(f'\nSuccess! The optimal thickness is: {best_thickness:.5f} nm')

# --- 4. PLOT FINAL RESULTS ---
# Run the function one last time to get the Simulated Array for plotting
_, R_best = target_function__peaks(best_thickness, n_aln, n_si, lambda_nm, x_max_exp, x_min_exp)

plt.figure(1, figsize=(8, 6))
plt.clf()

# Plot experimental data
plt.plot(x_full, y_full, 'k-', linewidth=1.5, label='Experimental Raw')

# Plot simulated data
plt.plot(lambda_nm, R_best, 'r--', linewidth=2, label=f'Simulated ({best_thickness:.2f} nm)')

# Plot true experimental peaks as markers
# np.interp performs basic linear interpolation, equivalent to Octave's default interp1
y_max_exp = np.interp(x_max_exp, x_full, y_full)
y_min_exp = np.interp(x_min_exp, x_full, y_full)

plt.plot(x_max_exp, y_max_exp, 'b^', markerfacecolor='b', markersize=8, label='Exp Max')
plt.plot(x_min_exp, y_min_exp, 'gv', markerfacecolor='g', markersize=8, label='Exp Min')

# Formatting the plot
plt.xlim([225, 390])
plt.xlabel('Wavelength (nm)')
plt.ylabel('Reflectance')
plt.title('Peak-to-Peak Optimization Match')
plt.legend(loc='upper right')
plt.grid(True)

# Display the plot
plt.show()


















