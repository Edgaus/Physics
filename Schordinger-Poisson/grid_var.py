import numpy as np

def heaviside(z):
    return np.where(z >= 0, 1.0, 0.0)

def grid_var(widths, masses, potential):
    width = (widths[0] + widths[1]) / 2
    upbound = 32
    lowbound = 2
    number_elements = 3
    n_val = 2

    x = np.zeros(number_elements + 1)
    x[0] = upbound
    factors = np.zeros(number_elements + 1)
    factors[0] = 1

    for i in range(1, number_elements):
        factors[i] = 1 / ((1/n_val)**i)
        x[i] = upbound / factors[i]

    x[-1] = lowbound
    factors[-1] = upbound / lowbound

    fact = np.floor(width / ((number_elements + 1) * upbound))
    factors = fact * factors

    sobrante = width - (number_elements + 1) * upbound * fact
    m = 2 

    factors[-2] += np.floor(sobrante / m / x[-2])
    factors[-1] += np.floor(((m - 1) / m) * sobrante / x[-1])

    grid_list = []
    for i in range(len(factors)):
        grid_list.extend([x[i]] * int(factors[i]))
    
    grid = np.array(grid_list)
    
    # Mirroring the grid
    flip_grid = grid[::-1]
    x_grid_half = np.cumsum(flip_grid)
    
    x_grid = np.concatenate([-x_grid_half[::-1], [0], x_grid_half])
    full_grid = np.concatenate([grid, grid[::-1]])

    # Define potential and mass profiles
    def funpar(z):
        return heaviside(z + widths[0]/2) - heaviside(z - widths[0]/2)

    V = potential * (1 - funpar(x_grid))
    M = masses[1] + (masses[0] - masses[1]) * funpar(x_grid)

    return V, M, full_grid, x_grid