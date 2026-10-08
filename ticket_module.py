import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai
from datetime import datetime
class TicketModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'ticket', 'Мои билеты', {})
        self.create_ticket_ui()
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        ctk.CTkEntry(filter_frame, textvariable=self.search_var, placeholder_text="🔍 Поиск...", width=200).pack(side=tk.LEFT, padx=5)

        # Чекбокс "Только требующие повторения" (например, last_review > 7 дней)
        self.need_review_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(filter_frame, text="Требуют повторения", variable=self.need_review_var, command=self.apply_filters).pack(side=tk.LEFT, padx=5)

        # Сортировка
        sort_options = ["По дате повторения (старые)", "По дате повторения (новые)", "По дате добавления"]
        self.sort_var = tk.StringVar(value="По дате повторения (старые)")
        ctk.CTkComboBox(filter_frame, values=sort_options, variable=self.sort_var, command=self.apply_filters, width=180).pack(side=tk.LEFT, padx=5)

        ctk.CTkButton(filter_frame, text="📤 Экспорт", command=self.export_data, width=100).pack(side=tk.RIGHT, padx=5)

        self.display_area = ctk.CTkTextbox(self, wrap=tk.WORD, font=("Arial", 12))
        self.display_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.apply_filters()

    def export_data(self):
        self.export_module_data()

    def create_ticket_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        module_color = "#CDBFFF"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Мои билеты", font=('Arial', 16, 'bold'), text_color="#333333").pack(pady=8)

        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='#ffffff')
        frame_add.pack(fill=tk.X, padx=5, pady=5)

        ctk.CTkLabel(frame_add, text="Тема:").pack(side=tk.LEFT, padx=2)
        self.entry_topic = ctk.CTkEntry(frame_add, width=120)
        self.entry_topic.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Вопрос:").pack(side=tk.LEFT, padx=2)
        self.entry_question = ctk.CTkEntry(frame_add, width=180)
        self.entry_question.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Ответ:").pack(side=tk.LEFT, padx=2)
        self.entry_answer = ctk.CTkEntry(frame_add, width=180)
        self.entry_answer.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Источник:").pack(side=tk.LEFT, padx=2)
        self.entry_source = ctk.CTkEntry(frame_add, width=100)
        self.entry_source.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Стр.").pack(side=tk.LEFT, padx=2)
        self.entry_page = ctk.CTkEntry(frame_add, width=50)
        self.entry_page.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_ticket, width=100)
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_refresh = ctk.CTkButton(frame_add, text="🔄 Обновить", command=self.refresh, width=100)
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_due = ctk.CTkButton(frame_add, text="📊 Просроченные", command=self.show_due, width=110)
        btn_due.pack(side=tk.LEFT, padx=5)

        container_search = ctk.CTkFrame(self, fg_color=module_color)
        container_search.pack(pady=5, padx=10, fill=tk.X)
        frame_search = ctk.CTkFrame(container_search, fg_color='#ffffff')
        frame_search.pack(fill=tk.X, padx=5, pady=5)

        ctk.CTkLabel(frame_search, text="Поиск:").pack(side=tk.LEFT, padx=5)
        self.entry_search = ctk.CTkEntry(frame_search, width=250)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind('<KeyRelease>', self.on_search_key)

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_tickets, width=90)
        btn_search.pack(side=tk.LEFT, padx=5)
        
        btn_clear_search = ctk.CTkButton(frame_search, text="✖ Сбросить", command=self.clear_search, width=90)
        btn_clear_search.pack(side=tk.LEFT, padx=5)

        btn_generate = ctk.CTkButton(frame_search, text="🤖 Сгенерировать", command=self.generate_aphorism, width=130)
        btn_generate.pack(side=tk.LEFT, padx=5)

        btn_ask = ctk.CTkButton(frame_search, text="💬 Спросить ИИ", command=self.ask_ai, width=110)
        btn_ask.pack(side=tk.LEFT, padx=5)
