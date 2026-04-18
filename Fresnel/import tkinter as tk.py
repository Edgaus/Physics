import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from pathlib import Path

# ================= CUSTOM VECTOR BUTTONS =================
class CircularRemoveButton(tk.Canvas):
    """Draws the dark grey circle with the red X inside."""
    def __init__(self, master, command=None, size=24, **kwargs):
        super().__init__(master, width=size, height=size, bg="#121212", highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        pad = 2
        
        # Circle outline
        self.circle = self.create_oval(pad, pad, size-pad, size-pad, outline="#444", width=1.5)
        # Red X
        offset = 7
        self.create_line(offset, offset, size-offset, size-offset, fill="#e74c3c", width=2.5, capstyle="round")
        self.create_line(size-offset, offset, offset, size-offset, fill="#e74c3c", width=2.5, capstyle="round")
        
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)
        self.bind("<Enter>", lambda e: self.itemconfig(self.circle, outline="#777"))
        self.bind("<Leave>", lambda e: self.itemconfig(self.circle, outline="#444"))

class CircularAddButton(tk.Canvas):
    """Draws the bold green plus sign to insert layers."""
    def __init__(self, master, command=None, size=20, **kwargs):
        super().__init__(master, width=size, height=size, bg="#121212", highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        offset = 2
        
        # Green +
        self.create_line(size/2, offset, size/2, size-offset, fill="#2ecc71", width=3.5, capstyle="round")
        self.create_line(offset, size/2, size-offset, size/2, fill="#2ecc71", width=3.5, capstyle="round")
        
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)

# ================= MAIN APPLICATION =================
MATERIALS = ["Air", "AlSb", "AlN (hexagonal)", "GaAs", "Si", "SiO2", "TiN"]

class LayerStackApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Layer Stack - Simulation & Experiment")
        self.geometry("1400x900")
        self.configure(background="#121212")

        # Variables
        self.sim_data = None
        self.exp_data = None
        self.file_name = "None"
        self.layers = []
        
        self.setup_styles()
        self.setup_layout()

        # Default Layers
        self.add_layer(material="Air", thickness=None, fixed=True)
        self.add_layer(material="AlSb", thickness=23.0, fixed=False)
        self.add_layer(material="SiO2", thickness=241.0, fixed=False)
        self.add_layer(material="Si", thickness=4.0, fixed=False)
        self.add_layer(material="Si", thickness=None, fixed=True)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        BG, FG, ACCENT = "#121212", "white", "#3498db"

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        
        style.configure("BlueTitle.TLabelframe", background=BG, foreground=FG, bordercolor=ACCENT)
        style.configure("BlueTitle.TLabelframe.Label", foreground=ACCENT, font=("Segoe UI", 12, "bold"))
        style.configure("BlackTitle.TLabelframe", background=BG, foreground=FG)
        style.configure("BlackTitle.TLabelframe.Label", foreground=FG, font=("Segoe UI", 11, "bold"))

        style.configure("Treeview", background="#1e1e1e", foreground=FG, fieldbackground="#1e1e1e")
        style.configure("Treeview.Heading", background="#333", foreground=FG, font=("Segoe UI", 10, "bold"))
        style.configure("TSeparator", background="#333") # Dark grey lines between layers

    def setup_layout(self):
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main, padding=10)
        left.grid(row=0, column=0, sticky="ns")

        # --- 1. Multilayer Structure ---
        layer_box = ttk.LabelFrame(left, text="Multilayer Structure", style="BlueTitle.TLabelframe", padding=10)
        layer_box.grid(row=0, column=0, sticky="nsew", pady=5)

        self.layer_container = ttk.Frame(layer_box)
        self.layer_container.pack(fill="both", expand=True)
        # Configure columns for precise alignment
        self.layer_container.columnconfigure(1, minsize=150)

        # --- 2. Interactive Peak Extraction (Matched to your image) ---
        peak_box = ttk.LabelFrame(left, text="Interactive Peak Extraction", style="BlackTitle.TLabelframe", padding=10)
        peak_box.grid(row=1, column=0, sticky="ew", pady=15)

        ttk.Label(peak_box, text="Click plot & use Arrows to move star.", font=("Segoe UI", 10, "italic"), foreground="#3498db").pack(pady=(0, 10))
        
        # Top Button Toolbar
        btn_row = ttk.Frame(peak_box)
        btn_row.pack(fill="x", pady=(0, 5))
        ttk.Button(btn_row, text="+ Maxima").pack(side="left", padx=2)
        ttk.Button(btn_row, text="+ Minima").pack(side="left", padx=2)
        ttk.Button(btn_row, text="✖ Remove", command=self.remove_peak).pack(side="left", padx=2)
        ttk.Button(btn_row, text="🗑 Clear All", command=self.clear_peaks).pack(side="left", padx=2)
        ttk.Button(btn_row, text="⚡ Auto-Dete").pack(side="left", padx=2)

        # Treeview Table
        self.peak_tree = ttk.Treeview(peak_box, columns=("type", "wl", "val"), show="headings", height=5)
        self.peak_tree.heading("type", text="Type"); self.peak_tree.heading("wl", text="λ (nm)"); self.peak_tree.heading("val", text="Exp Value")
        self.peak_tree.column("type", width=100, anchor="center"); self.peak_tree.column("wl", width=120, anchor="center"); self.peak_tree.column("val", width=120, anchor="center")
        self.peak_tree.pack(fill="x", pady=5)

        # Bottom Save Button
        ttk.Button(peak_box, text="💾 Save Peak Analysis").pack(fill="x", pady=(5, 0))

        # --- 3. Base Actions ---
        calc_box = ttk.Frame(left)
        calc_box.grid(row=2, column=0, sticky="ew", pady=10)
        ttk.Button(calc_box, text="📂 Load Data", command=self.load_experimental_data).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(calc_box, text="▶ Calculate", command=self.calculate).pack(side="right", fill="x", expand=True, padx=2)

        # ================= RIGHT PANEL (Plot) =================
        right = ttk.Frame(main, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(6, 8), facecolor='#121212')
        self.ax.set_facecolor('#121212')
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= LAYER LOGIC (GRID ALIGNMENT) =================
    def add_layer(self, material="", thickness=0, fixed=False, index=None):
        layer = {"material": tk.StringVar(value=material), "thickness": tk.DoubleVar(value=0.0 if thickness is None else thickness), "fixed": fixed}
        if index is None: self.layers.append(layer)
        else: self.layers.insert(index, layer)
        self.redraw_layers()

    def remove_layer(self, index):
        if not self.layers[index]["fixed"]:
            self.layers.pop(index)
            self.redraw_layers()

    def redraw_layers(self):
        for widget in self.layer_container.winfo_children():
            widget.destroy()

        # Iterate and build the grid
        for i, layer in enumerate(self.layers):
            row_idx = i * 2  # Leaves a space (i*2 + 1) for the separator and plus button

            # 1. Red X Button (Left)
            if not layer["fixed"]:
                CircularRemoveButton(self.layer_container, command=lambda idx=i: self.remove_layer(idx)).grid(row=row_idx, column=0, padx=(5, 10))

            # 2. Material Combobox
            ttk.Combobox(self.layer_container, values=MATERIALS, textvariable=layer["material"], width=16, state="readonly" if not layer["fixed"] else "disabled").grid(row=row_idx, column=1, sticky="w", pady=5)

            # 3. Thickness Input
            if not layer["fixed"]:
                ttk.Spinbox(self.layer_container, textvariable=layer["thickness"], from_=0.0, to=2000.0, increment=1.0, width=8).grid(row=row_idx, column=2, padx=(5, 2), sticky="w")
                ttk.Label(self.layer_container, text="nm").grid(row=row_idx, column=3, sticky="w")
            else:
                ttk.Label(self.layer_container, text="— (Infinite)").grid(row=row_idx, column=2, columnspan=2, sticky="w", padx=5)

            # 4. Interstitial Separator & Green Plus Button
            if i < len(self.layers) - 1:
                sep_row = row_idx + 1
                # Dark grey horizontal line
                ttk.Separator(self.layer_container, orient="horizontal").grid(row=sep_row, column=1, columnspan=3, sticky="ew", pady=5)
                # Green plus overlapping the line, centered between combobox and spinbox
                add_btn = CircularAddButton(self.layer_container, command=lambda idx=i+1: self.add_layer("AlN (hexagonal)", 100, False, idx))
                add_btn.grid(row=sep_row, column=1, columnspan=2, pady=2) # Spans across columns 1 and 2 to center it

    # ================= MOCK LOGIC =================
    def load_experimental_data(self): pass
    def remove_peak(self): pass
    def clear_peaks(self): pass
    def calculate(self): pass

if __name__ == "__main__":
    app = LayerStackApp()
    app.mainloop()