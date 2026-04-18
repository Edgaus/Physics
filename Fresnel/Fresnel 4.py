import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.interpolate import interp1d as interp1 
from pathlib import Path
import json 
import ComplexFresnelMatrix as cfm 
import fresnel_engine as fe

# --- Constants ---
MATERIALS = ["Air", "AlSb" ,  "Al49Ga51As","AlN (cubico)", "AlN Film" ,"AlN (hexagonal)", "GaN (hexagonal)", "GaAs","GaN (cubico)","InGaN (cubico) 10% San_Luis", "MgO", "Si" ,"SiC" ,"SiO2", "TiN","Pet" ]

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
        

        try:
            self.state('zoomed')
        except:
            self.attributes("-zoomed", True)

        self.configure(background="#121212")
        
        # Data State
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
        self.opt_active = tk.BooleanVar(value=False)
        self.opt_target = tk.StringVar(value="hybrid")
        self.opt_method = tk.StringVar(value="differential_evolution") 
        self.opt_lam_start = tk.DoubleVar(value=350.0)
        self.opt_lam_end = tk.DoubleVar(value=1000.0)
        
        self.setup_styles()
        self.setup_layout()

        # Default Layers
        self.add_layer(material="Air", thickness=None, fixed=True) 
        self.add_layer(material="AlN (hexagonal)", thickness=100.0, fixed=False)
        self.add_layer(material="Si", thickness=None, fixed=True)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        BG, FG, BLUE, WIDGET_BG = "#121212", "white", "#0066CC", "#333333"

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=BLUE, font=('Segoe UI', 10, 'italic'))
        style.configure("SubTitle.TLabelframe", background=BG, foreground=FG, bordercolor="#555")
        style.configure("SubTitle.TLabelframe.Label", background=BG, foreground=FG, font=("Segoe UI", 13, "bold"))
        style.configure("TSeparator", background="#333")

        # Dark Mode Spinbox & Combobox Styling
        style.configure("TSpinbox", fieldbackground=WIDGET_BG, background=WIDGET_BG, foreground=FG, arrowcolor=FG, bordercolor="#222", lightcolor="#444", darkcolor="#222", insertcolor=FG)            
        style.map("TSpinbox", fieldbackground=[("disabled", BG)], foreground=[("disabled", "#555")], background=[("active", "#4a4a4a")]) 

        style.configure("TCombobox", fieldbackground=WIDGET_BG, background=WIDGET_BG, foreground=FG, arrowcolor=FG, bordercolor="#222", lightcolor="#444", darkcolor="#222")
        style.map("TCombobox", fieldbackground=[("readonly", WIDGET_BG), ("disabled", BG)], foreground=[("disabled", "#555")], background=[("active", "#4a4a4a")])

        self.option_add('*TCombobox*Listbox.background', WIDGET_BG)
        self.option_add('*TCombobox*Listbox.foreground', FG)
        self.option_add('*TCombobox*Listbox.selectBackground', BLUE)
        self.option_add('*TCombobox*Listbox.selectForeground', FG)

    def setup_layout(self):
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main, padding=10)
        left.grid(row=0, column=0, sticky="ns")

        # ================= ROW 0 =================
        layer_box = ttk.LabelFrame(left, text="Multilayer Structure", labelanchor='n', style="SubTitle.TLabelframe", padding=10)
        layer_box.grid(row=0, column=0, sticky="nsew", pady=15)
        
        self.layer_canvas = tk.Canvas(layer_box, bg="#121212", highlightthickness=0, height=300, width=420)
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

        # ================= ROW 1: Centered Conditions =================
        initial_conditions_frame = ttk.LabelFrame(left, text="Condiciones Iniciales", labelanchor='n', style="SubTitle.TLabelframe", padding=15)
        initial_conditions_frame.grid(row=1, column=0, sticky="ew", pady=10)
        initial_conditions_frame.columnconfigure(0, weight=1) 

        ic_inner = ttk.Frame(initial_conditions_frame)
        ic_inner.grid(row=0, column=0)

        ttk.Label(ic_inner, text="Start Wavelength (nm)").grid(row=0, column=0) 
        ttk.Spinbox(ic_inner, textvariable=self.lambda_start, width=15, from_=200.0, to=2000.0, increment=1.0).grid(row=1, column=0)

        ttk.Label(ic_inner, text="End Wavelength (nm)").grid(row=0, column=1, padx=(30, 0)) 
        ttk.Spinbox(ic_inner, textvariable=self.lambda_end, width=15, from_=200.0, to=2000.0, increment=1.0).grid(row=1, column=1, padx=(30, 0))        

        ttk.Label(ic_inner, text="Angle of incidence").grid(row=2, column=0, pady=(15, 0)) 
        ttk.Spinbox(ic_inner, from_=0, to=90, width=5, textvariable=self.theta_inc).grid(row=3, column=0, pady=5)

        ttk.Label(ic_inner, text="Polarization").grid(row=2, column=1, padx=(30, 0), pady=(15, 0))
        ttk.Combobox(ic_inner, values=["Mixed", "S-Polarized", "P-Polarized"], textvariable=self.polarization, width=12, state="readonly").grid(row=3, column=1, padx=(30, 0), pady=5)


        # ================= ROW 2: Centered Optimization Process =================
        self.opt_frame = ttk.LabelFrame(left, text="Optimization Process", labelanchor='n', style="SubTitle.TLabelframe", padding=15)
        self.opt_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.opt_frame.columnconfigure(0, weight=1)

        self.opt_toggle_btn = tk.Button(self.opt_frame, text="🔴 Optimization: OFF", bg="#333333", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.toggle_optimization)
        self.opt_toggle_btn.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        opt_inner = ttk.Frame(self.opt_frame)
        opt_inner.grid(row=1, column=0)

        ttk.Label(opt_inner, text="Target Function").grid(row=0, column=0)
        self.opt_cb_target = ttk.Combobox(opt_inner, values=["spectra", "absolute", "derivative", "hybrid", "extrema_x", "extrema_xy"], textvariable=self.opt_target, state="disabled", width=12)
        self.opt_cb_target.grid(row=1, column=0, pady=5)

        ttk.Label(opt_inner, text="Opt. Method").grid(row=0, column=1, padx=(30, 0))
        self.opt_cb_method = ttk.Combobox(opt_inner, values=["differential_evolution", "least_squares", "Nelder-Mead", "L-BFGS-B"], textvariable=self.opt_method, state="disabled", width=18)
        self.opt_cb_method.grid(row=1, column=1, padx=(30, 0), pady=5)

        ttk.Label(opt_inner, text="λ Start (nm)").grid(row=2, column=0, pady=(15, 0))
        self.opt_spin_start = ttk.Spinbox(opt_inner, textvariable=self.opt_lam_start, from_=200, to=2000, increment=1.0, width=14, state="disabled")
        self.opt_spin_start.grid(row=3, column=0, pady=5)

        ttk.Label(opt_inner, text="λ End (nm)").grid(row=2, column=1, padx=(30, 0), pady=(15, 0))
        self.opt_spin_end = ttk.Spinbox(opt_inner, textvariable=self.opt_lam_end, from_=200, to=2000, increment=1.0, width=20, state="disabled")
        self.opt_spin_end.grid(row=3, column=1, padx=(30, 0), pady=5)

        # ================= ROW 3: Action Buttons =================
        action_box = ttk.Frame(left)
        action_box.grid(row=3, column=0, sticky="ew", pady=10) 
        
        action_box.columnconfigure(0, weight=1)
        action_box.columnconfigure(1, weight=1)

        ttk.Button(action_box, text="📂 Load Exp Data", command=self.load_experimental_data).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(action_box, text="💾 Save Sim Data", command=self.save_simulation_data).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        
        ttk.Button(action_box, text="⚙️ Load State", command=self.load_state).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(action_box, text="⚙️ Save State", command=self.save_state).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        
        calc_btn = tk.Button(action_box, text="▶ CALCULATE / OPTIMIZE", bg="#0066CC", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2", command=self.calculate)
        calc_btn.grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=(10, 2), ipady=5)

            # --- NUEVO: Efecto Hover (Brillo) para el botón ---
        calc_btn.bind("<Enter>", lambda e: calc_btn.config(bg="#1A85FF")) # Azul más claro al pasar el cursor
        calc_btn.bind("<Leave>", lambda e: calc_btn.config(bg="#0066CC")) # Vuelve al color original

        # ================= RIGHT PANEL =================
        right = ttk.Frame(main, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        
        # --- Etiqueta discreta para las coordenadas ---
        self.coord_label = tk.Label(right, text="λ: -- nm   |   Respuesta: --", bg="#121212", fg="#888888", font=("Segoe UI", 10, "bold"))
        self.coord_label.pack(side="top", anchor="ne", pady=(0, 5))
        
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(6, 8), facecolor='#121212') 
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Conectar el movimiento del mouse con la gráfica
        self.canvas.mpl_connect("motion_notify_event", self.on_plot_hover)

    # ================= EVENTOS DEL MOUSE =================
    def on_plot_hover(self, event):
        if event.inaxes == self.ax:
            x_val = event.xdata
            y_val = event.ydata
            self.coord_label.config(text=f"λ: {x_val:.1f} nm   |   Respuesta: {y_val:.2f}")
        else:
            self.coord_label.config(text="λ: -- nm   |   Respuesta: --")

    # ================= SCROLL AND LAYER LOGIC =================


    # ================= SCROLL AND LAYER LOGIC =================
    def _bound_to_mousewheel(self, event): self.layer_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event): self.layer_canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event): self.layer_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def add_layer(self, material="", thickness=0, fixed=False, index=None):
        layer = {
            "material": tk.StringVar(value=material), 
            "thickness": tk.DoubleVar(value=0.0 if thickness is None else thickness), 
            "opt_thickness": tk.DoubleVar(value=0.0 if thickness is None else thickness), 
            "bound_thickness": tk.DoubleVar(value=100.0), 
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
        for w in self.scrollable_frame.winfo_children(): 
            w.destroy()
            
        is_opt_on = self.opt_active.get() 
        
        for i, layer in enumerate(self.layers):
            # Reverted back to standard spacing
            row_idx = i * 2 
            
            if not layer["fixed"]:
                CircularRemoveButton(self.scrollable_frame, command=lambda idx=i: self.remove_layer(idx)).grid(row=row_idx, column=0, padx=5)
            
            cb = ttk.Combobox(self.scrollable_frame, values=MATERIALS, textvariable=layer["material"], width=20, state="readonly")
            cb.grid(row=row_idx, column=1, sticky="w", pady=8)
            
            if not layer["fixed"]:
                ttk.Spinbox(self.scrollable_frame, textvariable=layer["thickness"], from_=0, to=5000, width=8).grid(row=row_idx, column=2, padx=5)
                ttk.Label(self.scrollable_frame, text="nm").grid(row=row_idx, column=3)
                
                if is_opt_on:
                    ttk.Label(self.scrollable_frame, textvariable=layer["opt_thickness"], foreground="#2ecc71", font=("Segoe UI", 10, "bold")).grid(row=row_idx, column=4, padx=(10, 5))
                    ttk.Spinbox(self.scrollable_frame, textvariable=layer["bound_thickness"], width=5, from_=0, to=500.0, increment=1.0, foreground="#2ecc71", font=("Segoe UI", 10, "bold")).grid(row=row_idx, column=5, padx=(10, 5))        
            else:
                ttk.Label(self.scrollable_frame, text="— (Infinite)").grid(row=row_idx, column=2, columnspan=2, padx=5, sticky="w")
                if is_opt_on:
                    # --- THE FIX: Put the titles here ONLY if it's the very first layer (i == 0) ---
                    if i == 0: 
                        ttk.Label(self.scrollable_frame, text="Espesor\nÓptimo", foreground="#0066CC", font=("Segoe UI", 9, "bold"), justify="center").grid(row=row_idx, column=4, padx=(10, 5))
                        ttk.Label(self.scrollable_frame, text="Límite\nEspesor", foreground="#0066CC", font=("Segoe UI", 9, "bold"), justify="center").grid(row=row_idx, column=5, padx=(10, 5))
                    else:
                        # For any other infinite layers (like Si at the bottom), just draw the gray dashes
                        ttk.Label(self.scrollable_frame, text="—", foreground="#777").grid(row=row_idx, column=4, padx=(10, 5))
                        ttk.Label(self.scrollable_frame, text="—", foreground="#777").grid(row=row_idx, column=5, padx=(10, 5))

            if i < len(self.layers) - 1:
                sep_row = row_idx + 1
                span = 5 if is_opt_on else 3 
                ttk.Separator(self.scrollable_frame, orient="horizontal").grid(row=sep_row, column=1, columnspan=span, sticky="ew", pady=2)
                CircularAddButton(self.scrollable_frame, command=lambda idx=i+1: self.add_layer("AlN Film", 100, False, idx)).grid(row=sep_row, column=1, columnspan=span)

    # ==================== OPTIMIZATION LOGIC ==================
    def sync_opt_ui(self):
        if self.opt_active.get():
            self.opt_toggle_btn.config(text="🟢 Optimization: ON", bg="#2ecc71", fg="#121212")
            for w in [self.opt_cb_target, self.opt_cb_method, self.opt_spin_start, self.opt_spin_end]:
                w.config(state=("readonly" if isinstance(w, ttk.Combobox) else "normal"))
        else:
            self.opt_toggle_btn.config(text="🔴 Optimization: OFF", bg="#333333", fg="white")
            for w in [self.opt_cb_target, self.opt_cb_method, self.opt_spin_start, self.opt_spin_end]:
                w.config(state="disabled")
        self.Main_layers()

    def toggle_optimization(self):
        self.opt_active.set(not self.opt_active.get())
        self.sync_opt_ui()

    # ===================== DATA & STATE LOGIC ====================
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

    def save_simulation_data(self):
        if self.sim_data is None:
            messagebox.showwarning("Warning", "No simulation data to save! Calculate first.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt *.dat *.csv")], title="Save Simulation")
        if not file_path: return 
        try:
            # --- NEW: Build the Metadata Header with thicknesses and optimized results ---
            header_text = "Fresnel Simulation Metadata\n"
            header_text += "---------------------------\n"
            
            for i, layer in enumerate(self.layers):
                mat = layer["material"].get()
                if layer["fixed"]:
                    header_text += f"Layer {i}: {mat} (Espesor Infinito)\n"
                else:
                    guess = layer["thickness"].get()
                    opt = layer["opt_thickness"].get()
                    header_text += f"Layer {i}: {mat} | Input: {guess:.2f} nm | Optimized: {opt:.2f} nm\n"
            
            header_text += "\nWavelength(nm)\tResponse"

            # Combine data and save with the header
            data_to_save = np.column_stack((self.sim_data[0], self.sim_data[1]))
            
            # np.savetxt automatically puts a '#' in front of the header lines!
            np.savetxt(file_path, data_to_save, delimiter='\t', header=header_text)
            
            messagebox.showinfo("Success", f"Saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_state(self):
        state = {
            "sim_vars": {
                "lambda_start": self.lambda_start.get(),
                "lambda_end": self.lambda_end.get(),
                "theta_inc": self.theta_inc.get(),
                "polarization": self.polarization.get()
            },
            "opt_vars": {
                "opt_active": self.opt_active.get(),
                "opt_target": self.opt_target.get(),
                "opt_method": self.opt_method.get(),
                "opt_lam_start": self.opt_lam_start.get(),
                "opt_lam_end": self.opt_lam_end.get()
            },
            "layers": [
                {
                    "material": l["material"].get(),
                    "thickness": l["thickness"].get(),
                    "bound_thickness": l["bound_thickness"].get(),
                    "fixed": l["fixed"]
                } for l in self.layers
            ],
            "exp_data": None
        }
        
        if self.exp_data is not None:
            state["exp_data"] = {
                "x": self.exp_data[0].tolist(),
                "y": self.exp_data[1].tolist(),
                "file_name": self.file_name
            }

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Config", "*.json")], title="Save State")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(state, f, indent=4)
                messagebox.showinfo("Success", "State configuration saved!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save state: {str(e)}")

    def load_state(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Config", "*.json")], title="Load State")
        if not file_path: return
        
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)

            self.lambda_start.set(state["sim_vars"]["lambda_start"])
            self.lambda_end.set(state["sim_vars"]["lambda_end"])
            self.theta_inc.set(state["sim_vars"]["theta_inc"])
            self.polarization.set(state["sim_vars"]["polarization"])

            self.opt_active.set(state["opt_vars"]["opt_active"])
            self.opt_target.set(state["opt_vars"]["opt_target"])
            self.opt_method.set(state["opt_vars"]["opt_method"])
            self.opt_lam_start.set(state["opt_vars"]["opt_lam_start"])
            self.opt_lam_end.set(state["opt_vars"]["opt_lam_end"])
            self.sync_opt_ui()

            self.layers.clear()
            for l in state["layers"]:
                layer = {
                    "material": tk.StringVar(value=l["material"]), 
                    "thickness": tk.DoubleVar(value=l["thickness"]), 
                    "opt_thickness": tk.DoubleVar(value=l["thickness"]), 
                    "bound_thickness": tk.DoubleVar(value=l["bound_thickness"]),
                    "fixed": l["fixed"]
                }
                self.layers.append(layer)
            self.Main_layers()

            if state.get("exp_data"):
                self.exp_data = (np.array(state["exp_data"]["x"]), np.array(state["exp_data"]["y"]))
                self.file_name = state["exp_data"]["file_name"]
            else:
                self.exp_data = None
                self.file_name = None

            self.sim_data = None
            self.update_plot()
            messagebox.showinfo("Success", "State configuration loaded successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load state: {str(e)}")

    def update_plot(self, x_sim=None, y_sim=None):                                             
        if x_sim is not None and y_sim is not None:
            self.sim_data = (x_sim, y_sim)
        self.ax.clear()
        
        if self.exp_data is not None:
            self.ax.plot(self.exp_data[0], self.exp_data[1], 'r--', label=f"{self.file_name}", alpha=0.8, zorder=10)
        if self.sim_data is not None:
            self.ax.plot(self.sim_data[0], self.sim_data[1], 'b-', label='Simulation', linewidth=2, zorder=5)
            
        # ================= NUEVO: ETIQUETAS MEJORADAS =================
        self.ax.set_xlabel("Longitud de onda (nm)", 
                           fontsize=20, 
                           fontweight='bold', 
                           fontfamily='Segoe UI', 
                           labelpad=10) # <-- Pushes text down
                           
        self.ax.set_ylabel("Reflectancia (%)", 
                           fontsize=20, 
                           fontweight='bold', 
                           fontfamily='Segoe UI', 
                           labelpad=15) # <-- Pushes text left
        # ==============================================================

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
            except:
                return np.ones_like(wave_m) * 1.0 + 0j

    def calculate(self):
        try:
            # Degrees to Radians!
            theta_radians = float(self.theta_inc.get()) * np.pi / 180.0
            
            if self.opt_active.get() == True:
                lam_i, lam_f = self.opt_lam_start.get(), self.opt_lam_end.get()
            else:
                lam_i, lam_f = self.lambda_start.get(), self.lambda_end.get()

            wave = np.arange(lam_i, lam_f + 1, 1)
            index_refraction, thicknesses, bounds = [], [], []

            for layer in self.layers:
                n_array = self.get_n_array(layer["material"].get(), wave)
                index_refraction.append(n_array)

                if not layer["fixed"]:
                    current_thick = float(layer["thickness"].get())
                    range_val = float(layer["bound_thickness"].get())
                    
                    low = max(0, current_thick - range_val) 
                    high = current_thick + range_val
                    
                    thicknesses.append(current_thick)
                    bounds.append((low, high)) 

            n_stack = np.vstack(index_refraction)
            thickness_arr = np.array(thicknesses)
            
            if self.opt_active.get() == True:
                if self.exp_data is None:
                    messagebox.showwarning("Warning", "Please load experimental data to optimize.")
                    return

                initial_conditions = {
                    'index_refr': n_stack,
                    'thick_guess': thickness_arr,
                    'theta': theta_radians, 
                    'polar': self.polarization.get(),
                    'bounds': bounds
                }
                
                opt_range = [lam_i, lam_f]
                
                # Run the Optimizer
                optmized = fe.FresnelOptimizer(opt_range, self.exp_data[0], self.exp_data[1], initial_conditions, target_function=self.opt_target.get(), method_fit=self.opt_method.get())
                best_param_fit, best_plot_fit = optmized.fit()

                # Update the Tkinter UI directly
                opt_idx = 0
                for layer in self.layers:
                    if not layer["fixed"]:
                        layer["opt_thickness"].set(round(best_param_fit[opt_idx], 2))
                        opt_idx += 1

                self.update_plot(wave, best_plot_fit)
                messagebox.showinfo("Success", "Optimization complete!")
                
            else:
                Matrix_complex = cfm.ComplexFresnelMatrix(wave, n_stack, thickness_arr, theta_radians, self.polarization.get())
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

if __name__ == "__main__":
    app = LayerStackApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()