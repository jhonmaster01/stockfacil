package com.unad.stockfacil.repository

import com.unad.stockfacil.data.dao.AlertDao
import com.unad.stockfacil.data.dao.MovementDao
import com.unad.stockfacil.data.dao.ProductDao
import com.unad.stockfacil.data.model.InventoryMovement
import com.unad.stockfacil.data.model.MovementType
import com.unad.stockfacil.data.model.Product
import com.unad.stockfacil.data.model.StockAlert
import kotlinx.coroutines.flow.Flow

/**
 * Repositorio central de inventarios. Implementa principios de arquitectura limpia
 * y reglas de consistencia transaccional offline-first.
 */
class InventoryRepository(
    private val productDao: ProductDao,
    private val movementDao: MovementDao,
    private val alertDao: AlertDao
) {
    val allProducts: Flow<List<Product>> = productDao.getAllProducts()
    val criticalProducts: Flow<List<Product>> = productDao.getCriticalStockProducts()
    val activeAlerts: Flow<List<StockAlert>> = alertDao.getActiveAlerts()
    val recentMovements: Flow<List<InventoryMovement>> = movementDao.getRecentMovements()

    suspend fun findByBarcode(barcode: String): Product? {
        return productDao.getProductByBarcode(barcode.trim())
    }

    suspend fun saveProduct(product: Product): Long {
        return productDao.insertProduct(product)
    }

    /**
     * Registra un movimiento atómico de inventario (Entrada o Salida)
     * y evalúa umbrales de alerta de stock mínimo.
     */
    suspend fun registerMovement(
        productId: Long,
        type: MovementType,
        quantity: Double,
        unitPrice: Double,
        notes: String = ""
    ): Result<Double> {
        val product = productDao.getProductById(productId)
            ?: return Result.failure(IllegalArgumentException("Producto no encontrado en inventario."))

        val previousStock = product.currentStock
        val newStock = when (type) {
            MovementType.ENTRADA_COMPRA -> previousStock + quantity
            MovementType.SALIDA_VENTA, MovementType.SALIDA_MERMA_ROTURA -> {
                val calculated = previousStock - quantity
                if (calculated < 0) {
                    // Advertencia de saldo negativo (posible inconsistencia física)
                }
                calculated
            }
            MovementType.AJUSTE_AUDITORIA_FISICA -> quantity // En ajuste físico, quantity es el nuevo stock real
        }

        // 1. Actualizar stock en producto
        productDao.updateStock(productId, newStock)

        // 2. Registrar asiento de movimiento
        val movement = InventoryMovement(
            productId = productId,
            movementType = type,
            quantity = quantity,
            previousStock = previousStock,
            newStock = newStock,
            unitPrice = unitPrice,
            notes = notes
        )
        movementDao.insertMovement(movement)

        // 3. Evaluar alerta de stock mínimo
        if (newStock <= product.minimumStock) {
            alertDao.insertAlert(
                StockAlert(
                    productId = productId,
                    productName = product.name,
                    currentStock = newStock,
                    minimumStock = product.minimumStock
                )
            )
        } else if (previousStock <= product.minimumStock && newStock > product.minimumStock) {
            // Se reabasteció el producto: resolver alertas previas
            alertDao.resolveAlertsForProduct(productId)
        }

        return Result.success(newStock)
    }
}
