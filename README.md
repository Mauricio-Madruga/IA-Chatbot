# Asistente Virtual - Consulta de Productos

Chatbot para clientes que consultan especificaciones y precios de productos usando Amazon Bedrock Knowledge Base.

## Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (copia `.env.example`):

```bash
AWS_ACCESS_KEY_ID=tu_access_key_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_key_aqui
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
KNOWLEDGE_BASE_ID=tu_knowledge_base_id_aqui
```

**IMPORTANTE:**

- Obtén tus credenciales AWS desde la consola de AWS IAM
- Asegúrate de que tu usuario IAM tenga permisos para Amazon Bedrock
- Para usar Knowledge Base, obtén el ID desde la consola de Bedrock → Knowledge bases
- Nunca subas el archivo `.env` a control de versiones

### 2. Instalación

```bash
pip install -r requirements.txt
```

### 3. Ejecutar Backend

```bash
python app.py
```

El servidor correrá en `http://localhost:5000`

### 4. Ejecutar Frontend

Abre `index.html` en tu navegador o usa un servidor local:

```bash
python -m http.server 8000
```

Luego visita `http://localhost:8000`

## Características

### Sistema Inteligente de Consultas

- **Clasificación automática**: Detecta el tipo de pregunta (precio, comparación, recomendación, etc.)
- **Recuperación optimizada**: Ajusta cantidad de chunks según tipo de consulta
- **Prompts especializados**: Genera instrucciones específicas para cada tipo de pregunta
- **Validación de precios**: Verifica que precios mencionados existan en el contexto
- **Re-ranking inteligente**: Prioriza chunks con información crítica (precios, specs)

### Tipos de Consultas Soportadas

1. **Precios específicos**: "cuanto cuesta el iPhone 14 Pro?"
2. **Comparaciones**: "cuál es más barato, iPhone 13 o Samsung A54?"
3. **Superlativos**: "cuál es el teléfono más barato?", "mejor cámara"
4. **Especificaciones**: "cuánta RAM tiene?", "duración de batería?"
5. **Recomendaciones**: "qué me recomiendas para gaming?"
6. **Accesorios**: "fundas para iPhone 15?", "cargadores rápidos?"

### Optimizado para Producción

- **Modelo fijo**: Claude 3 Haiku (más económico)
- **Knowledge Base siempre activa**: Consulta automática a tus PDFs en S3
- **Límite de tokens**: 1000 tokens máximo por respuesta (control de costos)
- **Interfaz simplificada**: Sin opciones innecesarias para el cliente
- **Mensaje de bienvenida**: Guía al usuario desde el inicio

### Costos Estimados

- ~$0.0002 USD por consulta
- ~$6 USD/mes para 1000 consultas/día
- Almacenamiento KB: ~$0.05/mes

## Estructura del Proyecto

```
IA-Chatbot/
├── app.py              # Backend Flask
├── index.html          # Frontend HTML
├── style.css           # Estilos
├── script.js           # Lógica del chat
├── requirements.txt    # Dependencias Python
├── .env.example        # Ejemplo de variables de entorno
└── README.md          # Este archivo
```
