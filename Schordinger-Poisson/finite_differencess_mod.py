import numpy as np
from scipy.linalg import eigh_tridiagonal

def finite_differences_mod(P, Mass, diff, L):
    """
    Solves the Schrödinger equation using Finite Differences.
    Takes 'diff' (the step sizes) directly from the Grider class!
    """
    const = 3.80998 *2

    # We get 'n' from the Potential array now, since that is our true node count
    n = len(diff) 

    
    

    Asup = np.zeros(n-1)
    Ainf = np.zeros(n-1)
    Adiag = np.zeros(n)


################## Calculation of element of matrix  #####################

    ####### Start boundary
    Asup[0] = -const/( (Mass[0]+Mass[1])*diff[0]*(L[0]**2)   ) 
    Ainf[0] = -const/( (Mass[0]+Mass[1])*diff[0]*(L[1]**2)   ) 
    Adiag[0] = -2*Asup[0] + P[0]

    i = np.arange(1, n - 2)

    
    Asup[i] =  -const/( (Mass[i]+Mass[i+1])*diff[i]*(L[i]**2)  ) 
    Ainf[i] =   -const/( (Mass[i]+Mass[1+i])*diff[i]*(L[i+1]**2)   ) 
    Adiag[i] = -Asup[i] - Ainf[i-1] + P[i]


    ####### End boundary
    last = n - 2

    Asup[last] = -const/( (Mass[-2]+Mass[-1])*diff[last]*(L[last]**2)  ) 
    Ainf[last] = -const/( (Mass[-2]+Mass[-1])*diff[last]*(L[last+1]**2)   ) 
    
    Adiag[last] = -Asup[-1] - Ainf[-2] + P[-2]
    Adiag[last+1] = -2 *Ainf[-1] + P[-1]

    A = np.diag(Adiag, k=0) + np.diag(Ainf, k=-1) + np.diag(Asup, k=1)
    

    # 1. Do the broadcasting with the 1D array
    C = A * (L[:, np.newaxis] / L)

    # 2. Now C is a proper 2D matrix, and np.diag will work perfectly
    off_diag = np.diag(C, k=1)
    main_diag = np.diag(C, k=0)

    # 3. Solve
    Eigval, Eigfun = eigh_tridiagonal(main_diag, off_diag)

    sort_indices = np.argsort(Eigval)
    Eigval = Eigval[sort_indices]
    Eigfun = Eigfun[:, sort_indices]
    
    return Eigval, Eigfun