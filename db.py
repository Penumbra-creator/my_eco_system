import pyrebase
import datetime
import threading

class Database:
    def __init__(self, configure, email, password):   # без root
        self.firebase = pyrebase.initialize_app(configure)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
        self.email = email
        self.password = password
        self.token = None
        self.user_id = None
        self.root = None          # будет установлен позже
        self.login()

    def set_root(self, root):
        self.root = root

    def login(self):
        try:
            user = self.auth.sign_in_with_email_and_password(self.email, self.password)
            self.token = user['idToken']
            self.user_id = user['localId']
            print("Авторизация успешна")
        except Exception as e:
            print("Ошибка входа:", e)
            raise

    def add_entry(self, data):
        data['timestamp'] = datetime.datetime.now().isoformat()
        # ---- ДОБАВЛЕНО ДЛЯ МАТРИЦЫ ----
        if data.get('type') == 'strategy':
            data['urgency'] = data.get('urgency', 0)
            data['importance'] = data.get('importance', 0)
        # --------------------------------
        result = self.db.child("entries").push(data, self.token)
        return result['name']
    def get_entries(self, entry_type=None):
        all_entries = self.db.child("entries").get(self.token)
        if entry_type:
            filtered = []
            for entry in all_entries.each():
                if entry.val().get('type') == entry_type:
                    filtered.append((entry.key(), entry.val()))
            return filtered
        else:
            return [(entry.key(), entry.val()) for entry in all_entries.each()]

    def update_entry(self, entry_key, data):
        data['timestamp'] = datetime.datetime.now().isoformat()
        self.db.child("entries").child(entry_key).update(data, self.token)

    def delete_entry(self, entry_key):
        self.db.child("entries").child(entry_key).remove(self.token)

    def get_stats(self):
        """Собирает статистику для мотивационной фразы."""
        all_entries = self.get_entries()  # список (key, val)
        total_aphorisms = 0
        total_words = 0
        total_strategies = 0
        overdue_tasks = 0
        today = datetime.date.today()
        for key, val in all_entries:
            entry_type = val.get('type')
            if entry_type == 'philosophy':
                total_aphorisms += 1
            elif entry_type == 'language':
                total_words += 1
            elif entry_type == 'strategy':
                total_strategies += 1
                deadline_str = val.get('deadline')
                if deadline_str:
                    try:
                        deadline_date = datetime.datetime.strptime(deadline_str, '%Y-%m-%d').date()
                        if deadline_date < today:
                            overdue_tasks += 1
                    except (ValueError, TypeError):
                        pass
        return {
            'aphorisms': total_aphorisms,
            'words': total_words,
            'strategies': total_strategies,
            'overdue_tasks': overdue_tasks
        }
    def get_due_count(self):
        from datetime import datetime, timedelta
        today = datetime.now().date()
        due_count = 0
        # Проверяем модули, где есть повторения
        for module in ['language', 'exam', 'ticket']:
            entries = self.get_entries(module)
            for _, data in entries:
                last_review = data.get('last_review')
                interval = data.get('interval', 3)  # если нет интервала, берём 3 дня
                if last_review is None:
                    due_count += 1
                else:
                    try:
                        last_date = datetime.strptime(last_review, '%Y-%m-%d').date()
                        if (today - last_date).days >= interval:
                            due_count += 1
                    except:
                        due_count += 1
        return due_count
    def get_random_aphorism(self):
        """Возвращает случайный афоризм (текст) или None."""
        entries = self.get_entries('philosophy')
        if entries:
            import random
            random_entry = random.choice(entries)
            return random_entry[1].get('content')  # поле 'content' из вашей структуры
        return None

    def mark_reviewed(self, entry_key, interval=3):
        """Обновляет дату последнего повторения и интервал"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        self.update_entry(entry_key, {
            'last_review': today,
            'interval': interval
        })


    def get_entries_async(self, entry_type, callback):
        def _load():
            try:
                entries = self.get_entries(entry_type)
                if self.root:
                    self.root.after(0, lambda: callback(entries, None))
                else:
                    callback(entries, None)
            except Exception as e:
                if self.root:
                    self.root.after(0, lambda: callback(None, str(e)))
                else:
                    callback(None, str(e))
        threading.Thread(target=_load, daemon=True).start()

    def get_due_entries(self, module_type=None, days_threshold=3):
        """Возвращает просроченные записи для модуля"""
        from datetime import datetime, timedelta
        today = datetime.now().date()
        if module_type:
            entries = self.get_entries(module_type)
        else:
            entries = self.get_entries()  # все модули
        due = []
        for key, data in entries:
            # Проверяем, есть ли поле last_review
            last_review = data.get('last_review')
            if last_review is None:
                due.append((key, data))
            else:
                try:
                    last_date = datetime.strptime(last_review, '%Y-%m-%d').date()
                    interval = data.get('interval', days_threshold)
                    if (today - last_date).days >= interval:
                        due.append((key, data))
                except:
                    due.append((key, data))
        return due
    {
    "type": "dialog",
    "question": "текст вопроса",
    "answer": "текст ответа",
    "model": "llama3.2",
    "provider": "ollama",
    "timestamp": "2026-08-07T15:30:00",
    "rating": None,   # "like" или "dislike"
    "comment": ""     # комментарий (если был)
}