import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict


ANALYTICS_FILE = "analytics_data.json"


class AnalyticsService:
    """
    Servicio para registrar y analizar métricas de uso de los chatbots.
    Registra interacciones, consultas y métricas de rendimiento.
    """

    def __init__(self):
        self.analytics_file = ANALYTICS_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Crea el archivo de analytics si no existe"""
        if not os.path.exists(self.analytics_file):
            self._save_data({"interactions": [], "daily_stats": {}})

    def _load_data(self) -> dict:
        """Carga datos de analytics"""
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar analytics: {e}")
            return {"interactions": [], "daily_stats": {}}

    def _save_data(self, data: dict):
        """Guarda datos de analytics"""
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def log_interaction(
        self,
        bot_id: str,
        question: str,
        answer: str,
        sources_count: int,
        response_time_ms: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Registra una interacción de chat.
        """
        data = self._load_data()

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "bot_id": bot_id,
            "question": question,
            "answer": answer,
            "sources_count": sources_count,
            "response_time_ms": response_time_ms,
            "success": success,
            "error": error,
            "question_length": len(question),
            "answer_length": len(answer)
        }

        data["interactions"].append(interaction)

        # Limitar a las últimas 10000 interacciones para no crecer indefinidamente
        if len(data["interactions"]) > 10000:
            data["interactions"] = data["interactions"][-10000:]

        self._save_data(data)

    def log_document_upload(self, bot_id: str, filename: str, chunks_count: int):
        """Registra la subida de un documento"""
        data = self._load_data()

        if "document_uploads" not in data:
            data["document_uploads"] = []

        upload = {
            "timestamp": datetime.now().isoformat(),
            "bot_id": bot_id,
            "filename": filename,
            "chunks_count": chunks_count
        }

        data["document_uploads"].append(upload)
        self._save_data(data)

    def get_bot_stats(self, bot_id: str, days: int = 7) -> Dict:
        """
        Obtiene estadísticas de un bot en los últimos N días.
        """
        data = self._load_data()
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filtrar interacciones del bot en el rango de fechas
        bot_interactions = [
            i for i in data["interactions"]
            if i["bot_id"] == bot_id and datetime.fromisoformat(i["timestamp"]) > cutoff_date
        ]

        if not bot_interactions:
            return {
                "bot_id": bot_id,
                "period_days": days,
                "total_interactions": 0,
                "success_rate": 0,
                "avg_response_time_ms": 0,
                "avg_sources_count": 0,
                "avg_question_length": 0,
                "avg_answer_length": 0
            }

        total = len(bot_interactions)
        successful = sum(1 for i in bot_interactions if i["success"])

        return {
            "bot_id": bot_id,
            "period_days": days,
            "total_interactions": total,
            "success_rate": (successful / total) * 100 if total > 0 else 0,
            "avg_response_time_ms": sum(i["response_time_ms"] for i in bot_interactions) / total,
            "avg_sources_count": sum(i["sources_count"] for i in bot_interactions) / total,
            "avg_question_length": sum(i["question_length"] for i in bot_interactions) / total,
            "avg_answer_length": sum(i["answer_length"] for i in bot_interactions) / total,
            "daily_breakdown": self._get_daily_breakdown(bot_interactions)
        }

    def _get_daily_breakdown(self, interactions: List[dict]) -> List[Dict]:
        """Agrupa interacciones por día"""
        daily = defaultdict(int)

        for interaction in interactions:
            date = datetime.fromisoformat(interaction["timestamp"]).date().isoformat()
            daily[date] += 1

        return [{"date": date, "count": count} for date, count in sorted(daily.items())]

    def get_global_stats(self, days: int = 30) -> Dict:
        """
        Obtiene estadísticas globales de todos los bots.
        """
        data = self._load_data()
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_interactions = [
            i for i in data["interactions"]
            if datetime.fromisoformat(i["timestamp"]) > cutoff_date
        ]

        # Contar por bot
        bot_counts = defaultdict(int)
        for interaction in recent_interactions:
            bot_counts[interaction["bot_id"]] += 1

        total = len(recent_interactions)
        successful = sum(1 for i in recent_interactions if i["success"])

        return {
            "period_days": days,
            "total_interactions": total,
            "total_bots_used": len(bot_counts),
            "success_rate": (successful / total) * 100 if total > 0 else 0,
            "interactions_by_bot": dict(bot_counts),
            "avg_response_time_ms": sum(i["response_time_ms"] for i in recent_interactions) / total if total > 0 else 0,
            "daily_breakdown": self._get_daily_breakdown(recent_interactions)
        }

    def get_popular_questions(self, bot_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Obtiene las preguntas más frecuentes (agrupadas por similitud aproximada).
        """
        data = self._load_data()
        interactions = data["interactions"]

        if bot_id:
            interactions = [i for i in interactions if i["bot_id"] == bot_id]

        # Agrupar preguntas similares (simplificado: por longitud y primeras palabras)
        question_groups = defaultdict(list)

        for interaction in interactions[-1000:]:  # Últimas 1000 interacciones
            question = interaction["question"]
            # Clave simplificada: primeras 50 caracteres normalizados
            key = question[:50].lower().strip()
            question_groups[key].append(interaction)

        # Ordenar por frecuencia
        popular = sorted(
            [
                {
                    "question_sample": group[0]["question"],
                    "count": len(group),
                    "avg_response_time_ms": sum(i["response_time_ms"] for i in group) / len(group)
                }
                for group in question_groups.values()
            ],
            key=lambda x: x["count"],
            reverse=True
        )

        return popular[:limit]

    def clear_old_data(self, days_to_keep: int = 90):
        """Limpia datos antiguos para mantener el archivo manejable"""
        data = self._load_data()
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        data["interactions"] = [
            i for i in data["interactions"]
            if datetime.fromisoformat(i["timestamp"]) > cutoff_date
        ]

        self._save_data(data)
        print(f"🧹 Datos anteriores a {days_to_keep} días eliminados")
