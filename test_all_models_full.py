import os
import subprocess
import requests
from ai_orchestrator import ai
from openai import OpenAI                  # Для OpenRouter, Groq, Cerebras и Ollama
from google import genai                   # Только для Gemini
from google.genai import types
from config_data import OPENROUTER_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, CEREBRAS_API_KEY

# ========== 1. OLLAMA ==========
def get_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")[1:]  # пропускаем заголовок
        models = []
        for line in lines:
            if line.strip():
                name = line.split()[0]
                models.append(name)
        return models
    except Exception as e:
        print(f"❌ Can't fetch Ollama models: {e}")
        return []


# ========== 2. GEMINI ==========
def get_gemini_models():
    return [
        "gemini-3.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.5-pro"
    ]


# ========== 3. GROQ (актуально на 2026) ==========
def get_groq_models():
    return [
        "llama3-8b-8192",                    # самая стабильная и быстрая
        "gemma-7b-it",
        "llama-3.2-3b-preview",
        "llama-3.2-1b-preview",
        "llama-3.2-11b-vision-preview",
        # Лучшие бесплатные модели через OpenRouter (рекомендую использовать)
        "openai/gpt-oss-20b:free",
        "qwen/qwen3.6-27b:free",
        "meta-llama/llama-3.3-70b-instruct:free"
    ]


# ========== 4. CEREBRAS ==========
def get_cerebras_models():
    return [
        "llama3.1-70b",
        "qwen3-235b",
        "llama3.3-70b",
        # Лучшие бесплатные модели через OpenRouter
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "poolside/laguna-s-2.1:free"
    ]


# ========== 5. OpenRouter (самый актуальный список на сегодня) ==========
def get_openrouter_models():
    return [
        # 1. Самая сильная универсальная (дефолт для большинства модулей)
        "nvidia/nemotron-3-ultra-550b-a55b:free",

        # 2. Лучшая для кодинга и агентов
        "poolside/laguna-s-2.1:free",

        # 3. Очень быстрая
        "nvidia/nemotron-3.5-lightning:free",

        # 4. Хорошая для сложных задач и рефлексии
        "google/gemma-4-31b-it:free",

        # 5. Для анализа и длинных контекстов
        "nvidia/nemotron-3-super-120b-a12b:free",

        # 6. Специально для кода
        "cohere/north-mini-code:free",

        # 7. Запасной
        "z-ai/glm-5.2:free",

        # 8. Авто-выбор (самый умный вариант)
        "openrouter/free",
    ]
# ========== TEST FUNCTION ==========
def test_model(provider_name, model, prompt="Say 'ok' in one word."):
    try:
        response, used_model = ai.ask_model(prompt, model)
        if response and "не доступна" not in response:
            return True, response
        else:
            return False, response
    except Exception as e:
        return False, str(e)

# ========== MAIN ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 TESTING EVERY MODEL FROM EVERY PROVIDER")
    print("=" * 60)

    all_providers = {
        "OLLAMA": get_ollama_models(),
        "GEMINI": get_gemini_models(),
        "GROQ": get_groq_models(),
        "OPENROUTER": get_openrouter_models(),
        "CEREBRAS": get_cerebras_models(),
    }

    results = {}
    total_ok = 0
    total_fail = 0

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 TESTING EVERY MODEL FROM EVERY PROVIDER")
    print("=" * 60)

    all_providers = {
        "OLLAMA": get_ollama_models(),
        "GEMINI": get_gemini_models(),
        "GROQ": get_groq_models(),
        "OPENROUTER": get_openrouter_models(),
        "CEREBRAS": get_cerebras_models(),
    }

    results = {}
    total_ok = 0
    total_fail = 0

    for provider_name, models in all_providers.items():
        print(f"\n🔹 {provider_name} ({len(models)} models to test)")
        results[provider_name] = {"ok": [], "fail": []}

        if not models:
            print("   ⚠️ No models found for this provider (check key / connection)")
            continue

        for model in models:
            ok, msg = test_model(provider_name, model)
            if ok:
                print(f"   ✅ {model}")
                results[provider_name]["ok"].append(model)
                total_ok += 1
            else:
                # FIX: handle None or empty message
                if msg is None:
                    error_short = "⚠️ No response (unknown error)"
                else:
                    error_short = msg[:60] + "..." if len(msg) > 60 else msg
                print(f"   ❌ {model} — {error_short}")
                results[provider_name]["fail"].append((model, msg))
                total_fail += 1

    # ========== SUMMARY ==========
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Working models: {total_ok}")
    print(f"❌ Failing models: {total_fail}\n")

    for provider_name, data in results.items():
        if data["ok"]:
            print(f"✅ {provider_name.upper()} working: {', '.join(data['ok'])}")
        else:
            print(f"❌ {provider_name.upper()} — none working")

    print("\n💡 Tip: Now you know exactly which model IDs are active.")

    # ========== SUMMARY ==========
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Working models: {total_ok}")
    print(f"❌ Failing models: {total_fail}\n")

    for provider_name, data in results.items():
        if data["ok"]:
            print(f"✅ {provider_name.upper()} working: {', '.join(data['ok'])}")
        else:
            print(f"❌ {provider_name.upper()} — none working")

    print("\n💡 Tip: Now you know exactly which model IDs are active.")