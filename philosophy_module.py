import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai
from datetime import datetime

class PhilosophyModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'philosophy', 'Мои афоризмы', {})
        self.create_philosophy_ui()

    def create_philosophy_ui(self):
        print("create_philosophy_ui start")
        # Очищаем самого себя (self теперь CTkFrame)
        for widget in self.winfo_children():
            widget.destroy()

        # Заголовок
        module_color = "#D7FF7A"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(
            header_frame,
            text="Мои афоризмы",
            font=('Arial', 16, 'bold'),
            fg_color=module_color
        ).pack(pady=8)

        # Панель добавления
        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)

        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X, padx=5, pady=5)

        self.entry_aphorism = ctk.CTkEntry(frame_add, width=60)
        self.entry_aphorism.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_aphorism)
        btn_add.pack(side=tk.LEFT, padx=5)
        btn_refresh = ctk.CTkButton(frame_add, text="🔄 Обновить", command=self.refresh)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        # Панель поиска
        container_search = ctk.CTkFrame(self, fg_color=module_color)
        container_search.pack(pady=5, padx=10, fill=tk.X)

        frame_search = ctk.CTkFrame(container_search, fg_color='white')
        frame_search.pack(fill=tk.X, padx=5, pady=5)

        self.entry_search = ctk.CTkEntry(frame_search, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind('<KeyRelease>', self.on_search_key)

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_aphorisms)
        btn_search.pack(side=tk.LEFT, padx=5)
        btn_clear_search = ctk.CTkButton(frame_search, text="✖ Сбросить", command=self.clear_search)
        btn_clear_search.pack(side=tk.LEFT, padx=5)

        # Список
        self.listbox = tk.Listbox(self, width=80, height=15, font=('Arial', 10))
        self.listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_aphorism)

        # Панель редактирования
        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=10, fill=tk.X)

        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X, padx=5, pady=5)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_aphorism, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        # Запускаем загрузку с небольшой задержкой, чтобы интерфейс успел отрисоваться
        self.after(100, self.refresh)
        print("create_philosophy_ui done")

    def refresh(self):
        if not self._alive():
            return
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('philosophy', self._on_loaded)

    def _on_loaded(self, entries, error):
        if not self._alive():
            return
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

    def add_aphorism(self):
        if not self._alive():
            return
        text = self.entry_aphorism.get().strip()
        if not text:
            messagebox.showwarning("Пусто", "Введите текст афоризма")
            return
        try:
            data = {
                "type": "philosophy",
                "title": text[:30],
                "content": text
            }
            self.db.add_entry(data)
            self.entry_aphorism.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Афоризм сохранён!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_aphorism(self, event):
        if not self._alive():
            return
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        key, data = self.cache[index]
        self.editing_key = key
        self.btn_edit.configure(state=tk.NORMAL)
        self.btn_delete.configure(state=tk.NORMAL)

    def enable_edit(self):
        if not self._alive() or not self.editing_key:
            return
        key, data = None, None
        for k, d in self.cache:
            if k == self.editing_key:
                key, data = k, d
                break
        if not data:
            return
        edit_win = Toplevel(self)
        edit_win.title("Редактирование афоризма")
        edit_win.geometry("400x350")
        Label(edit_win, text="Заголовок:").pack(pady=5)
        title_entry = Entry(edit_win, width=40)
        title_entry.insert(0, data.get('title', ''))
        title_entry.pack(pady=5)
        Label(edit_win, text="Содержание:").pack(pady=5)
        content_text = scrolledtext.ScrolledText(edit_win, height=8, width=40)
        content_text.insert('1.0', data.get('content', ''))
        content_text.pack(pady=5)
        def save_changes():
            if not self._alive():
                return
            new_title = title_entry.get().strip()
            new_content = content_text.get('1.0', 'end-1c').strip()
            if not new_title or not new_content:
                messagebox.showwarning("Пусто", "Заполните оба поля")
                return
            try:
                self.db.update_entry(self.editing_key, {'title': new_title, 'content': new_content})
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")
        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_aphorism(self):
        if not self._alive() or not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить этот афоризм?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        if not self._alive():
            return
        self.search_aphorisms()

    def search_aphorisms(self):
        if not self._alive():
            return
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            title = data.get('title', '').lower()
            content = data.get('content', '').lower()
            if query in title or query in content:
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            title = data.get('title', 'Без названия')
            self.listbox.insert(tk.END, f"{i}. {title[:40]}")
        self.cache = filtered

    def clear_search(self):
        if not self._alive():
            return
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def cancel_edit(self):
        if not self._alive():
            return
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.editing_key = None