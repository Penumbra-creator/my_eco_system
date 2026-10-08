import os
import sys
import winreg

def add_to_startup():
    """Добавляет текущее приложение в автозагрузку Windows"""
    try:
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        else:
            python_path = sys.executable
            main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
            app_path = f'"{python_path}" "{main_path}"'
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MyEcoSystem", 0, winreg.REG_SZ, app_path)
        return True
    except Exception as e:
        print(f"Ошибка добавления в автозагрузку: {e}")
        return False

def remove_from_startup():
    """Удаляет приложение из автозагрузки"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "MyEcoSystem")
        return True
    except Exception:
        return False

def is_autostart_enabled():
    """Проверяет, добавлено ли приложение в автозагрузку"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "MyEcoSystem")
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Ошибка проверки автозагрузки: {e}")
        return False