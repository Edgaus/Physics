import numpy as np

# 1. Define your matrices
# a_diag is the 1D array containing the diagonal elements of A
a_diag = np.array([2.0, 4.0, 10.0])

# B is your standard 2D matrix
B = np.array([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
    [7.0, 8.0, 9.0]
])

# 2. The Math (O(n^2) instead of O(n^3))
# a_diag[:, np.newaxis] turns the 1D array into a column (scales rows by a_i)
# Dividing by a_diag scales the columns by a_j (which acts exactly like multiplying by A^-1)
C = B * (a_diag[:, np.newaxis] / a_diag)

print("Result of A * B * A^-1:")
print(C)