import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai

class ConflictModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'conflict', 'Симуляция конфликтов', {})
        self.create_conflict_ui()

    def create_conflict_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        module_color = "#A9A9FF"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Симуляция конфликтов", font=('Arial', 16, 'bold'), fg_color=module_color).pack(pady=8)

        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X)

        ctk.CTkLabel(frame_add, text="Ситуация:").pack(side=tk.LEFT, padx=2)
        self.entry_situation = ctk.CTkEntry(frame_add, width=25)
        self.entry_situation.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Стратегия:").pack(side=tk.LEFT, padx=2)
        self.entry_strategy = ctk.CTkEntry(frame_add, width=20)
        self.entry_strategy.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Оценка (0-10):").pack(side=tk.LEFT, padx=2)
        self.entry_assessment = ctk.CTkEntry(frame_add, width=4)
        self.entry_assessment.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_conflict)
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

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_conflicts)
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
        self.listbox.bind('<<ListboxSelect>>', self.on_select_conflict)

        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=5, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_conflict, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.after(0, self.refresh)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('conflict', self._on_loaded)

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
        situation = tk.simpledialog.askstring("Конфликт", "Опишите конфликтную ситуацию:", parent=self)
        if not situation:
            return
        prompt = f"""Смоделируй конфликтную ситуацию: {situation}. Предложи 3 стратегии выхода и их возможные последствия. Оцени каждую стратегию (эффективность, риски)."""
        response, provider, model = ai.ask_model(prompt, "mistral")
        if response:
            data = {
                "type": "conflict",
                "situation": situation,
                "strategy": response,
                "assessment": "0",
                "notes": f"Сгенерировано с помощью {provider} ({model})"
            }
            self.db.add_entry(data)
            self.refresh()
            messagebox.showinfo("Успех", f"Стратегии сохранены!\n\n{response}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать стратегии.")

    def ask_ai(self):
        from ai_dialog import AIDialog
        AIDialog(self, model_name="mistral", db=self.db)

    def add_conflict(self):
        situation = self.entry_situation.get().strip()
        strategy = self.entry_strategy.get().strip()
        assessment = self.entry_assessment.get().strip()
        if not situation:
            messagebox.showwarning("Пусто", "Ситуация обязательна.")
            return
        try:
            data = {
                "type": "conflict",
                "situation": situation,
                "strategy": strategy,
                "assessment": assessment or "0",
                "notes": ""
            }
            self.db.add_entry(data)
            self.entry_situation.delete(0, tk.END)
            self.entry_strategy.delete(0, tk.END)
            self.entry_assessment.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Конфликт сохранён!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_conflict(self, event):
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
        edit_win.title("Редактирование конфликта")
        edit_win.geometry("450x350")
        Label(edit_win, text="Ситуация:").pack(pady=5)
        situation_entry = Entry(edit_win, width=40)
        situation_entry.insert(0, data.get('situation', ''))
        situation_entry.pack(pady=5)
        Label(edit_win, text="Стратегия:").pack(pady=5)
        strategy_entry = Entry(edit_win, width=40)
        strategy_entry.insert(0, data.get('strategy', ''))
        strategy_entry.pack(pady=5)
        Label(edit_win, text="Оценка (0-10):").pack(pady=5)
        assessment_entry = Entry(edit_win, width=10)
        assessment_entry.insert(0, data.get('assessment', '0'))
        assessment_entry.pack(pady=5)
        Label(edit_win, text="Заметки:").pack(pady=5)
        notes_text = scrolledtext.ScrolledText(edit_win, height=5, width=40)
        notes_text.insert('1.0', data.get('notes', ''))
        notes_text.pack(pady=5)
        def save_changes():
            new_situation = situation_entry.get().strip()
            new_strategy = strategy_entry.get().strip()
            new_assessment = assessment_entry.get().strip()
            new_notes = notes_text.get('1.0', 'end-1c').strip()
            if not new_situation:
                messagebox.showwarning("Пусто", "Ситуация обязательна.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'situation': new_situation,
                    'strategy': new_strategy,
                    'assessment': new_assessment or "0",
                    'notes': new_notes
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")
        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_conflict(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить этот конфликт?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        self.search_conflicts()

    def search_conflicts(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if query in data.get('situation', '').lower() or query in data.get('strategy', '').lower() or query in data.get('notes', '').lower():
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            situation = data.get('situation', '')
            self.listbox.insert(tk.END, f"{i}. {situation[:40]}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def cancel_edit(self):
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.editing_key = None