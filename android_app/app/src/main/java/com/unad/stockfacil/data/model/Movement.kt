package com.unad.stockfacil.data.model

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * Entidad que registra transacciones atómicas de entrada, salida o ajuste.
 */
@Entity(
    tableName = "movimientos_inventario",
    foreignKeys = [
        ForeignKey(
            entity = Product::class,
            parentColumns = ["id"],
            childColumns = ["productId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["productId"]), Index(value = ["timestamp"])]
)
data class InventoryMovement(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val productId: Long,
    val movementType: MovementType,    // ENTRADA, SALIDA_VENTA, SALIDA_MERMA, AJUSTE_CONTEO
    val quantity: Double,             // Cantidad involucrada
    val previousStock: Double,        // Stock antes de la transacción
    val newStock: Double,             // Stock resultante
    val unitPrice: Double,            // Precio unitario aplicado
    val notes: String = "",           // Comentarios o proveedor
    val timestamp: Long = System.currentTimeMillis()
)

enum class MovementType {
    ENTRADA_COMPRA,
    SALIDA_VENTA,
    SALIDA_MERMA_ROTURA,
    AJUSTE_AUDITORIA_FISICA
}

/**
 * Entidad para registrar eventos de alerta de stock mínimo.
 */
@Entity(tableName = "alertas_stock")
data class StockAlert(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val productId: Long,
    val productName: String,
    val currentStock: Double,
    val minimumStock: Double,
    val timestamp: Long = System.currentTimeMillis(),
    val isResolved: Boolean = false
)
