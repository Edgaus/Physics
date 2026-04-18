import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.interpolate import interp1d as interp1
from scipy.signal import find_peaks
import json

# Import our custom Pure-Python Fresnel Engine
import fresnel_engine 

MATERIALS = ["Air", "AlSb" ,  "Al49Ga51As","AlN (cubico)", "AlN Film" ,"AlN (hexagonal)", "GaN (hexagonal)", "GaAs","GaN (cubico)","InGaN (cubico) 10% San_Luis", "MgO", "Si" ,"SiC" ,"SiO2", "TiN","Pet" ]

class LayerStackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Layer Stack - Simulation & Experiment")
        self.geometry("1920x1080") 

        # ================= AESTHETICS & FONTS =================
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        default_font = ('Segoe UI', 11)
        header_font = ('Segoe UI', 11, 'bold')
        
        style.configure('.', font=default_font)
        style.configure('TFrame', background='#F5F6F8')
        style.configure('TLabel', background='#F5F6F8')
        style.configure('TLabelframe', background='#F5F6F8')
        style.configure('TLabelframe.Label', font=header_font, background='#F5F6F8', foreground='#333333')
        
        style.configure('Stack.TFrame', background='#FFFFFF', borderwidth=1, relief='solid')
        style.configure('Stack.TLabel', background='#FFFFFF')
        style.configure('Stack.TCheckbutton', background='#FFFFFF')

