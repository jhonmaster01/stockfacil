package com.unad.stockfacil.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.unad.stockfacil.data.dao.AlertDao
import com.unad.stockfacil.data.dao.MovementDao
import com.unad.stockfacil.data.dao.ProductDao
import com.unad.stockfacil.data.model.InventoryMovement
import com.unad.stockfacil.data.model.Product
import com.unad.stockfacil.data.model.StockAlert

@Database(
    entities = [Product::class, InventoryMovement::class, StockAlert::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
    abstract fun movementDao(): MovementDao
    abstract fun alertDao(): AlertDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "stockfacil_inventory.db"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
