from fastapi import APIRouter, Query
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/bot/{bot_id}")
async def get_bot_analytics(
    bot_id: str,
    days: int = Query(default=7, ge=1, le=365, description="Número de días a analizar")
):
    """
    Obtiene estadísticas y métricas de un bot específico.
    """
    service = AnalyticsService()
    stats = service.get_bot_stats(bot_id=bot_id, days=days)

    return {"stats": stats}


@router.get("/global")
async def get_global_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Número de días a analizar")
):
    """
    Obtiene estadísticas globales de todos los bots.
    """
    service = AnalyticsService()
    stats = service.get_global_stats(days=days)

    return {"stats": stats}


@router.get("/popular-questions")
async def get_popular_questions(
    bot_id: str | None = Query(default=None, description="Filtrar por bot_id"),
    limit: int = Query(default=10, ge=1, le=50, description="Número de preguntas a retornar")
):
    """
    Obtiene las preguntas más frecuentes.
    """
    service = AnalyticsService()
    questions = service.get_popular_questions(bot_id=bot_id, limit=limit)

    return {
        "popular_questions": questions,
        "total": len(questions)
    }


@router.delete("/cleanup")
async def cleanup_old_analytics(
    days_to_keep: int = Query(default=90, ge=30, le=365, description="Días de datos a mantener")
):
    """
    Limpia datos de analytics antiguos para optimizar almacenamiento.
    """
    service = AnalyticsService()
    service.clear_old_data(days_to_keep=days_to_keep)

    return {
        "message": f"Datos anteriores a {days_to_keep} días eliminados correctamente"
    }


@router.get("/word-cloud")
async def get_word_cloud(
    bot_id: str | None = Query(default=None, description="Filtrar por bot_id"),
    days: int = Query(default=30, ge=1, le=365, description="Días a analizar"),
    limit: int = Query(default=50, ge=10, le=100, description="Número máximo de palabras")
):
    """
    Obtiene datos para generar nube de palabras basada en preguntas frecuentes.
    Retorna palabras clave con su frecuencia y peso normalizado.
    """
    service = AnalyticsService()
    word_cloud_data = service.get_word_cloud_data(bot_id=bot_id, days=days, limit=limit)

    return {
        "word_cloud": word_cloud_data,
        "total_words": len(word_cloud_data),
        "period_days": days,
        "bot_id": bot_id
    }


@router.get("/question-topics")
async def get_question_topics(
    bot_id: str | None = Query(default=None, description="Filtrar por bot_id"),
    days: int = Query(default=30, ge=1, le=365, description="Días a analizar")
):
    """
    Analiza los temas principales en las preguntas.
    Categoriza palabras por frecuencia: muy frecuente, frecuente, ocasional.
    """
    service = AnalyticsService()
    topics = service.get_question_topics(bot_id=bot_id, days=days)

    return {
        "topics": topics,
        "period_days": days,
        "bot_id": bot_id
    }


@router.get("/document-usage/{bot_id}")
async def get_document_usage(
    bot_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Días a analizar")
):
    """
    Obtiene estadísticas de uso de documentos para un bot específico.
    Muestra qué tan efectivos son los documentos en responder consultas.
    """
    service = AnalyticsService()
    usage_stats = service.get_document_usage_stats(bot_id=bot_id, days=days)

    return {
        "document_usage": usage_stats,
        "period_days": days
    }
