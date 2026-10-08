import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button, Scale, IntVar
from base_module import BaseModule
from ai_orchestrator import ai

class StrategyModule(BaseModule):
    def __init__(self, parent, db):
        print("StrategyModule: __init__ start")
        super().__init__(parent, db, 'strategy', 'Мои стратегии', {})
        self.matrix_frame = None
        self.canvas = None
        self.create_strategy_ui()
        print("StrategyModule: __init__ done")

    def create_strategy_ui(self):
        print("create_strategy_ui start")
        for widget in self.winfo_children():
            widget.destroy()

        # Создаём фрейм с ярким красным фоном внутри self
        frame = ctk.CTkFrame(self, fg_color="red")
        frame.pack(fill=tk.BOTH, expand=True)

        label = ctk.CTkLabel(
            frame,
            text="🔥 КРАСНЫЙ ФРЕЙМ РАБОТАЕТ 🔥",
            font=('Arial', 24, 'bold'),
            text_color="black"
        )
        label.pack(expand=True)

        print("create_strategy_ui done")
    # ---- ЗАГЛУШКИ МЕТОДОВ (чтобы интерфейс создался) ----
    def refresh(self):
        print("refresh called")

    def add_strategy(self):
        print("add_strategy called")

    def _on_loaded(self, entries, error):
        print("_on_loaded called")

    def generate_strategy(self):
        print("generate_strategy called")

    def ask_ai(self):
        from ai_dialog import AIDialog
        AIDialog(self, model_name="llama3.2", db=self.db)

    def on_select_strategy(self, event):
        print("on_select_strategy called")

    def enable_edit(self):
        print("enable_edit called")

    def delete_strategy(self):
        print("delete_strategy called")

    def on_search_key(self, event):
        print("on_search_key called")

    def search_strategies(self):
        print("search_strategies called")

    def clear_search(self):
        print("clear_search called")

    def cancel_edit(self):
        print("cancel_edit called")

    def create_eisenhower_matrix_ui(self):
        print("create_eisenhower_matrix_ui called")

    def refresh_matrix(self):
        print("refresh_matrix called")

    def export_data(self):
        print("export_data called")