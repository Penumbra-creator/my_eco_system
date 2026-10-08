import tkinter as tk
import customtkinter as ctk
import random
import datetime
from tkinter import messagebox, scrolledtext
from db import Database
from auto_start import is_autostart_enabled, add_to_startup, remove_from_startup
import threading

class App:
    def __init__(self, root):
        self.root = root          # сохраняем root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.title("Моя экосистема")
        self.root.geometry("900x600")
        self.root.option_add('*Font', ('Segoe UI', 10))

        self.menu_buttons = []

        # Статус-метка
        self.status_label = ctk.CTkLabel(
            root,
            text="🧠 Проверка ИИ...",
            font=("Arial", 10),
            fg_color="gray"
        )
        self.status_label.place(x=730, y=5)

        # Отложенная загрузка
        self.db = None
        self.db_ready = False
        self.ai_ready = False

        self.home_motivation_label = None

        light_colors = [
            "#D7FF7A", "#FFB16C", "#ABFFFF", "#F8F67F", "#CDBFFF",
            "#B6FFDB", "#FFFFAB", "#FFC1BA", "#A9A9FF", "#8AC9FF", "#FFD900"
        ]
        self.theme_color = random.choice(light_colors)

        # Меню
        self.menu_frame = ctk.CTkFrame(root, width=200, fg_color=self.theme_color)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.menu_frame.configure(border_width=2, border_color="gray")

        # Контент
        self.content_frame = ctk.CTkFrame(root, fg_color='white')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Функция создания кнопок
        def make_btn(text, module, tooltip):
            btn = ctk.CTkButton(
                self.menu_frame,
                text=text,
                text_color="black",  
                fg_color=self.theme_color,
                font=('Segoe UI', 16, 'bold')
            )
            btn.configure(command=lambda b=btn: self.switch_module(module, b))
            btn.pack(fill=tk.X, padx=5, pady=2)
            ToolTip(btn, tooltip)
            self.menu_buttons.append(btn)
            return btn

        # ---- Кнопка "Главная" ----
        btn_home = ctk.CTkButton(
            self.menu_frame,
            text="🏠 Главная",
            command=lambda: self.show_module('home'),
            fg_color=self.theme_color,
            text_color="black",
            font=('Segoe UI', 16, 'bold')
        )
        btn_home.pack(fill=tk.X, padx=5, pady=2)
        ToolTip(btn_home, "🏠 Вернуться на главную")
        self.menu_buttons.append(btn_home)
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)

        # ---- Кнопка "Настройки" ----
        btn_settings = ctk.CTkButton(
            self.menu_frame,
            text="⚙️ Настройки",
            command=self.open_settings,
            fg_color=self.theme_color,
            text_color="black",
            font=('Segoe UI', 16, 'bold')
        )
        btn_settings.pack(fill=tk.X, padx=5, pady=2)
        ToolTip(btn_settings, "Настройки приложения")
        self.menu_buttons.append(btn_settings)
        ctk.CTkFrame(self.menu_frame, height=1, fg_color="#000000").pack(fill=tk.X, padx=5)

        # ---- Кнопка "Философия" ----
        btn_phil = ctk.CTkButton(
            self.menu_frame,
            text="Философия",
            command=lambda: self.show_module('philosophy'),
            text_color="black",
            fg_color=self.theme_color,
            font=('Segoe UI', 16, 'bold')
        )
        btn_phil.pack(fill=tk.X, padx=5, pady=2)
        ToolTip(btn_phil, "📜 Афоризмы и мудрые мысли")
        self.menu_buttons.append(btn_phil)
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)

        # ---- Остальные кнопки (через make_btn) ----
        btn_lang = make_btn("🌐 Языки", "language", "🌐 Слова, переводы и языковая практика")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_strat = make_btn("📊 Стратегии", "strategy", "♟ Деревья решений и стратегические планы")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_exam = make_btn("📚 Экзамены", "exam", "📚 Вопросы для подготовки к экзаменам")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_tickets = make_btn("🎫 Билеты", "ticket", "🎫 Билеты с источниками и страницами")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_motor = make_btn("🏋️ Моторика", "motor", "✍️ Тренировки моторики и прогресс")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_clinic = make_btn("🏥 Клинический дневник", "clinic", "🏥 Клинические случаи и заметки")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_dreams = make_btn("💭 Сны", "dream", "💭 Сны, их содержание и интерпретация")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_conflict = make_btn("⚔️ Конфликты", "conflict", "⚔️ Симуляция конфликтов и стратегии поведения")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_article = make_btn("📄 Статьи", "article", "📄 Анализ статей, ключевые идеи")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_lifebook = make_btn("📖 Книга жизни", "lifebook", "📖 Книга жизни – события, эмоции, уроки")
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_chat = make_btn("🧠 Чат с ИИ", "chat", "💬 Свободное общение с ИИ")
        btn_stats = ctk.CTkButton(
            self.menu_frame,
            text="📊 Статистика",
            command=lambda: self.show_module('statistics'),
            fg_color=self.theme_color,
            text_color="black",
            font=('Segoe UI', 16, 'bold')
        )
        btn_stats.pack(fill=tk.X, padx=5, pady=2)
        self.menu_buttons.append(btn_stats)
        ctk.CTkFrame(self.menu_frame, height=1, fg_color='#cccccc').pack(fill=tk.X, padx=5)
        btn_global_search = ctk.CTkButton(
            self.menu_frame,
            text="🔍 Поиск",
            command=self.open_global_search,
            fg_color=self.theme_color,
            text_color="black",
            font=('Segoe UI', 16, 'bold')
        )
        btn_global_search.pack(fill=tk.X, padx=5, pady=2)
        self.menu_buttons.append(btn_global_search)

        self.current_module = None
        self.show_module('home')

        # Запускаем фоновую загрузку (уведомления будут показаны после загрузки БД)
        self.root.after(100, self._init_async)

    def _init_async(self):
        """Фоновая инициализация БД и ИИ."""
        import threading
        def load():
            try:
                from config_data import EMAIL, PASSWORD, firebaseConfig
                from db import Database
                self.db = Database(firebaseConfig, EMAIL, PASSWORD)   # без root
                self.db.set_root(self.root)                           # устанавливаем root
                self.db_ready = True
                self.root.after(0, lambda: self.status_label.configure(
                    text="🟢 База данных готова", text_color="#2ecc71"
                ))
                self.root.after(1000, self._show_notification)
                self.ai_ready = True
                self.root.after(0, self.update_home_motivation)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"❌ Ошибка: {error_msg}", text_color="#e74c3c"
                ))
                print(f"Ошибка инициализации: {e}")
        threading.Thread(target=load, daemon=True).start()

    def _show_notification(self):
        if self.db_ready:
            from notifications import show_startup_notification
            show_startup_notification(self.db)
    def get_module(self, module_name):
        """Ленивая загрузка модулей."""
        if module_name == 'philosophy':
            from philosophy_module import PhilosophyModule
            return PhilosophyModule
        elif module_name == 'language':
            from language_module import LanguageModule
            return LanguageModule
        elif module_name == 'strategy':
            from strategy_module import StrategyModule
            return StrategyModule
        elif module_name == 'exam':
            from exam_module import ExamModule
            return ExamModule
        elif module_name == 'ticket':
            from ticket_module import TicketModule
            return TicketModule
        elif module_name == 'motor':
            from motor_module import MotorModule
            return MotorModule
        elif module_name == 'clinic':
            from clinic_module import ClinicModule
            return ClinicModule
        elif module_name == 'dream':
            from dream_module import DreamModule
            return DreamModule
        elif module_name == 'conflict':
            from conflict_module import ConflictModule
            return ConflictModule
        elif module_name == 'article':
            from article_module import ArticleModule
            return ArticleModule
        elif module_name == 'lifebook':
            from lifebook_module import LifebookModule
            return LifebookModule
        elif module_name == 'chat':
            from chat_module import ChatModule
            return ChatModule
        elif module_name == 'statistics':
            from statistics_module import StatisticsModule
            return StatisticsModule
        else:
            return None

    def open_global_search(self):
        from global_search import GlobalSearchWindow
        GlobalSearchWindow(self.root, self.db)

    def switch_module(self, module_name, btn):
        # Сброс цвета для всех кнопок
        for b in self.menu_buttons:
            b.configure(fg_color=self.theme_color)
        # Подсветка выбранной
        btn.configure(fg_color='#b0d4f1')
        self.show_module(module_name)

    def show_module(self, module_name):
        print(f"show_module called with {module_name}")
        # Очистка
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if module_name == 'home':
            self.create_home_ui(self.content_frame)
            return

        if not self.db_ready or self.db is None:
            label = ctk.CTkLabel(
                self.content_frame,
                text="⏳ База данных загружается...\nПожалуйста, подождите и попробуйте снова.",
                font=('Arial', 14)
            )
            label.pack(expand=True)
            return

        ModuleClass = self.get_module(module_name)
        if ModuleClass:
            try:
                module = ModuleClass(self.content_frame, self.db)
                module.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                error_label = ctk.CTkLabel(
                    self.content_frame,
                    text=f"Ошибка при загрузке модуля:\n{str(e)}",
                    font=('Arial', 12),
                    text_color="red"
                )
                error_label.pack(expand=True)
                print(f"Ошибка модуля {module_name}: {e}")
        else:
            label = ctk.CTkLabel(self.content_frame, text="Модуль не найден")
            label.pack(expand=True)
    def create_home_ui(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        ctk.CTkLabel(parent, text="🌟 Моя экосистема", font=('Arial', 20, 'bold')).pack(pady=30)

        frame_quote = ctk.CTkFrame(parent, fg_color='#f0f0f0')
        frame_quote.pack(pady=20, padx=40, fill=tk.BOTH)
        # Статистика на главной
        stats_frame = ctk.CTkFrame(parent, fg_color='#f8f8f8')
        stats_frame.pack(pady=10, padx=40, fill=tk.X)

        try:
            stats = self.db.get_stats()
            due = self.db.get_due_count()
            label_text = f"📚 Афоризмы: {stats['aphorisms']}  |  🌐 Слова: {stats['words']}  |  📊 Стратегии: {stats['strategies']}  |  ⏳ Просрочено: {due}"
        except:
            label_text = "📊 Статистика загружается..."

        ctk.CTkLabel(stats_frame, text=label_text, font=('Arial', 12), justify='center').pack(pady=5)
        self.home_motivation_label = ctk.CTkLabel(
            frame_quote,
            text="",
            font=('Arial', 14, 'italic'),
            wraplength=600,
            justify='center',
            fg_color='#f0f0f0'
        )
        self.home_motivation_label.pack(pady=30, padx=20)

        self._fallback_motivation()

        ctk.CTkLabel(parent, text="Выберите раздел слева, чтобы начать работу", font=('Arial', 12)).pack(pady=10)
        ctk.CTkLabel(parent, text="✨ Каждый день — новая мысль", font=('Arial', 10, 'italic')).pack(pady=5)

    def _fallback_motivation(self):
        if not self.db_ready or self.db is None:
            if self.home_motivation_label and self.home_motivation_label.winfo_exists():
                self.home_motivation_label.configure(...)
            return
        if self.home_motivation_label:
            try:
                entries = self.db.get_entries('philosophy')
                if entries:
                    random_entry = random.choice(entries)
                    content = random_entry[1].get('content', '')
                    self.home_motivation_label.configure(text=f"✨ {content[:100]}")
                else:
                    self.home_motivation_label.configure(text="✨ Добро пожаловать в экосистему!")
            except:
                self.home_motivation_label.configure(text="✨ Добро пожаловать в экосистему!")

    def update_home_motivation(self):
        if not self.db_ready:
            self.root.after(2000, self.update_home_motivation)
            return

        import threading
        def load():
            try:
                from ai_orchestrator import ai
                stats = {
                    'aphorisms': len(self.db.get_entries('philosophy')),
                    'words': len(self.db.get_entries('language')),
                    'strategies': len(self.db.get_entries('strategy')),
                    'overdue_tasks': self.db.get_due_count() if hasattr(self.db, 'get_due_count') else 0
                }
                prompt = (f"У меня {stats['aphorisms']} афоризмов, {stats['words']} слов, "
                          f"{stats['strategies']} стратегий и {stats['overdue_tasks']} просроченных задач. "
                          "Напиши короткую мотивирующую фразу (1 предложение), связанную с моим прогрессом.")
                response, provider, model = ai.ask_auto(prompt)

                if response and response.strip():
                    self.root.after(0, lambda: self._set_motivation_text(f"🌟 {response.strip()}", model))
                else:
                    self.root.after(0, self._fallback_motivation)
                    self.root.after(0, lambda: self.update_status("не доступна"))
            except Exception as e:
                print(f"Ошибка мотивации: {e}")
                self.root.after(0, self._fallback_motivation)
                self.root.after(0, lambda: self.update_status("не доступна"))

        threading.Thread(target=load, daemon=True).start()

    def _set_motivation_text(self, text, model):
        if self.home_motivation_label:
            self.home_motivation_label.configure(text=text)
        self.update_status(model)

    def update_status(self, model_name):
        if model_name and str(model_name).lower() not in ("не доступна", "none", "False"):
            self.status_label.configure(text=f"🟢 ИИ: {model_name}", text_color="#2ecc71")
        else:
            self.status_label.configure(text="🔴 Модель недоступна", text_color="#e74c3c")

    def check_ai_status(self):
        try:
            from ai_orchestrator import ai
            models = ai.get_active_models() if hasattr(ai, 'get_active_models') else []
            if models:
                current_model = models[0] if isinstance(models, list) else "Активна"
                self.status_label.configure(text=f"🟢 ИИ: {current_model}", text_color="#2ecc71")
            else:
                self.status_label.configure(text="🔴 Модель недоступна", text_color="#e74c3c")
        except Exception:
            self.status_label.configure(text="🔴 Модель недоступна", text_color="#e74c3c")
        self.root.after(60000, self.check_ai_status)

    def on_model_selected(self, chosen_model):
        self.update_status(chosen_model)

    def open_settings(self):
        if hasattr(self, 'settings_window') and self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Настройки")
        self.settings_window.geometry("400x300")
        self.settings_window.resizable(False, False)
        self.settings_window.protocol("WM_DELETE_WINDOW", self._close_settings)

        ctk.CTkLabel(self.settings_window, text="Настройки приложения", font=('Arial', 14, 'bold')).pack(pady=10)

        frame_auto = ctk.CTkFrame(self.settings_window)
        frame_auto.pack(pady=10, padx=20, fill=tk.X)
        ctk.CTkLabel(frame_auto, text="Автозапуск при старте Windows:", font=('Arial', 11)).pack(side=tk.LEFT)

        enabled = is_autostart_enabled()
        status_lbl = ctk.CTkLabel(
            frame_auto,
            text="✅ Включён" if enabled else "❌ Выключен",
            fg_color="green" if enabled else "red"
        )
        status_lbl.pack(side=tk.RIGHT)

        def toggle_autostart():
            nonlocal enabled, status_lbl
            if enabled:
                remove_from_startup()
                enabled = False
                status_lbl.configure(text="❌ Выключен", fg_color="red")
            else:
                add_to_startup()
                enabled = True
                status_lbl.configure(text="✅ Включён", fg_color="green")

        ctk.CTkButton(
            self.settings_window,
            text="Переключить автозапуск",
            command=toggle_autostart,
            width=180
        ).pack(pady=10)

        ctk.CTkLabel(
            self.settings_window,
            text="При включении приложение будет запускаться\nавтоматически после входа в Windows.",
            font=('Arial', 9),
            text_color="gray"
        ).pack(pady=5)

        ctk.CTkButton(
            self.settings_window,
            text="Закрыть",
            command=self._close_settings,
            width=100
        ).pack(pady=20)

    def _close_settings(self):
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()

# ---------- ToolTip ----------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind('<Enter>', self.enter)
        widget.bind('<Leave>', self.leave)

    def enter(self, event):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text, justify=tk.LEFT,
                             fg_color="#ffffe0", text_color="black",
                             font=("Arial", 9))
        label.pack()

    def leave(self, event):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

if __name__ == '__main__':
    root = ctk.CTk()
    root.update()
    app = App(root)
    root.mainloop()