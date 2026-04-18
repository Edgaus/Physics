import tkinter as tk
from tkinter import ttk
from turtle import left
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import fresnelmtx 
import matlab

#Any problems with the fresnelmtx package, initialize it here with cmd: pip install .


fres = fresnelmtx.initialize()




MATERIALS = ["Air", "AlN (cubico)", "AlN (hexagonal)", "GaN (hexagonal)", "GaAs","GaN (cubico)","InGaN (cubico) 10_ San Luis", "MgO", "Si", "SiC" ,"SiO2"]



class LayerStackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Layer Stack")
        self.geometry("1400x800")

        # ================= MAIN LAYOUT =================
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=2, minsize=400)  # LEFT (bigger)
        main.columnconfigure(1, weight=1, minsize=800)  # RIGHT
        main.rowconfigure(0, weight=1)





        # ================= LEFT PANEL =================
        left = ttk.Frame(main, padding=30)  # Separacion del lado derecho

        left.grid(row=0, column=0, sticky="ns")  # The behaviur of the left panel with expanding the window

        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        left_style = ttk.Style()  # Create a style to be used in the left pannel
        left_style.configure('Custom.TFrame', background='lightblue', borderwidth=5, relief='raised')

        self.container = ttk.Frame(left, relief='solid', style='Custom.TFrame', padding=20)   # Modify the container left, like border. Padding gives a margain to the whole floors respect to the container of the left pannel
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

        # Default top & bottom layers
        self.add_layer(material="Air", thickness=None, fixed=True) 
        self.add_layer(material="AlN (hexagonal)", thickness=100, fixed=False)
        self.add_layer(material="Si", thickness=None, fixed=True)
 
        self.lambda_start = tk.DoubleVar(value=400.0)
        self.lambda_end   = tk.DoubleVar(value=900.0)
        self.theta_inc    = tk.DoubleVar(value=0.0)

        # Wavelength area


        wave_frame = ttk.Frame(left) # Modify the style of the area with the wavelength ini and end, also initial angle
        wave_frame.grid(row=1, column=0, sticky="ew", pady=50)

        ttk.Spinbox(
                    wave_frame,
                    width=20,
                    from_=200.0,
                    to=2000.0,
                    increment=1.0,
                    text="Wavelength Start (nm)",
                    textvariable=self.lambda_start,
                ).grid(row=1, column=0)

        ttk.Label(wave_frame, text="Initial Wvelength").grid(row=0, column=0) #separation of the nm and the
        ttk.Label(wave_frame, text="nm").grid(row=1, column=1, padx=10) #separation of the nm and the

        ttk.Spinbox(
                    wave_frame,
                    textvariable=self.lambda_end,
                    width=20,
                    from_=200.0,
                    to=2000.0,
                    increment=1.0,
                ).grid(row=1, column=2, padx=10)        

        ttk.Label(wave_frame, text="End Wvelength").grid(row=0, column=2) #separation of the nm and the
        ttk.Label(wave_frame, text="nm").grid(row=1, column=3, padx=10) # End wavelength nm

        ttk.Spinbox(wave_frame, from_=0, to=90, width=5, textvariable=self.theta_inc,).grid(row=2, column=1, padx=10)        
        ttk.Label(wave_frame, text="Angle of incidence").grid(row=2, column=0) # Angle of incidence label

        # Button Calculate area


        btn_frame = ttk.Frame(left) # Modify the style of the button with the style defined previously
        btn_frame.grid(row=2, column=0, sticky="ew", pady=20)

        ttk.Button(btn_frame, text="Calculate", command=self.calculate).pack(side='right')








        self.redraw_layers()

    # ==================================================
    def add_layer(self, material="", thickness=0, fixed=False, index=None):
        layer = {
            "material": tk.StringVar(value=material),
            "thickness": tk.StringVar(value="" if thickness is None else str(thickness)),
            "fixed": fixed
        }

        if index is None:
            self.layers.append(layer)
        else:
            self.layers.insert(index, layer)

    # ==================================================
    def redraw_layers(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        for i, layer in enumerate(self.layers):
   
            is_last  = (i == len(self.layers) - 1)

            floor_style = ttk.Style()  # Style of the floors
            floor_style.configure('Cusatom.TFrame', background='white', borderwidth=5, relief='raised')

            row = ttk.Frame(self.container, padding=2,style='Cusatom.TFrame' )
            row.grid(row=i, column=0, sticky="ew", pady=1, padx=10) # The separation between thr floors
            row.columnconfigure(1, weight=1)

            

            # + button (right side)
            if not is_last:
                ttk.Button(
                row,
                text="Add",
                width=5,
                command=lambda i=i: self.insert_layer(i)
                ).grid(row=0, column=0, padx=3)

            # Material dropdown
            if not is_last:
                ttk.Combobox(
                row,
                values=MATERIALS,
                textvariable=layer["material"],
                width=20,
                state="readonly"
            ).grid(row=0, column=1, sticky="w")

            if is_last:  #Customsize the list of materials layer for the last floor, gives a space to compansate the not add button in the last floor
                ttk.Combobox(
                row,
                values=MATERIALS,
                textvariable=layer["material"],
                width=20,
                state="readonly"
            ).grid(row=0, column=1, sticky="w", padx=45)

            # Thickness entry (only for non-fixed layers)
            if not layer["fixed"]:
                ttk.Spinbox(
                    row,
                    textvariable=layer["thickness"],
                    width=8,
                    from_=0.0,
                    to=2000.0,
                    increment=1.0,
                ).grid(row=0, column=2, padx=10)
                ttk.Label(row, text="nm").grid(row=0, column=3, padx=10) #separation of the nm and the 
            else:
                ttk.Label(row, text="—").grid(row=0, column=2, padx=15)

            # ❌ remove button (disabled for first & last)
            if not layer["fixed"]:
                ttk.Button(
                    row,
                    text="✖",
                    width=2,
                    command=lambda i=i: self.remove_layer(i)
                ).grid(row=0, column=4, padx=10)


    # ==================================================
    def insert_layer(self, index):
        self.add_layer(material="AlN (hexagonal)", thickness=100, fixed=False, index=index + 1)  # Modifies the text of the material layer 
        self.redraw_layers()

    # ==================================================
    def remove_layer(self, index):
        if self.layers[index]["fixed"]:
            return
        self.layers.pop(index)
        self.redraw_layers()

    def update_plot(self, x, y):
        self.ax.clear()                      # Clear old data
        self.ax.plot(x, y)
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Response")
        self.ax.grid(True)

        self.canvas.draw_idle()              # Refresh canvas



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
            if layer["fixed"]:
                continue
            thicknesses.append(float(layer["thickness"].get()) * 1e-9)


     
        print("Angle:", theta)

        print("Materials:", materials)
        print("Thicknesses:", thicknesses)

        wave = matlab.double( [lam_i,lam_f] )
        thicknesses = matlab.double(thicknesses)
        theta = float(theta) * np.pi / 180

        Matrix_complex = fres.Fresnel_Vectorized( wave, materials, thicknesses , theta ,'m'     ,nargout=1)
        y = np.squeeze(Matrix_complex)
        lambda_nm = np.arange( lam_i, lam_f+1, 1)
  

        self.update_plot(lambda_nm, y)


    def on_close(self):
        try:
            self.eng.quit()
        except:
            pass
        plt.close('all')
        self.destroy()
        import os
        os._exit(0)


# ================= RUN =================
if __name__ == "__main__":
    app = LayerStackApp()
    app.mainloop()
