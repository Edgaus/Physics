import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import ComplexFresnelMatrix as cfm 
from scipy.interpolate import interp1d as interp1 
from pathlib import Path
import fresnel_engine as fe
import ComplexFresnelMatrix as cfm
import pandas as pd

# --- Constants ---
MATERIALS = ["Air", "AlSb" ,  "Al49Ga51As","AlN (cubico)", "AlN Film" ,"AlN (hexagonal)", "GaN (hexagonal)", "GaAs","GaN (cubico)","InGaN (cubico) 10% San_Luis", "MgO", "Si" ,"SiC" ,"SiO2", "TiN","Pet" ]

values_target_functions = ["spectra", "absolute", "derivative", "hybrid", "extrema_x"]

# ================= CUSTOM VECTOR BUTTONS =================

class CircularRemoveButton(tk.Canvas):
    def __init__(self, master, command=None, size=24, **kwargs):
        super().__init__(master, width=size, height=size, bg="#121212", highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        pad = 2
        self.circle = self.create_oval(pad, pad, size-pad, size-pad, outline="#444", width=1.5)
        offset = 7
        self.create_line(offset, offset, size-offset, size-offset, fill="#e74c3c", width=2.5, capstyle="round")
        self.create_line(size-offset, offset, offset, size-offset, fill="#e74c3c", width=2.5, capstyle="round")
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)
        self.bind("<Enter>", lambda e: self.itemconfig(self.circle, outline="#777"))
        self.bind("<Leave>", lambda e: self.itemconfig(self.circle, outline="#444"))

class CircularAddButton(tk.Canvas):
    def __init__(self, master, command=None, size=20, **kwargs):
        super().__init__(master, width=size, height=size, bg="#121212", highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        offset = 2
        self.create_line(size/2, offset, size/2, size-offset, fill="#2ecc71", width=3.5, capstyle="round")
        self.create_line(offset, size/2, size-offset, size/2, fill="#2ecc71", width=3.5, capstyle="round")
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)

# ================= MAIN APPLICATION =================

class LayerStackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fresnel Reflectance Simulation (Edgaus)")
        
        # 1. WINDOW STATE: Open Maximized
        try:
            self.state('zoomed') # Windows
        except:
            self.attributes("-zoomed", True) # Linux/Mac

        self.configure(background="#121212")
        
        # 2. Initialize Variables
        self.layers = []
        self.sim_data = None
        self.exp_data = None
        self.file_name = None

        # Simulation Variables
        self.lambda_start = tk.DoubleVar(value=300.0)
        self.lambda_end   = tk.DoubleVar(value=1100.0)
        self.theta_inc    = tk.DoubleVar(value=15.0)
        self.polarization = tk.StringVar(value="Mixed")

        # Optimization Variables
        self.best_sucess = []
        self.opt_active = tk.BooleanVar(value=False)
        self.best_fit_success = tk.BooleanVar(value=False)
        self.opt_target = tk.StringVar(value="spectra")
        self.opt_method = tk.StringVar(value="differential_evolution")
        self.opt_lam_start = tk.DoubleVar(value=350.0)
        self.opt_lam_end = tk.DoubleVar(value=1000.0)

        
        # 3. Setup UI
        self.setup_styles()
        self.setup_layout()

        # 4. Add Default Layers
        self.add_layer(material="Air", thickness=None, fixed=True) 
        self.add_layer(material="AlN (hexagonal)", thickness=100.0, fixed=False)
        self.add_layer(material="Si", thickness=None, fixed=True)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        BG, FG, BLUE = "#121212", "white", "#0066CC"

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG,   foreground=BLUE, font=('Segoe UI', 10, 'italic'))
        
        
        style.configure("SubTitle.TLabelframe", background=BG, foreground=FG, bordercolor="#555")
        style.configure("SubTitle.TLabelframe.Label", background=BG, foreground=FG, font=("Segoe UI", 13, "bold"))

        style.configure("TSeparator", background="#333")

    def setup_layout(self):
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)


