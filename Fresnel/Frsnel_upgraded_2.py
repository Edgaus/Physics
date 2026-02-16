import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import fresnelmtx 
import matlab

# Inicializamos Fresnel
fres = fresnelmtx.initialize()

MATERIALS = ["Air", "AlSb" ,  "Al49Ga51As","AlN (cubico)", "AlN Film" ,"AlN (hexagonal)", "GaN (hexagonal)", "GaAs","GaN (cubico)","InGaN (cubico) 10% San_Luis", "MgO", "Si" ,"SiC" ,"SiO2", "TiN","Pet" ]

class LayerStackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Layer Stack - Simulation & Experiment")
        self.geometry("1400x800")

        # ================= MAIN LAYOUT =================
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=2, minsize=400)  
        main.columnconfigure(1, weight=1, minsize=800) 
        main.rowconfigure(0, weight=1)

        # ================= LEFT PANEL =================
        left = ttk.Frame(main, padding=30) 
        left.grid(row=0, column=0, sticky="ns") 
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        left_style = ttk.Style() 
        left_style.configure('Custom.TFrame', background='lightblue', borderwidth=5, relief='raised')

        self.container = ttk.Frame(left, relief='solid', style='Custom.TFrame', padding=20) 
        self.container.grid(row=0, column=0, sticky="nsew")

        # ================= RIGHT PANEL =================
        right = ttk.Frame(main, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(4, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # ================= DATA =================
        self.layers = []
        
        # Variables para almacenar datos en memoria
        self.sim_data = None  # (x, y) de la simulación
        self.exp_data = None  # (x, y) del archivo importado

        # Default top & bottom layers
        self.add_layer(material="Air", thickness=None, fixed=True) 
        self.add_layer(material="AlN (hexagonal)", thickness=100, fixed=False)
        self.add_layer(material="Si", thickness=None, fixed=True)
 
        self.lambda_start = tk.DoubleVar(value=400.0)
        self.lambda_end   = tk.DoubleVar(value=900.0)
        self.theta_inc    = tk.DoubleVar(value=0.0)

        # Wavelength area
        wave_frame = ttk.Frame(left) 
        wave_frame.grid(row=1, column=0, sticky="ew", pady=50)

        ttk.Spinbox(wave_frame, width=20, from_=200.0, to=2000.0, increment=1.0, 
                    text="Wavelength Start (nm)", textvariable=self.lambda_start).grid(row=1, column=0)
        ttk.Label(wave_frame, text="Initial Wvelength").grid(row=0, column=0) 
        ttk.Label(wave_frame, text="nm").grid(row=1, column=1, padx=10) 

        ttk.Spinbox(wave_frame, textvariable=self.lambda_end, width=20, from_=200.0, to=2000.0, 
                    increment=1.0).grid(row=1, column=2, padx=10)        
        ttk.Label(wave_frame, text="End Wvelength").grid(row=0, column=2) 
        ttk.Label(wave_frame, text="nm").grid(row=1, column=3, padx=10) 

        ttk.Spinbox(wave_frame, from_=0, to=90, width=5, textvariable=self.theta_inc).grid(row=2, column=1, padx=10)        
        ttk.Label(wave_frame, text="Angle of incidence").grid(row=2, column=0) 

        # Button Calculate area
        btn_frame = ttk.Frame(left) 
        btn_frame.grid(row=2, column=0, sticky="ew", pady=20)

        # Botón para importar datos experimentales
        ttk.Button(btn_frame, text="📂 Load Exp. Data", command=self.load_experimental_data).pack(side='left', padx=5)
        
        # ### NUEVO: Botón para GUARDAR la simulación
        ttk.Button(btn_frame, text="💾 Save Sim. Data", command=self.save_simulation_data).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Calculate", command=self.calculate).pack(side='right')

        self.redraw_layers()

    # ==================================================
    def add_layer(self, material="", thickness=0, fixed=False, index=None):
        layer = {
            "material": tk.StringVar(value=material),
            "thickness": tk.StringVar(value="" if thickness is None else str(thickness)),
            "fixed": fixed
        }
        if index is None: self.layers.append(layer)
        else: self.layers.insert(index, layer)

    # ==================================================
    def redraw_layers(self):
        for widget in self.container.winfo_children(): widget.destroy()

        for i, layer in enumerate(self.layers):
            is_last = (i == len(self.layers) - 1)
            floor_style = ttk.Style()  
            floor_style.configure('Cusatom.TFrame', background='white', borderwidth=5, relief='raised')
            row = ttk.Frame(self.container, padding=2, style='Cusatom.TFrame')
            row.grid(row=i, column=0, sticky="ew", pady=1, padx=10) 
            row.columnconfigure(1, weight=1)

            if not is_last:
                ttk.Button(row, text="Add", width=5, command=lambda i=i: self.insert_layer(i)).grid(row=0, column=0, padx=3)

            if not is_last:
                ttk.Combobox(row, values=MATERIALS, textvariable=layer["material"], width=20, state="readonly").grid(row=0, column=1, sticky="w")
            if is_last:  
                ttk.Combobox(row, values=MATERIALS, textvariable=layer["material"], width=20, state="readonly").grid(row=0, column=1, sticky="w", padx=45)

            if not layer["fixed"]:
                ttk.Spinbox(row, textvariable=layer["thickness"], width=8, from_=0.0, to=2000.0, increment=1.0).grid(row=0, column=2, padx=10)
                ttk.Label(row, text="nm").grid(row=0, column=3, padx=10) 
            else:
                ttk.Label(row, text="—").grid(row=0, column=2, padx=15)

            if not layer["fixed"]:
                ttk.Button(row, text="✖", width=2, command=lambda i=i: self.remove_layer(i)).grid(row=0, column=4, padx=10)

    # ==================================================
    def insert_layer(self, index):
        self.add_layer(material="AlN (hexagonal)", thickness=100, fixed=False, index=index + 1)  
        self.redraw_layers()

    # ==================================================
    def remove_layer(self, index):
        if self.layers[index]["fixed"]: return
        self.layers.pop(index)
        self.redraw_layers()

    # ==================================================
    def load_experimental_data(self):
        file_path = filedialog.askopenfilename(title="Select Experimental Data File", filetypes=[("Text Files", "*.txt *.dat *.csv"), ("All Files", "*.*")])
        if not file_path: return

        try:
            data = np.loadtxt(file_path)
            if data.ndim > 1 and data.shape[1] >= 2:
                x = data[:, 0]
                y = data[:, 1]
                self.exp_data = (x, y) 
                self.update_plot()     
                messagebox.showinfo("Success", "Experimental data loaded successfully.")
            else:
                messagebox.showerror("Error", "File must have at least two columns.")
        except Exception as e:
            try: # Fallback comma delimiter
                data = np.loadtxt(file_path, delimiter=",")
                self.exp_data = (data[:, 0], data[:, 1])
                self.update_plot()
            except:
                messagebox.showerror("Error", f"Could not read file.\nDetails: {e}")

    # ==================================================
    # ### NUEVO: Función para GUARDAR DATOS SIMULADOS
    def save_simulation_data(self):
        # 1. Verificar si hay datos simulados
        if self.sim_data is None:
            messagebox.showwarning("No Data", "Please calculate a simulation first before saving.")
            return

        # 2. Abrir cuadro de diálogo para guardar archivo
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Simulation Data"
        )

        if not filename:
            return # Usuario canceló

        try:
            # 3. Obtener datos y asegurar formato correcto
            x_sim, y_sim = self.sim_data
            
            # Si los datos son complejos, guardamos la parte real (o magnitud)
            if np.iscomplexobj(y_sim):
                y_sim = np.real(y_sim) 

            # Unir las columnas (X, Y)
            data_to_save = np.column_stack((x_sim, y_sim))

            # 4. Guardar usando NumPy
            header_text = "Wavelength(nm)  Reflectance"
            np.savetxt(filename, data_to_save, fmt='%.6f', header=header_text, comments='')
            
            messagebox.showinfo("Saved", f"File saved successfully:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error saving file:\n{e}")

    # ==================================================
    def update_plot(self, x_sim=None, y_sim=None):
        if x_sim is not None and y_sim is not None:
            self.sim_data = (x_sim, y_sim)

        self.ax.clear()

        if self.exp_data is not None:
            self.ax.plot(self.exp_data[0], self.exp_data[1], 'r--', label='Experimental', alpha=0.6)

        if self.sim_data is not None:
            self.ax.plot(self.sim_data[0], self.sim_data[1], 'b-', label='Simulation', linewidth=2)

        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Response")
        self.ax.grid(True)
        
        if self.exp_data is not None or self.sim_data is not None:
            self.ax.legend()

        self.canvas.draw_idle()

    # ==================================================
    def calculate(self):
        print("Starting MATLAB...")
        theta = self.theta_inc.get()
        lam_i = self.lambda_start.get()
        lam_f = self.lambda_end.get()
        materials = []
        thicknesses = []

        for layer in self.layers:
            materials.append(layer["material"].get())
            if layer["fixed"]: continue
            thicknesses.append(float(layer["thickness"].get()) * 1e-9)

        wave = matlab.double([lam_i, lam_f])
        thicknesses_mat = matlab.double(thicknesses)
        theta_rad = float(theta) * np.pi / 180

        # Llamada a librería
        Matrix_complex = fres.Fresnel_Vectorized(wave, materials, thicknesses_mat, theta_rad, 'm', nargout=1)
        y = np.squeeze(Matrix_complex)
        lambda_nm = np.arange(lam_i, lam_f + 1, 1)

        print('Done.')
        self.update_plot(lambda_nm, y)

    def on_close(self):
        try: self.eng.quit()
        except: pass
        plt.close('all')
        self.destroy()
        import os
        os._exit(0)

# ================= RUN =================
if __name__ == "__main__":
    app = LayerStackApp()
    app.mainloop()