import numpy as np
from scipy.interpolate import interp1d

# Read data from input file
input_file = "Refraction Index\Cardona_dialectrica_imaginaria.txt"
output_file = "Refraction Index\Cardona_dialectrica_imaginaria_interpolated.txt"

# Load data (assuming x and y values in two columns)
data = np.loadtxt(input_file)
x = data[:, 0]
y = data[:, 1]

# Create interpolation function
f = interp1d(x, y, kind='linear', fill_value='extrapolate')

# Generate new x values for interpolation
x_new = np.linspace(5.5, 6.5, 2000)
y_new = f(x_new)

# Save to output file
with open(output_file, 'w') as file:
    for xi, yi in zip(x_new, y_new):
        file.write(f"{xi}\t{yi}\n")

print(f"Interpolated data saved to {output_file}")