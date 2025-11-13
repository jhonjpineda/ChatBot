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
