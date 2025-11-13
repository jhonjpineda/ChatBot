import os
import json
import requests

class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: int = 0):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.session = requests.Session()
        # timeout=0 para streaming largo; ajusta si quieres

    def chat(self, messages: list[dict], *, temperature: float = 0.2) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {"temperature": temperature},
            "stream": True  # <- dejamos streaming activado
        }
        resp = self.session.post(url, json=payload, stream=True)
        resp.raise_for_status()

        chunks = []
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # algunas líneas pueden venir con espacios/barras; ignora o loguea
                continue
            msg = obj.get("message", {}).get("content")
            if msg:
                chunks.append(msg)
        return "".join(chunks)

    def chat_stream(self, messages: list[dict], *, temperature: float = 0.2):
        """
        Generador que yields chunks de texto en tiempo real para streaming.
        Usado para respuestas progresivas en el frontend.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {"temperature": temperature},
            "stream": True
        }
        resp = self.session.post(url, json=payload, stream=True)
        resp.raise_for_status()

        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = obj.get("message", {}).get("content")
            if msg:
                yield msg