# Кнопка обычного добавления
        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_ticket, width=100)
        btn_add.pack(side=tk.LEFT, padx=5)

        # ВОТ ТУТ МЫ ДОБАВЛЯЕМ КНОПКУ МАССОВОГО ИМПОРТА:
        btn_mass = ctk.CTkButton(frame_add, text="📋 Массовый импорт", command=self.mass_import_from_clipboard, width=130)
        btn_mass.pack(side=tk.LEFT, padx=5)
        # Список (оставляем tk.Listbox, так как в CTk нет аналога)
        self.listbox = tk.Listbox(self, width=80, height=15, font=('Arial', 10), bg="#FFFFFF", fg="#ffffff", selectbackground="#1f538d")
        self.listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_ticket)

        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=5, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='#ffffff')
        frame_edit.pack(fill=tk.X, padx=5, pady=5)

        self.btn_review = ctk.CTkButton(frame_edit, text="📅 Отметить повторение", command=self.mark_reviewed, state="disabled")
        self.btn_review.pack(side=tk.LEFT, padx=5)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state="disabled")
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        
        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_ticket, state="disabled", fg_color="#d9534f", hover_color="#c9302c")
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.after(0, self.refresh)   # или self.after(0, self.refresh)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('ticket', self._on_loaded)

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

    def apply_filters(self, *args):
        entries = self.db.get_entries('ticket')
        search_text = self.search_var.get().lower()
        if search_text:
            entries = [e for e in entries if search_text in e[1].get('content', '').lower()]
        
        # Фильтр "требуют повторения" (last_review > 7 дней)
        if self.need_review_var.get():
            from datetime import datetime, timedelta
            today = datetime.now().date()
            threshold = today - timedelta(days=7)
            entries = [e for e in entries if datetime.strptime(e[1].get('last_review', '2000-01-01'), '%Y-%m-%d').date() < threshold]
        
        sort_type = self.sort_var.get()
        if sort_type == "По дате повторения (старые)":
            entries.sort(key=lambda x: x[1].get('last_review', '2000-01-01'))
        elif sort_type == "По дате повторения (новые)":
            entries.sort(key=lambda x: x[1].get('last_review', '2000-01-01'), reverse=True)
        elif sort_type == "По дате добавления":
            entries.sort(key=lambda x: x[1].get('date', ''), reverse=True)
        self.display_entries(entries)
        
    def display_entries(self, entries):
        self.display_area.delete('1.0', tk.END)
        for idx, (doc_id, data) in enumerate(entries, 1):
            content = data.get('content', '')
            last_review = data.get('last_review', '')
            date = data.get('date', '')
            self.display_area.insert(tk.END, f"{idx}. {content}\n")
            if last_review:
                self.display_area.insert(tk.END, f"   🔄 Последнее повторение: {last_review}")
            if date:
                self.display_area.insert(tk.END, f"   📆 Добавлен: {date}")
            self.display_area.insert(tk.END, "\n" + "-"*50 + "\n")
    def generate_aphorism(self):
        topic = tk.simpledialog.askstring("Билет", "Введите тему билета:", parent=self)
        if not topic:
            return
        source = tk.simpledialog.askstring("Билет", "Введите источник (книга, статья):", parent=self)
        
        prompt = f"Создай билет (вопрос-ответ) по теме: {topic}. Источник: {source or 'нет'}. Формат: 'Вопрос: ... Ответ: ...'."
        response, provider, model = ai.ask_model(prompt, "llama3.2")
        
        if response:
            parts = response.split("Ответ:")
            question = parts[0].replace("Вопрос:", "").strip() if len(parts) > 0 else response[:50]
            answer = parts[1].strip() if len(parts) > 1 else response[:50]
            
            data = {
                "type": "ticket",
                "topic": topic,
                "question": question,
                "answer": answer,
                "source": source or "",
                "page": ""
            }
            self.db.add_entry(data)
            self.refresh()
            messagebox.showinfo("Успех", f"Билет сохранён!\n\nВопрос: {question}\nОтвет: {answer}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать билет.")

    def ask_ai(self):
        from ai_dialog import AIDialog
        AIDialog(self, model_name="llama3.2", db=self.db)

    def show_due(self):
        due_entries = self.db.get_due_entries(self.module_type) if hasattr(self.db, 'get_due_entries') else []
        if not due_entries:
            messagebox.showinfo("Инфо", "Нет просроченных записей!")
            return

        due_win = Toplevel(self)
        due_win.title("Просроченные записи")
        due_win.geometry("600x400")

        listbox = tk.Listbox(due_win, width=80, height=15)
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        due_cache = []
        for key, data in due_entries:
            text = f"{data.get('topic', '')}: {data.get('question', '')[:30]}"
            listbox.insert(tk.END, text)
            due_cache.append((key, data))

        def mark_selected():
            selection = listbox.curselection()
            if not selection:
                return
            index = selection[0]
            key, _ = due_cache[index]
            try:
                if hasattr(self.db, 'mark_reviewed'):
                    self.db.mark_reviewed(key)
                listbox.delete(index)
                due_cache.pop(index)
                if not due_cache:
                    due_win.destroy()
                    messagebox.showinfo("Успех", "Все записи повторены!")
                else:
                    messagebox.showinfo("Успех", "Запись отмечена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось отметить: {e}")

        Button(due_win, text="📅 Отметить выбранное", command=mark_selected).pack(pady=5)
        Button(due_win, text="Закрыть", command=due_win.destroy).pack(pady=5)

    def add_ticket(self):
        topic = self.entry_topic.get().strip()
        question = self.entry_question.get().strip()
        answer = self.entry_answer.get().strip()
        source = self.entry_source.get().strip()
        page = self.entry_page.get().strip()
        
        if not topic or not question or not answer:
            messagebox.showwarning("Пусто", "Тема, вопрос и ответ обязательны.")
            return
        try:
            data = {
                "type": "ticket",
                "topic": topic,
                "question": question,
                "answer": answer,
                "source": source,
                "page": page
            }
            self.db.add_entry(data)
            self.entry_topic.delete(0, tk.END)
            self.entry_question.delete(0, tk.END)
            self.entry_answer.delete(0, tk.END)
            self.entry_source.delete(0, tk.END)
            self.entry_page.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Билет сохранён!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    def mass_import_from_clipboard(self):
        try:
            # Получаем весь текст из буфера обмена операционной системы
            clipboard_data = self.clipboard_get()
            if not clipboard_data.strip():
                messagebox.showwarning("Пусто", "Буфер обмена пуст! Скопируйте текст перед импортом.")
                return

            # Разделяем текст по строкам
            lines = clipboard_data.split('\n')
            imported_count = 0

            for line in lines:
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue # Пропускаем пустые строки
                
                # Формируем структуру данных для базы (подгоняй под поля своего модуля)
                data = {
                    "type": self.module_type,
                    "title": cleaned_line,  # или "content": cleaned_line
                    "timestamp": str(datetime.now()) # если нужно
                }
                
                # Загоняем в базу данных Firebase
                self.db.add_entry(data)
                imported_count += 1

            self.refresh()
            messagebox.showinfo("Успех!", f"Успешно импортировано записей: {imported_count}")

        except Exception as e:
            messagebox.showerror("Ошибка импорта", f"Не удалось прочитать буфер обмена: {e}")
    def on_select_ticket(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index < len(self.cache):
            key, data = self.cache[index]
            self.editing_key = key
            self.btn_edit.configure(state="normal")
            self.btn_delete.configure(state="normal")
            self.btn_review.configure(state="normal")

    def enable_edit(self):
        if not self.editing_key:
            return
        data = None
        for k, d in self.cache:
            if k == self.editing_key:
                data = d
                break
        if not data:
            return

        edit_win = Toplevel(self)
        edit_win.title("Редактирование билета")
        edit_win.geometry("450x400")

        Label(edit_win, text="Тема:").pack(pady=5)
        topic_entry = Entry(edit_win, width=40)
        topic_entry.insert(0, data.get('topic', ''))
        topic_entry.pack(pady=5)

        Label(edit_win, text="Вопрос:").pack(pady=5)
        question_entry = Entry(edit_win, width=40)
        question_entry.insert(0, data.get('question', ''))
        question_entry.pack(pady=5)

        Label(edit_win, text="Ответ:").pack(pady=5)
        answer_entry = Entry(edit_win, width=40)
        answer_entry.insert(0, data.get('answer', ''))
        answer_entry.pack(pady=5)

        Label(edit_win, text="Источник:").pack(pady=5)
        source_entry = Entry(edit_win, width=40)
        source_entry.insert(0, data.get('source', ''))
        source_entry.pack(pady=5)

        Label(edit_win, text="Страница:").pack(pady=5)
        page_entry = Entry(edit_win, width=10)
        page_entry.insert(0, data.get('page', ''))
        page_entry.pack(pady=5)

        def save_changes():
            new_topic = topic_entry.get().strip()
            new_question = question_entry.get().strip()
            new_answer = answer_entry.get().strip()
            new_source = source_entry.get().strip()
            new_page = page_entry.get().strip()
            
            if not new_topic or not new_question or not new_answer:
                messagebox.showwarning("Пусто", "Тема, вопрос и ответ обязательны.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'topic': new_topic,
                    'question': new_question,
                    'answer': new_answer,
                    'source': new_source,
                    'page': new_page
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")

        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_ticket(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить этот билет?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        self.search_tickets()

    def search_tickets(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if (query in data.get('topic', '').lower() or 
                query in data.get('question', '').lower() or 
                query in data.get('answer', '').lower() or 
                query in data.get('source', '').lower()):
                filtered.append((key, data))
        
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            topic = data.get('topic', '')
            question = data.get('question', '')
            self.listbox.insert(tk.END, f"{i}. {topic}: {question[:30]}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def mark_reviewed(self):
        if not self.editing_key:
            messagebox.showinfo("Инфо", "Сначала выберите запись.")
            return
        try:
            if hasattr(self.db, 'mark_reviewed'):
                self.db.mark_reviewed(self.editing_key)
            self.refresh()
            messagebox.showinfo("Успех", "Запись отмечена как повторённая!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отметить: {e}")

    def cancel_edit(self):
        if hasattr(self, 'btn_edit') and self.btn_edit:
            self.btn_edit.configure(state="disabled")
        if hasattr(self, 'btn_delete') and self.btn_delete:
            self.btn_delete.configure(state="disabled")
        if hasattr(self, 'btn_review') and self.btn_review:
            self.btn_review.configure(state="disabled")
        self.editing_key = None