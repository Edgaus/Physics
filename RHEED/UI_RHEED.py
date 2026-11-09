# UI for the kinematic RHEED phosphor screen.
# Physics:
#   Visulation.compute_spots()   → ideal points (thin rods)
#   Visulation_streaks.compute_streaks() → vertical lines (finite rod width)

import tkinter as tk
from tkinter import ttk

import numpy as np

from Visulation import compute_spots
from Visulation_streaks import compute_streaks


class RheedScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RHEED — pantalla cinemática")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg="#1b1b1b")

        self._spots = []
        self._streaks = []
        self._hit_map = []

        self.var_a = tk.DoubleVar(value=3.61)
        self.var_kV = tk.DoubleVar(value=10.0)
        self.var_theta = tk.DoubleVar(value=2.5)
        self.var_phi = tk.DoubleVar(value=45.0)
        self.var_L = tk.DoubleVar(value=30.0)
        self.var_hmax = tk.IntVar(value=10)
        self.var_D = tk.DoubleVar(value=80.0)  # domain/terrace size (Å)
        self.var_mode = tk.StringVar(value="streaks")  # "spots" | "streaks"
        self.status = tk.StringVar(value="")

        self._build()
        self.recompute()

    def _build(self):
        side = tk.Frame(self, bg="#242424", width=280)
        side.pack(side=tk.LEFT, fill=tk.Y)
        side.pack_propagate(False)

        tk.Label(
            side,
            text="Parámetros",
            bg="#242424",
            fg="#e8e8e8",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=16, pady=(18, 8))

        mode = tk.Frame(side, bg="#242424")
        mode.pack(fill=tk.X, padx=16, pady=(0, 8))
        tk.Label(mode, text="Patrón", bg="#242424", fg="#d0d0d0", font=("Segoe UI", 9)).pack(
            anchor="w"
        )
        tk.Radiobutton(
            mode,
            text="Puntos (rods ideales)",
            variable=self.var_mode,
            value="spots",
            command=self.recompute,
            bg="#242424",
            fg="#d0d0d0",
            selectcolor="#3a3a3a",
            activebackground="#242424",
            activeforeground="#d0d0d0",
        ).pack(anchor="w")
        tk.Radiobutton(
            mode,
            text="Líneas verticales (streaks)",
            variable=self.var_mode,
            value="streaks",
            command=self.recompute,
            bg="#242424",
            fg="#d0d0d0",
            selectcolor="#3a3a3a",
            activebackground="#242424",
            activeforeground="#d0d0d0",
        ).pack(anchor="w")

        self._slider(side, "a (Å)", self.var_a, 3.2, 5.0, 0.01)
        self._slider(side, "Energía (kV)", self.var_kV, 5.0, 20.0, 0.1)
        self._slider(side, "θ incidencia (°)", self.var_theta, 0.5, 5.0, 0.1)
        self._slider(side, "φ azimut (°)", self.var_phi, 0.0, 90.0, 0.5)
        self._slider(side, "L cámara (cm)", self.var_L, 10.0, 50.0, 0.5)
        self._slider(side, "rango (h,k)", self.var_hmax, 2, 15, 1)
        self._slider(side, "D terraza/dominio (Å)", self.var_D, 20.0, 400.0, 5.0)

        ttk.Button(side, text="Recalcular", command=self.recompute).pack(
            fill=tk.X, padx=16, pady=(12, 8)
        )

        tk.Label(
            side,
            textvariable=self.status,
            bg="#242424",
            fg="#b8b8b8",
            font=("Segoe UI", 9),
            justify="left",
            wraplength=240,
        ).pack(anchor="w", padx=16, pady=8)

        tk.Label(
            side,
            text="Puntos: Visulation.compute_spots()\n"
            "Líneas: Visulation_streaks\n"
            "  (rod width δ≈2π/D)\n"
            "D grande → streaks cortos.\n"
            "D chico → streaks largos.",
            bg="#242424",
            fg="#8d8d8d",
            font=("Segoe UI", 8),
            justify="left",
        ).pack(side=tk.BOTTOM, anchor="w", padx=16, pady=16)

        main = tk.Frame(self, bg="#111111")
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main, bg="#050805", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        self.canvas.bind("<Configure>", lambda _e: self.redraw())
        self.canvas.bind("<Motion>", self._on_motion)

        self.hover = tk.Label(
            main,
            text="",
            bg="#111111",
            fg="#c8c8c8",
            font=("Consolas", 10),
            anchor="w",
        )
        self.hover.pack(fill=tk.X, padx=16, pady=(0, 10))

    def _slider(self, parent, label, var, vmin, vmax, step):
        box = tk.Frame(parent, bg="#242424")
        box.pack(fill=tk.X, padx=16, pady=4)
        header = tk.Frame(box, bg="#242424")
        header.pack(fill=tk.X)
        tk.Label(header, text=label, bg="#242424", fg="#d0d0d0", font=("Segoe UI", 9)).pack(
            side=tk.LEFT
        )
        val = tk.Label(header, text="", bg="#242424", fg="#9fd89f", font=("Consolas", 9))
        val.pack(side=tk.RIGHT)

        def shown(_=None):
            x = var.get()
            val.config(text=f"{x:.2f}" if isinstance(x, float) else str(int(x)))

        scale = tk.Scale(
            box,
            from_=vmin,
            to=vmax,
            resolution=step,
            orient=tk.HORIZONTAL,
            variable=var,
            showvalue=False,
            bg="#242424",
            fg="#d0d0d0",
            troughcolor="#3a3a3a",
            highlightthickness=0,
            bd=0,
            command=lambda _v: (shown(), self.recompute()),
        )
        scale.pack(fill=tk.X)
        shown()

    def recompute(self):
        kwargs = dict(
            a=self.var_a.get(),
            Volt=self.var_kV.get() * 1000.0,
            angle_razante=self.var_theta.get(),
            phi_deg=self.var_phi.get(),
            L_cm=self.var_L.get(),
            h_max=int(self.var_hmax.get()),
        )
        if self.var_mode.get() == "streaks":
            data = compute_streaks(D_A=self.var_D.get(), **kwargs)
            self._streaks = data["streaks"]
            self._spots = data["spots"]
            self.status.set(
                f"{data['n_streaks']} streaks  |  D = {data['D_A']:.0f} Å\n"
                f"δG = {data['delta_G']:.3f} Å⁻¹\n"
                f"especular z = {data['z_specular_cm']:.2f} cm"
            )
        else:
            data = compute_spots(**kwargs)
            self._streaks = []
            self._spots = data["spots"]
            self.status.set(
                f"{data['n_spots']} puntos (rods ideales)\n"
                f"especular z = {data['z_specular_cm']:.2f} cm"
            )
        self.redraw()

    def _to_canvas(self, v_cm, z_cm, width, height):
        span = max(4.0, self.var_L.get() * np.tan(np.deg2rad(self.var_theta.get())) * 4.0)
        zs = [s["z_cm"] for s in self._spots]
        vs = [s["v_cm"] for s in self._spots]
        for st in self._streaks:
            zs.extend([st["z_min"], st["z_max"]])
            vs.extend([st["v_min"], st["v_max"]])
        if zs and vs:
            span = max(span, max(abs(v) for v in vs) * 1.3, max(abs(z) for z in zs) * 1.3)
        margin = 40
        usable_w = max(width - 2 * margin, 1)
        usable_h = max(height - 2 * margin, 1)
        scale = min(usable_w / (2 * span), usable_h / (1.4 * span))
        cx = width / 2.0
        z0 = margin + 0.18 * usable_h
        x = cx + v_cm * scale
        y = z0 + z_cm * scale
        return x, y, scale, z0, cx

    def redraw(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 20 or h < 20:
            return

        _x0, _y0, scale, z0, cx = self._to_canvas(0.0, 0.0, w, h)

        c.create_rectangle(8, 8, w - 8, h - 8, outline="#2f4f2f", width=2)
        c.create_text(
            18, 18, text="pantalla de fósforo", fill="#6a9a6a", anchor="nw", font=("Segoe UI", 10)
        )
        c.create_text(w - 18, 18, text="+v →", fill="#6a9a6a", anchor="ne", font=("Segoe UI", 9))

        c.create_line(40, z0, w - 40, z0, fill="#3d5c3d", dash=(6, 4))
        c.create_text(
            44,
            z0 - 12,
            text="z = 0  borde de sombra",
            fill="#7a9a7a",
            anchor="w",
            font=("Segoe UI", 8),
        )
        c.create_line(cx, 30, cx, h - 30, fill="#243024")

        bar = scale
        c.create_line(w - 40 - bar, h - 28, w - 40, h - 28, fill="#8fbf8f", width=2)
        c.create_text(w - 40 - bar / 2, h - 42, text="1 cm", fill="#8fbf8f", font=("Segoe UI", 8))

        self._hit_map.clear()

        if self.var_mode.get() == "streaks" and self._streaks:
            for st in self._streaks:
                color = "#e8ffe8" if st["specular"] else "#5dff5d"
                width_px = 3 if st["specular"] else 2
                pts = st["points"]
                # Draw as connected segments (usually nearly vertical)
                for i in range(len(pts) - 1):
                    x1, y1, *_ = self._to_canvas(pts[i][0], pts[i][1], w, h)
                    x2, y2, *_ = self._to_canvas(pts[i + 1][0], pts[i + 1][1], w, h)
                    c.create_line(x1, y1, x2, y2, fill=color, width=width_px)
                # Center hit target for hover
                x, y, *_ = self._to_canvas(st["v_cm"], st["z_cm"], w, h)
                self._hit_map.append((int(x), int(y), 14, st))
                if st["specular"] or (abs(st["h"]) + abs(st["k"]) <= 2):
                    c.create_text(
                        x + 8,
                        y - 8,
                        text=f"{st['h']}{st['k']}",
                        fill="#cfe8cf",
                        anchor="w",
                        font=("Consolas", 8),
                    )
        else:
            for spot in self._spots:
                x, y, *_ = self._to_canvas(spot["v_cm"], spot["z_cm"], w, h)
                r = 7 if spot["specular"] else 4
                color = "#d8ffd8" if spot["specular"] else "#5dff5d"
                c.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
                if spot["specular"] or (abs(spot["h"]) + abs(spot["k"]) <= 2):
                    c.create_text(
                        x + 8,
                        y - 8,
                        text=f"{spot['h']}{spot['k']}",
                        fill="#cfe8cf",
                        anchor="w",
                        font=("Consolas", 8),
                    )
                self._hit_map.append((int(x), int(y), 12, spot))

    def _on_motion(self, event):
        best = None
        best_d = 14
        for x, y, rad, spot in self._hit_map:
            d = (event.x - x) ** 2 + (event.y - y) ** 2
            if d <= rad * rad and d < best_d * best_d:
                best = spot
                best_d = d ** 0.5
        if best is None:
            self.hover.config(text="")
            return
        extra = ""
        if "z_min" in best:
            extra = f"   streak z = [{best['z_min']:.2f}, {best['z_max']:.2f}] cm"
        self.hover.config(
            text=(
                f"({best['h']},{best['k']})   "
                f"v = {best['v_cm']:+.3f} cm   "
                f"z = {best['z_cm']:+.3f} cm"
                f"{extra}"
            )
        )


if __name__ == "__main__":
    RheedScreen().mainloop()
