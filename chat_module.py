import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, ttk
import datetime
from ai_orchestrator import ai

class ChatModule(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.history = []  # для хранения текущей сессии
        self.current_model = tk.StringVar(value="llama3.2")
        
        self.create_widgets()
        self.load_recent_history()
    
    def create_widgets(self):
        # Заголовок
        ctk.CTkLabel(self, text="🧠 Чат с ИИ", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Верхняя панель: выбор модели + кнопки
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=5, padx=10, fill=tk.X)
        
        ctk.CTkLabel(top_frame, text="Модель:").pack(side=tk.LEFT, padx=5)
        
        # --- ДИНАМИЧЕСКИ СОБИРАЕМ ДОСТУПНЫЕ МОДЕЛИ ИЗ ОРКЕСТРАТОРА ---
        available_models = []
        for prov, models in ai.get_available_models().items():
            for m in models:
                available_models.append(m) # или можете добавить префикс f"{prov}:{m}"
                
        # Если вдруг оркестратор ничего не нашел, оставим дефолтную, чтобы программа не упала
        if not available_models:
            available_models = ["llama3.2"]

        # Установим первую доступную модель по умолчанию, если текущая не задана
        if self.current_model.get() not in available_models:
            self.current_model.set(available_models[0])

        model_combo = ttk.Combobox(
            top_frame, 
            textvariable=self.current_model,
            values=available_models,  # <--- теперь здесь живой список из оркестратора!
            state="readonly",
            width=20
        )
        model_combo.pack(side=tk.LEFT, padx=5)
        
        btn_clear = ctk.CTkButton(top_frame, text="🗑 Очистить", command=self.clear_history)
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        btn_export = ctk.CTkButton(top_frame, text="📤 Экспорт", command=self.export_history)
        btn_export.pack(side=tk.LEFT, padx=5)
        
        # ... (остальной код метода без изменений)
    
    def load_recent_history(self):
        """Загружает последние 20 диалогов из БД"""
        entries = self.db.get_entries('chat')
        if not entries:
            return
        # Сортируем по времени, берём последние 20
        entries.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
        recent = entries[:20]
        recent.reverse()  # чтобы старые были сверху
        
        self.text_history.configure(state=tk.NORMAL)
        self.text_history.delete(1.0, tk.END)
        for key, data in recent:
            question = data.get('question', '')
            answer = data.get('answer', '')
            model = data.get('model', '')
            timestamp = data.get('timestamp', '')[:16]
            self.text_history.insert(tk.END, f"[{timestamp}] {model}\n")
            self.text_history.insert(tk.END, f"Вы: {question}\n")
            self.text_history.insert(tk.END, f"ИИ: {answer}\n\n")
        self.text_history.configure(state=tk.DISABLED)
        self.text_history.see(tk.END)
    
    def send_message(self):
        question = self.entry_question.get().strip()
        if not question:
            messagebox.showwarning("Пусто", "Введите вопрос")
            return
        
        model = self.current_model.get()
        
        # Отображаем вопрос в истории
        self.text_history.configure(state=tk.NORMAL)
        self.text_history.insert(tk.END, f"Вы: {question}\n")
        self.text_history.insert(tk.END, f"ИИ: ⏳ думает...\n\n")
        self.text_history.configure(state=tk.DISABLED)
        self.text_history.see(tk.END)
        self.entry_question.delete(0, tk.END)
        self.update()
        
        # Вызываем ИИ
        try:
            response, provider, model_used = ai.ask_model(question, model)
            if response:
                # Сохраняем в БД
                data = {
                    "type": "chat",
                    "question": question,
                    "answer": response,
                    "model": model_used,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.db.add_entry(data)
                
                # Обновляем историю (заменяем "думает..." на ответ)
                self.text_history.configure(state=tk.NORMAL)
                # Находим последнюю строку с "думает..." и заменяем
                end_pos = self.text_history.index("end-2c")
                self.text_history.delete("end-2c linestart", "end-1c")
                self.text_history.insert("end-2c linestart", f"ИИ ({model_used}): {response}\n\n")
                self.text_history.configure(state=tk.DISABLED)
                self.text_history.see(tk.END)
            else:
                messagebox.showerror("Ошибка", "Не удалось получить ответ от ИИ.")
                # Удаляем строку с "думает..."
                self.text_history.configure(state=tk.NORMAL)
                self.text_history.delete("end-2c linestart", "end-1c")
                self.text_history.configure(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить ответ: {e}")
            self.text_history.configure(state=tk.NORMAL)
            self.text_history.delete("end-2c linestart", "end-1c")
            self.text_history.configure(state=tk.DISABLED)
    
    def clear_history(self):
        """Очищает только локальную историю (не удаляет из БД)"""
        if messagebox.askyesno("Подтверждение", "Очистить историю диалога в окне? (записи останутся в БД)"):
            self.text_history.configure(state=tk.NORMAL)
            self.text_history.delete(1.0, tk.END)
            self.text_history.configure(state=tk.DISABLED)
    
    def export_history(self):
        """Экспортирует все диалоги в JSON"""
        import json
        from tkinter import filedialog, messagebox
        
        entries = self.db.get_entries('chat')
        if not entries:
            messagebox.showinfo("Экспорт", "Нет диалогов для экспорта.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return
        
        data = [data for key, data in entries]
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Экспортировано {len(data)} диалогов.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {e}")