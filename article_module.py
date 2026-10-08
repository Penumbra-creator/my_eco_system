import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai

class ArticleModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'article', 'Анализ статей', {})
        self.create_article_ui()

    def create_article_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        module_color = "#8AC9FF"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Анализ статей", font=('Arial', 16, 'bold'), fg_color=module_color).pack(pady=8)

        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X)

        ctk.CTkLabel(frame_add, text="Название:").pack(side=tk.LEFT, padx=2)
        self.entry_title = ctk.CTkEntry(frame_add, width=20)
        self.entry_title.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Источник:").pack(side=tk.LEFT, padx=2)
        self.entry_source = ctk.CTkEntry(frame_add, width=15)
        self.entry_source.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Ключ. слова:").pack(side=tk.LEFT, padx=2)
        self.entry_keywords = ctk.CTkEntry(frame_add, width=15)
        self.entry_keywords.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_article)
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

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_articles)
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
        self.listbox.bind('<<ListboxSelect>>', self.on_select_article)

        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=5, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_article, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.after(0, self.refresh)   # или self.after(0, self.refresh)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('article', self._on_loaded)

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
        title = tk.simpledialog.askstring("Статья", "Название статьи:", parent=self)
        if not title:
            return
        source = tk.simpledialog.askstring("Статья", "Источник:", parent=self)
        keywords = tk.simpledialog.askstring("Статья", "Ключевые слова (через запятую):", parent=self)
        
        prompt = f"""Сделай краткую выжимку из статьи: {title}. 
Источник: {source}. 
Ключевые слова: {keywords}. 
Выдели 3–5 ключевых идей, методологию и выводы."""
        
        response, provider, model = ai.ask_model(prompt, "llama3.2")
        if response:
            data = {
                "type": "article",
                "title": title,
                "source": source or "",
                "keywords": keywords or "",
                "summary": response,
                "rating": "0"
            }
            self.db.add_entry(data)
            self.refresh()
            messagebox.showinfo("Успех", f"Выжимка сохранена!\n\n{response}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать выжимку.")

    def ask_ai(self):
            from ai_dialog import AIDialog
            AIDialog(self, model_name="llama3.2", db=self.db)
        
    def add_article(self):
        title = self.entry_title.get().strip()
        source = self.entry_source.get().strip()
        keywords = self.entry_keywords.get().strip()
        if not title:
            messagebox.showwarning("Пусто", "Название обязательно.")
            return
        try:
            data = {
                "type": "article",
                "title": title,
                "source": source,
                "keywords": keywords,
                "summary": "",
                "rating": "0"
            }
            self.db.add_entry(data)
            self.entry_title.delete(0, tk.END)
            self.entry_source.delete(0, tk.END)
            self.entry_keywords.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Статья сохранена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_article(self, event):
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
        edit_win.title("Редактирование статьи")
        edit_win.geometry("450x400")

        Label(edit_win, text="Название:").pack(pady=5)
        title_entry = Entry(edit_win, width=40)
        title_entry.insert(0, data.get('title', ''))
        title_entry.pack(pady=5)

        Label(edit_win, text="Источник:").pack(pady=5)
        source_entry = Entry(edit_win, width=40)
        source_entry.insert(0, data.get('source', ''))
        source_entry.pack(pady=5)

        Label(edit_win, text="Ключ. слова:").pack(pady=5)
        keywords_entry = Entry(edit_win, width=40)
        keywords_entry.insert(0, data.get('keywords', ''))
        keywords_entry.pack(pady=5)

        Label(edit_win, text="Резюме:").pack(pady=5)
        summary_text = scrolledtext.ScrolledText(edit_win, height=5, width=40)
        summary_text.insert('1.0', data.get('summary', ''))
        summary_text.pack(pady=5)

        Label(edit_win, text="Оценка (0-10):").pack(pady=5)
        rating_entry = Entry(edit_win, width=10)
        rating_entry.insert(0, data.get('rating', '0'))
        rating_entry.pack(pady=5)

        def save_changes():
            new_title = title_entry.get().strip()
            new_source = source_entry.get().strip()
            new_keywords = keywords_entry.get().strip()
            new_summary = summary_text.get('1.0', 'end-1c').strip()
            new_rating = rating_entry.get().strip()
            if not new_title:
                messagebox.showwarning("Пусто", "Название обязательно.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'title': new_title,
                    'source': new_source,
                    'keywords': new_keywords,
                    'summary': new_summary,
                    'rating': new_rating or "0"
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")

        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_article(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить эту статью?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        self.search_articles()

    def search_articles(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if query in data.get('title', '').lower() or query in data.get('source', '').lower() or query in data.get('keywords', '').lower() or query in data.get('summary', '').lower():
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            title = data.get('title', '')
            self.listbox.insert(tk.END, f"{i}. {title[:40]}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def cancel_edit(self):
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.editing_key = None