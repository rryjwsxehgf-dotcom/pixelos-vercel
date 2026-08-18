"""
ДИАГНОСТИКА G4F — выводит все доступные провайдеры
Запуск: python check_g4f.py
"""
print("=" * 60)
print("🔍 ДИАГНОСТИКА G4F ПРОВАЙДЕРОВ")
print("=" * 60)

# 1. Версия g4f
try:
    import g4f
    print(f"\n📦 Версия g4f: {g4f.__version__}")
except Exception as e:
    print(f"❌ Ошибка импорта g4f: {e}")
    exit(1)

# 2. Все классы в g4f.Provider
print("\n📋 Все провайдеры в g4f.Provider:")
print("-" * 60)
try:
    import g4f.Provider as P
    provider_names = [name for name in dir(P) if not name.startswith('_')]
    provider_names.sort()
    
    working = []
    broken = []
    
    for name in provider_names:
        try:
            cls = getattr(P, name)
            if isinstance(cls, type):
                print(f"  ✅ {name}")
                working.append(name)
            else:
                print(f"  ⚠️ {name} (не класс)")
        except Exception as e:
            print(f"  ❌ {name} — {str(e)[:50]}")
            broken.append(name)
    
    print(f"\n📊 Итого: {len(working)} рабочих, {len(broken)} с ошибками")
    print(f"\n✅ Рабочие провайдеры ({len(working)}):")
    for n in working:
        print(f"   '{n}',")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. Тест быстрого запроса
print("\n🧪 Тестовый запрос (первый рабочий провайдер)...")
try:
    from g4f.client import Client
    client = Client()
    
    # Пробуем без указания провайдера
    print("  Пробую авто-выбор...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Скажи 'Привет' одним словом"}],
        timeout=10
    )
    print(f"  ✅ Ответ: {response.choices[0].message.content}")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")

print("\n" + "=" * 60)
print("✅ Диагностика завершена")
print("=" * 60)
