import numpy as np
from scipy.interpolate import UnivariateSpline


class ComplexFresnelMatrix:

    def __init__(self, wave, index_refraction_total, thickness_structure, theta0, polarization):
        """
        Initializes the reflectance model with internal parameters.
        """
        self.wave = np.asarray(wave)
        self.index = np.asarray(index_refraction_total, dtype=complex)
        self.thickness = np.asarray(thickness_structure)
        self.theta0 = theta0
        self.polar = polarization
        
        # Initialize result attributes as None until calculated
        self.spectrum = None
        self.x_maxima = None
        self.y_maxima = None
        self.x_minima = None
        self.y_minima = None

    def spectra(self):
        
        W = len(self.wave)
        n = np.asarray(self.index, dtype=complex)


        # Initialize transfer matrices
        M_P = np.tile(np.eye(2, dtype=complex), (W, 1, 1))
        M_S = np.tile(np.eye(2, dtype=complex), (W, 1, 1))

        for m in range(1, n.shape[0] - 1):
            sin_theta_j = (n[0, :] / n[m, :]) * np.sin(self.theta0)
            cos_theta_j = np.sqrt(1 - sin_theta_j**2 + 0j)

            d_m = self.thickness[m-1] 
            beta = (2 * np.pi / self.wave) * d_m * n[m, :] * cos_theta_j

            Mp = np.zeros((W, 2, 2), dtype=complex)
            Mp[:, 0, 0] = np.cos(beta)
            Mp[:, 0, 1] = 1j * cos_theta_j * np.sin(beta) / n[m, :]
            Mp[:, 1, 0] = 1j * n[m, :] * np.sin(beta) / cos_theta_j
            Mp[:, 1, 1] = np.cos(beta)

            Ms = np.zeros((W, 2, 2), dtype=complex)
            Ms[:, 0, 0] = np.cos(beta)
            Ms[:, 0, 1] = 1j * np.sin(beta) / (n[m, :] * cos_theta_j)
            Ms[:, 1, 0] = 1j * n[m, :] * np.sin(beta) * cos_theta_j
            Ms[:, 1, 1] = np.cos(beta)

            M_P = M_P @ Mp
            M_S = M_S @ Ms

        cos_theta_0 = np.cos(self.theta0)
        sin_theta_L = (n[0, :] / n[-1, :]) * np.sin(self.theta0)
        cos_theta_L = np.sqrt(1 - sin_theta_L**2 + 0j)
        
        # Extract the dispersive index of the incident medium
        n0 = n[0, :]

        # ---------- TM / P-Polarization ----------
        P_in = np.zeros((W, 2, 2), dtype=complex)
        P_in[:, 0, 0] = n0
        P_in[:, 0, 1] = cos_theta_0
        P_in[:, 1, 0] = n0
        P_in[:, 1, 1] = -cos_theta_0
        
        P_out = np.zeros((W, 2, 2), dtype=complex)
        P_out[:, 0, 0], P_out[:, 1, 0] = cos_theta_L, n[-1, :]
        
        A_P = P_in @ M_P @ P_out
        r_P = A_P[:, 1, 0] / A_P[:, 0, 0]

        # ---------- TE / S-Polarization ----------
        S_in = np.zeros((W, 2, 2), dtype=complex)
        S_in[:, 0, 0] = n0 * cos_theta_0
        S_in[:, 0, 1] = 1
        S_in[:, 1, 0] = n0 * cos_theta_0
        S_in[:, 1, 1] = -1
        
        S_out = np.zeros((W, 2, 2), dtype=complex)
        S_out[:, 0, 0], S_out[:, 1, 0] = 1, cos_theta_L * n[-1, :]
        
        A_S = S_in @ M_S @ S_out
        r_S = A_S[:, 1, 0] / A_S[:, 0, 0]

        if self.polar == 'S-Polarized': R = np.abs(r_S)**2
        elif self.polar == 'P-Polarized': R = np.abs(r_P)**2
        else: R = 0.5*(np.abs(r_P)**2 + np.abs(r_S)**2)

        # FIX: Apply offset, amplitude, AND scale to 100 before making the spline
        self.spectrum = 100 * R


        return self

    def extract_extrema(self):
        
        # ---------- Extrema Detection ----------
        xs = self.wave 
        ys = self.spectrum
        
        idx = np.argsort(xs)
        xs, ys = xs[idx], ys[idx]

        spline = UnivariateSpline(xs, ys, k=3, s=0)
        dy_dx = spline.derivative()

        x_dense = np.linspace(xs[0], xs[-1], 2000)
        dy_dense = dy_dx(x_dense)

        sign_change = np.where(np.diff(np.sign(dy_dense)))[0]
        critical_points = x_dense[sign_change]

        d2y_dx2 = spline.derivative(n=2)
        self.x_maxima = np.array([cp for cp in critical_points if d2y_dx2(cp) < 0])
        self.x_minima = np.array([cp for cp in critical_points if d2y_dx2(cp) > 0])

        # Evaluate the spline at the found x-coordinates to get the precise y-values
        self.y_maxima = spline(self.x_maxima)
        self.y_minima = spline(self.x_minima)

        return self

        
