import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai
from ai_dialog import AIDialog
from tts_engine import HybridTTS  # импорт движка TTS

class LanguageModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'language', 'Мои слова и фразы', {})
        self.tts = HybridTTS()  # инициализация TTS
        self.create_language_ui()

        # Панель фильтров
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поиск
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        ctk.CTkEntry(filter_frame, textvariable=self.search_var, placeholder_text="🔍 Поиск слова...", width=200).pack(side=tk.LEFT, padx=5)

        # Чекбокс "Показать только горящие"
        self.show_hot_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(filter_frame, text="🔥 Только горящие", variable=self.show_hot_var, command=self.apply_filters).pack(side=tk.LEFT, padx=5)

        # Сортировка
        sort_options = [
            "По срочности (горящие сверху)",
            "По алфавиту (А-Я)",
            "По дате добавления (новые)",
            "По дате добавления (старые)"
        ]
        self.sort_var = tk.StringVar(value="По срочности (горящие сверху)")
        ctk.CTkComboBox(filter_frame, values=sort_options, variable=self.sort_var, command=self.apply_filters, width=180).pack(side=tk.LEFT, padx=5)

        # Кнопка экспорта
        ctk.CTkButton(filter_frame, text="📤 Экспорт", command=self.export_data, width=100).pack(side=tk.RIGHT, padx=5)

        # Текстовое поле для вывода
        self.display_area = ctk.CTkTextbox(self, wrap=tk.WORD, font=("Arial", 12))
        self.display_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # После создания виджетов — загружаем данные
        self.apply_filters()

    def create_language_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        module_color = "#FFB16C"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Мои слова и фразы", font=('Arial', 16, 'bold'), fg_color=module_color).pack(pady=8)

        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X)

        ctk.CTkLabel(frame_add, text="Слово:").pack(side=tk.LEFT, padx=2)
        self.entry_word = ctk.CTkEntry(frame_add, width=15)
        self.entry_word.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Перевод:").pack(side=tk.LEFT, padx=2)
        self.entry_translation = ctk.CTkEntry(frame_add, width=15)
        self.entry_translation.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Контекст:").pack(side=tk.LEFT, padx=2)
        self.entry_context = ctk.CTkEntry(frame_add, width=20)
        self.entry_context.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Язык:").pack(side=tk.LEFT, padx=2)
        self.lang_var = tk.StringVar(value="en")
        lang_menu = ttk.Combobox(frame_add, textvariable=self.lang_var, values=["en", "de"], width=5)
        lang_menu.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_word)
        btn_add.pack(side=tk.LEFT, padx=5)
        btn_refresh = ctk.CTkButton(frame_add, text="🔄 Обновить", command=self.refresh)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        container_search = ctk.CTkFrame(self, fg_color=module_color)
        container_search.pack(pady=5, padx=10, fill=tk.X)
        frame_search = ctk.CTkFrame(container_search, fg_color='white')
        frame_search.pack(fill=tk.X)

        ctk.CTkLabel(frame_search, text="Поиск:").pack(side=tk.LEFT, padx=5)
        self.entry_search = ctk.CTkEntry(frame_search, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind('<KeyRelease>', self.on_search_key)

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_words)
        btn_search.pack(side=tk.LEFT, padx=5)
        btn_clear_search = ctk.CTkButton(frame_search, text="✖ Сбросить", command=self.clear_search)
        btn_clear_search.pack(side=tk.LEFT, padx=5)

        # ---- КНОПКА ГЕНЕРАЦИИ ИИ ----
        btn_generate = ctk.CTkButton(frame_add, text="🤖 Сгенерировать", command=self.generate_aphorism)
        btn_generate.pack(side=tk.LEFT, padx=5)

        btn_ask = ctk.CTkButton(frame_add, text="💬 Спросить ИИ", command=self.ask_ai)
        btn_ask.pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(self, width=80, height=15, font=('Arial', 10))
        self.listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_word)

        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=5, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X)

        self.btn_review = ctk.CTkButton(frame_edit, text="📅 Отметить повторение", command=self.mark_reviewed, state=tk.DISABLED)
        self.btn_review.pack(side=tk.LEFT, padx=5)

        # ---- КНОПКА ОЗВУЧИВАНИЯ (добавлена) ----
        self.btn_speak = ctk.CTkButton(frame_edit, text="🔊 Озвучить", command=self.speak_selected, state=tk.DISABLED)
        self.btn_speak.pack(side=tk.LEFT, padx=5)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_word, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.after(0, self.refresh)   # или self.after(0, self.refresh)

    # ---------- ОСНОВНЫЕ МЕТОДЫ ----------
    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('language', self._on_loaded)

    def _on_loaded(self, entries, error):
        self.listbox.delete(0, tk.END)
        if error:
            self.listbox.insert(tk.END, f"❌ Ошибка: {error}")
            return
        try:
            if entries is None:
                entries = []
            entries.sort(key=lambda x: x[1].get('timestamp', ''))
            self.cache = entries
            for i, (key, data) in enumerate(entries, start=1):
                title = data.get('title', 'Без названия')
                self.listbox.insert(tk.END, f"{i}. {title[:40]}")
        except Exception as e:
            self.listbox.insert(tk.END, f"Ошибка загрузки: {e}")
        self.cancel_edit()

    def add_word(self):
        word = self.entry_word.get().strip()
        translation = self.entry_translation.get().strip()
        context = self.entry_context.get().strip()
        lang = self.lang_var.get()
        if not word or not translation:
            messagebox.showwarning("Пусто", "Слово и перевод обязательны.")
            return
        try:
            data = {
                "type": "language",
                "word": word,
                "translation": translation,
                "context": context,
                "lang": lang
            }
            self.db.add_entry(data)
            self.entry_word.delete(0, tk.END)
            self.entry_translation.delete(0, tk.END)
            self.entry_context.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Слово сохранено!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_word(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        key, data = self.cache[index]
        self.editing_key = key
        self.btn_edit.configure(state=tk.NORMAL)
        self.btn_delete.configure(state=tk.NORMAL)
        self.btn_review.configure(state=tk.NORMAL)
        self.btn_speak.configure(state=tk.NORMAL)   # активируем кнопку озвучивания

    def enable_edit(self):
        if not self.editing_key:
            return
        key, data = None, None
        for k, d in self.cache:
            if k == self.editing_key:
                key, data = k, d
                break
        if not data:
            return

        edit_win = Toplevel(self)
        edit_win.title("Редактирование слова")
        edit_win.geometry("400x350")

        Label(edit_win, text="Слово:").pack(pady=5)
        word_entry = Entry(edit_win, width=30)
        word_entry.insert(0, data.get('word', ''))
        word_entry.pack(pady=5)

        Label(edit_win, text="Перевод:").pack(pady=5)
        trans_entry = Entry(edit_win, width=30)
        trans_entry.insert(0, data.get('translation', ''))
        trans_entry.pack(pady=5)

        Label(edit_win, text="Контекст:").pack(pady=5)
        context_entry = Entry(edit_win, width=30)
        context_entry.insert(0, data.get('context', ''))
        context_entry.pack(pady=5)

        Label(edit_win, text="Язык:").pack(pady=5)
        lang_var = tk.StringVar(value=data.get('lang', 'en'))
        lang_combo = ttk.Combobox(edit_win, textvariable=lang_var, values=["en", "de"], width=10)
        lang_combo.pack(pady=5)

        def save_changes():
            new_word = word_entry.get().strip()
            new_trans = trans_entry.get().strip()
            new_context = context_entry.get().strip()
            new_lang = lang_var.get()
            if not new_word or not new_trans:
                messagebox.showwarning("Пусто", "Слово и перевод обязательны.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'word': new_word,
                    'translation': new_trans,
                    'context': new_context,
                    'lang': new_lang
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")

        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_word(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить это слово?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def cancel_edit(self):
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.btn_review.configure(state=tk.DISABLED)
        self.btn_speak.configure(state=tk.DISABLED)  # деактивируем кнопку озвучивания
        self.editing_key = None

    def speak_selected(self):
        """Озвучивает выбранное слово и перевод."""
        if not self.editing_key:
            return
        for key, data in self.cache:
            if key == self.editing_key:
                word = data.get('word', '')
                translation = data.get('translation', '')
                if word:
                    text = f"{word} — {translation}"
                    self.tts.speak(text)
                return

    # ---------- ФИЛЬТРАЦИЯ, ПОИСК, ЭКСПОРТ ----------
    def apply_filters(self, *args):
        from datetime import datetime, timedelta
        entries = self.db.get_entries('language')

        search_text = self.search_var.get().lower()
        if search_text:
            entries = [e for e in entries
                       if search_text in e[1].get('word', '').lower()
                       or search_text in e[1].get('translation', '').lower()]

        if self.show_hot_var.get():
            today = datetime.now().date()
            threshold = today - timedelta(days=3)
            entries = [e for e in entries
                       if e[1].get('last_review') is None
                       or datetime.strptime(e[1].get('last_review', '2000-01-01'), '%Y-%m-%d').date() < threshold]

        sort_type = self.sort_var.get()
        if sort_type == "По срочности (горящие сверху)":
            def hot_score(entry):
                last_review = entry[1].get('last_review')
                if last_review is None:
                    return 0
                try:
                    days_since = (datetime.now().date() - datetime.strptime(last_review, '%Y-%m-%d').date()).days
                    return days_since
                except:
                    return 0
            entries.sort(key=lambda x: hot_score(x), reverse=True)
        elif sort_type == "По алфавиту (А-Я)":
            entries.sort(key=lambda x: x[1].get('word', '').lower())
        elif sort_type == "По дате добавления (новые)":
            entries.sort(key=lambda x: x[1].get('date', ''), reverse=True)
        elif sort_type == "По дате добавления (старые)":
            entries.sort(key=lambda x: x[1].get('date', ''))

        self.display_entries(entries)

    def display_entries(self, entries):
        self.display_area.delete('1.0', tk.END)
        from datetime import datetime, timedelta
        today = datetime.now().date()
        threshold = today - timedelta(days=3)

        for idx, (doc_id, data) in enumerate(entries, 1):
            word = data.get('word', '')
            translation = data.get('translation', '')
            date_added = data.get('date', '')
            last_review = data.get('last_review', '')
            interval = data.get('interval', '')

            is_hot = False
            if last_review is None:
                is_hot = True
            else:
                try:
                    if datetime.strptime(last_review, '%Y-%m-%d').date() < threshold:
                        is_hot = True
                except:
                    pass

            prefix = "🔥 " if is_hot else "   "
            self.display_area.insert(tk.END, f"{prefix}{idx}. {word} — {translation}\n")
            if date_added:
                self.display_area.insert(tk.END, f"   📅 Добавлено: {date_added}")
            if last_review:
                self.display_area.insert(tk.END, f"   🔄 Повтор: {last_review}")
            if interval:
                self.display_area.insert(tk.END, f"   📆 Интервал: {interval} дн.")
            self.display_area.insert(tk.END, "\n" + "-"*50 + "\n")

    def export_data(self):
        entries = self.db.get_entries('language')
        search_text = self.search_var.get().lower()
        if search_text:
            entries = [e for e in entries
                       if search_text in e[1].get('word', '').lower()
                       or search_text in e[1].get('translation', '').lower()]
        from export_utils import export_to_json
        export_to_json(entries, "languages.json")

    def on_search_key(self, event):
        self.search_words()

    def search_words(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if query in data.get('word', '').lower() or query in data.get('translation', '').lower() or query in data.get('context', '').lower():
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            word = data.get('word', '')
            translation = data.get('translation', '')
            self.listbox.insert(tk.END, f"{i}. {word} — {translation}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def mark_reviewed(self):
        if not self.editing_key:
            messagebox.showinfo("Инфо", "Сначала выберите запись.")
            return
        try:
            self.db.mark_reviewed(self.editing_key)
            self.refresh()
            messagebox.showinfo("Успех", "Запись отмечена как повторённая!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отметить: {e}")

    def generate_aphorism(self):
        word = tk.simpledialog.askstring("Языки", "Введите слово для практики:", parent=self)
        if not word:
            return
        lang = self.lang_var.get() or "en"

        prompt = f"""Составь 3 предложения с использованием слова '{word}' на языке {lang}.
Дай перевод на русский для каждого предложения.
Формат:
1. (на {lang}) ...
Перевод: ..."""

        response, provider, model = ai.ask_model(prompt, "mistral")
        if response:
            data = {
                "type": "language",
                "word": word,
                "translation": response,
                "context": f"Сгенерировано с помощью {provider} ({model})",
                "lang": lang
            }
            self.db.add_entry(data)
            self.refresh()
            messagebox.showinfo("Успех", f"Предложения сохранены!\n\n{response}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать предложения.")

    def ask_ai(self):
        from ai_dialog import AIDialog
        AIDialog(self, model_name="phi3", db=self.db)