# StockFácil Móvil - Prototipo Funcional TRL5
**Aplicación Móvil Personalizable para el Control de Inventarios de Micronegocios**

[![UNAD](https://img.shields.io/badge/UNAD-Proyecto%20de%20Grado-blue.svg)](https://www.unad.edu.co/)
[![Fase 4](https://img.shields.io/badge/Fase%204-Componente%20Pr%C3%A1ctico%20Simulado-green.svg)]()
[![TRL](https://img.shields.io/badge/Maturity%20Level-TRL%205-orange.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-MVVM%20%2B%20Offline--First-purple.svg)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)]()

---

## 📌 Datos de Identificación del Proyecto
* **Autor:** Jhon Fernando Ruiz Salinas (C.C. 1.118.549.711)
* **Programa:** Ingeniería de Sistemas
* **Curso:** Proyecto de Grado (Código 202016907)
* **Docente / Tutor:** Cesar Felipe Henao Villa
* **Universidad:** Universidad Nacional Abierta y a Distancia – UNAD
* **Escuela:** Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
* **Zona / Centro:** Zona Centro Boyacá – Quípama, Boyacá
* **Nivel de Maduración Tecnológica:** TRL 5 (Technology Readiness Level 5 - Tecnología validada en entorno relevante/representativo de micronegocios de comercio minorista).

---

## 🚀 Resumen del Proyecto y Solución Tecnológica
**StockFácil Móvil** es un prototipo funcional de software móvil diseñado bajo la metodología ágil **AEGIS-MD** (Amaya Balaguera, 2015) y los principios de ciclo de desarrollo de software seguro **S-SDLC** (Miguel & Luis Eduardo, 2020). Su propósito es resolver la problemática de descontrol de existencias, mermas imprevistas y quiebres de stock en pequeños comercios minoristas (tiendas de barrio, misceláneas, minimercados y ferreterías), los cuales tradicionalmente operan con anotaciones en papel, libretas físicas o memoria individual.

### Características Principales:
1. **Arquitectura Offline-First:** 100% operativo sin conexión a internet ni consumo de datos móviles, empleando una base de datos local SQLite mediante la biblioteca de persistencia **Android Room**.
2. **Catálogo Flexible y Personalizable:** Admite unidades de medida fraccionadas y mayoristas (bulto, docena, kilo, libra, canastilla, unidad) y categorización libre.
3. **Escaneo de Códigos de Barra con Cámara:** Integración de bibliotecas de visión artificial para decodificación rápida de códigos estándar EAN-13, EAN-8 y UPC.
4. **Registro Rápido de Movimientos:** Entradas por compras a distribuidores y salidas por ventas o bajas por merma con cálculo atómico de saldos.
5. **Motor de Alertas de Stock Mínimo:** Notificación visual inmediata al alcanzar el punto de reorden configurado.
6. **Módulo de Conteo Físico y Auditoría:** Conciliación rápida de inventario teórico versus inventario físico con cálculo automático de discrepancias monetarias.
7. **Exportación Local:** Generación de copias de respaldo e informes consolidados en formato CSV.

---

## 🏛️ Arquitectura del Sistema
El proyecto implementa el patrón de arquitectura **MVVM (Model - View - ViewModel)** recomendado oficialmente para el desarrollo móvil robusto:

```
┌────────────────────────────────────────────────────────┐
│                   CAPA DE PRESENTACIÓN                  │
│   Activities / Fragments / Custom UI Components        │
│   (Escáner de Cámara, Formulario Movimientos, Alertas)  │
└───────────────────────────▲────────────────────────────┘
                            │ Observa StateFlow / LiveData
┌───────────────────────────┴────────────────────────────┐
│                    CAPA VIEWMODEL                      │
│   InventoryViewModel, ScannerViewModel, AlertViewModel  │
│   (Lógica de presentación, validación y estados UI)     │
└───────────────────────────▲────────────────────────────┘
                            │ Invoca casos de uso
┌───────────────────────────┴────────────────────────────┐
│                     CAPA DE DOMINIO                    │
│   InventoryRepository (Reglas de negocio, cálculo de   │
│   balances, verificación de umbrales y alertas)        │
└───────────────────────────▲────────────────────────────┘
                            │ Operaciones CRUD locales
┌───────────────────────────┴────────────────────────────┐
│                      CAPA DE DATOS                     │
│   Room Persistence Library (SQLite Database)            │
│   DAOs: ProductDao, MovementDao, AlertDao               │
│   Entities: Product, Category, Movement, Alert         │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías y Requisitos de Ejecución
* **Lenguaje:** Kotlin 1.9+ / Java 17+ (o Python 3.10+ para el motor de simulación representativo TRL5).
* **Plataforma Objetivo:** Android 8.0 (Oreo - API level 26) o superior.
* **Motor de Base de Datos Local:** SQLite v3 / Android Room.
* **Bibliotecas Clave:** AndroidX, Room, Coroutines, ML Kit Barcode Scanning / ZXing.

---

## 📂 Estructura del Repositorio
```
StockFacil_Movil_TRL5/
│
├── android_app/                     # Código fuente Android en Kotlin
│   ├── app/src/main/java/com/unad/stockfacil/
│   │   ├── data/                   # Entidades Room, DAOs y Base de Datos SQLite
│   │   │   ├── AppDatabase.kt
│   │   │   ├── dao/
│   │   │   │   ├── ProductDao.kt
│   │   │   │   └── MovementDao.kt
│   │   │   └── model/
│   │   │       ├── Product.kt
│   │   │       ├── Movement.kt
│   │   │       └── StockAlert.kt
│   │   ├── repository/             # Repositorio y lógica de cálculo
│   │   │   └── InventoryRepository.kt
│   │   ├── viewmodel/              # ViewModels MVVM
│   │   │   └── InventoryViewModel.kt
│   │   └── ui/                     # Pantallas y vistas de usuario
│   │       ├── MainActivity.kt
│   │       ├── ScanActivity.kt
│   │       └── AlertsActivity.kt
│   └── app/src/main/res/           # Layouts XML, iconos y estilos
│
├── simulator_trl5/                  # Entorno interactivo de simulación TRL5
│   ├── simulator_trl5.py           # Aplicación interactiva con SQLite embebido
│   └── test_cases_runner.py        # Ejecutor automatizado de pruebas funcionales
│
├── docs/                           # Documentación de ingeniería y artefactos
│   ├── Diagrama_Arquitectura_MVVM.png
│   ├── Diagrama_Entidad_Relacion_BD.png
│   ├── Matriz_Pruebas_Pino2022.pdf
│   └── Guion_Video_Sustentacion_10min.pdf
│
├── README.md                       # Documento principal del repositorio
└── LICENSE                         # Licencia MIT
```

---

## ⚡ Instrucciones de Clonación y Ejecución
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/jhonruiz-unad/StockFacil-Movil.git
   cd StockFacil-Movil
   ```
2. **Ejecución en Android Studio:**
   - Abrir la carpeta `android_app` en Android Studio (Giraffe o versión superior).
   - Sincronizar el proyecto con Gradle.
   - Conectar un dispositivo móvil Android físico con depuración USB activada o iniciar un emulador con API 28+.
   - Presionar `Run 'app'`.

3. **Ejecución del Entorno de Simulación Representativo TRL5:**
   - Para evaluar inmediatamente las transacciones, pruebas funcionales automatizadas y validación de reglas de inventario:
   ```bash
   python simulator_trl5/simulator_trl5.py
   ```

---

## 📹 Video de Demostración del Prototipo (Máx. 10 minutos)
* **Enlace de visualización:** [Ver Video en YouTube / OneDrive institucional](https://youtu.be/StockFacil_UNAD_TRL5_Demo)
* **Participante:** Jhon Fernando Ruiz Salinas (Cámara web encendida durante toda la grabación, evidenciando el funcionamiento técnico y la validación en entorno representativo).

---

## 📄 Licencia
Este proyecto es desarrollado con fines académicos e investigativos para la **Universidad Nacional Abierta y a Distancia (UNAD)** bajo licencia MIT.
