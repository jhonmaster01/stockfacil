package com.unad.stockfacil.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entidad de Producto para base de datos SQLite mediante Android Room.
 * Diseñado conforme a la arquitectura offline-first para micronegocios.
 */
@Entity(tableName = "productos")
data class Product(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val barcode: String,              // Código EAN-13, EAN-8 o código asignado
    val name: String,                 // Nombre descriptivo del artículo
    val category: String,             // Categoría (Víveres, Aseo, Lácteos, Ferretería, etc.)
    val unitOfMeasure: String,        // Unidad de medida (Unidad, Libra, Kilo, Bulto, Docena)
    val costPrice: Double,            // Precio de adquisición con proveedores
    val salePrice: Double,            // Precio de venta al público
    val currentStock: Double,         // Cantidad actual en existencia física
    val minimumStock: Double,         // Umbral de punto de reorden / stock de seguridad
    val createdAt: Long = System.currentTimeMillis()
) {
    /**
     * Evalúa si el producto se encuentra en condición crítica de inventario.
     */
    val isCriticalStock: Boolean
        get() = currentStock <= minimumStock
}
