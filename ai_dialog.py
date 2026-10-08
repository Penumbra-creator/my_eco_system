import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext, messagebox, simpledialog
import datetime
from ai_orchestrator import ai

class AIDialog:
    def __init__(self, parent, model_name, db):
        self.parent = parent
        self.model_name = model_name
        self.db = db
        self.dialog_key = None  # для обновления оценки
        
        # Окно
        self.window = tk.Toplevel(parent)
        self.window.title("Спросить ИИ")
        self.window.geometry("600x500")
        
        # Поле ввода
        ctk.CTkLabel(self.window, text="Введите ваш вопрос:").pack(pady=5)
        self.question_entry = ctk.CTkEntry(self.window, width=60)
        self.question_entry.pack(pady=5)
        self.question_entry.bind('<Return>', lambda e: self.send_question())
        
        # Текстовое поле для ответа
        self.answer_text = scrolledtext.ScrolledText(self.window, height=10, wrap=tk.WORD)
        self.answer_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Кнопки
        btn_frame = ctk.CTkFrame(self.window)
        btn_frame.pack(pady=5)
        
        self.btn_send = ctk.CTkButton(btn_frame, text="📤 Отправить", command=self.send_question)
        self.btn_send.pack(side=tk.LEFT, padx=5)
        
        self.btn_like = ctk.CTkButton(btn_frame, text="👍", command=lambda: self.rate_answer("like"), state=tk.DISABLED)
        self.btn_like.pack(side=tk.LEFT, padx=5)
        
        self.btn_dislike = ctk.CTkButton(btn_frame, text="👎", command=lambda: self.rate_answer("dislike"), state=tk.DISABLED)
        self.btn_dislike.pack(side=tk.LEFT, padx=5)
        
        self.btn_close = ctk.CTkButton(btn_frame, text="❌ Закрыть", command=self.window.destroy)
        self.btn_close.pack(side=tk.LEFT, padx=5)
        
        # Переменные для хранения последнего ответа
        self.last_response = None
        self.last_provider = None
        self.last_model = None
        self.last_question = None
    
    def send_question(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Пусто", "Введите вопрос")
            return
        
        self.last_question = question
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "⏳ Думаю...")
        self.window.update()
        
        # Вызов ИИ
        response, provider, model = ai.ask_model(question, self.model_name)
        
        if response:
            self.last_response = response
            self.last_provider = provider
            self.last_model = model
            
            # Сохраняем диалог в БД
            dialog_data = {
                "type": "dialog",
                "question": question,
                "answer": response,
                "model": model,
                "provider": provider,
                "timestamp": datetime.datetime.now().isoformat(),
                "rating": None,
                "comment": ""
            }
            result = self.db.add_entry(dialog_data)
            self.dialog_key = result  # ключ для обновления оценки
            
            self.answer_text.delete(1.0, tk.END)
            self.answer_text.insert(tk.END, f"Ответ от {provider}/{model}:\n\n{response}")
            
            # Активируем кнопки оценки
            self.btn_like.configure(state=tk.NORMAL)
            self.btn_dislike.configure(state=tk.NORMAL)
        else:
            self.answer_text.delete(1.0, tk.END)
            self.answer_text.insert(tk.END, "Не удалось получить ответ.")
    
    def rate_answer(self, rating):
        if not self.dialog_key:
            return
        comment = ""
        if rating == "dislike":
            comment = simpledialog.askstring("Комментарий", "Что не так с ответом?", parent=self.window)
        try:
            update_data = {"rating": rating}
            if comment:
                update_data["comment"] = comment
            self.db.update_entry(self.dialog_key, update_data)
            messagebox.showinfo("Спасибо!", "Ваша оценка сохранена.")
            self.btn_like.configure(state=tk.DISABLED)
            self.btn_dislike.configure(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить оценку: {e}")