# ================= LEFT PANEL =================
        left = ttk.Frame(main, padding=10)
        left.grid(row=0, column=0, sticky="ns")

        # ================= ROW 0: Multilayer Structure (SCROLLABLE) =================
        layer_box = ttk.LabelFrame(left, text="Multilayer Structure",  labelanchor= 'n' ,style="SubTitle.TLabelframe", padding=10)
        layer_box.grid(row=0, column=0, sticky="nsew", pady=15)
        
        # Scrollable Canvas Setup
        self.layer_canvas = tk.Canvas(layer_box, bg="#121212", highlightthickness=0, height=350, width=420)
        self.layer_scrollbar = ttk.Scrollbar(layer_box, orient="vertical", command=self.layer_canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.layer_canvas)
        self.scrollable_frame.columnconfigure(1, minsize=130)
        
        self.canvas_window = self.layer_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.layer_canvas.configure(scrollregion=self.layer_canvas.bbox("all")))
        self.layer_canvas.configure(yscrollcommand=self.layer_scrollbar.set)

        self.layer_canvas.grid(row=0, column=0, sticky="nsew")
        self.layer_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.layer_canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.layer_canvas.bind('<Leave>', self._unbound_to_mousewheel)

        # ================= ROW 1: Initial Conditions =================


        initial_conditions_frame = ttk.LabelFrame(left, text="Condiciones Iniciales",  labelanchor= 'n', style="SubTitle.TLabelframe", padding=15)
        initial_conditions_frame.grid(row=1, column=0, sticky="ew", pady=10)
        
        ttk.Label(initial_conditions_frame, text="Start Wavelength (nm)").grid(row=0, column=0) 
        ttk.Spinbox(initial_conditions_frame, textvariable=self.lambda_start, width=15, from_=200.0, to=2000.0, increment=1.0).grid(row=1, column=0)

        ttk.Label(initial_conditions_frame, text="End Wavelength (nm)").grid(row=0, column=2) 
        ttk.Spinbox(initial_conditions_frame, textvariable=self.lambda_end, width=15, from_=200.0, to=2000.0, increment=1.0).grid(row=1, column=2, padx=10)        

        ttk.Label(initial_conditions_frame, text="Angle of incidence").grid(row=2, column=0, pady=5) 
        ttk.Spinbox(initial_conditions_frame, from_=0, to=90, width=5, textvariable=self.theta_inc).grid(row=3, column=0, padx=5, pady=5)

        ttk.Label(initial_conditions_frame, text="Polarization").grid(row=2, column=2, pady=5)
        ttk.Combobox(initial_conditions_frame, values=["Mixed", "S-Polarized", "P-Polarized"], 
                     textvariable=self.polarization, width=12, state="readonly").grid(row=3, column=2, padx=5, pady=5)



        # ================= ROW 2: Optimization Process =================



        self.opt_frame = ttk.LabelFrame(left, text="Optimization Process", labelanchor= 'n', style="SubTitle.TLabelframe", padding=15)
        self.opt_frame.grid(row=2, column=0, sticky="ew", pady=10)

        self.opt_toggle_btn = tk.Button(
            self.opt_frame, text="🔴 Optimization: OFF", bg="#333333", fg="white", 
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.toggle_optimization
        )
        self.opt_toggle_btn.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))

        ttk.Label(self.opt_frame, text="Target Function").grid(row=1, column=0, sticky="w")
        self.opt_cb_target = ttk.Combobox(self.opt_frame, values= values_target_functions, textvariable=self.opt_target, state="disabled", width=12)
        self.opt_cb_target.grid(row=2, column=0, padx=5, pady=5)

        ttk.Label(self.opt_frame, text="Opt. Method").grid(row=1, column=2, sticky="w", padx=(10, 0))
        self.opt_cb_method = ttk.Combobox(self.opt_frame, values=["least_squares", "Nelder-Mead", "L-BFGS-B",'differential_evolution' ], textvariable=self.opt_method, state="disabled", width=18)
        self.opt_cb_method.grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(self.opt_frame, text="λ Start (nm)").grid(row=3, column=0, sticky="w")
        self.opt_spin_start = ttk.Spinbox(self.opt_frame, textvariable=self.opt_lam_start, from_=200, to=2000, increment=1.0, width=14, state="disabled")
        self.opt_spin_start.grid(row=4, column=0, padx=5, pady=5)

        ttk.Label(self.opt_frame, text="λ End (nm)").grid(row=3, column=2, sticky="w", padx=(10, 0))
        self.opt_spin_end = ttk.Spinbox(self.opt_frame, textvariable=self.opt_lam_end, from_=200, to=2000, increment=1.0, width=20, state="disabled")
        self.opt_spin_end.grid(row=4, column=2, padx=5, pady=5)

        self.opt_run_btn = ttk.Button(self.opt_frame, text="⚡ Run Optimizer", state="disabled", command=self.run_optimization)
        self.opt_run_btn.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(15, 0))

        # ================= ROW 3: Action Buttons =================
        action_box = ttk.Frame(left)
        action_box.grid(row=3, column=0, sticky="ew", pady=10) 
        
        # Changed 'side' to "left" for all three so they stack neatly horizontally
        ttk.Button(action_box, text="📂 Load Exp", command=self.load_experimental_data).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(action_box, text="💾 Save Sim", command=self.save_simulation_data).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(action_box, text="▶ Calculate", command=self.calculate).pack(side="left", fill="x", expand=True, padx=2)

        # ================= RIGHT PANEL (Plot) =================
        right = ttk.Frame(main, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(6, 8), facecolor='#121212')
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= SCROLL AND LAYER LOGIC =================

    def _bound_to_mousewheel(self, event): self.layer_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event): self.layer_canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event): self.layer_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_layer(self, material="", thickness=0, fixed=False, index=None):
        layer = {
            "material": tk.StringVar(value=material), 
            "thickness": tk.DoubleVar(value=0.0 if thickness is None else thickness), 
            "opt_thickness": tk.DoubleVar(value=0.0 if thickness is None else thickness), # Stores optimized result
            "bound_thickness": tk.DoubleVar(value=0.0 if thickness is None else thickness), # Stores bound range
            "fixed": fixed
        }
        if index is None: self.layers.append(layer)
        else: self.layers.insert(index, layer)
        self.Main_layers()

    def remove_layer(self, index):
        if not self.layers[index]["fixed"]:
            self.layers.pop(index)
            self.Main_layers()

    def Main_layers(self):
        # Clear out current drawing from the scrollable frame
        for w in self.scrollable_frame.winfo_children(): 
            w.destroy()
           
        is_opt_on = self.opt_active.get() # Check if optimization is toggled ON
    
        best_thickness_array = self.best_sucess
        for i, layer in enumerate(self.layers):
            row_idx = i * 2
            
            # 1. Red X Button
            if not layer["fixed"]:
                CircularRemoveButton(self.scrollable_frame, command=lambda idx=i: self.remove_layer(idx)).grid(row=row_idx, column=0, padx=5)
            
            # 2. Material Dropdown
            cb = ttk.Combobox(self.scrollable_frame, values=MATERIALS, textvariable=layer["material"], width=20, state="readonly")
            cb.grid(row=row_idx, column=1, sticky="w", pady=8)
            
            # 3. Thickness Input & Optimization Column
            if not layer["fixed"]:
                ttk.Spinbox(self.scrollable_frame, textvariable=layer["thickness"], from_=0, to=5000, width=8).grid(row=row_idx, column=2, padx=5)
                ttk.Label(self.scrollable_frame, text="nm").grid(row=row_idx, column=3)
                
                # Show Optimized Thickness if active
                
                if is_opt_on:
                    ttk.Spinbox(self.scrollable_frame, textvariable=layer["bound_thickness"], width=5, from_= 0, to=100.0, increment=1.0, foreground="#2ecc71", font=("Segoe UI", 10, "bold")).grid(row=row_idx, column=5, padx=(10, 5))        
                    # THE FIX:
                    ttk.Label(self.scrollable_frame, textvariable=layer["opt_thickness"], foreground="#2ecc71", font=("Segoe UI", 10, "bold")).grid(row=row_idx, column=4, padx=(10, 5))
                  
            else:
                ttk.Label(self.scrollable_frame, text="— (Infinite)").grid(row=row_idx, column=2, columnspan=2, padx=5, sticky="w")
                if is_opt_on:
                    ttk.Label(self.scrollable_frame, text="—", foreground="#777").grid(row=row_idx, column=4, padx=(10, 5))
                    ttk.Label(self.scrollable_frame, text="—", foreground="#777").grid(row=row_idx, column=4, padx=(10, 5))

            # 4. Green Plus Button & Separator
            if i < len(self.layers) - 1:
                sep_row = row_idx + 1
                span = 5 if is_opt_on else 3 # Widen separator to cover new column
                ttk.Separator(self.scrollable_frame, orient="horizontal").grid(row=sep_row, column=1, columnspan=span, sticky="ew", pady=2)
                CircularAddButton(self.scrollable_frame, command=lambda idx=i+1: self.add_layer("AlN (hexagonal)", 100, False, idx)).grid(row=sep_row, column=1, columnspan=span)

