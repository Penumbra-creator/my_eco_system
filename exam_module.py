import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai

class ExamModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'exam', 'Мои экзаменационные вопросы', {})
        self.create_exam_ui()

    def create_exam_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        module_color = "#F8F67F"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Мои экзаменационные вопросы", font=('Arial', 16, 'bold'), fg_color=module_color).pack(pady=8)

        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X)

        ctk.CTkLabel(frame_add, text="Тема:").pack(side=tk.LEFT, padx=2)
        self.entry_topic = ctk.CTkEntry(frame_add, width=15)
        self.entry_topic.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Вопрос:").pack(side=tk.LEFT, padx=2)
        self.entry_question = ctk.CTkEntry(frame_add, width=25)
        self.entry_question.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Ответ:").pack(side=tk.LEFT, padx=2)
        self.entry_answer = ctk.CTkEntry(frame_add, width=25)
        self.entry_answer.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Сложность (1-5):").pack(side=tk.LEFT, padx=2)
        self.entry_difficulty = ctk.CTkEntry(frame_add, width=3)
        self.entry_difficulty.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_exam)
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

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_exams)
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
        self.listbox.bind('<<ListboxSelect>>', self.on_select_exam)

        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=5, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X)

        self.btn_review = ctk.CTkButton(frame_edit, text="📅 Отметить повторение", command=self.mark_reviewed, state=tk.DISABLED)
        self.btn_review.pack(side=tk.LEFT, padx=5)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_exam, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.after(0, self.refresh)   # или self.after(0, self.refresh)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('exam', self._on_loaded)

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

    def generate_aphorism(self):
        topic = tk.simpledialog.askstring("Экзамен", "Введите тему для вопросов:", parent=self)
        if not topic:
            return
        
        prompt = f"""Сгенерируй 5 вопросов с ответами по теме: {topic}. 
Формат: "Вопрос: ... Ответ: ..."."""
        
        response, provider, model = ai.ask_model(prompt, "phi3")
        if response:
            data = {
                "type": "exam",
                "topic": topic,
                "question": response[:50],
                "answer": response,
                "difficulty": "3",
                "correct_count": 0
            }
            self.db.add_entry(data)
            self.refresh()
            messagebox.showinfo("Успех", f"Вопросы сохранены!\n\n{response}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать вопросы.")

    def ask_ai(self):
            from ai_dialog import AIDialog
            AIDialog(self, model_name="phi3", db=self.db)
    

    def add_exam(self):
        topic = self.entry_topic.get().strip()
        question = self.entry_question.get().strip()
        answer = self.entry_answer.get().strip()
        difficulty = self.entry_difficulty.get().strip()
        if not topic or not question or not answer:
            messagebox.showwarning("Пусто", "Тема, вопрос и ответ обязательны.")
            return
        try:
            data = {
                "type": "exam",
                "topic": topic,
                "question": question,
                "answer": answer,
                "difficulty": difficulty or "3",
                "correct_count": 0
            }
            self.db.add_entry(data)
            self.entry_topic.delete(0, tk.END)
            self.entry_question.delete(0, tk.END)
            self.entry_answer.delete(0, tk.END)
            self.entry_difficulty.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Вопрос сохранён!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_exam(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        key, data = self.cache[index]
        self.editing_key = key
        self.btn_edit.configure(state=tk.NORMAL)
        self.btn_delete.configure(state=tk.NORMAL)
        self.btn_review.configure(state=tk.NORMAL)

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
        edit_win.title("Редактирование вопроса")
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

        Label(edit_win, text="Сложность (1-5):").pack(pady=5)
        difficulty_entry = Entry(edit_win, width=10)
        difficulty_entry.insert(0, data.get('difficulty', '3'))
        difficulty_entry.pack(pady=5)

        def save_changes():
            new_topic = topic_entry.get().strip()
            new_question = question_entry.get().strip()
            new_answer = answer_entry.get().strip()
            new_difficulty = difficulty_entry.get().strip()
            if not new_topic or not new_question or not new_answer:
                messagebox.showwarning("Пусто", "Все поля обязательны.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'topic': new_topic,
                    'question': new_question,
                    'answer': new_answer,
                    'difficulty': new_difficulty
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")

        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_exam(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить этот вопрос?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        self.search_exams()

    def search_exams(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if query in data.get('topic', '').lower() or query in data.get('question', '').lower() or query in data.get('answer', '').lower():
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
        """Отмечает выбранную запись как повторённую"""
        if not self.editing_key:
            messagebox.showinfo("Инфо", "Сначала выберите запись.")
            return
        try:
            self.db.mark_reviewed(self.editing_key)
            self.refresh()
            messagebox.showinfo("Успех", "Запись отмечена как повторённая!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отметить: {e}")
    def cancel_edit(self):
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.editing_key = None
        self.btn_review.configure(state=tk.DISABLED)