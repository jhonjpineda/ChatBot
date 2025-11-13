from fastapi import APIRouter, HTTPException, Query
from app.services.bot_service import BotService
from app.models.bot import BotCreate, BotUpdate

router = APIRouter()


@router.post("/")
async def create_bot(bot_data: BotCreate):
    """
    Crea un nuevo bot con su configuración personalizada.
    """
    service = BotService()

    try:
        bot = service.create_bot(bot_data)
        return {
            "message": "Bot creado correctamente",
            "bot": bot
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear bot: {str(e)}")


@router.get("/")
async def list_bots(
    active_only: bool = Query(default=False, description="Listar solo bots activos")
):
    """
    Lista todos los bots configurados.
    """
    service = BotService()
    bots = service.list_bots(active_only=active_only)

    return {
        "bots": bots,
        "total": len(bots)
    }


@router.get("/{bot_id}")
async def get_bot(bot_id: str):
    """
    Obtiene la configuración de un bot específico.
    """
    service = BotService()
    bot = service.get_bot(bot_id)

    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot no encontrado: {bot_id}")

    return {"bot": bot}


@router.put("/{bot_id}")
async def update_bot(bot_id: str, bot_data: BotUpdate):
    """
    Actualiza la configuración de un bot existente.
    """
    service = BotService()

    try:
        bot = service.update_bot(bot_id, bot_data)
        if not bot:
            raise HTTPException(status_code=404, detail=f"Bot no encontrado: {bot_id}")

        return {
            "message": "Bot actualizado correctamente",
            "bot": bot
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar bot: {str(e)}")


@router.delete("/{bot_id}")
async def delete_bot(bot_id: str):
    """
    Elimina un bot y toda su configuración.
    NOTA: No se puede eliminar el bot 'default'.
    """
    service = BotService()

    try:
        success = service.delete_bot(bot_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Bot no encontrado: {bot_id}")

        return {
            "message": "Bot eliminado correctamente",
            "bot_id": bot_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar bot: {str(e)}")


@router.get("/presets/prompts")
async def get_preset_prompts():
    """
    Obtiene todos los prompts predefinidos disponibles para usar en bots.
    """
    service = BotService()
    presets = service.get_preset_prompts()

    return {
        "presets": presets,
        "available": list(presets.keys())
    }
