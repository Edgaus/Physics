import numpy as np
from scipy.linalg import eig

def finite_differences(P, Mass, diff, L):
    """
    Solves the Schrödinger equation using Finite Differences.
    Takes 'diff' (the step sizes) directly from the Grider class!
    """
    const = 3.80998

    # We get 'n' from the Potential array now, since that is our true node count
    n = len(diff) 



    Asup = np.zeros(n-1)
    Ainf = np.zeros(n-1)
    Adiag = np.zeros(n)

    for i in range(n-1):
        Asup[i] = -const/( ( Mass[i]) *diff[i]*L[i])
    for i in range(1,n): 
        Ainf[i-1] = -const/ ( ( Mass[i-1] ) *diff[i-1]*L[i] )
    for i in range(1,n-1):
        Adiag[i] = -Asup[i] - Ainf[i-1] + P[i]
    
    Adiag[0], Adiag[n-1] =  -2* Asup[0] + P[0], -2*Ainf[-1] + P[-1]
 
    A =  np.diag(Adiag, 0) + np.diag(Asup, 1) + np.diag(Ainf, -1)
    
    Eigval, Eigfun = eig(A) 


    sort_indices = np.argsort(Eigval)
    Eigval = Eigval[sort_indices]
    Eigfun = Eigfun[:, sort_indices]
    
    # 9. Scale to meV
    Eigval = Eigval* 1000
    
    return Eigval, Eigfun