# export_utils.py
import json
import csv
import os
from tkinter import filedialog, messagebox

def export_to_json(data, default_name="data.json"):
    """Экспортирует данные в JSON-файл"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile=default_name
    )
    if not file_path:
        return
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Успех", f"Экспортировано {len(data)} записей.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось экспортировать: {e}")

def export_to_csv(data, fieldnames=None, default_name="data.csv"):
    """Экспортирует данные в CSV-файл"""
    if not data:
        messagebox.showwarning("Нет данных", "Нет записей для экспорта.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=default_name
    )
    if not file_path:
        return
    try:
        # Если fieldnames не указаны, берём ключи первого элемента
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        messagebox.showinfo("Успех", f"Экспортировано {len(data)} записей в CSV.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось экспортировать: {e}")