# ==================== OPTIMIZATION LOGIC ==================
    
    def toggle_optimization(self):
        is_active = self.opt_active.get()
        if not is_active:
            self.opt_active.set(True)
            self.opt_toggle_btn.config(text="🟢 Optimization: ON", bg="#2ecc71", fg="#121212")
            self.opt_cb_target.config(state="readonly")
            self.opt_cb_method.config(state="readonly")
            self.opt_spin_start.config(state="normal")
            self.opt_spin_end.config(state="normal")
            self.opt_run_btn.config(state="normal")
        else:
            self.opt_active.set(False)
            self.opt_toggle_btn.config(text="🔴 Optimization: OFF", bg="#333333", fg="white")
            self.opt_cb_target.config(state="disabled")
            self.opt_cb_method.config(state="disabled")
            self.opt_spin_start.config(state="disabled")
            self.opt_spin_end.config(state="disabled")
            self.opt_run_btn.config(state="disabled")
            
        # Redraw the structure to add/remove the green optimization column
        self.Main_layers()

    def run_optimization(self):
        try:
            target = self.opt_target.get()
            method = self.opt_method.get()
            l_start = self.opt_lam_start.get()
            l_end = self.opt_lam_end.get()

            print(f"Running {method} optimizing {target} from {l_start} to {l_end} nm...")
            
            self.calculate()
            self.update_plot()
            self.Main_layers()
            
            messagebox.showinfo("Optimization Complete", "Structure optimized successfully! Check the green values.")

        except Exception as e:
            messagebox.showerror("Optimizer Error", str(e))

