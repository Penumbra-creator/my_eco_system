import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatisticsModule(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.create_ui()
        self.load_data()

    def create_ui(self):
        # Заголовок
        header = ctk.CTkLabel(self, text="📊 Статистика", font=('Arial', 20, 'bold'))
        header.pack(pady=10)

        # Фрейм для графиков
        self.canvas_frame = ctk.CTkFrame(self, fg_color='white')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопка обновления
        btn_refresh = ctk.CTkButton(self, text="🔄 Обновить", command=self.load_data)
        btn_refresh.pack(pady=5)

    def load_data(self):
        # Очистка старого canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Получаем статистику
        try:
            # Количество записей по модулям
            modules = ['philosophy', 'language', 'strategy', 'exam', 'ticket', 'motor', 'clinic', 'dream', 'conflict', 'article', 'lifebook']
            counts = {}
            for mod in modules:
                entries = self.db.get_entries(mod)
                counts[mod] = len(entries)

            # Просроченные записи (SRS)
            due_count = self.db.get_due_count()

            # Динамика добавления за последние 30 дней
            today = datetime.now().date()
            thirty_days_ago = today - timedelta(days=30)
            daily_counts = { (today - timedelta(days=i)).strftime('%Y-%m-%d'): 0 for i in range(30, -1, -1) }

            all_entries = self.db.get_entries()
            for _, data in all_entries:
                ts = data.get('timestamp', '')
                if ts:
                    try:
                        # Предполагаем формат ISO: "2026-08-20T10:00:00"
                        date_part = ts.split('T')[0]
                        if thirty_days_ago <= datetime.strptime(date_part, '%Y-%m-%d').date() <= today:
                            daily_counts[date_part] += 1
                    except:
                        pass

            # Создаём два графика в одном окне
            fig = Figure(figsize=(8, 6), dpi=100)

            # График 1: столбчатая диаграмма по модулям
            ax1 = fig.add_subplot(211)
            mod_names = list(counts.keys())
            mod_counts = list(counts.values())
            ax1.bar(mod_names, mod_counts, color='#4CAF50')
            ax1.set_title('Количество записей по модулям')
            ax1.set_ylabel('Количество')
            ax1.tick_params(axis='x', rotation=45, labelsize=8)

            # Добавляем надпись с количеством просроченных
            if due_count > 0:
                ax1.text(0.5, 0.95, f'⚠ Просроченных записей: {due_count}', 
                         transform=ax1.transAxes, ha='center', color='red', fontsize=10)

            # График 2: динамика за 30 дней
            ax2 = fig.add_subplot(212)
            dates = list(daily_counts.keys())
            values = list(daily_counts.values())
            ax2.plot(dates, values, marker='o', linestyle='-', color='#2196F3')
            ax2.set_title('Динамика добавления записей (последние 30 дней)')
            ax2.set_xlabel('Дата')
            ax2.set_ylabel('Количество')
            ax2.tick_params(axis='x', rotation=45, labelsize=8)

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {e}")
