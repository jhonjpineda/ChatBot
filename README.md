# 🤖 ChatBot - Proyecto con FastAPI + Ollama

**ChatBot** es un proyecto backend desarrollado con **Python 3.11** y **FastAPI**, diseñado para integrar modelos de lenguaje locales a través de **Ollama** (como LLaMA 3, Phi-3, Mistral, entre otros).  
Permite ejecutar consultas, mantener conversaciones contextuales y servir como base para la construcción de asistentes inteligentes.

---

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/jhonjpineda/ChatBot.git
cd ChatBot/backend

2️⃣ Crear entorno virtual

python -m venv .venv

3️⃣ Activar entorno virtual

Windows:

.venv\Scripts\activate

Linux / macOS:

source .venv/bin/activate

4️⃣ Instalar dependencias

pip install -r requirements.txt

⚙️ Configuración del entorno

    Copia el archivo .env.example y renómbralo como .env

    Define las variables necesarias (tokens, URLs, puertos, etc.)

    Ejemplo:

    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=llama3.2:3b

▶️ Ejecución del servidor

Desde la carpeta backend:

uvicorn app.main:app --reload --port 8000

Una vez iniciado, abre en tu navegador:
👉 http://localhost:8000/docs

Allí encontrarás la documentación interactiva Swagger UI de la API.
📂 Estructura del proyecto

ChatBot/
├── backend/
│   ├── app/
│   │   ├── api/                 # Rutas y controladores de la API
│   │   ├── core/                # Configuraciones base del proyecto
│   │   ├── llm_providers/       # Conectores para modelos (Ollama, OpenAI, etc.)
│   │   ├── models/              # Definición de modelos Pydantic
│   │   ├── repositories/        # Persistencia y acceso a datos
│   │   ├── services/            # Lógica de negocio y servicios
│   │   └── main.py              # Punto de entrada FastAPI
│   ├── chroma_db/               # Base vectorial (ChromaDB)
│   ├── uploads/                 # Archivos subidos (se ignoran en Git)
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
└── README.md

🧠 Tecnologías utilizadas

    Python 3.11+

FastAPI

Uvicorn

Ollama

ChromaDB

Requests
🧩 Endpoints principales
Método	Endpoint	Descripción
POST	/chat/	Envía una pregunta al modelo LLM
GET	/api/version	Comprueba el estado de la conexión con Ollama
GET	/docs	Documentación interactiva Swagger
💻 Requisitos

    Python 3.10 o superior

    FastAPI 1.0+

    Ollama instalado y corriendo localmente (http://localhost:11434)

    Al menos 4 GB de RAM (8 GB recomendados)

🧰 Comandos útiles
Acción	Comando
Crear entorno virtual	python -m venv .venv
Activar entorno	.venv\Scripts\activate
Instalar dependencias	pip install -r requirements.txt
Ejecutar servidor	uvicorn app.main:app --reload
Actualizar dependencias	pip freeze > requirements.txt
🧑‍💻 Autor

Jhon Jairo Pineda Muñoz
Ingeniero en Sistemas y Computación
GitHub: jhonjpineda

    Proyecto desarrollado como base para un sistema de chatbot inteligente con modelos locales y APIs LLM, adaptable a múltiples contextos educativos, empresariales y de soporte técnico.


---

📋 **Pasos finales para subirlo:**

1. Guarda el archivo como `README.md` en la raíz del proyecto (`D:\2025\ChatBot\README.md`).
2. En tu consola:
   ```powershell
   git add README.md
   git commit -m "Agregar README completo del proyecto"
   git push