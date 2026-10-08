import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class GlobalSearchWindow(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("🔍 Глобальный поиск")
        self.geometry("700x500")
        self.resizable(True, True)
        
        # Поле поиска
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search())
        
        frame_top = ctk.CTkFrame(self)
        frame_top.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkEntry(frame_top, textvariable=self.search_var, placeholder_text="Введите текст для поиска...", width=400).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(frame_top, text="Поиск", command=self.search, width=100).pack(side=tk.LEFT, padx=5)
        
        # Область вывода
        self.text_area = ctk.CTkTextbox(self, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def search(self):
        query = self.search_var.get().strip().lower()
        self.text_area.delete('1.0', tk.END)
        if not query:
            self.text_area.insert(tk.END, "Введите текст для поиска.")
            return
        
        # Список модулей и их коллекций (имя в БД, отображаемое имя)
        modules = [
            ('philosophy', 'Философия'),
            ('language', 'Языки'),
            ('strategy', 'Стратегии'),
            ('exam', 'Экзамены'),
            ('ticket', 'Билеты'),
            ('motor', 'Моторика'),
            ('clinic', 'Клинический дневник'),
            ('dream', 'Сны'),
            ('conflict', 'Конфликты'),
            ('article', 'Статьи'),
            ('lifebook', 'Книга жизни')
        ]
        
        found = False
        for collection, display_name in modules:
            entries = self.db.get_entries(collection)  # предполагается, что метод возвращает список (doc_id, data)
            for doc_id, data in entries:
                # Ищем в содержимом (поле content или text)
                content = data.get('content', '') + data.get('text', '') + data.get('word', '') + data.get('translation', '')
                if query in content.lower():
                    found = True
                    self.text_area.insert(tk.END, f"📂 [{display_name}] ", 'bold')
                    # Выводим содержимое (обрезка до 200 символов)
                    preview = content[:200] + '...' if len(content) > 200 else content
                    self.text_area.insert(tk.END, preview + "\n\n")
        if not found:
            self.text_area.insert(tk.END, "Ничего не найдено.")