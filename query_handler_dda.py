"""
Sistema inteligente para clasificar y manejar consultas sobre documentos de arquitectura (DDA)
"""
import re
from typing import Dict, List

class QueryHandler:
    """Clasifica y optimiza consultas sobre documentación de arquitectura"""
    
    # Patrones de preguntas arquitectónicas
    COMPONENT_KEYWORDS = ['componente', 'servicio', 'módulo', 'microservicio', 'api', 'base de datos', 'sistema']
    DECISION_KEYWORDS = ['decisión', 'por qué', 'razón', 'justificación', 'alternativa', 'elegir', 'seleccionar']
    PATTERN_KEYWORDS = ['patrón', 'arquitectura', 'diseño', 'estructura', 'organización']
    TECH_KEYWORDS = ['tecnología', 'framework', 'librería', 'herramienta', 'lenguaje', 'stack']
    INTEGRATION_KEYWORDS = ['integración', 'comunicación', 'protocolo', 'api', 'endpoint', 'flujo']
    REQUIREMENT_KEYWORDS = ['requisito', 'escalabilidad', 'performance', 'seguridad', 'disponibilidad', 'sla']
    
    @staticmethod
    def classify_query(query: str) -> Dict:
        """Clasifica el tipo de consulta arquitectónica"""
        query_lower = query.lower()
        
        classification = {
            'type': 'general',  # general, component, decision, pattern, tech, integration, requirement
            'needs_many_results': False,
            'needs_context': True,
            'category': None,
            'keywords': [],
            'is_decision_query': False,
            'is_technical_query': False
        }
        
        # Detectar tipo de consulta
        if any(kw in query_lower for kw in QueryHandler.COMPONENT_KEYWORDS):
            classification['type'] = 'component'
            classification['needs_many_results'] = False
            
        if any(kw in query_lower for kw in QueryHandler.DECISION_KEYWORDS):
            classification['type'] = 'decision'
            classification['needs_many_results'] = True
            classification['is_decision_query'] = True
            
        if any(kw in query_lower for kw in QueryHandler.PATTERN_KEYWORDS):
            classification['type'] = 'pattern'
            classification['needs_many_results'] = True
            
        if any(kw in query_lower for kw in QueryHandler.TECH_KEYWORDS):
            classification['type'] = 'tech'
            classification['is_technical_query'] = True
            
        if any(kw in query_lower for kw in QueryHandler.INTEGRATION_KEYWORDS):
            classification['type'] = 'integration'
            classification['needs_many_results'] = True
            
        if any(kw in query_lower for kw in QueryHandler.REQUIREMENT_KEYWORDS):
            classification['type'] = 'requirement'
            classification['needs_many_results'] = True
        
        # Extraer palabras clave técnicas
        keywords = []
        tech_words = ['aws', 'azure', 'gcp', 'kubernetes', 'docker', 'lambda', 'dynamodb', 
                     'postgres', 'redis', 'kafka', 'rest', 'graphql', 'microservicio',
                     'monolito', 'serverless', 'event-driven', 'cqrs', 'saga']
        
        for word in query_lower.split():
            if len(word) > 3 and word in tech_words:
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
            config['numberOfResults'] = 20
        elif classification['is_decision_query']:
            config['numberOfResults'] = 15
        
        return config
    
    @staticmethod
    def enhance_prompt(query: str, classification: Dict, context: str) -> str:
        """Genera prompt optimizado según tipo de consulta arquitectónica"""
        
        base_instructions = """Eres un asistente experto en arquitectura de software. Tu trabajo es ayudar a desarrolladores y arquitectos con información precisa de los documentos DDA."""
        
        if classification['type'] == 'component':
            return f"""{base_instructions}

DOCUMENTACIÓN DDA:
{context}

PREGUNTA: {query}

INSTRUCCIONES PARA COMPONENTES:
1. Identifica el componente específico mencionado
2. Describe su responsabilidad principal
3. Lista las tecnologías utilizadas
4. Menciona dependencias con otros componentes
5. Incluye consideraciones de escalabilidad o seguridad si están documentadas

RESPUESTA:"""

        elif classification['type'] == 'decision':
            return f"""{base_instructions}

DOCUMENTACIÓN DDA:
{context}

PREGUNTA: {query}

INSTRUCCIONES PARA DECISIONES ARQUITECTÓNICAS:
1. Identifica la decisión específica
2. Explica el CONTEXTO que llevó a esa decisión
3. Lista las ALTERNATIVAS consideradas
4. Detalla la JUSTIFICACIÓN de la elección
5. Menciona TRADE-OFFS o compromisos aceptados
6. Cita la sección del documento si es posible

RESPUESTA:"""

        elif classification['type'] == 'pattern':
            return f"""{base_instructions}

DOCUMENTACIÓN DDA:
{context}

PREGUNTA: {query}

INSTRUCCIONES PARA PATRONES:
1. Identifica el patrón arquitectónico mencionado
2. Explica cómo se aplica en el sistema
3. Describe los beneficios que aporta
4. Menciona componentes que implementan el patrón
5. Incluye diagramas o referencias si están en el documento

RESPUESTA:"""

        elif classification['type'] == 'integration':
            return f"""{base_instructions}

DOCUMENTACIÓN DDA:
{context}

PREGUNTA: {query}

INSTRUCCIONES PARA INTEGRACIONES:
1. Identifica los sistemas o componentes que se integran
2. Describe el PROTOCOLO de comunicación (REST, gRPC, eventos, etc.)
3. Especifica el FORMATO de datos (JSON, Protobuf, etc.)
4. Explica el FLUJO de la integración
5. Menciona manejo de errores o reintentos si está documentado

RESPUESTA:"""

        elif classification['type'] == 'requirement':
            return f"""{base_instructions}

DOCUMENTACIÓN DDA:
{context}

PREGUNTA: {query}

INSTRUCCIONES PARA REQUISITOS NO FUNCIONALES:
1. Identifica el requisito específico (escalabilidad, seguridad, performance, etc.)
2. Describe las MÉTRICAS objetivo (ej: 1000 req/s, 99.9% uptime)
3. Explica las ESTRATEGIAS implementadas para cumplirlo
4. Menciona TECNOLOGÍAS específicas que lo soportan
5. Incluye consideraciones de monitoreo si están documentadas

RESPUESTA:"""

        else:
            # Consulta general
            return f"""{base_instructions}

DOCUMENTACIÓN DDA:
{context}

PREGUNTA: {query}

INSTRUCCIONES:
1. Busca la información específica solicitada
2. Responde con datos exactos del documento
3. Usa terminología técnica apropiada
4. Estructura la respuesta claramente
5. Si no tienes la información, dilo claramente

RESPUESTA:"""
