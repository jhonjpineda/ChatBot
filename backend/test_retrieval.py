"""Script para probar el retrieval y ver qué chunks se recuperan"""
import sys
sys.path.append('.')

from app.services.retriever_service import RetrieverService

# Crear servicio
rs = RetrieverService()

# Pregunta del usuario
query = "enlace plataforma SIGA"
bot_id = "SoporteTech"

print(f"\n{'='*80}")
print(f"PRUEBA DE RETRIEVAL")
print(f"{'='*80}")
print(f"Bot ID: {bot_id}")
print(f"Query: {query}")
print(f"{'='*80}\n")

# Recuperar chunks
results = rs.search(query, bot_id=bot_id)

print(f"Total chunks recuperados: {len(results)}\n")

for i, result in enumerate(results, 1):
    score = result.get('score', 'N/A')
    text = result['text'][:400]  # Primeros 400 caracteres

    print(f"\n--- CHUNK {i} (Distance: {score}) ---")
    print(f"{text}...")
    print(f"Metadata: {result.get('metadata', {})}")
    print()

print(f"\n{'='*80}")
print("FIN DE LA PRUEBA")
print(f"{'='*80}\n")
