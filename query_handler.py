"""
Sistema inteligente para clasificar y manejar diferentes tipos de consultas
"""
import re
from typing import Dict, List, Tuple

class QueryHandler:
    """Clasifica y optimiza consultas para mejor recuperación de Knowledge Base"""
    
    COMPARISON_KEYWORDS = ['comparar', 'diferencia', 'vs', 'versus', 'mejor', 'peor', 'mayor', 'menor', 'más', 'menos']
    DETAIL_KEYWORDS = ['detalle', 'explica', 'describe', 'cómo funciona', 'qué es', 'para qué']
    RECOMMENDATION_KEYWORDS = ['recomienda', 'recomendación', 'sugerir', 'mejor opción', 'cuál elegir', 'qué me conviene']
    LIST_KEYWORDS = ['lista', 'todos', 'cuáles', 'enumera', 'muestra', 'disponibles']
    
    @staticmethod
    def classify_query(query: str) -> Dict:
        """Clasifica el tipo de consulta y extrae información relevante"""
        query_lower = query.lower()
        
        classification = {
            'type': 'specific',
            'needs_many_results': False,
            'keywords': [],
            'is_price_query': False,
            'is_documentation_query': False
        }
        
        if any(kw in query_lower for kw in QueryHandler.COMPARISON_KEYWORDS):
            classification['type'] = 'comparison'
            classification['needs_many_results'] = True
            
        elif any(kw in query_lower for kw in QueryHandler.LIST_KEYWORDS):
            classification['type'] = 'list'
            classification['needs_many_results'] = True
            
        elif any(kw in query_lower for kw in QueryHandler.RECOMMENDATION_KEYWORDS):
            classification['type'] = 'recommendation'
            classification['needs_many_results'] = True
            
        elif any(kw in query_lower for kw in QueryHandler.DETAIL_KEYWORDS):
            classification['type'] = 'detail'

        keywords = [w for w in query_lower.split() if len(w) > 3]
        classification['keywords'] = keywords
        
        return classification
    
    @staticmethod
    def get_retrieval_config(classification: Dict) -> Dict:
        """Genera configuración de recuperación basada en clasificación"""
        config = {'numberOfResults': 10}
        
        if classification['needs_many_results']:
            config['numberOfResults'] = 25
        
        return config
    
    @staticmethod
    def enhance_prompt(query: str, classification: Dict, context: str) -> str:
        """Genera prompt optimizado según tipo de consulta"""
        
        base = """Eres un asistente virtual. Responde basándote ÚNICAMENTE en el contexto proporcionado.
Si no encuentras la información, dilo claramente. NUNCA inventes datos."""

        if classification['type'] == 'comparison':
            instructions = """INSTRUCCIONES:
1. Identifica los elementos que el usuario quiere comparar
2. Presenta una comparación clara y objetiva con datos del contexto
3. Usa datos exactos"""

        elif classification['type'] == 'recommendation':
            instructions = """INSTRUCCIONES:
1. Identifica las necesidades del usuario
2. Busca opciones relevantes en el contexto
3. Recomienda con justificación basada en los datos"""

        elif classification['type'] == 'list':
            instructions = """INSTRUCCIONES:
1. Busca todos los elementos relevantes en el contexto
2. Presenta una lista organizada
3. Incluye detalles clave de cada elemento"""

        else:
            instructions = """INSTRUCCIONES:
1. Busca la información específica solicitada
2. Responde con datos exactos del contexto
3. Sé conciso y claro"""

        return f"""{base}

CONTEXTO:
{context}

PREGUNTA: {query}

{instructions}

RESPUESTA:"""
