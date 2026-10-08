import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, Toplevel, Label, Entry, Button
from base_module import BaseModule
from ai_orchestrator import ai

class ClinicModule(BaseModule):
    def __init__(self, parent, db):
        super().__init__(parent, db, 'clinic', 'Клинический дневник', {})
        self.create_clinic_ui()

    def create_clinic_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        module_color = "#FFFFAB"
        header_frame = ctk.CTkFrame(self, fg_color=module_color)
        header_frame.pack(fill=tk.X, pady=(10,5))
        ctk.CTkLabel(header_frame, text="Клинический дневник", font=('Arial', 16, 'bold'), fg_color=module_color).pack(pady=8)

        container_add = ctk.CTkFrame(self, fg_color=module_color)
        container_add.pack(pady=5, padx=10, fill=tk.X)
        frame_add = ctk.CTkFrame(container_add, fg_color='white')
        frame_add.pack(fill=tk.X)

        ctk.CTkLabel(frame_add, text="Источник:").pack(side=tk.LEFT, padx=2)
        self.entry_patient = ctk.CTkEntry(frame_add, width=15)
        self.entry_patient.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Диагноз:").pack(side=tk.LEFT, padx=2)
        self.entry_diagnosis = ctk.CTkEntry(frame_add, width=20)
        self.entry_diagnosis.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_add, text="Лечение:").pack(side=tk.LEFT, padx=2)
        self.entry_treatment = ctk.CTkEntry(frame_add, width=20)
        self.entry_treatment.pack(side=tk.LEFT, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="➕ Добавить", command=self.add_clinic)
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

        btn_search = ctk.CTkButton(frame_search, text="🔍 Найти", command=self.search_clinic)
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
        self.listbox.bind('<<ListboxSelect>>', self.on_select_clinic)

        container_edit = ctk.CTkFrame(self, fg_color=module_color)
        container_edit.pack(pady=5, padx=5, fill=tk.X)
        frame_edit = ctk.CTkFrame(container_edit, fg_color='white')
        frame_edit.pack(fill=tk.X)

        self.btn_edit = ctk.CTkButton(frame_edit, text="✏️ Редактировать", command=self.enable_edit, state=tk.DISABLED)
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ctk.CTkButton(frame_edit, text="🗑 Удалить", command=self.delete_clinic, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)


        self.after(0, self.refresh)   # или self.after(0, self.refresh)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "⏳ Загрузка записей...")
        self.db.get_entries_async('clinic', self._on_loaded)

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
        patient = tk.simpledialog.askstring("Клинический дневник", "Опишите случай (источник, симптомы):", parent=self)
        if not patient:
            return
        diagnosis = tk.simpledialog.askstring("Клинический дневник", "Предположительный диагноз:", parent=self)
        
        prompt = f"""Опиши клиническое мышление для случая: {patient}. 
Предположительный диагноз: {diagnosis}. 
Предложи дифференциальный ряд (3-5 возможных диагнозов) и план дополнительных обследований."""
        
        response, provider, model = ai.ask_model(prompt, "mistral")
        if response:
            data = {
                "type": "clinic",
                "patient": patient,
                "diagnosis": diagnosis or "",
                "treatment": response,
                "outcome": "",
                "notes": f"Сгенерировано с помощью {provider} ({model})"
            }
            self.db.add_entry(data)
            self.refresh()
            messagebox.showinfo("Успех", f"Анализ сохранён!\n\n{response}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать анализ.")
            
    def ask_ai(self):
            from ai_dialog import AIDialog
            AIDialog(self, model_name="mistral", db=self.db)

    def add_clinic(self):
        patient = self.entry_patient.get().strip()
        diagnosis = self.entry_diagnosis.get().strip()
        treatment = self.entry_treatment.get().strip()
        if not patient or not diagnosis:
            messagebox.showwarning("Пусто", "Источник и диагноз обязательны.")
            return
        try:
            data = {
                "type": "clinic",
                "patient": patient,
                "diagnosis": diagnosis,
                "treatment": treatment,
                "outcome": "",
                "notes": ""
            }
            self.db.add_entry(data)
            self.entry_patient.delete(0, tk.END)
            self.entry_diagnosis.delete(0, tk.END)
            self.entry_treatment.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("Успех", "Случай сохранён!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def on_select_clinic(self, event):
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
        edit_win.title("Редактирование случая")
        edit_win.geometry("450x400")

        Label(edit_win, text="Источник:").pack(pady=5)
        patient_entry = Entry(edit_win, width=40)
        patient_entry.insert(0, data.get('patient', ''))
        patient_entry.pack(pady=5)

        Label(edit_win, text="Диагноз:").pack(pady=5)
        diagnosis_entry = Entry(edit_win, width=40)
        diagnosis_entry.insert(0, data.get('diagnosis', ''))
        diagnosis_entry.pack(pady=5)

        Label(edit_win, text="Лечение:").pack(pady=5)
        treatment_entry = Entry(edit_win, width=40)
        treatment_entry.insert(0, data.get('treatment', ''))
        treatment_entry.pack(pady=5)

        Label(edit_win, text="Исход:").pack(pady=5)
        outcome_entry = Entry(edit_win, width=40)
        outcome_entry.insert(0, data.get('outcome', ''))
        outcome_entry.pack(pady=5)

        Label(edit_win, text="Заметки:").pack(pady=5)
        notes_text = scrolledtext.ScrolledText(edit_win, height=5, width=40)
        notes_text.insert('1.0', data.get('notes', ''))
        notes_text.pack(pady=5)

        def save_changes():
            new_patient = patient_entry.get().strip()
            new_diagnosis = diagnosis_entry.get().strip()
            new_treatment = treatment_entry.get().strip()
            new_outcome = outcome_entry.get().strip()
            new_notes = notes_text.get('1.0', 'end-1c').strip()
            if not new_patient or not new_diagnosis:
                messagebox.showwarning("Пусто", "Источник и диагноз обязательны.")
                return
            try:
                self.db.update_entry(self.editing_key, {
                    'patient': new_patient,
                    'diagnosis': new_diagnosis,
                    'treatment': new_treatment,
                    'outcome': new_outcome,
                    'notes': new_notes
                })
                edit_win.destroy()
                self.refresh()
                messagebox.showinfo("Успех", "Запись обновлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")

        Button(edit_win, text="💾 Сохранить", command=save_changes).pack(pady=10)
        Button(edit_win, text="❌ Отмена", command=edit_win.destroy).pack()

    def delete_clinic(self):
        if not self.editing_key:
            return
        if messagebox.askyesno("Подтверждение", "Удалить этот случай?"):
            try:
                self.db.delete_entry(self.editing_key)
                self.cancel_edit()
                self.refresh()
                messagebox.showinfo("Успех", "Запись удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def on_search_key(self, event):
        self.search_clinic()

    def search_clinic(self):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.refresh()
            return
        filtered = []
        for key, data in self.cache:
            if query in data.get('patient', '').lower() or query in data.get('diagnosis', '').lower() or query in data.get('notes', '').lower():
                filtered.append((key, data))
        self.listbox.delete(0, tk.END)
        for i, (key, data) in enumerate(filtered, start=1):
            patient = data.get('patient', '')
            diagnosis = data.get('diagnosis', '')
            self.listbox.insert(tk.END, f"{i}. {patient} — {diagnosis[:30]}")
        self.cache = filtered

    def clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.refresh()

    def cancel_edit(self):
        self.btn_edit.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)
        self.editing_key = None