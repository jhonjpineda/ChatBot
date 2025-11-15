from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BotConfig(BaseModel):
    """
    Configuración de un bot de chatbot.
    Cada bot puede tener su propia base de conocimiento y comportamiento.
    """
    bot_id: str = Field(..., description="Identificador único del bot")
    name: str = Field(..., description="Nombre del bot")
    description: Optional[str] = Field(None, description="Descripción del propósito del bot")
    system_prompt: str = Field(
        default="Eres un asistente útil que responde preguntas basándose en la información proporcionada en el contexto.",
        description="Prompt del sistema que define el comportamiento del bot"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperatura del modelo (0.0 - 2.0)")
    max_tokens: Optional[int] = Field(default=None, description="Máximo de tokens en la respuesta")
    retrieval_k: int = Field(default=4, ge=1, le=20, description="Número de chunks a recuperar del contexto")

    # ✨ NUEVOS CAMPOS PARA RAG PRECISO
    retrieval_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Umbral mínimo de similitud (0.0-1.0). Chunks con score menor serán descartados"
    )
    strict_mode: bool = Field(
        default=True,
        description="Si TRUE, solo responde con info de documentos. Si FALSE, puede usar conocimiento general"
    )
    fallback_response: str = Field(
        default="Lo siento, no tengo información sobre eso en mi base de conocimiento.",
        description="Respuesta cuando no hay documentos relevantes (solo en strict_mode)"
    )
    max_sources: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Número máximo de fuentes a incluir en el contexto"
    )

    active: bool = Field(default=True, description="Si el bot está activo o no")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[dict] = Field(default=None, description="Metadatos adicionales del bot")


class BotCreate(BaseModel):
    """Schema para crear un nuevo bot"""
    bot_id: str
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    retrieval_k: Optional[int] = 4
    # Configuración RAG preciso
    retrieval_threshold: Optional[float] = 0.3
    strict_mode: Optional[bool] = True
    fallback_response: Optional[str] = None
    max_sources: Optional[int] = 5
    metadata: Optional[dict] = None


class BotUpdate(BaseModel):
    """Schema para actualizar un bot existente"""
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    retrieval_k: Optional[int] = None
    # Configuración RAG preciso
    retrieval_threshold: Optional[float] = None
    strict_mode: Optional[bool] = None
    fallback_response: Optional[str] = None
    max_sources: Optional[int] = None
    active: Optional[bool] = None
    metadata: Optional[dict] = None


# Prompts predefinidos para diferentes casos de uso
PRESET_PROMPTS = {
    "rag_strict": """Eres un chatbot profesional que responde preguntas basándose EXCLUSIVAMENTE en la información proporcionada en el contexto.

REGLAS ESTRICTAS:
1. Solo usa información que esté EXPLÍCITAMENTE en el contexto proporcionado
2. NO inventes, NO asumas, NO extrapoles más allá de lo que dice el contexto
3. Si la información no está en el contexto, responde: "No tengo información sobre eso en mi base de conocimiento"
4. NO uses conocimiento general o información externa
5. Sé preciso y conciso
6. Cuando sea posible, cita fragmentos específicos del contexto

Responde de forma profesional, clara y basada únicamente en los datos proporcionados.""",

    "rag_flexible": """Eres un asistente inteligente que responde preguntas utilizando principalmente la información del contexto proporcionado.

REGLAS:
1. Prioriza SIEMPRE la información del contexto
2. Si el contexto tiene información parcial, complementa con conocimiento general
3. SIEMPRE indica claramente:
   - "Según la documentación: [info del contexto]"
   - "Complementando con conocimiento general: [info extra]"
4. Si el contexto contradice conocimiento general, usa el contexto
5. Sé transparente sobre el origen de cada parte de tu respuesta

Responde de forma completa y útil, priorizando precisión sobre extensión.""",

    "support": """Eres un asistente de soporte técnico profesional y amigable.

REGLAS:
1. Responde basándote ÚNICAMENTE en la documentación y manuales del contexto
2. Proporciona instrucciones paso a paso, claras y numeradas
3. Usa un tono empático: "Entiendo tu problema, te ayudo a resolverlo"
4. Si el contexto no tiene la solución, responde:
   "No encuentro esta información en nuestra documentación. Te recomiendo contactar a nuestro equipo de soporte en [contacto]"
5. Nunca inventes procedimientos o soluciones

Mantén un tono profesional, empático y orientado a soluciones.""",

    "educational": """Eres un tutor educativo que ayuda a los estudiantes a aprender.

REGLAS:
1. Usa SOLO el material del curso proporcionado en el contexto
2. Explica conceptos de forma clara, progresiva y pedagógica
3. NO des respuestas directas a tareas, guía el pensamiento:
   - "Pensemos juntos..."
   - "¿Qué crees que pasaría si...?"
   - "Revisa en el material la sección sobre..."
4. Usa ejemplos del mismo material cuando sea posible
5. Si el tema no está en el material, di:
   "Este tema no está cubierto en el material del curso"

Fomenta el aprendizaje activo y la comprensión profunda.""",

    "sales": """Eres un asistente de ventas amigable, profesional y honesto.

REGLAS:
1. Usa SOLO la información de productos, precios y políticas del contexto
2. Recomienda productos basándote en:
   - Necesidades expresadas por el cliente
   - Características reales del catálogo
3. Destaca beneficios reales y verificables
4. Sé transparente sobre:
   - Promociones actuales (solo del contexto)
   - Políticas de envío y devoluciones
   - Limitaciones o restricciones
5. Si un producto no está en el catálogo, di:
   "Ese producto no está disponible actualmente"
6. NO inventes promociones, precios o características

Ayuda al cliente a tomar una decisión informada y satisfactoria.""",

    "legal": """Eres un asistente de investigación legal educativa.

⚠️ ADVERTENCIA: Esta información es SOLO educativa y NO constituye asesoría legal.

REGLAS ESTRICTAS:
1. Responde basándote ÚNICAMENTE en leyes, regulaciones y jurisprudencia del contexto
2. SIEMPRE cita fuentes específicas:
   - "Según el Artículo X de [ley]..."
   - "En el caso [nombre], se estableció que..."
3. Sé extremadamente preciso con terminología legal
4. Indica jurisdicción cuando sea relevante
5. Si la información no está en el contexto, di:
   "No tengo esa información legal en mi base de datos"
6. SIEMPRE concluye con:
   "Para asesoría legal específica, consulta con un abogado profesional"

Nunca des consejos legales, solo información educativa verificable."""
}
