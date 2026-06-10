# 📘 Reporte Técnico — Modelo Entidad–Relación (ERD)

Este reporte documenta el diseño del modelo de datos basado en los diagramas proporcionados. Incluye la definición de entidades, campos, relaciones y restricciones necesarias para implementar un sistema de inventario con entradas, salidas y ventas de productos.

---

# 🧩 1. Entidades y Campos

A continuación se describen las tablas identificadas en el modelo.

---

## 🟦 Tabla: `product`

Representa los productos gestionados en el inventario.

| Campo   | Tipo           | Restricciones                         |
|---------|----------------|----------------------------------------|
| idProd  | SERIAL         | PRIMARY KEY                            |
| cant    | INTEGER        | NOT NULL, CHECK (cant ≥ 0)             |
| cost    | NUMERIC(10,2)  | NOT NULL, CHECK (cost ≥ 0)             |
| price   | NUMERIC(10,2)  | NOT NULL, CHECK (price ≥ 0)            |

---

## 🟩 Tabla: `Entry`

Registra las entradas de productos al inventario.

| Campo     | Tipo           | Restricciones                                      |
|-----------|----------------|---------------------------------------------------|
| idEntry   | SERIAL         | PRIMARY KEY                                       |
| idProd    | INTEGER        | NOT NULL, FOREIGN KEY → product(idProd)           |
| cant      | INTEGER        | NOT NULL, CHECK (cant > 0)                        |
| date      | DATE           | NOT NULL                                          |
| attribute | TEXT           | NULL                                              |

---

## 🟥 Tabla: `Out`

Registra las salidas de productos del inventario.

| Campo       | Tipo           | Restricciones                                      |
|-------------|----------------|---------------------------------------------------|
| idOut       | SERIAL         | PRIMARY KEY                                       |
| idProd      | INTEGER        | NOT NULL, FOREIGN KEY → product(idProd)           |
| cant        | INTEGER        | NOT NULL, CHECK (cant > 0)                        |
| destination | TEXT           | NOT NULL                                          |
| date        | DATE           | NOT NULL                                          |

---

## 🟨 Tabla: `Sell`

Registra las ventas realizadas.

| Campo    | Tipo           | Restricciones                         |
|----------|----------------|----------------------------------------|
| idSell   | SERIAL         | PRIMARY KEY                            |
| cant     | INTEGER        | NOT NULL, CHECK (cant > 0)             |
| revenue  | NUMERIC(10,2)  | NOT NULL, CHECK (revenue ≥ 0)          |
| date     | DATE           | NOT NULL                               |

---

## 🟪 Tabla intermedia: `prod_sell` (Relación N:M)

Relaciona productos con ventas.

| Campo   | Tipo     | Restricciones                                      |
|---------|----------|---------------------------------------------------|
| idProd  | INTEGER  | FOREIGN KEY → product(idProd)                     |
| idSell  | INTEGER  | FOREIGN KEY → sell(idSell)                        |
| cant    | INTEGER  | NOT NULL, CHECK (cant > 0)                        |
| PRIMARY KEY (idProd, idSell) | — | — |

---

# 🔗 2. Relaciones del Modelo

| Relación              | Tipo | Descripción                                                |
|-----------------------|------|------------------------------------------------------------|
| product 1:N Entry     | 1:N  | Un producto puede tener múltiples entradas.               |
| product 1:N Out       | 1:N  | Un producto puede tener múltiples salidas.                |
| product N:M Sell      | N:M  | Una venta puede incluir varios productos y viceversa.     |

---

# ⚙️ 3. Restricciones del Modelo

### ✔️ Integridad de entidad
- Todas las tablas poseen claves primarias (`PRIMARY KEY`).
- Los identificadores usan `SERIAL` para autoincremento.

### ✔️ Integridad referencial
- Las claves foráneas garantizan la relación entre movimientos y productos.
- Se recomienda `ON DELETE CASCADE` para mantener consistencia.

### ✔️ Integridad de dominio
- Las cantidades deben ser mayores que cero.
- Precios, costos y revenue no pueden ser negativos.

### ✔️ Integridad de negocio
- No se permiten movimientos con cantidad cero.
- Las ventas deben registrar ingresos válidos.

---

# 🧾 4. Documentación del Diseño

## 🎯 Objetivo del sistema
El sistema permite gestionar el ciclo completo de un producto dentro del inventario:

- Entrada al almacén  
- Salida por traslado  
- Venta al cliente  

Todo con trazabilidad completa y control de cantidades, costos y ganancias.

---

## 🧠 Modelo conceptual
- **Product** es la entidad central del sistema.
- **Entry** representa abastecimientos o compras.
- **Out** representa salidas o despachos.
- **Sell** representa ventas.
- **prod_sell** permite ventas con múltiples productos.

---

## 🧩 Modelo lógico
- Las entidades se transforman en tablas con claves primarias.
- Las relaciones 1:N se implementan mediante claves foráneas.
- La relación N:M se implementa mediante la tabla intermedia `prod_sell`.

---

# 📌 5. Conclusión

El modelo proporciona una estructura sólida para gestionar inventario, ventas y movimientos de productos, con integridad garantizada mediante restricciones bien definidas.

