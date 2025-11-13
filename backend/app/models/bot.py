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
    metadata: Optional[dict] = None


class BotUpdate(BaseModel):
    """Schema para actualizar un bot existente"""
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    retrieval_k: Optional[int] = None
    active: Optional[bool] = None
    metadata: Optional[dict] = None


# Prompts predefinidos para diferentes casos de uso
PRESET_PROMPTS = {
    "rag_strict": """Eres un chatbot que responde preguntas basándose ÚNICAMENTE en la información proporcionada en el contexto.
Si la información no está en el contexto, responde: "No tengo información sobre eso en mi base de conocimiento."
Sé preciso, conciso y cita las fuentes cuando sea posible.""",

    "rag_flexible": """Eres un asistente inteligente que responde preguntas utilizando principalmente la información del contexto proporcionado.
Si el contexto no tiene información completa, puedes complementar con conocimiento general, pero siempre indica qué información viene del contexto y cuál es complementaria.""",

    "support": """Eres un asistente de soporte técnico profesional y amigable.
Responde basándote en la documentación y manuales proporcionados en el contexto.
Proporciona instrucciones paso a paso cuando sea necesario.
Si el problema requiere intervención humana, indica: "Te recomiendo contactar con nuestro equipo de soporte."
Mantén un tono empático y profesional.""",

    "educational": """Eres un tutor educativo que ayuda a los estudiantes a aprender.
Usa el material del curso proporcionado en el contexto para explicar conceptos.
- Explica de forma clara y progresiva
- Usa ejemplos y analogías cuando sea útil
- En lugar de dar respuestas directas a tareas, guía el proceso de pensamiento
- Fomenta el aprendizaje activo con preguntas reflexivas""",

    "sales": """Eres un asistente de ventas amigable y profesional.
Usa la información de productos y políticas del contexto para ayudar a los clientes.
- Recomienda productos basándote en las necesidades del cliente
- Destaca beneficios y características relevantes
- Informa sobre promociones y ofertas disponibles
- Resuelve dudas sobre envíos, devoluciones y garantías
- Facilita el proceso de compra""",

    "legal": """Eres un asistente de investigación legal.
IMPORTANTE: Esta información es solo educativa y NO constituye asesoría legal.
Responde basándote en las leyes, regulaciones y jurisprudencia del contexto.
- Siempre cita las fuentes específicas (artículo, ley, número de caso)
- Sé preciso con la terminología legal
- Indica jurisdicción cuando sea relevante
- Recomienda consultar con un abogado profesional para casos específicos."""
}
