# -*- coding: utf-8 -*-
"""
StockFácil Móvil - Simulador de Entorno Relevante TRL5
Universidad Nacional Abierta y a Distancia (UNAD)
Curso: Proyecto de Grado 202016907 - Fase 4
Autor: Jhon Fernando Ruiz Salinas (C.C. 1.118.549.711)

Este módulo simula la lógica del prototipo Android con persistencia SQLite
offline-first, permitiendo validar transacciones, escaneo, alertas y métricas TRL5.
"""
import sqlite3
import datetime
import os
import sys
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), "stockfacil_local.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # 1. Tabla de Productos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_measure TEXT NOT NULL,
        cost_price REAL NOT NULL,
        sale_price REAL NOT NULL,
        current_stock REAL NOT NULL,
        minimum_stock REAL NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    # 2. Tabla de Movimientos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS movimientos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL,
        quantity REAL NOT NULL,
        previous_stock REAL NOT NULL,
        new_stock REAL NOT NULL,
        unit_price REAL NOT NULL,
        notes TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES productos(id)
    );
    """)
    # 3. Tabla de Alertas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS alertas_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        current_stock REAL NOT NULL,
        minimum_stock REAL NOT NULL,
        timestamp TEXT NOT NULL,
        is_resolved INTEGER DEFAULT 0,
        FOREIGN KEY (product_id) REFERENCES productos(id)
    );
    """)
    conn.commit()

    # Pre-cargar catálogo semilla si está vacía (datos representativos de Quípama, Boyacá)
    cur.execute("SELECT COUNT(*) as total FROM productos")
    if cur.fetchone()["total"] == 0:
        seed_data = [
            ("7702001001234", "Arroz Diana Tradicional 1000g", "Víveres", "Libra/Paquete", 3800.0, 4600.0, 24.0, 8.0),
            ("7702002005678", "Aceite Premier Girasol 1000ml", "Víveres", "Botella", 11500.0, 13800.0, 6.0, 5.0),
            ("7702003009012", "Azúcar Blanca Incauca 1000g", "Víveres", "Kilo", 4200.0, 5000.0, 18.0, 6.0),
            ("7702004003456", "Café Sello Rojo 500g", "Víveres", "Libra", 9800.0, 12000.0, 4.0, 5.0), # Alerta inicial (4 <= 5)
            ("7702005007890", "Detergente Fab Polvo 1000g", "Aseo", "Bolsa", 7200.0, 8900.0, 15.0, 4.0),
            ("7702006001122", "Leche Alquería Entera 1000ml", "Lácteos", "Bolsa", 3600.0, 4400.0, 3.0, 10.0), # Alerta crítica
            ("7702007003344", "Huevos AA Santa Anita", "Víveres", "Canastilla x30", 16000.0, 19500.0, 5.0, 2.0),
            ("7702008005566", "Panela Pastilla Boyacense", "Víveres", "Atado 4 un", 4800.0, 6000.0, 12.0, 4.0)
        ]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for item in seed_data:
            cur.execute("""
            INSERT INTO productos (barcode, name, category, unit_measure, cost_price, sale_price, current_stock, minimum_stock, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (*item, now))
            # Verificar si entra con alerta
            if item[6] <= item[7]:
                p_id = cur.lastrowid
                cur.execute("""
                INSERT INTO alertas_stock (product_id, product_name, current_stock, minimum_stock, timestamp, is_resolved)
                VALUES (?, ?, ?, ?, ?, 0)
                """, (p_id, item[1], item[6], item[7], now))
        conn.commit()
    conn.close()

def list_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos ORDER BY name ASC")
    rows = cur.fetchall()
    print("\n" + "="*85)
    print(f"{'CÓDIGO':<15} {'PRODUCTO':<32} {'CAT.':<10} {'UNIDAD':<12} {'STOCK':<8} {'MÍN.':<6} {'ESTADO'}")
    print("="*85)
    for r in rows:
        status = "⚠️ CRÍTICO" if r["current_stock"] <= r["minimum_stock"] else "✅ OK"
        print(f"{r['barcode']:<15} {r['name'][:30]:<32} {r['category'][:9]:<10} {r['unit_measure'][:11]:<12} {r['current_stock']:<8.1f} {r['minimum_stock']:<6.1f} {status}")
    print("="*85)
    conn.close()

def scan_or_register_movement():
    conn = get_connection()
    cur = conn.cursor()
    print("\n--- REGISTRO RÁPIDO DE MOVIMIENTO (SIMULACIÓN DE ESCÁNER CÁMARA) ---")
    barcode = input("Escanee o digite el código de barras del producto: ").strip()
    cur.execute("SELECT * FROM productos WHERE barcode = ?", (barcode,))
    p = cur.fetchone()
    if not p:
        print(f"❌ Error: El producto con código [{barcode}] no se encuentra registrado en el catálogo.")
        conn.close()
        return

    print(f"\n📦 Producto Detectado: {p['name']}")
    print(f"   Categoría: {p['category']} | Unidad: {p['unit_measure']}")
    print(f"   Stock Actual: {p['current_stock']} | Stock Mínimo: {p['minimum_stock']}")
    print(f"   Precio Costo: ${p['cost_price']:,.0f} | Precio Venta: ${p['sale_price']:,.0f}")

    print("\nTipo de movimiento a registrar:")
    print("1. [ENTRADA] Compra o recepción de mercancía mayorista")
    print("2. [SALIDA]  Venta al cliente")
    print("3. [SALIDA]  Baja por merma, rotura o vencimiento")
    opc = input("Seleccione (1/2/3): ").strip()

    try:
        qty = float(input("Ingrese la cantidad: ").strip())
        if qty <= 0:
            print("❌ La cantidad debe ser un número positivo.")
            conn.close()
            return
    except ValueError:
        print("❌ Entrada numérica inválida.")
        conn.close()
        return

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prev_stock = p["current_stock"]

    if opc == "1":
        m_type = "ENTRADA_COMPRA"
        new_stock = prev_stock + qty
        u_price = p["cost_price"]
        notes = "Recepción de pedido / Compra"
    elif opc == "2":
        m_type = "SALIDA_VENTA"
        new_stock = prev_stock - qty
        u_price = p["sale_price"]
        notes = "Venta mostrador"
    elif opc == "3":
        m_type = "SALIDA_MERMA_ROTURA"
        new_stock = prev_stock - qty
        u_price = p["cost_price"]
        notes = "Merma / Daño en estantería"
    else:
        print("❌ Opción inválida.")
        conn.close()
        return

    # Actualizar producto
    cur.execute("UPDATE productos SET current_stock = ? WHERE id = ?", (new_stock, p["id"]))

    # Registrar movimiento
    cur.execute("""
    INSERT INTO movimientos_inventario (product_id, movement_type, quantity, previous_stock, new_stock, unit_price, notes, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (p["id"], m_type, qty, prev_stock, new_stock, u_price, notes, now))

    # Evaluar alerta de stock mínimo
    alert_msg = ""
    if new_stock <= p["minimum_stock"]:
        cur.execute("""
        INSERT INTO alertas_stock (product_id, product_name, current_stock, minimum_stock, timestamp, is_resolved)
        VALUES (?, ?, ?, ?, ?, 0)
        """, (p["id"], p["name"], new_stock, p["minimum_stock"], now))
        alert_msg = f"\n🚨 ¡ALERTA DE STOCK MÍNIMO ACTIVADA! Quedan {new_stock:.1f} unidades (Punto de reorden: {p['minimum_stock']:.1f})."
    elif prev_stock <= p["minimum_stock"] and new_stock > p["minimum_stock"]:
        cur.execute("UPDATE alertas_stock SET is_resolved = 1 WHERE product_id = ?", (p["id"],))
        alert_msg = f"\n✅ Alerta de desabastecimiento resuelta satisfactoriamente."

    conn.commit()
    conn.close()
    print(f"\n✔️ Transacción completada con éxito. Stock anterior: {prev_stock:.1f} ➔ Nuevo stock: {new_stock:.1f}{alert_msg}")

def check_alerts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT p.barcode, p.name, p.current_stock, p.minimum_stock, p.category, p.unit_measure
    FROM productos p
    WHERE p.current_stock <= p.minimum_stock
    ORDER BY p.current_stock ASC
    """)
    alerts = cur.fetchall()
    print("\n" + "="*75)
    print("🚨 PANEL DE MONITOREO Y ALERTAS DE REABASTECIMIENTO CRÍTICO")
    print("="*75)
    if not alerts:
        print("✅ No hay productos en nivel crítico. Todos los artículos superan el stock de seguridad.")
    else:
        print(f"Total de productos en quiebre o riesgo de desabastecimiento: {len(alerts)}")
        print(f"{'CÓDIGO':<15} {'PRODUCTO':<30} {'STOCK':<10} {'MÍNIMO':<10} {'DÉFICIT'}")
        print("-"*75)
        for a in alerts:
            deficit = a["minimum_stock"] - a["current_stock"]
            print(f"{a['barcode']:<15} {a['name'][:28]:<30} {a['current_stock']:<10.1f} {a['minimum_stock']:<10.1f} -{deficit:.1f}")
    print("="*75)
    conn.close()

def audit_physical_count():
    conn = get_connection()
    cur = conn.cursor()
    print("\n--- MÓDULO DE AUDITORÍA Y CONTEO FÍSICO DE INVENTARIO ---")
    barcode = input("Escanee o digite el código de barras a auditar: ").strip()
    cur.execute("SELECT * FROM productos WHERE barcode = ?", (barcode,))
    p = cur.fetchone()
    if not p:
        print("❌ Producto no hallado.")
        conn.close()
        return

    print(f"Artículo: {p['name']} | Stock Teórico en Sistema: {p['current_stock']} {p['unit_measure']}")
    try:
        physical = float(input("Ingrese las unidades físicas contadas en estante: ").strip())
    except ValueError:
        print("❌ Valor inválido.")
        conn.close()
        return

    diff = physical - p["current_stock"]
    diff_val = diff * p["cost_price"]

    print(f"\n📊 Resultado de Conciliación:")
    print(f"   Diferencia en unidades: {diff:+.1f} {p['unit_measure']}")
    print(f"   Impacto monetario (al costo): ${diff_val:+,.2f} COP")

    confirm = input("¿Desea ajustar automáticamente el saldo del sistema al conteo físico? (s/n): ").strip().lower()
    if confirm == "s":
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("UPDATE productos SET current_stock = ? WHERE id = ?", (physical, p["id"]))
        cur.execute("""
        INSERT INTO movimientos_inventario (product_id, movement_type, quantity, previous_stock, new_stock, unit_price, notes, timestamp)
        VALUES (?, 'AJUSTE_AUDITORIA_FISICA', ?, ?, ?, ?, 'Ajuste por conteo físico', ?)
        """, (p["id"], physical, p["current_stock"], physical, p["cost_price"], now))
        conn.commit()
        print("✔️ Inventario conciliado y actualizado en base de datos local.")
    else:
        print("ℹ️ Ajuste cancelado por el usuario.")
    conn.close()

def export_csv():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT barcode, name, category, unit_measure, cost_price, sale_price, current_stock, minimum_stock FROM productos")
    rows = cur.fetchall()
    csv_file = os.path.join(os.path.dirname(__file__), "inventario_consolidado_backup.csv")
    with open(csv_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Código de Barras", "Nombre del Producto", "Categoría", "Unidad", "Costo ($)", "Venta ($)", "Stock Actual", "Stock Mínimo", "Valor Inventario ($)"])
        for r in rows:
            val = r["current_stock"] * r["cost_price"]
            writer.writerow([r["barcode"], r["name"], r["category"], r["unit_measure"], r["cost_price"], r["sale_price"], r["current_stock"], r["minimum_stock"], val])
    conn.close()
    print(f"\n📁 Archivo de respaldo exportado exitosamente en: {csv_file}")

def main_menu():
    init_db()
    while True:
        print("\n" + "="*60)
        print("   STOCKFÁCIL MÓVIL - PROTOTIPO TRL5 (UNAD FASE 4)")
        print("   Arquitectura Offline-First | Persistencia SQLite Local")
        print("   Autor: Jhon Fernando Ruiz Salinas | ECBTI UNAD")
        print("="*60)
        print("1. Consultar Catálogo Completo y Existencias")
        print("2. Registrar Movimiento Rápido (Entrada / Salida con Escáner)")
        print("3. Monitor de Alertas de Stock Mínimo")
        print("4. Módulo de Conteo Físico y Conciliación")
        print("5. Exportar Respaldo CSV del Inventario")
        print("6. Salir")
        print("="*60)
        op = input("Seleccione una opción (1-6): ").strip()
        if op == "1":
            list_products()
        elif op == "2":
            scan_or_register_movement()
        elif op == "3":
            check_alerts()
        elif op == "4":
            audit_physical_count()
        elif op == "5":
            export_csv()
        elif op == "6":
            print("\n¡Gracias por utilizar el prototipo StockFácil Móvil!")
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    main_menu()
