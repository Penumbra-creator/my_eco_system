import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai

class MotorModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'motor', 'Тренировки моторики', {})
        self.create_motor_ui()

    def create_motor_ui(self):
        print("create_motor_ui start")
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self, fg_color="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        module_color = "#B6FFDB"
        header_frame = ctk.CTkFrame(main_frame, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Тренировки моторики", font=('Arial', 16, 'bold'), fg_color=module_color).pack(pady=8)

        container_add = ctk.CTkFrame(main_frame, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X, padx=5, pady=5)

        ctk.CTkLabel(frame_add, text="Упражнение:").pack(side=tk.LEFT, padx=2)
        self.entry_exercise = ctk.CTkEntry(frame_add, width=20)
        self.entry_exercise.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Время (сек):").pack(side=tk.LEFT, padx=2)
        self.entry_duration = ctk.CTkEntry(frame_add, width=6)
        self.entry_duration.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Точность (0-1):").pack(side=tk.LEFT, padx=2)
        self.entry_accuracy = ctk.CTkEntry(frame_add, width=5)
        self.entry_accuracy.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Ошибки:").pack(side=tk.LEFT, padx=2)
        self.entry_errors = ctk.CTkEntry(frame_add, width=5)
        self.entry_errors.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_motor)
        btn_add.pack(side=tk.LEFT, padx=5)
        btn_refresh = ctk.CTkButton(frame_add, text="🔄 Обновить", command=self.refresh)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        container_search = ctk.CTkFrame(main_frame, fg_color=module_color)
        container_search.pack(pady=5, padx=10, fill=tk.X)
        frame_search = ctk.CTkFrame(container_search, fg_color='white')
        frame_search.pack(fill=tk.X, padx=5, pady=5)

        self.entry_search = ctk.CTkEntry(frame_search, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind('<KeyRelease>', self.on_search_key)

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_motor)
        btn_search.pack(side=tk.LEFT, padx=5)
        btn_clear_search = ctk.CTkButton(frame_search, text="✖ Сбросить", command=self.clear_search)
        btn_clear_search.pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(main_frame, width=80, height=15, font=('Arial', 10))
        self.listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_motor)

        container_edit = ctk.CTkFrame(main_frame, fg_color=module_color)
        container_edit.pack(pady=5, padx=10, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X, padx=5, pady=5)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_motor, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.after(0, self.refresh)
        print("create_motor_ui done")

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('motor', self._on_loaded)

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

    def add_motor(self):
        exercise = self.entry_exercise.get().strip()
        duration = self.entry_duration.get().strip()
        accuracy = self.entry_accuracy.get().strip()
        errors = self.entry_errors.get().strip()
        if not exercise:
            messagebox.showwarning("Пусто", "Введите название упражнения.")
            return
        try:
            data = {
                "type": "motor",
                "exercise": exercise,
                "duration": duration or "0",
                "accuracy": accuracy or "0",
                "errors": errors or "0",
                "notes": ""
            }
            self.db.add_entry(data)
            self.entry_exercise.delete(0, tk.END)
            self.entry_duration.delete(0, tk.END)
            self.entry_accuracy.delete(0, tk.END)
            self.entry_errors.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Тренировка сохранена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_motor(self, event):
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
        edit_win.title("Редактирование тренировки")
        edit_win.geometry("450x350")
        Label(edit_win, text="Упражнение:").pack(pady=5)
        exercise_entry = Entry(edit_win, width=40)
        exercise_entry.insert(0, data.get('exercise', ''))
        exercise_entry.pack(pady=5)
        Label(edit_win, text="Время (сек):").pack(pady=5)
        duration_entry = Entry(edit_win, width=10)
        duration_entry.insert(0, data.get('duration', '0'))
        duration_entry.pack(pady=5)
        Label(edit_win, text="Точность (0-1):").pack(pady=5)
        accuracy_entry = Entry(edit_win, width=10)
        accuracy_entry.insert(0, data.get('accuracy', '0'))
        accuracy_entry.pack(pady=5)
        Label(edit_win, text="Ошибки:").pack(pady=5)
        errors_entry = Entry(edit_win, width=10)
        errors_entry.insert(0, data.get('errors', '0'))
        errors_entry.pack(pady=5)
        Label(edit_win, text="Заметки:").pack(pady=5)
        notes_text = scrolledtext.ScrolledText(edit_win, height=4, width=40)
        notes_text.insert('1.0', data.get('notes', ''))
        notes_text.pack(pady=5)
        def save_changes():
            new_exercise = exercise_entry.get().strip()
            new_duration = duration_entry.get().strip()
            new_accuracy = accuracy_entry.get().strip()
            new_errors = errors_entry.get().strip()
            new_notes = notes_text.get('1.0', 'end-1c').strip()
            if not new_exercise:
                messagebox.showwarning("Пусто", "Название упражнения обязательно.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'exercise': new_exercise,
                    'duration': new_duration or "0",
                    'accuracy': new_accuracy or "0",
                    'errors': new_errors or "0",
                    'notes': new_notes
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")
        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_motor(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить эту тренировку?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        self.search_motor()

    def search_motor(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if query in data.get('exercise', '').lower() or query in data.get('notes', '').lower():
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            exercise = data.get('exercise', '')
            self.listbox.insert(tk.END, f"{i}. {exercise}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def cancel_edit(self):
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.editing_key = None

    def export_data(self):
        print("export_data called (заглушка)")