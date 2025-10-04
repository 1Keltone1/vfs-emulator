#!/usr/bin/env python3
"""
VFS Emulator - Stage 5: GUI Version
Полнофункциональный графический интерфейс
"""

import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, messagebox, Menu
import os
import sys
import time
import argparse
from datetime import datetime

# Импорт логики VFS
from vfs_core import VFSConfig, VirtualFileSystem, ScriptRunner


class VFSGUIEmulator:
    def __init__(self):
        # Парсим аргументы командной строки
        self.config = VFSConfig().parse_arguments()

        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("VFS Emulator - Virtual File System")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Инициализируем VFS
        self.vfs = VirtualFileSystem(self.config)

        # Сначала создаем GUI элементы
        self.create_gui()

        # Теперь инициализируем ScriptRunner (после создания GUI)
        self.script_runner = ScriptRunner(self)

        # Отложенная инициализация VFS и скриптов
        self.root.after(100, self.initialize_after_gui)

    def create_gui(self):
        """Создает графический интерфейс"""

        # ==================== МЕНЮ ====================
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # Меню File
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Меню Commands
        commands_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Commands", menu=commands_menu)
        commands_menu.add_command(label="PWD", command=self.cmd_pwd)
        commands_menu.add_command(label="LS", command=self.cmd_ls)
        commands_menu.add_command(label="Config", command=self.cmd_config)
        commands_menu.add_separator()
        commands_menu.add_command(label="Clear", command=self.clear_output)

        # Меню Help
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Commands Help", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)

        # ==================== ОБЛАСТЬ ВЫВОДА ====================
        output_frame = Frame(self.root, relief=tk.GROOVE, bd=2)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        tk.Label(output_frame, text="VFS Terminal", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # Текстовая область (терминал)
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=100,
            height=25,
            bg='black',
            fg='white',
            insertbackground='white',
            font=('Courier New', 10),
            relief=tk.FLAT
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)

        # ==================== ПАНЕЛЬ ВВОДА ====================
        input_frame = Frame(self.root, relief=tk.GROOVE, bd=2)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Приглашение
        self.prompt_label = tk.Label(
            input_frame,
            text="$",
            bg='black',
            fg='green',
            font=('Courier New', 12, 'bold'),
            width=4
        )
        self.prompt_label.pack(side=tk.LEFT, padx=(5, 0), pady=5)

        # Поле ввода
        self.command_entry = Entry(
            input_frame,
            bg='black',
            fg='white',
            insertbackground='white',
            font=('Courier New', 11),
            relief=tk.FLAT
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.command_entry.bind('<Return>', self.execute_command_gui)
        self.command_entry.focus()

        # ==================== ПАНЕЛЬ КНОПОК ====================
        button_frame = Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки команд
        commands = [
            ("Help", self.show_help),
            ("PWD", self.cmd_pwd),
            ("LS", self.cmd_ls),
            ("Config", self.cmd_config),
            ("Uptime", self.cmd_uptime),
            ("Who", self.cmd_who),
            ("Clear", self.clear_output),
            ("Exit", self.root.quit)
        ]

        for text, command in commands:
            tk.Button(button_frame, text=text, command=command, width=8).pack(side=tk.LEFT, padx=2)

        # ==================== СТАТУСНАЯ СТРОКА ====================
        status_frame = Frame(self.root, relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, padx=10, pady=2)

        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            bd=1,
            font=('Arial', 9)
        )
        self.status_label.pack(fill=tk.X, padx=2, pady=1)

        # Начальное сообщение
        self.print_output("VFS Emulator GUI v1.0\n")
        self.print_output("Virtual File System Emulator\n")
        self.print_output("Type 'help' for available commands\n")
        self.print_output("-" * 50 + "\n")
        self.update_prompt()

    def initialize_after_gui(self):
        """Инициализация после создания GUI"""
        # Загружаем VFS если указан путь
        if self.config.vfs_path:
            try:
                self.vfs.load_from_xml(self.config.vfs_path)
                self.print_output(f"VFS loaded from: {self.config.vfs_path}\n")
            except Exception as e:
                messagebox.showerror("VFS Error", f"Failed to load VFS: {e}")

        # Запускаем стартовый скрипт если указан
        if self.config.startup_script:
            self.execute_startup_script(self.config.startup_script)

        self.update_prompt()

    # ==================== ОСНОВНЫЕ МЕТОДЫ ====================

    def print_output(self, text):
        """Вывод текста в область"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_prompt(self):
        """Обновление приглашения"""
        current_path = self.vfs.get_current_path()
        self.prompt_label.config(text=f"{current_path}$")
        self.status_label.config(text=f"Current: {current_path} | VFS: {self.config.vfs_path or 'Default'}")

    def execute_command_gui(self, event=None):
        """Обработка команды из GUI"""
        command_string = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)

        if not command_string:
            return

        # Показываем команду
        current_path = self.vfs.get_current_path()
        self.print_output(f"{current_path}$ {command_string}\n")

        # Выполняем команду
        success = self.execute_command(command_string)

        if not success:
            self.print_output(f"Error executing command\n")

        self.update_prompt()

    def execute_startup_script(self, script_path):
        """Выполнение стартового скрипта"""
        if not os.path.exists(script_path):
            messagebox.showerror("Script Error", f"Script not found: {script_path}")
            return

        try:
            self.script_runner.execute_script(script_path)
            self.update_prompt()
        except Exception as e:
            messagebox.showerror("Script Error", f"Failed to execute script: {e}")

    def execute_command(self, command_string):
        """Выполнение команды"""
        parts = command_string.split()
        if not parts:
            return True

        command = parts[0].lower()
        args = parts[1:]

        try:
            if command == "pwd":
                self.print_output(f"{self.vfs.get_current_path()}\n")

            elif command == "ls":
                detailed = '-l' in args
                path = None

                for arg in args:
                    if not arg.startswith('-') and not detailed:
                        path = arg

                if detailed:
                    items, error = self.vfs.list_directory(path, detailed=True)
                    if error:
                        self.print_output(f"ls: {error}\n")
                    else:
                        self.print_output(f"total {len(items)}\n")
                        for item in items:
                            self.print_output(item + '\n')
                else:
                    items, error = self.vfs.list_directory(path)
                    if error:
                        self.print_output(f"ls: {error}\n")
                    else:
                        self.print_output('  '.join(items) + '\n')

            elif command == "cd":
                path = args[0] if args else None
                error = self.vfs.change_directory(path)
                if error:
                    self.print_output(f"cd: {error}\n")

            elif command == "cat":
                if not args:
                    self.print_output("cat: missing file operand\n")
                else:
                    content, error = self.vfs.read_file(args[0])
                    if error:
                        self.print_output(f"cat: {error}\n")
                    else:
                        self.print_output(content + '\n')

            elif command == "uptime":
                days, hours, minutes, seconds = self.vfs.get_uptime()
                if days > 0:
                    self.print_output(f" up {days} day(s), {hours:02d}:{minutes:02d}:{seconds:02d}\n")
                else:
                    self.print_output(f" up {hours:02d}:{minutes:02d}:{seconds:02d}\n")

            elif command == "who":
                users = self.vfs.get_who_info()
                for user_info in users:
                    line = f"{user_info['user']:8} {user_info['terminal']:8} {user_info['login_time']:5}"
                    if user_info['host']:
                        line += f" ({user_info['host']})"
                    self.print_output(line + '\n')

            elif command == "config":
                self.print_output("Current configuration:\n")
                self.print_output(f"  VFS Path: {self.config.vfs_path or 'Not specified'}\n")
                self.print_output(f"  Startup Script: {self.config.startup_script or 'Not specified'}\n")
                self.print_output(f"  Debug Mode: {self.config.debug_mode}\n")
                self.print_output(f"  VFS Loaded: {self.vfs.loaded}\n")

            elif command == "vfsinfo":
                if self.vfs.loaded:
                    self.print_output("VFS Information:\n")
                    self.print_output(f"  Source: {self.config.vfs_path}\n")
                    file_count, dir_count = self.count_vfs_items(self.vfs.root)
                    self.print_output(f"  Directories: {dir_count}\n")
                    self.print_output(f"  Files: {file_count}\n")
                else:
                    self.print_output("VFS: Default structure\n")

            elif command == "echo":
                self.print_output(' '.join(args) + '\n')

            elif command == "help":
                self.show_help()

            elif command == "exit":
                self.root.quit()

            else:
                self.print_output(f"Unknown command: {command}\n")
                return False

            return True

        except Exception as e:
            self.print_output(f"Error executing command: {e}\n")
            return False

    # ==================== МЕТОДЫ ДЛЯ КНОПОК ====================

    def cmd_pwd(self):
        self.print_output(f"{self.vfs.get_current_path()}$ pwd\n")
        self.execute_command("pwd")

    def cmd_ls(self):
        self.print_output(f"{self.vfs.get_current_path()}$ ls\n")
        self.execute_command("ls")

    def cmd_config(self):
        self.print_output(f"{self.vfs.get_current_path()}$ config\n")
        self.execute_command("config")

    def cmd_uptime(self):
        self.print_output(f"{self.vfs.get_current_path()}$ uptime\n")
        self.execute_command("uptime")

    def cmd_who(self):
        self.print_output(f"{self.vfs.get_current_path()}$ who\n")
        self.execute_command("who")

    def show_help(self):
        help_text = """
Available commands:
  pwd               - Print current directory
  ls [path]         - List directory contents
  ls -l [path]      - Detailed directory listing
  cd [dir]          - Change directory
  cat [file]        - Display file content
  uptime            - Show system uptime
  who               - Show logged in users
  config            - Show current configuration
  vfsinfo           - Show VFS information
  echo [text]       - Display text
  help              - Show this help message
  exit              - Exit the emulator

Quick access:
  Use toolbar buttons or menu for quick command execution
"""
        self.print_output(help_text)

    def show_about(self):
        messagebox.showinfo("About VFS Emulator",
                            "VFS Emulator GUI v1.0\n"
                            "Virtual File System Emulator\n"
                            "Graphical Interface Version\n\n"
                            "Implementation of UNIX-like command line emulator")

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def count_vfs_items(self, node):
        """Подсчет файлов и папок в VFS"""
        if node.type == 'file':
            return 1, 0

        file_count = 0
        dir_count = 1

        for child in node.children.values():
            if child.type == 'file':
                file_count += 1
            else:
                child_files, child_dirs = self.count_vfs_items(child)
                file_count += child_files
                dir_count += child_dirs

        return file_count, dir_count

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    """Точка входа"""
    try:
        app = VFSGUIEmulator()
        app.run()
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()