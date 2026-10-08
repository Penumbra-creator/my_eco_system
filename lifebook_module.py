import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai

class LifebookModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'lifebook', 'Книга жизни', {})
        self.create_lifebook_ui()

    def create_lifebook_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        module_color = "#FFD900"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Книга жизни", font=('Arial', 16, 'bold'), fg_color=module_color).pack(pady=8)

        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X)

        ctk.CTkLabel(frame_add, text="Событие:").pack(side=tk.LEFT, padx=2)
        self.entry_event = ctk.CTkEntry(frame_add, width=30)
        self.entry_event.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Эмоция:").pack(side=tk.LEFT, padx=2)
        self.entry_emotion = ctk.CTkEntry(frame_add, width=15)
        self.entry_emotion.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Урок:").pack(side=tk.LEFT, padx=2)
        self.entry_lesson = ctk.CTkEntry(frame_add, width=20)
        self.entry_lesson.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_lifebook)
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

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_lifebook)
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
        self.listbox.bind('<<ListboxSelect>>', self.on_select_lifebook)

        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=5, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_lifebook, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.after(0, self.refresh)   # или self.after(0, self.refresh)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('lifebook', self._on_loaded)

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
        event = tk.simpledialog.askstring("Книга жизни", "Опишите значимое событие:", parent=self)
        if not event:
            return
        
        prompt = f"""Осмысли событие: {event}. 
Сформулируй: 1) эмоцию, которую оно вызвало, 2) главный урок, который ты извлёк, 3) как это повлияло на твою жизнь."""
        
        response, provider, model = ai.ask_model(prompt, "llama3.2")
        if response:
            data = {
                "type": "lifebook",
                "event": event[:50],
                "emotion": "рефлексия",
                "lesson": response,
                "tags": f"ИИ-рефлексия ({provider})"
            }
            self.db.add_entry(data)
            self.refresh()
            messagebox.showinfo("Успех", f"Рефлексия сохранена!\n\n{response}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать рефлексию.")
    def ask_ai(self):
            from ai_dialog import AIDialog
            AIDialog(self, model_name="llama3.2", db=self.db)
        
       
    def add_lifebook(self):
        event = self.entry_event.get().strip()
        emotion = self.entry_emotion.get().strip()
        lesson = self.entry_lesson.get().strip()
        if not event:
            messagebox.showwarning("Пусто", "Событие обязательно.")
            return
        try:
            data = {
                "type": "lifebook",
                "event": event,
                "emotion": emotion,
                "lesson": lesson,
                "tags": ""
            }
            self.db.add_entry(data)
            self.entry_event.delete(0, tk.END)
            self.entry_emotion.delete(0, tk.END)
            self.entry_lesson.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Событие сохранено!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_lifebook(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        key, data = self.cache[index]
        self.editing_key = key
        self.btn_edit.configure(state=tk.NORMAL)
        self.btn_delete.configure(state=tk.NORMAL)

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
        edit_win.title("Редактирование события")
        edit_win.geometry("450x400")

        Label(edit_win, text="Событие:").pack(pady=5)
        event_entry = Entry(edit_win, width=40)
        event_entry.insert(0, data.get('event', ''))
        event_entry.pack(pady=5)

        Label(edit_win, text="Эмоция:").pack(pady=5)
        emotion_entry = Entry(edit_win, width=40)
        emotion_entry.insert(0, data.get('emotion', ''))
        emotion_entry.pack(pady=5)

        Label(edit_win, text="Урок:").pack(pady=5)
        lesson_entry = Entry(edit_win, width=40)
        lesson_entry.insert(0, data.get('lesson', ''))
        lesson_entry.pack(pady=5)

        Label(edit_win, text="Теги:").pack(pady=5)
        tags_entry = Entry(edit_win, width=40)
        tags_entry.insert(0, data.get('tags', ''))
        tags_entry.pack(pady=5)

        def save_changes():
            new_event = event_entry.get().strip()
            new_emotion = emotion_entry.get().strip()
            new_lesson = lesson_entry.get().strip()
            new_tags = tags_entry.get().strip()
            if not new_event:
                messagebox.showwarning("Пусто", "Событие обязательно.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'event': new_event,
                    'emotion': new_emotion,
                    'lesson': new_lesson,
                    'tags': new_tags
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")

        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_lifebook(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить это событие?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        self.search_lifebook()

    def search_lifebook(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if query in data.get('event', '').lower() or query in data.get('emotion', '').lower() or query in data.get('lesson', '').lower() or query in data.get('tags', '').lower():
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            event = data.get('event', '')
            self.listbox.insert(tk.END, f"{i}. {event[:40]}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def cancel_edit(self):
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.editing_key = None