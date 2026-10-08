from tkinter import messagebox
import threading

def show_startup_notification(db):
    """Показывает уведомление о количестве просроченных записей"""
    def _show():
        try:
            due_count = db.get_due_count()
            if due_count > 0:
                messagebox.showinfo(
                    "📚 Моя экосистема",
                    f"У тебя {due_count} записей для повторения! Пора открыть приложение."
                )
            else:
                messagebox.showinfo(
                    "🌟 Моя экосистема",
                    "Добро пожаловать! Все записи повторены."
                )
        except Exception as e:
            print(f"Ошибка уведомления: {e}")
    
    # Запуск в отдельном потоке, чтобы не блокировать UI
    threading.Thread(target=_show, daemon=True).start()