import openai
from config_data import GEMINI_API_KEY, OPENROUTER_API_KEY

class AIOrchestrator:
    def __init__(self):
        self.providers = {}
        self.current_model = None   # Имя последней использованной модели

        # ---- OLLAMA (локальный) ----
        self.providers['ollama'] = {
            'api_key': 'ollama',
            'base_url': 'http://localhost:11434/v1',
            'models': ['llama3.2', 'mistral', 'gemma2', 'phi3'],
            'available_models': []  
        }

        # ---- GEMINI (через OpenAI-совместимый эндпоинт Google) ----
        if GEMINI_API_KEY:
            self.providers['gemini'] = {
                'api_key': GEMINI_API_KEY,
                'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/',
                'models': ['gemini-3.5-flash', 'gemini-3.7-flash'],
                'available_models': []
            }


        # ---- OPENROUTER ----
        if OPENROUTER_API_KEY:
            self.providers['openrouter'] = {
                'api_key': OPENROUTER_API_KEY,
                'base_url': 'https://openrouter.ai/api/v1',
                'models': ['openai/gpt-3.5-turbo', 'meta-llama/llama-3-8b-instruct:free'],
                'available_models': []
            }

        # Автоматическое тестирование доступных моделей при старте
        self._test_all_providers()

    def _test_model(self, provider_name, model):
        """Проверяет доступность конкретной модели (короткий запрос)"""
        provider = self.providers[provider_name]
        client = openai.OpenAI(
            api_key=provider['api_key'],
            base_url=provider['base_url']
        )
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                temperature=0.0
            )
            return True
        except Exception as e:
            if "429" in str(e):
                return True  # Квота исчерпана, но модель технически существует
            return False

    def _test_all_providers(self):
        """Тестирует все модели для всех провайдеров"""
        for provider_name, provider in self.providers.items():
            available = []
            for model in provider['models']:
                if self._test_model(provider_name, model):
                    available.append(model)
            provider['available_models'] = available

    def get_available_models(self, provider_name=None):
        if provider_name:
            return self.providers.get(provider_name, {}).get('available_models', [])
        result = {}
        for name, provider in self.providers.items():
            result[name] = provider['available_models']
        return result

    def get_status(self):
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                'total_models': len(provider['models']),
                'available_models': provider['available_models'],
                'is_ready': len(provider['available_models']) > 0
            }
        return status

    def ask_provider(self, provider_name, model, prompt):
        if provider_name not in self.providers:
            return None, f"Провайдер {provider_name} не найден"
        provider = self.providers[provider_name]
        client = openai.OpenAI(
            api_key=provider['api_key'],
            base_url=provider['base_url']
        )
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=500
            )
            return response.choices[0].message.content, None
        except Exception as e:
            return None, f"{provider_name}:{model} error: {str(e)}"

    def ask_model(self, prompt, model_name):
        for provider_name, provider in self.providers.items():
            if model_name in provider['models'] and model_name in provider['available_models']:
                result, error = self.ask_provider(provider_name, model_name, prompt)
                if result is not None:
                    self.current_model = model_name
                    return result, model_name
                else:
                    if "429" in error:
                        continue
                    self.current_model = None
                    return None, "не доступна"
        self.current_model = None
        return None, "не доступна"

    def ask_auto(self, prompt, preferred_provider=None):
        providers_order = list(self.providers.keys())
        if preferred_provider and preferred_provider in providers_order:
            providers_order.remove(preferred_provider)
            providers_order.insert(0, preferred_provider)

        for provider_name in providers_order:
            provider = self.providers[provider_name]
            for model in provider['available_models']:
                result, error = self.ask_provider(provider_name, model, prompt)
                if result is not None:
                    self.current_model = model
                    return result, model
                if "429" in error:
                    continue
        self.current_model = None
        return None, "не доступна"

    def get_current_model(self):
        return self.current_model if self.current_model else "не доступна"

# ========== ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР ==========
# ========== ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР ==========
ai = AIOrchestrator()

# --- ДОБАВЬТЕ ЭТОТ БЛОК В САМЫЙ КОНЕЦ ФАЙЛА ---
if __name__ == "__main__":
    print("=== ТЕСТ ОРКЕСТРАТОРА ЗАПУЩЕН ===")
    
    # Спросим статусы
    status = ai.get_status()
    for provider_name, info in status.items():
        print(f"Провайдер [{provider_name}]: готов = {info['is_ready']}")
        print(f"  Доступные модели: {info['available_models']}")
    
    print("-" * 30)
    print("Пробуем отправить тестовый запрос...")
    
    answer, model_used = ai.ask_auto("Привет! Скажи одно слово: Работает.")
    print(f"Ответ от модели ({model_used}):")
    print(answer)