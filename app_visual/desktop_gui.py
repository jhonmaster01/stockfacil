# -*- coding: utf-8 -*-
"""
StockFácil Móvil - Interfaz de Escritorio Nativa (Tkinter)
Universidad Nacional Abierta y a Distancia (UNAD)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "simulator_trl5", "stockfacil_local.db")

class StockFacilDesktopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("StockFácil Móvil - Prototipo TRL5 (UNAD Proyecto de Grado)")
        self.root.geometry("820x620")
        self.root.configure(bg="#f1f5f9")

        # Header
        header = tk.Frame(self.root, bg="#4f46e5", height=60)
        header.pack(fill="x")
        lbl_title = tk.Label(header, text="StockFácil Móvil - Control de Inventarios (TRL 5)", font=("Arial", 14, "bold"), fg="white", bg="#4f46e5")
        lbl_title.pack(side="left", padx=15, pady=12)
        lbl_sub = tk.Label(header, text="Jhon Fernando Ruiz Salinas | Quípama", font=("Arial", 10), fg="#c7d2fe", bg="#4f46e5")
        lbl_sub.pack(side="right", padx=15)

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=12)

        # Tab 1: Catálogo y Stock
        self.tab_catalog = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_catalog, text="  📦 Catálogo y Existencias  ")
        self.setup_catalog_tab()

        # Tab 2: Movimientos Rápidos
        self.tab_movements = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_movements, text="  ⚡ Registrar Movimiento  ")
        self.setup_movements_tab()

        # Tab 3: Alertas Críticas
        self.tab_alerts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_alerts, text="  🚨 Alertas de Stock Mínimo  ")
        self.setup_alerts_tab()

        self.load_data()

    def get_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def setup_catalog_tab(self):
        top_frame = ttk.Frame(self.tab_catalog)
        top_frame.pack(fill="x", padx=10, pady=8)
        ttk.Button(top_frame, text="🔄 Actualizar", command=self.load_data).pack(side="left")

        # Treeview
        cols = ("Código", "Producto", "Categoría", "Unidad", "Costo", "Venta", "Stock Actual", "Mínimo", "Estado")
        self.tree = ttk.Treeview(self.tab_catalog, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=85, anchor="center")
        self.tree.column("Producto", width=180, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    def setup_movements_tab(self):
        f = ttk.LabelFrame(self.tab_movements, text=" Registrar Entrada o Salida con Escáner ", padding=15)
        f.pack(fill="x", padx=15, pady=15)

        ttk.Label(f, text="Código de Barras:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_barcode = ttk.Entry(f, width=25)
        self.ent_barcode.grid(row=0, column=1, sticky="w", pady=5)
        ttk.Button(f, text="🔍 Buscar", command=self.find_product).grid(row=0, column=2, padx=10)

        self.lbl_prod_info = ttk.Label(f, text="Producto no seleccionado", font=("Arial", 10, "italic"), foreground="#64748b")
        self.lbl_prod_info.grid(row=1, column=0, columnspan=3, sticky="w", pady=8)

        ttk.Label(f, text="Tipo de Movimiento:").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_type = ttk.Combobox(f, values=["ENTRADA_COMPRA", "SALIDA_VENTA", "SALIDA_MERMA_ROTURA"], state="readonly", width=22)
        self.combo_type.set("ENTRADA_COMPRA")
        self.combo_type.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Label(f, text="Cantidad:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_qty = ttk.Entry(f, width=12)
        self.ent_qty.insert(0, "1")
        self.ent_qty.grid(row=3, column=1, sticky="w", pady=5)

        ttk.Button(f, text="✔️ Confirmar Transacción", command=self.save_movement).grid(row=4, column=1, sticky="w", pady=15)

    def setup_alerts_tab(self):
        top_frame = ttk.Frame(self.tab_alerts)
        top_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(top_frame, text="Productos en o por debajo del Punto de Reorden", font=("Arial", 10, "bold"), foreground="#dc2626").pack(side="left")

        cols = ("Código", "Producto", "Stock Actual", "Stock Mínimo", "Déficit Requerido")
        self.tree_alerts = ttk.Treeview(self.tab_alerts, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree_alerts.heading(c, text=c)
            self.tree_alerts.column(c, width=120, anchor="center")
        self.tree_alerts.column("Producto", width=240, anchor="w")
        self.tree_alerts.pack(fill="both", expand=True, padx=10, pady=5)

    def load_data(self):
        conn = self.get_db()
        cur = conn.cursor()
        for item in self.tree.get_children():
            self.tree.delete(item)
        cur.execute("SELECT * FROM productos ORDER BY name ASC")
        for r in cur.fetchall():
            status = "CRÍTICO" if r["current_stock"] <= r["minimum_stock"] else "OK"
            self.tree.insert("", "end", values=(
                r["barcode"], r["name"], r["category"], r["unit_measure"],
                f"${r['cost_price']:,.0f}", f"${r['sale_price']:,.0f}",
                r["current_stock"], r["minimum_stock"], status
            ))

        for item in self.tree_alerts.get_children():
            self.tree_alerts.delete(item)
        cur.execute("SELECT * FROM productos WHERE current_stock <= minimum_stock")
        for r in cur.fetchall():
            deficit = r["minimum_stock"] - r["current_stock"]
            self.tree_alerts.insert("", "end", values=(
                r["barcode"], r["name"], r["current_stock"], r["minimum_stock"], f"-{deficit:.1f}"
            ))
        conn.close()

    def find_product(self):
        code = self.ent_barcode.get().strip()
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM productos WHERE barcode = ?", (code,))
        p = cur.fetchone()
        conn.close()
        if p:
            self.current_prod = p
            self.lbl_prod_info.config(
                text=f"📦 {p['name']} | Stock Actual: {p['current_stock']} {p['unit_measure']} (Mínimo: {p['minimum_stock']})",
                foreground="#0f172a"
            )
        else:
            messagebox.showerror("Error", f"No se halló producto con código {code}")

    def save_movement(self):
        if not hasattr(self, 'current_prod') or not self.current_prod:
            messagebox.showwarning("Atención", "Busque primero un producto.")
            return
        try:
            qty = float(self.ent_qty.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.")
            return

        m_type = self.combo_type.get()
        prev = self.current_prod["current_stock"]
        new_stk = prev + qty if m_type == "ENTRADA_COMPRA" else prev - qty

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("UPDATE productos SET current_stock = ? WHERE id = ?", (new_stk, self.current_prod["id"]))
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
        INSERT INTO movimientos_inventario (product_id, movement_type, quantity, previous_stock, new_stock, unit_price, notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, 'Transacción Desktop GUI', ?)
        """, (self.current_prod["id"], m_type, qty, prev, new_stk, self.current_prod["cost_price"], now))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", f"Movimiento registrado. Nuevo stock: {new_stk}")
        self.load_data()
        self.find_product()

if __name__ == "__main__":
    root = tk.Tk()
    app = StockFacilDesktopGUI(root)
    root.mainloop()
