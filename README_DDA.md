# Asistente Virtual - Consulta de Documentos de Arquitectura (DDA)

Chatbot para desarrolladores y arquitectos que consultan documentación técnica de arquitectura de software usando Amazon Bedrock Knowledge Base.

## Rama: testing-dda-architecture

Esta rama está optimizada para consultas sobre **Documentos de Diseño de Arquitectura (DDA)** en lugar de productos comerciales.

## Diferencias con la Rama Principal

### Tipos de Consultas Soportadas

1. **Componentes**: "¿Qué hace el Order Service?", "¿Qué tecnología usa Payment Service?"
2. **Decisiones Arquitectónicas**: "¿Por qué eligieron microservicios?", "¿Por qué Kafka en lugar de SQS?"
3. **Patrones**: "¿Qué patrones de diseño usan?", "¿Cómo implementan el Circuit Breaker?"
4. **Tecnologías**: "¿Qué base de datos usan?", "¿Qué stack tecnológico tienen?"
5. **Integraciones**: "¿Cómo se integran con Stripe?", "¿Qué protocolo usan entre servicios?"
6. **Requisitos No Funcionales**: "¿Cuál es el SLA?", "¿Cómo manejan la escalabilidad?"

### Archivos Modificados

- **config.py**: Prompts adaptados para consultas arquitectónicas
- **query_handler_dda.py**: Clasificador específico para preguntas técnicas de arquitectura
- **DDA_TESTING_SAMPLE.txt**: Documento de ejemplo con arquitectura de e-commerce

### Archivos Sin Cambios

- **app.py**: Backend Flask (sin cambios)
- **index.html**: Frontend (sin cambios)
- **script.js**: Lógica del chat (sin cambios)
- **style.css**: Estilos (sin cambios)

## Configuración

### 1. Variables de Entorno

Usa el mismo archivo `.env`:

```bash
AWS_ACCESS_KEY_ID=tu_access_key_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_key_aqui
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
KNOWLEDGE_BASE_ID=tu_knowledge_base_id_dda_aqui
```

**IMPORTANTE**: Crea un Knowledge Base separado para documentos DDA en AWS Bedrock.

### 2. Subir Documentos DDA a S3

```bash
# Sube DDA_TESTING_SAMPLE.txt o tus propios documentos DDA
aws s3 cp DDA_TESTING_SAMPLE.txt s3://tu-bucket-dda/
```

### 3. Sincronizar Knowledge Base

En AWS Console → Bedrock → Knowledge Base → Sync

### 4. Ejecutar

```bash
# Backend
python app.py

# Frontend
python -m http.server 8000
```

## Ejemplos de Consultas

### Componentes
```
Usuario: ¿Qué hace el Order Service?
Bot: El Order Service es responsable de la gestión del ciclo de vida completo de pedidos...
```

### Decisiones
```
Usuario: ¿Por qué eligieron Kafka en lugar de SQS?
Bot: La decisión de usar Apache Kafka se basó en...
```

### Patrones
```
Usuario: ¿Qué patrones de diseño implementan?
Bot: El sistema implementa varios patrones:
- Saga Pattern para transacciones distribuidas
- Circuit Breaker para resiliencia
- Event Sourcing para auditoría...
```

### Tecnologías
```
Usuario: ¿Qué base de datos usan?
Bot: El sistema utiliza PostgreSQL 15 como base de datos principal...
```

## Optimizaciones para DDA

### Query Handler Especializado

El `query_handler_dda.py` clasifica consultas en:
- **component**: Preguntas sobre servicios/módulos específicos
- **decision**: Preguntas sobre decisiones arquitectónicas
- **pattern**: Preguntas sobre patrones de diseño
- **tech**: Preguntas sobre tecnologías
- **integration**: Preguntas sobre integraciones
- **requirement**: Preguntas sobre requisitos no funcionales

### Prompts Optimizados

Los prompts están diseñados para:
- Extraer información técnica precisa
- Explicar el "por qué" de las decisiones
- Citar secciones específicas del documento
- Usar terminología técnica apropiada
- Estructurar respuestas con formato claro

## Costos

Mismos costos que la rama principal:
- ~$0.0002 USD por consulta
- ~$6 USD/mes para 1000 consultas/día
- Knowledge Base storage: ~$0.05/mes

## Casos de Uso

- Onboarding de nuevos desarrolladores
- Consultas rápidas durante desarrollo
- Revisión de decisiones arquitectónicas
- Documentación de integraciones
- Auditoría de tecnologías utilizadas
- Preparación de presentaciones técnicas

## Volver a la Rama Principal

```bash
git checkout main
```

## Estructura de Documentos DDA Recomendada

Para mejores resultados, estructura tus documentos DDA con secciones claras:

```
1. RESUMEN EJECUTIVO
2. DECISIONES ARQUITECTÓNICAS
   - Contexto
   - Alternativas
   - Justificación
   - Trade-offs
3. COMPONENTES DEL SISTEMA
   - Responsabilidad
   - Tecnología
   - Dependencias
4. PATRONES DE DISEÑO
5. REQUISITOS NO FUNCIONALES
6. INTEGRACIONES EXTERNAS
7. STACK TECNOLÓGICO
```

## Notas

- Esta rama NO valida precios (no aplica para arquitectura)
- Los prompts son más técnicos y detallados
- El clasificador detecta términos arquitectónicos específicos
- Ideal para equipos de desarrollo que necesitan consultar documentación técnica rápidamente
