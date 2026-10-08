import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, scrolledtext
import json
import csv
import os
from tkinter import filedialog

class BaseModule(ctk.CTkFrame):   # теперь наследник CTkFrame
    def __init__(self, parent, db, module_type, title, fields):
        super().__init__(parent)
        self.db = db
        self.module_type = module_type
        self.title = title
        self.fields = fields
        self.cache = []
        self.editing_key = None
        self.edit_mode = False
        self.entry_widgets = {}
        # Флаг, чтобы проверять, жив ли объект
        self._destroyed = False

    def destroy(self):
        """Переопределяем destroy, чтобы пометить объект как уничтоженный."""
        self._destroyed = True
        super().destroy()

    def _alive(self):
        """Проверка, что виджет существует и не уничтожен."""
        return not self._destroyed and self.winfo_exists()

    # ---- Общие методы для всех модулей ----

    def refresh(self):
        """Обновить список – переопределяется в дочерних классах"""
        pass

    def add_entry(self):
        """Добавить запись – переопределяется в дочерних классах"""
        pass

    def on_select(self, event):
        pass

    def enable_edit(self):
        messagebox.showinfo("Инфо", "Редактирование реализовано в дочернем модуле")

    def delete_entry(self):
        if not self.editing_key:
            messagebox.showinfo("Инфо", "Сначала выберите запись")
            return
        if messagebox.askyesno("Подтверждение", "Удалить запись?"):
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
        self.editing_key = None
        if hasattr(self, 'text_info'):
            self.text_info.configure(state=tk.NORMAL)
            self.text_info.delete(1.0, tk.END)
            self.text_info.configure(state=tk.DISABLED)

    def search(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            found = False
            for field_name in self.fields.keys():
                if query in data.get(field_name, '').lower():
                    found = True
                    break
            if found:
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            first_field = list(self.fields.keys())[0]
            value = data.get(first_field, '')
            self.listbox.insert(tk.END, f"{i}. {value[:40]}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def on_search(self, event):
        self.search()

    def export_module_data(self):
        entries = self.db.get_entries(self.module_type)
        if not entries:
            messagebox.showinfo("Экспорт", "Нет записей для экспорта.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        data = [data for key, data in entries]

        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Успех", f"Экспортировано {len(data)} записей в JSON.")
            elif file_path.endswith('.csv'):
                if not data:
                    messagebox.showwarning("Нет данных", "Нет записей для CSV.")
                    return
                fieldnames = list(data[0].keys())
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                messagebox.showinfo("Успех", f"Экспортировано {len(data)} записей в CSV.")
            else:
                messagebox.showerror("Ошибка", "Неизвестный формат файла.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {e}")