# ===================== DATA AND PLOTTING LOGIC ====================
    def save_simulation_data(self):
        if self.sim_data is None:
            messagebox.showwarning("Warning", "No simulation data to save! Please click 'Calculate' first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("Text Files", "*.txt *.dat *.csv"), ("All Files", "*.*")],
            title="Save Simulation Data"
        )
        
        if not file_path: 
            return # User canceled
            
        try:
            # Combine X and Y into a 2D array and save
            data_to_save = np.column_stack((self.sim_data[0], self.sim_data[1]))
            np.savetxt(file_path, data_to_save, delimiter='\t', header="Wavelength(nm)\tResponse", comments='')
            messagebox.showinfo("Success", f"Simulation saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

            
    def load_experimental_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt *.dat *.csv"), ("All Files", "*.*")])
        if not file_path: return
        try:                                                                                        
            data = np.loadtxt(file_path)                                    
            if data.ndim > 1 and data.shape[1] >= 2:                                
                self.exp_data = (data[:, 0], data[:, 1])                                  
                self.file_name = Path(file_path).stem                              
                self.update_plot()                                                           
                messagebox.showinfo("Success", "Data loaded.")         
            else:                                                                                       
                messagebox.showerror("Error", "File needs 2 columns.")                            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

    def update_plot(self, x_sim=None, y_sim=None):                                             
        if x_sim is not None and y_sim is not None:
            self.sim_data = (x_sim, y_sim)
        
        self.ax.clear()
        
        # EXPERIMENTAL DATA plotted with high zorder (10) to stay in front
        if self.exp_data is not None:
            self.ax.plot(self.exp_data[0], self.exp_data[1], 'r--', label=f"{self.file_name}", alpha=0.8, zorder=10)
        
        # SIMULATION DATA plotted with lower zorder (5) to stay behind
        if self.sim_data is not None:
            self.ax.plot(self.sim_data[0], self.sim_data[1], 'b-', label='Simulation', linewidth=2, zorder=5)
            
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Response")
        self.ax.grid(True, alpha=0.3, zorder=1)
        
        if self.exp_data or self.sim_data:
            self.ax.legend()
            
        self.canvas.draw_idle()

    # ================= MATH CALCULATION =================

    def get_n_array(self, material_name, wave_m):
        if "Air" in material_name:
            return np.ones_like(wave_m) * 1.0 + 0j
        else:
            try:
                data_n = np.loadtxt(f"Fresnel/Data/{material_name}_n.txt", delimiter="\t", skiprows=1)
                data_k = np.loadtxt(f"Fresnel/Data/{material_name}_k.txt", delimiter="\t", skiprows=1)
                f_n = interp1(data_n[:, 0], data_n[:, 1], kind='cubic', fill_value="extrapolate")
                f_k = interp1(data_k[:, 0], data_k[:, 1], kind='cubic', fill_value="extrapolate")
                return f_n(wave_m) - 1j * f_k(wave_m)
            except Exception as e:
                #print(f"Error loading {material_name}: {e}")
                return np.ones_like(wave_m) * 1.0 + 0j

    def calculate(self):
        try:
            theta = float(self.theta_inc.get()) * np.pi / 180
            
            if  self.opt_active.get() == True:
                lam_i = self.opt_lam_start.get()
                lam_f = self.opt_lam_end.get()
                
            else:
                lam_i = self.lambda_start.get()
                lam_f = self.lambda_end.get()

            wave = np.arange(lam_i, lam_f + 1, 1)

            index_refraction = []
            thicknesses = []
            bounds = []

            for layer in self.layers:
                n_array = self.get_n_array(layer["material"].get(), wave)
                index_refraction.append(n_array)

                if not layer["fixed"]:
                    # 1. Get values from UI
                    current_thick = float(layer["thickness"].get())
                    range_val = float(layer["bound_thickness"].get())
                    
                    # 2. Define the Search Window
                    low = max(0, current_thick - range_val) # Don't go below 0nm
                    high = current_thick + range_val
                    
                    thicknesses.append(current_thick)
                    bounds.append((low, high)) # Pack as a tuple for SciPy


            n_stack = np.vstack(index_refraction)
            thickness_arr = np.array(thicknesses)
            

            if self.opt_active.get() == True:
                
                initial_conditions = {
                'index_refr': n_stack,
                'thick_guess': thickness_arr,
                'theta': theta,
                'polar': self.polarization.get(),
                'bounds': bounds}

                range_optimization = [self.opt_lam_start.get(), self.opt_lam_end.get()]

                optmized = fe.FresnelOptimizer(  range_optimization, self.exp_data[0] , self.exp_data[1],  initial_conditions, target_function = self.opt_cb_target.get(), method_fit = self.opt_cb_method.get()    )
                best_param_fit, best_plot_fit = optmized.fit()

                opt_idx = 0
                for layer in self.layers:
                    if not layer["fixed"]:
                        # This automatically updates the green number on the screen!
                        layer["opt_thickness"].set(round(best_param_fit[opt_idx], 2))
                        opt_idx += 1

                self.update_plot(wave, best_plot_fit )
                
            else:
                Matrix_complex = cfm.ComplexFresnelMatrix(wave, n_stack, thickness_arr, theta, self.polarization.get())
                Matrix_complex.spectra()
                y = np.squeeze(Matrix_complex.spectrum) 
                self.update_plot(wave, y)
        except Exception as e:
            messagebox.showerror("Calc Error", str(e))

    def on_close(self):
        plt.close('all')
        self.destroy()
        import os
        os._exit(0)

# ================= RUN =================
if __name__ == "__main__":
    app = LayerStackApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()