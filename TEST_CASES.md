# CASOS DE PRUEBA - Chatbot de Productos

## 1. PREGUNTAS DE PRECIO ESPECÍFICO
✅ "cuanto cuesta el iphone 14 pro?"
✅ "precio del samsung galaxy a54"
✅ "cuál es el valor del xiaomi redmi note 13 pro?"

**Respuesta esperada**: Precio exacto del producto específico

---

## 2. PREGUNTAS DE COMPARACIÓN
❓ "cuál es más barato, iphone 13 o samsung a54?"
❓ "diferencia de precio entre iphone 14 pro y iphone 15 pro max"
❓ "compara el galaxy s24 ultra vs iphone 15 pro max"

**Respuesta esperada**: Comparación clara con precios de ambos productos

---

## 3. BÚSQUEDA DE SUPERLATIVOS (MÁS/MENOS)
❌ "cuál es el teléfono más barato?" → Debe responder: Xiaomi Redmi A3 ($79) o Nokia 225 ($39)
❓ "cuál tiene la mejor cámara?"
❓ "qué teléfono tiene mayor batería?"
❓ "el más caro que tienes"

**Respuesta esperada**: Producto que cumple el criterio de TODOS los disponibles

---

## 4. ESPECIFICACIONES TÉCNICAS
✅ "cuánta ram tiene el iphone 14 pro?"
✅ "cuánto dura la batería del iphone 14 pro?"
❓ "qué procesador usa el samsung galaxy s24 ultra?"
❓ "cuántos megapíxeles tiene la cámara del xiaomi redmi note 13 pro?"

**Respuesta esperada**: Especificación exacta del producto

---

## 5. RECOMENDACIONES POR USO
❓ "qué teléfono me recomiendas para gaming?"
❓ "cuál es mejor para fotografía?"
❓ "necesito un teléfono con buena batería, qué me sugieres?"
❓ "quiero algo económico pero bueno"

**Respuesta esperada**: 2-3 opciones con justificación y precios

---

## 6. ACCESORIOS
❓ "tienen fundas para iphone 15 pro?"
❓ "cuánto cuesta un cargador rápido?"
❓ "qué protectores de pantalla tienen?"
❓ "audífonos bluetooth precio"

**Respuesta esperada**: Accesorios disponibles con precios

---

## 7. DISPONIBILIDAD Y COLORES
❓ "qué colores tiene el iphone 14 pro?"
❓ "tienen el samsung galaxy a54 en stock?"
❓ "qué modelos de xiaomi tienen?"

**Respuesta esperada**: Información de disponibilidad/colores

---

## 8. RANGOS DE PRECIO
❓ "qué teléfonos tienen entre 200 y 400 dólares?"
❓ "opciones de menos de 300 dólares"
❓ "smartphones gama alta disponibles"

**Respuesta esperada**: Lista de productos en ese rango con precios

---

## 9. MARCAS ESPECÍFICAS
❓ "qué iphones tienen disponibles?"
❓ "modelos de samsung"
❓ "opciones de xiaomi"

**Respuesta esperada**: Lista de productos de esa marca con precios

---

## 10. PROMOCIONES Y OFERTAS
❓ "qué ofertas tienen?"
❓ "hay descuentos en iphones?"
❓ "cuál es el descuento del iphone 14 pro?"

**Respuesta esperada**: Información de promociones y descuentos

---

## PRIORIDAD DE IMPLEMENTACIÓN:

### ✅ FUNCIONANDO:
1. Precio específico
2. Especificaciones básicas

### 🔧 MEJORAR:
3. Superlativos (más barato, mejor, etc.)
4. Comparaciones
5. Recomendaciones

### 📋 PENDIENTE:
6. Accesorios
7. Disponibilidad/colores
8. Rangos de precio
9. Filtros por marca
10. Promociones

---

## COMANDOS DE PRUEBA RÁPIDA:

```bash
# Precio específico
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message":"cuanto cuesta el iphone 14 pro?","use_knowledge_base":true}'

# Superlativo
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message":"cual es el telefono mas barato?","use_knowledge_base":true}'

# Comparación
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message":"cual es mas barato, iphone 13 o samsung a54?","use_knowledge_base":true}'

# Recomendación
curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -d '{"message":"que telefono me recomiendas para gaming?","use_knowledge_base":true}'
```
