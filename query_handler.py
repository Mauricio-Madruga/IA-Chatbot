"""
Sistema inteligente para clasificar y manejar diferentes tipos de consultas de clientes
"""
import re
from typing import Dict, List, Tuple

class QueryHandler:
    """Clasifica y optimiza consultas de clientes para mejor recuperación"""
    
    # Patrones de preguntas
    COMPARISON_KEYWORDS = ['más barato', 'más caro', 'mejor', 'peor', 'mayor', 'menor', 'comparar', 'diferencia', 'vs', 'versus']
    SUPERLATIVE_KEYWORDS = ['más barato', 'más económico', 'más caro', 'mejor', 'mayor batería', 'mejor cámara', 'más rápido']
    PRICE_KEYWORDS = ['precio', 'cuesta', 'cuanto', 'cuánto', 'vale', 'valor', 'costar']
    SPEC_KEYWORDS = ['ram', 'memoria', 'almacenamiento', 'procesador', 'cámara', 'batería', 'pantalla', 'duración']
    RECOMMENDATION_KEYWORDS = ['recomienda', 'recomendación', 'sugerir', 'mejor opción', 'qué comprar', 'cuál elegir']
    ACCESSORY_KEYWORDS = ['funda', 'mica', 'protector', 'cargador', 'audífonos', 'auriculares', 'cable', 'accesorio']
    
    @staticmethod
    def classify_query(query: str) -> Dict:
        """Clasifica el tipo de consulta y extrae información relevante"""
        query_lower = query.lower()
        
        classification = {
            'type': 'specific',  # specific, comparison, superlative, recommendation, accessory
            'needs_many_results': False,
            'needs_filtering': False,
            'category': None,
            'keywords': [],
            'is_price_query': False,
            'is_spec_query': False
        }
        
        # Detectar tipo de consulta
        if any(kw in query_lower for kw in QueryHandler.COMPARISON_KEYWORDS):
            classification['type'] = 'comparison'
            classification['needs_many_results'] = True
            
        if any(kw in query_lower for kw in QueryHandler.SUPERLATIVE_KEYWORDS):
            classification['type'] = 'superlative'
            classification['needs_many_results'] = True
            classification['needs_filtering'] = True
            
        if any(kw in query_lower for kw in QueryHandler.RECOMMENDATION_KEYWORDS):
            classification['type'] = 'recommendation'
            classification['needs_many_results'] = True
            
        if any(kw in query_lower for kw in QueryHandler.ACCESSORY_KEYWORDS):
            classification['type'] = 'accessory'
            classification['category'] = 'Accesorios'
            
        # Detectar si pregunta por precio o especificaciones
        classification['is_price_query'] = any(kw in query_lower for kw in QueryHandler.PRICE_KEYWORDS)
        classification['is_spec_query'] = any(kw in query_lower for kw in QueryHandler.SPEC_KEYWORDS)
        
        # Extraer palabras clave importantes (productos, marcas, modelos)
        keywords = []
        important_words = ['iphone', 'samsung', 'xiaomi', 'galaxy', 'redmi', 'motorola', 'nokia', 
                          'pro', 'max', 'ultra', 'lite', 'plus', 'note', 'gaming', 'fotografía']
        
        for word in query_lower.split():
            if len(word) > 3 and (word in important_words or word.isdigit()):
                keywords.append(word)
        
        classification['keywords'] = keywords
        
        return classification
    
    @staticmethod
    def get_retrieval_config(classification: Dict) -> Dict:
        """Genera configuración de recuperación basada en clasificación"""
        config = {
            'numberOfResults': 10,  # Default
            'filter': None
        }
        
        # Ajustar número de resultados según tipo de consulta
        if classification['needs_many_results']:
            config['numberOfResults'] = 30  # Reducido de 50 a 30 para balance costo/precisión
        elif classification['is_price_query']:
            config['numberOfResults'] = 15  # Reducido de 20 a 15
        
        # Agregar filtros si es necesario
        if classification['category']:
            config['filter'] = {'category': classification['category']}
        
        return config
    
    @staticmethod
    def enhance_prompt(query: str, classification: Dict, context: str) -> str:
        """Genera prompt optimizado según tipo de consulta"""
        
        base_instructions = """Eres un asistente de ventas experto. Tu trabajo es ayudar al cliente con información precisa."""
        
        if classification['type'] == 'superlative':
            return f"""{base_instructions}

INFORMACIÓN DE PRODUCTOS:
{context}

PREGUNTA DEL CLIENTE: {query}

INSTRUCCIONES ESPECIALES PARA BÚSQUEDA DE MÁXIMOS/MÍNIMOS:
1. Revisa TODOS los productos en la información proporcionada
2. Extrae el valor numérico relevante de CADA producto (precio, megapíxeles, mAh, etc.)
3. Compara TODOS los valores numéricamente
4. Identifica el producto con el valor MÁXIMO o MÍNIMO según la pregunta
5. Verifica que sea realmente el extremo de TODOS los productos listados
6. Responde con el producto correcto, su valor exacto, y menciona que revisaste todos

EJEMPLOS:
- "más barato" → Busca el PRECIO OFERTA más bajo de TODOS
- "mejor cámara" → Busca los MEGAPÍXELES más altos de TODOS (ej: 200MP > 50MP > 48MP)
- "mayor batería" → Busca los mAh más altos de TODOS (ej: 6000mAh > 5000mAh)

IMPORTANTE: Si encuentras múltiples productos con el mismo valor máximo/mínimo, menciónalos todos.

RESPUESTA:"""

        elif classification['type'] == 'comparison':
            return f"""{base_instructions}

INFORMACIÓN DE PRODUCTOS:
{context}

PREGUNTA DEL CLIENTE: {query}

INSTRUCCIONES PARA COMPARACIÓN:
1. Identifica los productos específicos que el cliente quiere comparar
2. Encuentra la información de CADA producto
3. Compara los aspectos relevantes (precio, especificaciones, características)
4. Presenta una comparación clara y objetiva
5. Usa números exactos del contexto

RESPUESTA:"""

        elif classification['type'] == 'recommendation':
            return f"""{base_instructions}

INFORMACIÓN DE PRODUCTOS:
{context}

PREGUNTA DEL CLIENTE: {query}

INSTRUCCIONES PARA RECOMENDACIÓN:
1. Identifica las necesidades del cliente (gaming, fotografía, presupuesto, etc.)
2. Busca productos que cumplan esas necesidades
3. Considera precio, especificaciones y uso recomendado
4. Recomienda 2-3 opciones con justificación
5. Menciona precios exactos

RESPUESTA:"""

        elif classification['is_price_query']:
            return f"""{base_instructions}

INFORMACIÓN DE PRODUCTOS:
{context}

PREGUNTA DEL CLIENTE: {query}

INSTRUCCIONES CRÍTICAS PARA PRECIOS:
1. Busca el producto EXACTO que menciona el cliente
2. Encuentra la línea "PRECIO OFERTA:" para ESE producto específico
3. Copia el precio EXACTAMENTE como aparece
4. Si hay "PRECIO NORMAL:" también, menciónalo
5. NUNCA inventes o adivines precios
6. Si no encuentras el producto exacto, di "No tengo información sobre ese producto"

RESPUESTA:"""

        else:
            # Consulta específica estándar
            return f"""{base_instructions}

INFORMACIÓN DE PRODUCTOS:
{context}

PREGUNTA DEL CLIENTE: {query}

INSTRUCCIONES:
1. Busca la información específica que el cliente solicita
2. Responde con datos exactos del contexto
3. Sé conciso y profesional
4. Si no tienes la información, dilo claramente

RESPUESTA:"""
