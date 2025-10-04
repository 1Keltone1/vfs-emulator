#!/usr/bin/env python3
"""
VFS Core Logic - Stage 5: Complete Implementation
Полная логика виртуальной файловой системы
"""

import os
import xml.etree.ElementTree as ET
import time
import argparse
from datetime import datetime


class VFSConfig:
    """Конфигурация эмулятора"""

    def __init__(self):
        self.vfs_path = None
        self.startup_script = None
        self.debug_mode = False

    def parse_arguments(self):
        """Парсинг аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='VFS Emulator - Virtual File System Emulator',
            epilog='Example: python main.py --vfs ./vfs.xml --script startup.txt --debug'
        )

        parser.add_argument(
            '--vfs',
            dest='vfs_path',
            metavar='PATH',
            help='Path to VFS physical location (XML file)'
        )

        parser.add_argument(
            '--script',
            dest='startup_script',
            metavar='SCRIPT',
            help='Path to startup script'
        )

        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug output'
        )

        args = parser.parse_args()

        self.vfs_path = args.vfs_path
        self.startup_script = args.startup_script
        self.debug_mode = args.debug

        # Отладочный вывод
        if self.debug_mode:
            print("=== VFS Emulator Configuration ===")
            print(f"VFS Path: {self.vfs_path}")
            print(f"Startup Script: {self.startup_script}")
            print(f"Debug Mode: {self.debug_mode}")
            print("==================================")

        return self


class VFSNode:
    """Узел виртуальной файловой системы"""

    def __init__(self, name, node_type, content=None, permissions="rw-r--r--", owner="user", group="users", size=0):
        self.name = name
        self.type = node_type  # 'file' или 'directory'
        self.content = content
        self.children = {} if node_type == 'directory' else None
        self.parent = None
        self.permissions = permissions
        self.owner = owner
        self.group = group
        self.size = size
        self.created_time = time.time()
        self.modified_time = time.time()

    def add_child(self, node):
        """Добавление дочернего узла"""
        if self.type == 'directory':
            node.parent = self
            self.children[node.name] = node
            self.modified_time = time.time()
        else:
            raise ValueError("Can only add children to directories")

    def get_path(self):
        """Получение полного пути"""
        if self.name == '':  # Корневой узел
            return "/"

        path_parts = []
        current = self
        while current and current.name:
            path_parts.append(current.name)
            current = current.parent

        return '/' + '/'.join(reversed(path_parts))

    def get_detailed_info(self):
        """Детальная информация для ls -l"""
        if self.type == 'directory':
            perm = "d" + self.permissions
            size = 4096  # Стандартный размер директории
        else:
            perm = "-" + self.permissions
            size = len(self.content) if self.content else self.size

        # Форматирование времени
        mod_time = datetime.fromtimestamp(self.modified_time)
        now = datetime.now()
        if mod_time.year == now.year:
            time_str = mod_time.strftime("%b %d %H:%M")
        else:
            time_str = mod_time.strftime("%b %d  %Y")

        return f"{perm} {self.owner:>8} {self.group:>8} {size:>8} {time_str} {self.name}"


class VirtualFileSystem:
    """Виртуальная файловая система"""

    def __init__(self, config):
        self.config = config
        self.root = VFSNode('', 'directory', permissions="rwxr-xr-x", owner="root", group="root")
        self.current_directory = self.root
        self.loaded = False
        self.start_time = time.time()

        # Создаем структуру по умолчанию
        self._create_default_structure()

    def _create_default_structure(self):
        """Создание структуры по умолчанию"""
        # Основные директории
        bin_dir = VFSNode("bin", "directory", permissions="rwxr-xr-x", owner="root", group="root")
        home_dir = VFSNode("home", "directory", permissions="rwxr-xr-x", owner="root", group="root")
        etc_dir = VFSNode("etc", "directory", permissions="rwxr-xr-x", owner="root", group="root")
        tmp_dir = VFSNode("tmp", "directory", permissions="rwxrwxrwt", owner="root", group="root")
        var_dir = VFSNode("var", "directory", permissions="rwxr-xr-x", owner="root", group="root")

        self.root.add_child(bin_dir)
        self.root.add_child(home_dir)
        self.root.add_child(etc_dir)
        self.root.add_child(tmp_dir)
        self.root.add_child(var_dir)

        # Домашняя директория пользователя
        user_dir = VFSNode("user", "directory", permissions="rwxr-xr-x", owner="user", group="user")
        home_dir.add_child(user_dir)

        # Файлы
        readme_file = VFSNode("readme.txt", "file",
                              "Welcome to VFS Emulator!\nThis is a virtual file system.",
                              permissions="rw-r--r--", owner="user", group="user", size=150)
        user_dir.add_child(readme_file)

        passwd_file = VFSNode("passwd", "file",
                              "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:User:/home/user:/bin/bash",
                              permissions="rw-r--r--", owner="root", group="root", size=100)
        etc_dir.add_child(passwd_file)

        hosts_file = VFSNode("hosts", "file",
                             "127.0.0.1 localhost\n::1 localhost ip6-localhost ip6-loopback",
                             permissions="rw-r--r--", owner="root", group="root", size=80)
        etc_dir.add_child(hosts_file)

    def load_from_xml(self, xml_path):
        """Загрузка VFS из XML файла"""
        try:
            if not os.path.exists(xml_path):
                raise FileNotFoundError(f"VFS file not found: {xml_path}")

            tree = ET.parse(xml_path)
            root_element = tree.getroot()

            if root_element.tag != 'vfs':
                raise ValueError("Invalid VFS format: root element must be 'vfs'")

            # Очищаем существующую структуру
            self.root.children = {}
            self._parse_directory(self.root, root_element)
            self.loaded = True

            if self.config.debug_mode:
                print(f"[DEBUG] VFS loaded successfully from {xml_path}")
                print(f"[DEBUG] Root directory contains {len(self.root.children)} items")

            return True

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            raise ValueError(f"Error loading VFS: {e}")

    def _parse_directory(self, parent_node, xml_element):
        """Парсинг директории из XML"""
        for child in xml_element:
            if child.tag == 'directory':
                dir_name = child.get('name')
                if not dir_name:
                    raise ValueError("Directory missing 'name' attribute")

                permissions = child.get('permissions', 'rwxr-xr-x')
                owner = child.get('owner', 'user')
                group = child.get('group', 'users')

                dir_node = VFSNode(dir_name, 'directory', permissions=permissions, owner=owner, group=group)
                parent_node.add_child(dir_node)
                self._parse_directory(dir_node, child)

            elif child.tag == 'file':
                file_name = child.get('name')
                if not file_name:
                    raise ValueError("File missing 'name' attribute")

                # Обработка содержимого файла
                content = child.text.strip() if child.text else ""
                encoding = child.get('encoding', 'text')

                if encoding == 'base64':
                    # Для бинарных файлов - храним как есть
                    content = content

                permissions = child.get('permissions', 'rw-r--r--')
                owner = child.get('owner', 'user')
                group = child.get('group', 'users')
                size = int(child.get('size', len(content)))

                file_node = VFSNode(file_name, 'file', content, permissions=permissions, owner=owner, group=group,
                                    size=size)
                parent_node.add_child(file_node)

    def resolve_path(self, path):
        """Разрешение пути к узлу VFS"""
        if not path or path == '/':
            return self.root

        # Абсолютные пути
        if path.startswith('/'):
            current = self.root
            path_parts = [p for p in path[1:].split('/') if p]
        else:
            # Относительные пути
            current = self.current_directory
            path_parts = [p for p in path.split('/') if p]

        # Обработка каждой части пути
        for part in path_parts:
            if part == '..':
                if current.parent:
                    current = current.parent
            elif part == '.':
                continue
            else:
                if current.type != 'directory' or part not in current.children:
                    return None
                current = current.children[part]

        return current

    def list_directory(self, path=None, detailed=False):
        """Список содержимого директории"""
        target_dir = self.resolve_path(path) if path else self.current_directory
        if not target_dir:
            return None, f"Directory not found: {path}"
        if target_dir.type != 'directory':
            return None, f"Not a directory: {path}"

        if detailed:
            # Детализированный список
            items = []
            # Родительская директория
            if target_dir != self.root:
                parent_info = VFSNode("..", "directory", permissions="rwxr-xr-x", owner="root", group="root")
                items.append(parent_info.get_detailed_info())

            for name, node in sorted(target_dir.children.items()):
                items.append(node.get_detailed_info())

            return items, None
        else:
            # Простой список
            items = []
            for name, node in sorted(target_dir.children.items()):
                if node.type == 'directory':
                    items.append(f"{name}/")
                else:
                    items.append(name)

            return items, None

    def change_directory(self, path):
        """Смена текущей директории"""
        if not path:
            # cd без аргументов - домашняя директория
            home_dir = self.resolve_path("/home/user")
            if home_dir:
                self.current_directory = home_dir
                return None
            else:
                self.current_directory = self.root
                return None

        target_dir = self.resolve_path(path)
        if not target_dir:
            return f"Directory not found: {path}"
        if target_dir.type != 'directory':
            return f"Not a directory: {path}"

        self.current_directory = target_dir
        return None

    def get_current_path(self):
        """Получение текущего пути"""
        return self.current_directory.get_path()

    def read_file(self, path):
        """Чтение файла"""
        file_node = self.resolve_path(path)
        if not file_node:
            return None, f"File not found: {path}"
        if file_node.type != 'file':
            return None, f"Not a file: {path}"

        return file_node.content, None

    def get_uptime(self):
        """Получение времени работы системы"""
        uptime_seconds = time.time() - self.start_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        return days, hours, minutes, seconds

    def get_who_info(self):
        """Информация о вошедших пользователях"""
        # Имитация данных who
        users = [
            {"user": "user", "terminal": "tty1", "login_time": "10:30", "host": ""},
            {"user": "root", "terminal": "pts/0", "login_time": "09:15", "host": "192.168.1.100"},
        ]
        return users

    def touch(self, filename):
        """
        Создать пустой файл или обновить время модификации
        Возвращает error message или None при успехе
        """
        if not filename:
            return "укажите имя файла"

        filename = filename.strip()

        # Проверяем валидность имени файла
        if not self.is_valid_name(filename):
            return f"недопустимое имя файла '{filename}'"

        # Получаем текущую директорию
        current_dir = self.current_directory

        # Проверяем, существует ли файл
        if filename in current_dir.children:
            # Обновляем время модификации существующего файла
            current_dir.children[filename].modified_time = time.time()
            return None  # Успех
        else:
            # Создаем новый файл
            new_file = VFSNode(
                filename,
                'file',
                content="",
                permissions="rw-r--r--",
                owner="user",
                group="user",
                size=0
            )
            current_dir.add_child(new_file)
            return None  # Успех

    def is_valid_name(self, name):
        """
        Проверяет валидность имени файла/директории
        """
        if not name or name.strip() == '':
            return False
        # Запрещенные символы в именах
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return all(char not in name for char in invalid_chars)

class ScriptRunner:
    """Выполнение стартовых скриптов"""

    def __init__(self, emulator):
        self.emulator = emulator
        self.config = emulator.config

    def execute_script(self, script_path):
        """Выполнение скрипта с поддержкой комментариев"""
        if not os.path.exists(script_path):
            # Используем безопасный вывод
            self._safe_print(f"Error: Script file not found: {script_path}")
            return False

        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            self._safe_print(f"\n=== Executing startup script: {script_path} ===\n")

            line_number = 0
            for line in lines:
                line_number += 1
                original_line = line.rstrip()
                line = line.strip()

                # Пропускаем пустые строки и комментарии
                if not line:
                    continue
                if line.startswith('#'):
                    if self.config.debug_mode:
                        self._safe_print(f"[DEBUG] Line {line_number}: Comment - {line}\n")
                    continue

                # Отображаем выполняемую команду
                self._safe_print(f"$ {original_line}\n")

                # Выполняем команду
                success = self.emulator.execute_command(line)
                if not success:
                    self._safe_print(f"Error in script at line {line_number}: {line}\n")
                    return False

                self._safe_print("\n")  # Пустая строка для читаемости

            self._safe_print(f"=== Script execution completed: {script_path} ===\n")
            return True

        except Exception as e:
            self._safe_print(f"Error reading script {script_path}: {str(e)}\n")
            return False

    def _safe_print(self, text):
        """Безопасный вывод текста - работает даже если GUI не готов"""
        try:
            # Пробуем использовать GUI вывод
            if hasattr(self.emulator, 'print_output'):
                self.emulator.print_output(text)
            else:
                # Fallback на консольный вывод
                print(text, end='')
        except Exception:
            # Если и это не работает - просто игнорируем
            pass