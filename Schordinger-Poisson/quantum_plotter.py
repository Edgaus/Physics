import numpy as np
import matplotlib.pyplot as plt
import os

class QuantumAnalyzer:
    def __init__(self, x_grid, potential, energies, wavefunctions):
        """
        Initializes the c-InGaN Quantum Analyzer.
        
        Parameters:
        - x_grid: 1D array of spatial coordinates (e.g., in Ångströms)
        - potential: 1D array of the band edge potential (in eV)
        - energies: 1D array of eigenvalues from the FD solver (in eV)
        - wavefunctions: 2D array of eigenvectors from the FD solver
        """
        self.x = np.asarray(x_grid)
        self.P = np.asarray(potential)
        self.E = np.asarray(energies)
        self.psi = np.asarray(wavefunctions)
        
        # 1. Identify the barrier height to filter bound states
        # Assuming the first and last points of the grid are in the barrier
        self.barrier_height = min(self.P[0], self.P[-1])
        
        # 2. Filter only "physically accepted" bound states (E < V_barrier)
        self.bound_indices = np.where(self.E < self.barrier_height)[0]
        self.bound_energies = self.E[self.bound_indices]
        self.bound_psi = self.psi[:, self.bound_indices]
        
        print(f"c-InGaN Analyzer: Found {len(self.bound_energies)} bound states in the well.")

    def plot_wavefunctions(self, scale_factor=0.2, show_probability=False):
        """
        Plots the quantum well, energy levels, and wave functions.
        
        - scale_factor: Adjusts the vertical height of the wavefunctions for aesthetics.
        - show_probability: If True, plots |psi|^2 instead of psi.
        """
        plt.figure(figsize=(10, 6))
        
        # Plot the Band Edge Potential
        plt.plot(self.x, self.P, color='black', linewidth=2.5, label='Band Edge Potential')
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i in range(len(self.bound_energies)):
            energy = self.bound_energies[i]
            wavefunc = self.bound_psi[:, i]
            
            # Normalize the wavefunction relative to its maximum peak for consistent plotting
            wavefunc_norm = wavefunc / np.max(np.abs(wavefunc))
            
            color = colors[i % len(colors)]
            
            # Draw the energy level
            plt.axhline(y=energy, color=color, linestyle='--', alpha=0.6)
            
            if show_probability:
                # Plot Probability Density shifted up to the Energy level
                y_plot = energy + scale_factor * (wavefunc_norm**2)
                label_str = f'$|\\Psi_{i+1}|^2$ (E = {energy:.4f} eV)'
            else:
                # Plot standard Wavefunction shifted up to the Energy level
                y_plot = energy + scale_factor * wavefunc_norm
                label_str = f'$\\Psi_{i+1}$ (E = {energy:.4f} eV)'
                
            plt.plot(self.x, y_plot, color=color, linewidth=2, label=label_str)

        plt.xlabel('Position (Å)', fontsize=12)
        plt.ylabel('Energy (eV)', fontsize=12)
        plt.title('Quantum Well: Confined States and Wavefunctions', fontsize=14)
        plt.legend(loc='upper right', framealpha=0.9)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.show()

    def save_data(self, output_dir="Data/new.txt"):
        """
        Saves the physical energies and wave functions into column-formatted text files.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 1. Save Energies
        energy_file = os.path.join(output_dir, "accepted_energies.txt")
        with open(energy_file, "w") as f:
            f.write("State\tEnergy(eV)\n")
            for i, energy in enumerate(self.bound_energies):
                f.write(f"{i+1}\t{energy:.6f}\n")
        
        # 2. Save Wavefunctions and Grid Data
        wf_file = os.path.join(output_dir, "wavefunctions_data.txt")
        
        # Create Header: x, Potential, Psi_1, Psi_2, ...
        header = "x(A)\tPotential(eV)"
        for i in range(len(self.bound_energies)):
            header += f"\tPsi_{i+1}"
            
        # Stack columns together
        data_matrix = np.column_stack((self.x, self.P, self.bound_psi))
        
        # Save to file
        np.savetxt(wf_file, data_matrix, delimiter="\t", header=header, comments="")
        
        print(f"c-InGaN Analyzer: Data successfully saved to '{output_dir}'.")