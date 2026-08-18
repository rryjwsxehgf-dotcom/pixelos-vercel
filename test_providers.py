"""
ТЕСТ ПРОВАЙДЕРОВ G4F
Запусти: python test_providers.py
"""
from g4f.client import Client

# Список реально работающих провайдеров на июнь 2026
providers_to_test = [
    "PollinationsAI",
    "Free2GPT", 
    "FreeGpt",
    "ChatGptEs",
    "GizAI",
]

print("🧪 Тестирую провайдеры g4f...\n")

for provider_name in providers_to_test:
    try:
        client = Client()
        print(f"🔍 Тест: {provider_name}...", end=" ")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Скажи 'Привет, я работаю!' одним предложением"}],
            provider=provider_name,
            timeout=15
        )
        result = response.choices[0].message.content
        print(f"✅ ОТВЕТ: {result[:50]}...")
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)[:80]}")

print("\n✅ Тест завершён. Используй первый работающий провайдер в core.py")
