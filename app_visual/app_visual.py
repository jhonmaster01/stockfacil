# -*- coding: utf-8 -*-
"""
StockFácil Móvil - Backend Visual Prototipo TRL5
Universidad Nacional Abierta y a Distancia (UNAD)
Proyecto de Grado - Fase 4
Autor: Jhon Fernando Ruiz Salinas
"""
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import datetime
import os
import webbrowser
import threading
import csv

app = Flask(__name__, template_folder="templates")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "simulator_trl5", "stockfacil_local.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total_prod, SUM(current_stock) as total_units, SUM(current_stock * cost_price) as total_val FROM productos")
    row = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) as critical_count FROM productos WHERE current_stock <= minimum_stock")
    crit = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) as total_movs FROM movimientos_inventario")
    movs = cur.fetchone()
    
    conn.close()
    return jsonify({
        "total_products": row["total_prod"] or 0,
        "total_units": round(row["total_units"] or 0, 1),
        "total_value_cop": round(row["total_val"] or 0, 2),
        "critical_count": crit["critical_count"] or 0,
        "total_movements": movs["total_movs"] or 0
    })

@app.route("/api/products", methods=["GET", "POST"])
def handle_products():
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        data = request.json
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur.execute("""
            INSERT INTO productos (barcode, name, category, unit_measure, cost_price, sale_price, current_stock, minimum_stock, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["barcode"],
                data["name"],
                data["category"],
                data["unit_measure"],
                float(data["cost_price"]),
                float(data["sale_price"]),
                float(data["current_stock"]),
                float(data["minimum_stock"]),
                now
            ))
            conn.commit()
            p_id = cur.lastrowid
            conn.close()
            return jsonify({"success": True, "id": p_id, "message": "Producto agregado exitosamente"})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"success": False, "message": "El código de barras ya existe en el sistema"}), 400
    else:
        cur.execute("SELECT * FROM productos ORDER BY name ASC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return jsonify(rows)

@app.route("/api/products/barcode/<barcode>")
def get_by_barcode(barcode):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE barcode = ?", (barcode.strip(),))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"found": True, "product": dict(row)})
    return jsonify({"found": False, "message": "Producto no registrado"}), 404

@app.route("/api/movement", methods=["POST"])
def register_movement():
    data = request.json
    p_id = data["product_id"]
    m_type = data["movement_type"] # ENTRADA_COMPRA, SALIDA_VENTA, SALIDA_MERMA_ROTURA
    qty = float(data["quantity"])
    notes = data.get("notes", "")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE id = ?", (p_id,))
    p = cur.fetchone()
    if not p:
        conn.close()
        return jsonify({"success": False, "message": "Producto no hallado"}), 404

    prev_stock = p["current_stock"]
    if m_type == "ENTRADA_COMPRA":
        new_stock = prev_stock + qty
        u_price = p["cost_price"]
    else:
        new_stock = prev_stock - qty
        u_price = p["sale_price"]

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("UPDATE productos SET current_stock = ? WHERE id = ?", (new_stock, p_id))

    cur.execute("""
    INSERT INTO movimientos_inventario (product_id, movement_type, quantity, previous_stock, new_stock, unit_price, notes, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (p_id, m_type, qty, prev_stock, new_stock, u_price, notes, now))

    alert_triggered = False
    if new_stock <= p["minimum_stock"]:
        alert_triggered = True
        cur.execute("""
        INSERT INTO alertas_stock (product_id, product_name, current_stock, minimum_stock, timestamp, is_resolved)
        VALUES (?, ?, ?, ?, ?, 0)
        """, (p_id, p["name"], new_stock, p["minimum_stock"], now))
    elif prev_stock <= p["minimum_stock"] and new_stock > p["minimum_stock"]:
        cur.execute("UPDATE alertas_stock SET is_resolved = 1 WHERE product_id = ?", (p_id,))

    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "previous_stock": prev_stock,
        "new_stock": new_stock,
        "alert_triggered": alert_triggered,
        "message": "Movimiento registrado satisfactoriamente"
    })

@app.route("/api/alerts")
def get_alerts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM productos 
    WHERE current_stock <= minimum_stock 
    ORDER BY (current_stock / NULLIF(minimum_stock, 0)) ASC
    """)
    alerts = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(alerts)

@app.route("/api/audit", methods=["POST"])
def audit_reconcile():
    data = request.json
    p_id = data["product_id"]
    physical_stock = float(data["physical_stock"])

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE id = ?", (p_id,))
    p = cur.fetchone()
    if not p:
        conn.close()
        return jsonify({"success": False, "message": "Producto no hallado"}), 404

    prev_stock = p["current_stock"]
    diff_units = physical_stock - prev_stock
    diff_val = diff_units * p["cost_price"]

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("UPDATE productos SET current_stock = ? WHERE id = ?", (physical_stock, p_id))

    cur.execute("""
    INSERT INTO movimientos_inventario (product_id, movement_type, quantity, previous_stock, new_stock, unit_price, notes, timestamp)
    VALUES (?, 'AJUSTE_AUDITORIA_FISICA', ?, ?, ?, ?, 'Ajuste de auditoría física de estante', ?)
    """, (p_id, physical_stock, prev_stock, physical_stock, p["cost_price"], now))

    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "diff_units": round(diff_units, 2),
        "diff_value_cop": round(diff_val, 2),
        "new_stock": physical_stock
    })

@app.route("/api/export-csv")
def export_csv_file():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT barcode, name, category, unit_measure, cost_price, sale_price, current_stock, minimum_stock FROM productos")
    rows = cur.fetchall()
    csv_path = os.path.join(os.path.dirname(__file__), "inventario_stockfacil_export.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Código Barras", "Producto", "Categoría", "Unidad", "Costo ($)", "Venta ($)", "Stock Actual", "Stock Mínimo", "Valor Inventario ($)"])
        for r in rows:
            val = r["current_stock"] * r["cost_price"]
            w.writerow([r["barcode"], r["name"], r["category"], r["unit_measure"], r["cost_price"], r["sale_price"], r["current_stock"], r["minimum_stock"], val])
    conn.close()
    return send_file(csv_path, as_attachment=True, download_name="inventario_micronegocio_quipama.csv")

def open_browser():
    webbrowser.open_new("http://localhost:5000")

if __name__ == "__main__":
    print("="*65)
    print(" INICIANDO SERVIDOR VISUAL PROTOTIPO TRL5 - STOCKFÁCIL MÓVIL")
    print(" Abriendo interfaz gráfica interactiva en el navegador...")
    print(" URL: http://localhost:5000")
    print("="*65)
    threading.Timer(1.2, open_browser).start()
    app.run(port=5000, debug=False)
