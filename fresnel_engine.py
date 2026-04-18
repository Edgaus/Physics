import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
from scipy.optimize import minimize, least_squares, differential_evolution
import ComplexFresnelMatrix as cfm

class FresnelOptimizer:
    def __init__(self, range_of_fit, exp_x, exp_y, initial_conditions, target_function, method_fit):
        """
        range_of_fit: [lambda_start, lambda_end]
        initial_conditions: Dictionary containing {'index_refr': matrix, 'thick_guess': array, 'theta': float, 'polar': str}
        """
        self.lam_start, self.lam_end = range_of_fit[0], range_of_fit[1]
        self.sim_wave = np.arange(self.lam_start, self.lam_end + 1, 1)
        
        # Align Experimental Data
        exp_x_flat = np.asarray(exp_x).flatten()
        exp_y_flat = np.asarray(exp_y).flatten()
        f_interp = interp1d(exp_x_flat, exp_y_flat, kind='cubic', fill_value="extrapolate")
        self.exp_y_aligned = f_interp(self.sim_wave)

        # Physics Conditions
        self.index_matrix = initial_conditions['index_refr']
        self.initial_guess = np.asarray(initial_conditions['thick_guess'])
        self.theta = initial_conditions['theta'] # Arrives safely in Radians
        self.polar = initial_conditions['polar']
        
        # Optimizer Settings
        self.target = target_function
        self.method_fit = method_fit
        self.bounds = initial_conditions.get('bounds', None)
        
# --- OFFSET LOGIC: Apply to EVERYTHING except extrema_x ---
        self.fit_offset = (self.target != 'extrema_x')
        
        if self.fit_offset:
            self.initial_guess = np.append(self.initial_guess, 0.0)
            if self.bounds is not None:
                self.bounds = list(self.bounds)
                
                # --- CHANGE THIS LINE ---
                # Old code: self.bounds.append((-0.5, 0.5))
                # New code: Allow a massive shift of up to +/- 100 units
                self.bounds.append((-25.0, 25.0))

        # Pre-calculate Peaks for extrema matching
        if 'extrema' in self.target:
            peak_indices, _ = find_peaks(self.exp_y_aligned)
            self.exp_x_maxima = self.sim_wave[peak_indices]
            self.exp_y_maxima = self.exp_y_aligned[peak_indices]

        # Results
        self.best_params = None
        self.best_fit_spectrum = None

    def _run_physics_model(self, trial_thicknesses):
        model = cfm.ComplexFresnelMatrix(
            self.sim_wave, 
            self.index_matrix, 
            trial_thicknesses, 
            self.theta, 
            polarization=self.polar
        )
        model.spectra()
        return model

    def target_function_residuals(self, trial_params):
        # Unpack the offset if it exists
        if self.fit_offset:
            trial_thicknesses = trial_params[:-1]
            trial_offset = trial_params[-1]
        else:
            trial_thicknesses = trial_params
            trial_offset = 0.0

        model = self._run_physics_model(trial_thicknesses)
        sim_spectrum = np.real(model.spectrum).astype(np.float64).flatten() + trial_offset

        # ================= TARGET ROUTING =================
        if self.target == 'spectra': 
            safe_exp = np.where(self.exp_y_aligned == 0, 1e-10, self.exp_y_aligned)
            residuals = (sim_spectrum / safe_exp) - 1.0
            
        elif self.target == 'absolute': 
            residuals = sim_spectrum - self.exp_y_aligned
            
        elif self.target == 'derivative': 
            grad_sim = np.gradient(sim_spectrum)
            grad_exp = np.gradient(self.exp_y_aligned)
            residuals = grad_sim - grad_exp
            
        elif self.target == 'hybrid': 
            residuals = sim_spectrum - self.exp_y_aligned
            sim_peaks, _ = find_peaks(sim_spectrum)
            exp_peaks, _ = find_peaks(self.exp_y_aligned)
            if len(sim_peaks) != len(exp_peaks):
                residuals *= 10.0 
                
        elif self.target == 'extrema_x':
            model.extract_extrema()
            residuals = self._error_extrema(model, use_y=False)
            
        elif self.target == 'extrema_xy':
            model.extract_extrema()
            # Pass the offset into the extrema error function to adjust the peak heights!
            residuals = self._error_extrema(model, use_y=True, offset=trial_offset)
            
        else:
            raise ValueError(f"Unknown target: {self.target}")

        return np.asarray(residuals, dtype=np.float64).flatten()

    def _mse_wrapper(self, trial_params):
        relative_residuals = self.target_function_residuals(trial_params)
        return np.mean(relative_residuals**2)

    def _error_extrema(self, model, use_y=False, offset=0.0):
        error_list = []
        if len(model.x_maxima) == 0:
            return np.array([9999.0] * len(self.exp_x_maxima)) 
            
        for i, exp_x in enumerate(self.exp_x_maxima):
            closest_idx = np.argmin(np.abs(model.x_maxima - exp_x))
            sim_x = model.x_maxima[closest_idx]
            error_list.append(sim_x - exp_x)
            
            if use_y:
                # Add the offset to the simulated peak height before comparing!
                sim_y_shifted = model.y_maxima[closest_idx] + offset
                error_list.append(sim_y_shifted - self.exp_y_maxima[i])
                
        return np.array(error_list)

    def fit(self):
        print(f"Running {self.method_fit} optimization for {self.target}...")

        if self.method_fit == 'Least_squares':
            bnds = ([-np.inf]*len(self.initial_guess), [np.inf]*len(self.initial_guess)) if self.bounds is None else ([b[0] for b in self.bounds], [b[1] for b in self.bounds])
            res = least_squares(self.target_function_residuals, x0=self.initial_guess, bounds=bnds)
            self.best_params = res.x
            
        elif self.method_fit in ['Nelder-Mead', 'L-BFGS-B']:
            res = minimize(self._mse_wrapper, x0=self.initial_guess, method=self.method_fit, bounds=self.bounds)
            self.best_params = res.x
            
        elif self.method_fit == 'Differential_evolution':
            # Tuned settings for thin-film interference!
            res = differential_evolution(
                self._mse_wrapper, 
                bounds=self.bounds,
                strategy='best1bin', 
                popsize=15, 
                mutation=(0.5, 1.0), 
                recombination=0.7, 
                tol=1e-5
            )
            self.best_params = res.x
        else:
            raise ValueError(f"Unknown method selected: '{self.method_fit}'. Please check the UI dropdown.")

        # Separate the offset from the thicknesses to send back to the UI
        if self.fit_offset:
            final_thicknesses = self.best_params[:-1]
            final_offset = self.best_params[-1]
            print(f"Calculated Baseline Offset: {final_offset:.4f}")
        else:
            final_thicknesses = self.best_params
            final_offset = 0.0

        best_model = self._run_physics_model(final_thicknesses)
        self.best_fit_spectrum = np.real(best_model.spectrum).flatten() + final_offset

        return final_thicknesses, self.best_fit_spectrum