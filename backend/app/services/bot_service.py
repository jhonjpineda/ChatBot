import json
import os
from typing import List, Optional
from app.models.bot import BotConfig, BotCreate, BotUpdate, PRESET_PROMPTS
from datetime import datetime

BOTS_DB_FILE = "bots_config.json"


class BotService:
    """
    Servicio para gestionar configuraciones de bots.
    Usa un archivo JSON simple como persistencia (puede migrarse a DB después).
    """

    def __init__(self):
        self.db_file = BOTS_DB_FILE
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Crea el archivo de BD si no existe con un bot por defecto"""
        if not os.path.exists(self.db_file):
            default_bot = BotConfig(
                bot_id="default",
                name="Bot Principal",
                description="Bot de propósito general con RAG estricto",
                system_prompt=PRESET_PROMPTS["rag_strict"]
            )
            self._save_bots([default_bot.model_dump()])

    def _load_bots(self) -> List[dict]:
        """Carga todos los bots del archivo JSON"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar bots: {e}")
            return []

    def _save_bots(self, bots: List[dict]):
        """Guarda todos los bots en el archivo JSON"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(bots, f, indent=2, ensure_ascii=False)

    def create_bot(self, bot_data: BotCreate) -> BotConfig:
        """Crea un nuevo bot"""
        bots = self._load_bots()

        # Verificar si ya existe
        if any(b['bot_id'] == bot_data.bot_id for b in bots):
            raise ValueError(f"Ya existe un bot con el ID: {bot_data.bot_id}")

        # Crear configuración
        new_bot = BotConfig(
            bot_id=bot_data.bot_id,
            name=bot_data.name,
            description=bot_data.description,
            system_prompt=bot_data.system_prompt or PRESET_PROMPTS["rag_strict"],
            temperature=bot_data.temperature or 0.7,
            retrieval_k=bot_data.retrieval_k or 4,
            metadata=bot_data.metadata or {}
        )

        bots.append(new_bot.model_dump())
        self._save_bots(bots)

        print(f"✅ Bot creado: {bot_data.bot_id} - {bot_data.name}")
        return new_bot

    def get_bot(self, bot_id: str) -> Optional[BotConfig]:
        """Obtiene la configuración de un bot específico"""
        bots = self._load_bots()
        bot_data = next((b for b in bots if b['bot_id'] == bot_id), None)

        if bot_data:
            return BotConfig(**bot_data)
        return None

    def list_bots(self, active_only: bool = False) -> List[BotConfig]:
        """Lista todos los bots"""
        bots = self._load_bots()

        if active_only:
            bots = [b for b in bots if b.get('active', True)]

        return [BotConfig(**b) for b in bots]

    def update_bot(self, bot_id: str, bot_data: BotUpdate) -> Optional[BotConfig]:
        """Actualiza un bot existente"""
        bots = self._load_bots()
        bot_index = next((i for i, b in enumerate(bots) if b['bot_id'] == bot_id), None)

        if bot_index is None:
            return None

        # Actualizar solo los campos proporcionados
        current_bot = bots[bot_index]
        update_data = bot_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            current_bot[key] = value

        current_bot['updated_at'] = datetime.now().isoformat()

        bots[bot_index] = current_bot
        self._save_bots(bots)

        print(f"✅ Bot actualizado: {bot_id}")
        return BotConfig(**current_bot)

    def delete_bot(self, bot_id: str) -> bool:
        """Elimina un bot (no se puede eliminar el bot 'default')"""
        if bot_id == "default":
            raise ValueError("No se puede eliminar el bot 'default'")

        bots = self._load_bots()
        original_len = len(bots)
        bots = [b for b in bots if b['bot_id'] != bot_id]

        if len(bots) < original_len:
            self._save_bots(bots)
            print(f"🗑️ Bot eliminado: {bot_id}")
            return True

        return False

    def get_preset_prompts(self) -> dict:
        """Obtiene todos los prompts predefinidos disponibles"""
        return PRESET_PROMPTS