# ================= MAIN LAYOUT =================
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        # COLUMN 0: LEFT PANEL (Controls)
        # weight=0 strictly forbids this column from stretching when maximized.
        # minsize=600 gives it just enough room for your buttons and text.
        main.columnconfigure(0, weight=0, minsize=600)  
        
        # COLUMN 1: RIGHT PANEL (Plot)
        # weight=1 tells this column to absorb ALL leftover screen space.
        # Note: No minsize here so it remains fully flexible.
        main.columnconfigure(1, weight=1) 
        
        main.rowconfigure(0, weight=1)

        # ================= LEFT PANEL =================
        left = ttk.Frame(main, padding=20) 
        # sticky="nsew" ensures the gray background neatly fills its fixed column
        left.grid(row=0, column=0, sticky="nsew") 
        left.columnconfigure(0, weight=1)

        # Session Header
        header_frame = ttk.Frame(left)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header_frame, text="Multi-Layer Structure", font=('Segoe UI', 18, 'bold')).pack(side='left')
        ttk.Button(header_frame, text="📂 Load Session", command=self.load_session).pack(side='right', padx=2)
        ttk.Button(header_frame, text="💾 Save Session", command=self.save_session).pack(side='right', padx=2)

        self.container = ttk.Frame(left, style='Stack.TFrame', padding=15) 
        self.container.grid(row=1, column=0, sticky="nsew")

        # ================= RIGHT PANEL (PLOT) =================
        right = ttk.Frame(main, padding=20)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        self.fig, self.ax1 = plt.subplots(figsize=(10, 10))
        self.ax2 = self.ax1.twinx() 
        self.fig.subplots_adjust(left=0.08, right=0.92, top=0.95, bottom=0.1)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        self.bind("<Left>", self.move_selection_left)
        self.bind("<Right>", self.move_selection_right)

        # ================= DATA STATE =================
        self.layers = []
        self.sim_data = None 
        self.exp_data = None 
        self.exp_data_name = None 
        self.peak_data = []      
        self.current_click = None 

        self.lambda_start = tk.DoubleVar(value=300.0)
        self.lambda_end   = tk.DoubleVar(value=1100.0)
        self.theta_inc    = tk.DoubleVar(value=15)
        self.polarization = tk.StringVar(value="Mixed") 

        # Initial Default Setup (Feature 1: Boundary vs Inner layers)
        self.add_layer(material="Air", is_boundary=True) 
        self.add_layer(material="AlN (hexagonal)", t_val=100, t_min=50, t_max=200, is_opt=True, is_boundary=False)
        self.add_layer(material="Si", is_boundary=True)
 
        # ================= CONTROLS UI =================
        controls_group = ttk.LabelFrame(left, text="Simulation Parameters", padding=10)
        controls_group.grid(row=2, column=0, sticky="ew", pady=20)

        ttk.Label(controls_group, text="Start λ (nm)").grid(row=0, column=0, padx=5, sticky='w') 
        ttk.Spinbox(controls_group, width=8, from_=200.0, to=2000.0, textvariable=self.lambda_start).grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Label(controls_group, text="End λ (nm)").grid(row=0, column=1, padx=5, sticky='w') 
        ttk.Spinbox(controls_group, width=8, from_=200.0, to=2000.0, textvariable=self.lambda_end).grid(row=1, column=1, padx=5)        

        ttk.Label(controls_group, text="Angle (°)").grid(row=0, column=2, padx=5, sticky='w') 
        ttk.Spinbox(controls_group, from_=0, to=90, width=6, textvariable=self.theta_inc).grid(row=1, column=2, padx=5)        

        ttk.Label(controls_group, text="Polarization").grid(row=0, column=3, padx=5, sticky='w')
        ttk.Combobox(controls_group, values=["Mixed", "S-Polarized", "P-Polarized"], 
                     textvariable=self.polarization, width=12, state="readonly").grid(row=1, column=3, padx=5)

        btn_frame = ttk.Frame(left) 
        btn_frame.grid(row=3, column=0, sticky="ew", pady=5)

        ttk.Button(btn_frame, text="📂 Load Exp Data", command=self.load_experimental_data).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="💾 Save Sim Data", command=self.save_simulation_data).pack(side='left', padx=5)
        
        style.configure('Action.TButton', font=('Segoe UI', 11, 'bold'), foreground='darkblue')
        ttk.Button(btn_frame, text="▶ Calculate & Fit", style='Action.TButton', command=self.calculate).pack(side='right', fill='x', expand=True, padx=(20,0))

        self.build_peak_panel(left)
        self.redraw_layers()
        self.focus_set()

    def build_peak_panel(self, parent):
        peak_frame = ttk.LabelFrame(parent, text="Interactive Peak Extraction", padding=10)
        peak_frame.grid(row=4, column=0, sticky="ew", pady=15)

        self.lbl_current_point = ttk.Label(peak_frame, text="Click plot & use Arrows to move star.", foreground="#0066CC", font=('Segoe UI', 10, 'italic'))
        self.lbl_current_point.grid(row=0, column=0, columnspan=5, pady=(0, 10))

        ttk.Button(peak_frame, text="+ Maxima", width=10, command=lambda: self.add_peak("Maxima")).grid(row=1, column=0, padx=2)
        ttk.Button(peak_frame, text="+ Minima", width=10, command=lambda: self.add_peak("Minima")).grid(row=1, column=1, padx=2)
        ttk.Button(peak_frame, text="✖ Remove", width=10, command=self.remove_peak).grid(row=1, column=2, padx=2)
        ttk.Button(peak_frame, text="🗑 Clear All", width=10, command=self.clear_all_peaks).grid(row=1, column=3, padx=2)
        
        # Feature 3: Auto-detect Peaks
        ttk.Button(peak_frame, text="⚡ Auto-Detect", width=12, command=self.auto_detect_peaks).grid(row=1, column=4, padx=2)

        cols = ("type", "x", "y")
        self.tree_peaks = ttk.Treeview(peak_frame, columns=cols, show="headings", height=5)
        self.tree_peaks.heading("type", text="Type")
        self.tree_peaks.heading("x", text="λ (nm)")
        self.tree_peaks.heading("y", text="Exp Value")
        self.tree_peaks.column("type", width=80, anchor="center")
        self.tree_peaks.column("x", width=120, anchor="center")
        self.tree_peaks.column("y", width=120, anchor="center")
        self.tree_peaks.grid(row=2, column=0, columnspan=5, pady=(15, 0), sticky="ew")
        
        ttk.Button(peak_frame, text="💾 Save Peak Analysis", command=self.save_peaks).grid(row=3, column=0, columnspan=5, pady=(5,0), sticky="ew")

    # ================= SESSION SAVING & LOADING (Feature 4) =================
    def save_session(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", title="Save Session")
        if not path: return

        session_data = {
            "params": {
                "lambda_start": self.lambda_start.get(),
                "lambda_end": self.lambda_end.get(),
                "theta_inc": self.theta_inc.get(),
                "polarization": self.polarization.get()
            },
            "layers": [],
            "peaks": self.peak_data
        }

        for layer in self.layers:
            session_data["layers"].append({
                "material": layer["material"].get(),
                "t_val": layer["t_val"].get(),
                "t_min": layer["t_min"].get(),
                "t_max": layer["t_max"].get(),
                "is_opt": layer["is_opt"].get(),
                "is_boundary": layer["is_boundary"]
            })

        try:
            with open(path, 'w') as f:
                json.dump(session_data, f, indent=4)
            messagebox.showinfo("Success", "Session saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {e}")

    def load_session(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Load Session")
        if not path: return

        try:
            with open(path, 'r') as f:
                session_data = json.load(f)

            # Load Params
            p = session_data.get("params", {})
            self.lambda_start.set(p.get("lambda_start", 200.0))
            self.lambda_end.set(p.get("lambda_end", 1000.0))
            self.theta_inc.set(p.get("theta_inc", 0.0))
            self.polarization.set(p.get("polarization", "Mixed"))

            # Load Layers
            self.layers.clear()
            for l_data in session_data.get("layers", []):
                self.add_layer(
                    material=l_data.get("material", "Air"),
                    t_val=l_data.get("t_val", 100.0),
                    t_min=l_data.get("t_min", 100.0),
                    t_max=l_data.get("t_max", 200.0),
                    is_opt=l_data.get("is_opt", False),
                    is_boundary=l_data.get("is_boundary", False)
                )

            # Load Peaks
            self.clear_all_peaks()
            for p_data in session_data.get("peaks", []):
                self.current_click = (p_data['x'], p_data['y'])
                self.add_peak(p_data['type'])
            self.current_click = None

            messagebox.showinfo("Success", "Session loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session: {e}")


    # ================= PEAK NAVIGATION & LOGIC =================
    def on_plot_click(self, event):
        self.focus_set()
        if self.exp_data is None: return
        if event.inaxes != self.ax1 and event.inaxes != self.ax2: return
        
        x_exp, y_exp = self.exp_data
        idx = np.argmin(np.abs(x_exp - event.xdata))
        self.current_click = (x_exp[idx], y_exp[idx])
        self.lbl_current_point.config(text=f"Selected Peak: λ = {self.current_click[0]:.1f} nm, Response = {self.current_click[1]:.4f}")
        self.update_plot()

    def move_selection_left(self, event=None): self._move_selection(-1)
    def move_selection_right(self, event=None): self._move_selection(1)

    def _move_selection(self, direction):
        if self.exp_data is None or self.current_click is None: return
        x_exp, y_exp = self.exp_data
        idx = np.argmin(np.abs(x_exp - self.current_click[0]))
        new_idx = np.clip(idx + direction, 0, len(x_exp)-1)
        self.current_click = (x_exp[new_idx], y_exp[new_idx])
        self.lbl_current_point.config(text=f"Selected Peak: λ = {self.current_click[0]:.1f} nm, Response = {self.current_click[1]:.4f}")
        self.update_plot()

    def add_peak(self, p_type):
        if not self.current_click: return
        x, y = self.current_click
        self.peak_data.append({'type': p_type, 'x': x, 'y': y, 'sim_y': 0.0})
        self.tree_peaks.insert("", tk.END, values=(p_type, f"{x:.1f}", f"{y:.4f}"))
        self.update_plot()

    def remove_peak(self):
        selected = self.tree_peaks.selection()
        if not selected: return
        for item in selected:
            vals = self.tree_peaks.item(item, 'values')
            self.peak_data = [p for p in self.peak_data if not (abs(p['x'] - float(vals[1])) < 0.1)]
            self.tree_peaks.delete(item)
        self.update_plot()

    # Feature 2: Clear All Peaks
# Feature 2: Clear All Peaks
    def clear_all_peaks(self, redraw=True):
        self.peak_data.clear()
        for item in self.tree_peaks.get_children():
            self.tree_peaks.delete(item)
        if redraw:
            self.update_plot()

    # Feature 3: Auto-Detect Peaks using Scipy Signal (Robust against noise)
    def auto_detect_peaks(self):
        if self.exp_data is None:
            messagebox.showwarning("No Data", "Please load experimental data first.")
            return

        # Pass redraw=False so the screen doesn't momentarily blank out
        self.clear_all_peaks(redraw=False)
        x, y = self.exp_data
        
        # Dynamically calculate a baseline prominence based on the signal amplitude
        # This prevents the algorithm from picking up tiny random noise fluctuations
        signal_range = np.max(y) - np.min(y)
        prominence_threshold = signal_range * 0.05 
        
        # Find Maxima
        max_idx, _ = find_peaks(y, distance=5, prominence=prominence_threshold)
        # Find Minima (by looking for peaks in the inverted signal)
        min_idx, _ = find_peaks(-y, distance=5, prominence=prominence_threshold)
        
        for idx in max_idx:
            self.peak_data.append({'type': 'Maxima', 'x': float(x[idx]), 'y': float(y[idx]), 'sim_y': 0.0})
            self.tree_peaks.insert("", tk.END, values=('Maxima', f"{x[idx]:.1f}", f"{y[idx]:.4f}"))
            
        for idx in min_idx:
            self.peak_data.append({'type': 'Minima', 'x': float(x[idx]), 'y': float(y[idx]), 'sim_y': 0.0})
            self.tree_peaks.insert("", tk.END, values=('Minima', f"{x[idx]:.1f}", f"{y[idx]:.4f}"))

        self.update_plot()
        
        # We update the label instead of using an annoying popup window that freezes the UI
        self.lbl_current_point.config(text=f"Auto-Detection Complete: Found {len(max_idx) + len(min_idx)} peaks.")

    # ================= PEAK NAVIGATION & LOGIC =================
    def on_plot_click(self, event):
        self.focus_set()
        if self.exp_data is None: return
        if event.inaxes != self.ax1 and event.inaxes != self.ax2: return
        
        # Safeguard: Matplotlib can occasionally fire 'None' if you click the exact edge of the border
        if event.xdata is None or event.ydata is None: return 
        
        x_exp, y_exp = self.exp_data
        idx = np.argmin(np.abs(x_exp - event.xdata))
        self.current_click = (x_exp[idx], y_exp[idx])
        self.lbl_current_point.config(text=f"Selected Peak: λ = {self.current_click[0]:.1f} nm, Response = {self.current_click[1]:.4f}")
        self.update_plot()
        
        for cp in valid_roots:
            val = float(spline(cp))
            d2_val = d2y_dx2(cp)
            
            # Second derivative test for concavity
            p_type = "Maxima" if d2_val < 0 else "Minima"
            
            self.peak_data.append({'type': p_type, 'x': float(cp), 'y': val, 'sim_y': 0.0})
            self.tree_peaks.insert("", tk.END, values=(p_type, f"{cp:.1f}", f"{val:.4f}"))

        self.update_plot()
        messagebox.showinfo("Detection Complete", f"Found {len(valid_roots)} peaks automatically.")

        self.clear_all_peaks()
        x, y = self.exp_data
        
        # Sort and fit spline
        idx = np.argsort(x)
        xs, ys = x[idx], y[idx]
        
        spline = interp1(xs, ys, kind='cubic', fill_value="extrapolate")

        # First and second derivatives
        dy_dx = spline.derivative()
        d2y_dx2 = spline.derivative(n=2)
        
        # Find roots of first derivative (critical points)
        roots = dy_dx.roots()
        
        # Filter roots to be within data range
        valid_roots = roots[(roots >= xs[0]) & (roots <= xs[-1])]
        
        for cp in valid_roots:
            val = float(spline(cp))
            d2_val = d2y_dx2(cp)
            
            p_type = "Maxima" if d2_val < 0 else "Minima"
            self.peak_data.append({'type': p_type, 'x': float(cp), 'y': val, 'sim_y': 0.0})
            self.tree_peaks.insert("", tk.END, values=(p_type, f"{cp:.1f}", f"{val:.4f}"))

        self.update_plot()
        messagebox.showinfo("Detection Complete", f"Found {len(valid_roots)} peaks automatically.")

    def save_peaks(self):
        if not self.peak_data: return
        path = filedialog.asksaveasfilename(defaultextension=".txt", title="Save Analysis")
        if path:
            with open(path, 'w') as f:
                f.write("Type\tλ(nm)\tExp_Val\tSim_Val\tDelta\n")
                for p in self.peak_data:
                    sim_v = p.get('sim_y', 0.0)
                    f.write(f"{p['type']}\t{p['x']:.2f}\t{p['y']:.4f}\t{sim_v:.4f}\t{p['y']-sim_v:.4f}\n")
            messagebox.showinfo("Saved", "Data exported.")

    # ================= MATERIALS LIBRARY =================
    def get_n_array(self, material_name, wave_m):
        if "Air" in material_name:
            return np.ones_like(wave_m) * 1.0 + 0j
        else:
            try:
                # Remove 'import pandas as pd' at the top of your file
                # In your get_n_array function, replace the pandas lines with:
                data_n = np.loadtxt(f"Fresnel/Data/{material_name}_n.txt", delimiter="\t", skiprows=1)
                data_k = np.loadtxt(f"Fresnel/Data/{material_name}_k.txt", delimiter="\t", skiprows=1)

                # Bug Fix: Interpolate functions separately, then evaluate, then combine
                f_n = interp1(data_n[:, 0], data_n[:, 1], kind='cubic', fill_value="extrapolate")
                f_k = interp1(data_k[:, 0], data_k[:, 1], kind='cubic', fill_value="extrapolate")

                n_vals = f_n(wave_m)
                k_vals = f_k(wave_m)
                return n_vals - 1j * k_vals
            
            except Exception as e:
                messagebox.showerror("Error", f"Could not load data for {material_name}.\n{str(e)}")
                return np.ones_like(wave_m) * 1.0 + 0j

    # ================= CORE CALCULATIONS =================
# ================= CORE CALCULATIONS =================
    def calculate(self):
        print("Running Python Fresnel Optimization and Simulation...")
        lam_i, lam_f = self.lambda_start.get(), self.lambda_end.get()
        
        wave = np.linspace(int(lam_i), int(lam_f), int(abs(lam_i - lam_f)) + 1)
        theta_rad = float(self.theta_inc.get()) * np.pi / 180

        polar_map = {"Mixed": "m", "S-Polarized": "s", "P-Polarized": "p"}
        engine_polarization = polar_map.get(self.polarization.get(), "m")

        n_stack_list = []
        full_internal_thicknesses = []
        bounds = []
        active_indices = [] 

        for idx, layer in enumerate(self.layers):
            mat_name = layer["material"].get()
            n_stack_list.append(self.get_n_array(mat_name, wave))
            
            # Feature 1: Only optimize if the checkbox is active
            if not layer["is_boundary"]:
                if layer["is_opt"].get():
                    min_nm = layer["t_min"].get()
                    max_nm = layer["t_max"].get()
                    bounds.append((min_nm, max_nm))
                    active_indices.append(idx - 1) # Engine expects inner layer index
                    full_internal_thicknesses.append(0.5 * (min_nm + max_nm))
                else:
                    # Append the fixed thickness directly
                    fixed_val = layer["t_val"].get()
                    full_internal_thicknesses.append(fixed_val) 
                    layer["t_opt"].set(f"Fixed: {fixed_val:.2f} nm")

        n_stack = np.vstack(n_stack_list)

        # Default values in case we are just simulating without optimizing
        # --- OPTIMIZATION PHASE ---
        if len(self.peak_data) > 0 and len(bounds) > 0:
            print("Optimizing based on selected extrema bounds...")
            
            # Append the bounds for Offset and Amplitude at the very end

            
            max_exp_x = np.array([p['x'] for p in self.peak_data if p['type'] == 'Maxima'])            
            min_exp_x = np.array([p['x'] for p in self.peak_data if p['type'] == 'Minima']) 
    

            opt_results = fresnel_engine.optimize_thickness_from_extrema(
                min_exp_x, max_exp_x,  wave, n_stack, bounds, 
                full_internal_thicknesses, active_indices, theta_rad, polarization=engine_polarization
            )
            
            if opt_results is not None:
                # Unpack the results: the last two are Offset and Amplitude
                opt_amplitude = opt_results[-1]
                opt_offset = opt_results[-2]
                opt_active_thicknesses = opt_results[:-2]
                
                print(f"Fitted Offset: {opt_offset:.4f} | Fitted Amplitude: {opt_amplitude:.4f}")

                for active_i, opt_t in zip(active_indices, opt_active_thicknesses):
                    full_internal_thicknesses[active_i] = opt_t
                    gui_layer_idx = active_i + 1
                    self.layers[gui_layer_idx]["t_opt"].set(f"Fit: {opt_t:.2f} nm")

        # --- FORWARD SIMULATION PHASE ---
        print("Calculating final reflectance curve...")
        
        # Pass the Offset and Amplitude to the final drawing phase, and unpack all 5 return variables
        R_sim, _, _, = fresnel_engine.complex_fresnel_matrix(
            wave, n_stack, full_internal_thicknesses, theta_rad, polar=engine_polarization        )

        self.update_plot(wave, R_sim)

    # ================= UI & UTILS =================
    def add_layer(self, material="", t_val=100.0, t_min=50.0, t_max=200.0, is_opt=True, is_boundary=False, index=None):
        layer = {
            "material": tk.StringVar(value=material), 
            "t_val": tk.DoubleVar(value=t_val),       # Used if fixed
            "t_min": tk.DoubleVar(value=t_min),       # Used if opt
            "t_max": tk.DoubleVar(value=t_max),       # Used if opt
            "is_opt": tk.BooleanVar(value=is_opt),    # Toggle state
            "t_opt": tk.StringVar(value="Fit: --"), 
            "is_boundary": is_boundary                # Top/Bottom flag
        }
        
        # Attach a trace to the checkbox so UI updates instantly when toggled
        layer["is_opt"].trace_add("write", lambda *args: self.redraw_layers())

        if index is None: self.layers.append(layer)
        else: self.layers.insert(index, layer)
        self.redraw_layers()

    def redraw_layers(self):
        for widget in self.container.winfo_children(): widget.destroy()
        
        ttk.Label(self.container, text="Material", style='Stack.TLabel', font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=35)
        ttk.Label(self.container, text="Result", style='Stack.TLabel', font=('Segoe UI', 10, 'bold')).grid(row=0, column=6, sticky="w")

        for i, layer in enumerate(self.layers):
            row = ttk.Frame(self.container, padding=4, style='Stack.TFrame')
            row.grid(row=i+1, column=0, sticky="ew", pady=2) 
            
            if not layer["is_boundary"]:
                ttk.Button(row, text="+", width=3, command=lambda idx=i: self.add_layer(index=idx+1)).grid(row=0, column=0, padx=5)
            
            ttk.Combobox(row, values=MATERIALS, textvariable=layer["material"], width=20, state="readonly").grid(row=0, column=1, sticky="w", padx=(0 if not layer["is_boundary"] else 43))

            if not layer["is_boundary"]:
                # Optimization Toggle Checkbox
                ttk.Checkbutton(row, text="Optimize", variable=layer["is_opt"], style='Stack.TCheckbutton').grid(row=0, column=2, padx=(5, 10))

                if layer["is_opt"].get():
                    # Show Min/Max boxes
                    ttk.Spinbox(row, textvariable=layer["t_min"], width=7, from_=0.0, to=5000.0).grid(row=0, column=3, padx=(2,2))
                    ttk.Label(row, text="to", style='Stack.TLabel').grid(row=0, column=4)
                    ttk.Spinbox(row, textvariable=layer["t_max"], width=7, from_=0.0, to=5000.0).grid(row=0, column=5, padx=(2,10))
                else:
                    # Show single Fixed Thickness box
                    ttk.Label(row, text="Fixed (nm):", style='Stack.TLabel').grid(row=0, column=3, padx=2)
                    ttk.Spinbox(row, textvariable=layer["t_val"], width=8, from_=0.0, to=5000.0).grid(row=0, column=4, columnspan=2, sticky='w', padx=2)
                
                ttk.Label(row, textvariable=layer["t_opt"], width=15, foreground="#28a745", style='Stack.TLabel', font=('Segoe UI', 11, 'bold')).grid(row=0, column=6, padx=5)
                ttk.Button(row, text="✖", width=3, command=lambda idx=i: self.remove_layer(idx)).grid(row=0, column=7, padx=5)
            else:
                if i == 0:
                    ttk.Label(row, text="(Incident Medium)", style='Stack.TLabel', foreground="gray").grid(row=0, column=2, columnspan=4, sticky="w", padx=10)
                else:
                    ttk.Label(row, text="(Substrate)", style='Stack.TLabel', foreground="gray").grid(row=0, column=2, columnspan=4, sticky="w", padx=10)

    def remove_layer(self, index):
        if not self.layers[index]["is_boundary"]:
            self.layers.pop(index)
            self.redraw_layers()

    def load_experimental_data(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                data = np.loadtxt(path)
                self.exp_data = (data[:, 0], data[:, 1])
                self.exp_data_name = path.split("/")[-1]
                self.update_plot()
            except: messagebox.showerror("Error", "Check file format (2 columns).")

    def save_simulation_data(self):
        if self.sim_data:
            path = filedialog.asksaveasfilename(defaultextension=".txt")
            if path: np.savetxt(path, np.column_stack(self.sim_data))

    def update_plot(self, x_sim=None, y_sim=None):
        if x_sim is not None: self.sim_data = (x_sim, y_sim)
        
        self.ax1.clear()
        self.ax2.clear()
        
        if self.exp_data: 
            self.ax2.plot(self.exp_data[0], self.exp_data[1], color='#e74c3c', linestyle='--', linewidth=1.5, label=f'{self.exp_data_name}', alpha=0.8)
        
        if self.current_click: 
            self.ax2.plot(self.current_click[0], self.current_click[1], '*', color='#f1c40f', ms=15, mec='black')
        
        max_pts = [p for p in self.peak_data if p['type'] == 'Maxima']
        min_pts = [p for p in self.peak_data if p['type'] == 'Minima']
        if max_pts: self.ax2.plot([p['x'] for p in max_pts], [p['y'] for p in max_pts], "kx", ms=8, label='Target Max')
        if min_pts: self.ax2.plot([p['x'] for p in min_pts], [p['y'] for p in min_pts], "go", mfc='none', ms=8, label='Target Min')

        if self.sim_data: 
            self.ax1.plot(self.sim_data[0], self.sim_data[1], color='#2980b9', linestyle='-', linewidth=2.5, label='Simulation')

        self.ax1.set_xlabel("Wavelength (nm)", fontsize=13, fontweight='bold')
        self.ax1.set_ylabel("Reflectance (Simulation)", color='#2980b9', fontsize=13, fontweight='bold')
        self.ax2.set_ylabel("Response (Experiment)", color='#e74c3c', fontsize=13, fontweight='bold')
        
        self.ax1.tick_params(axis='y', labelcolor='#2980b9')
        self.ax2.tick_params(axis='y', labelcolor='#e74c3c')
        self.ax1.tick_params(axis='x', labelsize=11)
        
        self.ax1.grid(True, linestyle=':', alpha=0.7)

        lines1, labels1 = self.ax1.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        if lines1 or lines2:
            self.ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=11)

        self.canvas.draw()
        self.update_idletasks()

if __name__ == "__main__":
    app = LayerStackApp()
    app.mainloop()