package com.unad.stockfacil.data.dao

import androidx.room.*
import com.unad.stockfacil.data.model.Product
import com.unad.stockfacil.data.model.InventoryMovement
import com.unad.stockfacil.data.model.StockAlert
import kotlinx.coroutines.flow.Flow

@Dao
interface ProductDao {
    @Query("SELECT * FROM productos ORDER BY name ASC")
    fun getAllProducts(): Flow<List<Product>>

    @Query("SELECT * FROM productos WHERE barcode = :barcode LIMIT 1")
    suspend fun getProductByBarcode(barcode: String): Product?

    @Query("SELECT * FROM productos WHERE id = :id LIMIT 1")
    suspend fun getProductById(id: Long): Product?

    @Query("SELECT * FROM productos WHERE currentStock <= minimumStock ORDER BY currentStock ASC")
    fun getCriticalStockProducts(): Flow<List<Product>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProduct(product: Product): Long

    @Update
    suspend fun updateProduct(product: Product)

    @Delete
    suspend fun deleteProduct(product: Product)

    @Query("UPDATE productos SET currentStock = :newStock WHERE id = :productId")
    suspend fun updateStock(productId: Long, newStock: Double)
}

@Dao
interface MovementDao {
    @Insert
    suspend fun insertMovement(movement: InventoryMovement): Long

    @Query("SELECT * FROM movimientos_inventario ORDER BY timestamp DESC LIMIT 100")
    fun getRecentMovements(): Flow<List<InventoryMovement>>

    @Query("SELECT * FROM movimientos_inventario WHERE productId = :productId ORDER BY timestamp DESC")
    fun getMovementsForProduct(productId: Long): Flow<List<InventoryMovement>>
}

@Dao
interface AlertDao {
    @Insert
    suspend fun insertAlert(alert: StockAlert): Long

    @Query("SELECT * FROM alertas_stock WHERE isResolved = 0 ORDER BY timestamp DESC")
    fun getActiveAlerts(): Flow<List<StockAlert>>

    @Query("UPDATE alertas_stock SET isResolved = 1 WHERE productId = :productId")
    suspend fun resolveAlertsForProduct(productId: Long)
}
