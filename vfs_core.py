#!/usr/bin/env python3
"""
VFS Core - Stage 3: Virtual File System
XML-based virtual file system implementation
"""

import xml.etree.ElementTree as ET
import os
import time
from datetime import datetime

class VFSNode:
    def __init__(self, name, node_type, content=None):
        self.name = name
        self.type = node_type
        self.content = content
        self.children = {} if node_type == 'directory' else None
        self.parent = None

    def add_child(self, node):
        if self.type == 'directory':
            node.parent = self
            self.children[node.name] = node

    def get_path(self):
        if self.name == '':
            return "/"
        path_parts = []
        current = self
        while current and current.name:
            path_parts.append(current.name)
            current = current.parent
        return '/' + '/'.join(reversed(path_parts))

class VirtualFileSystem:
    def __init__(self, config):
        self.config = config
        self.root = VFSNode('', 'directory')
        self.current_directory = self.root
        self.loaded = False

        # Базовая структура по умолчанию
        self._create_default_structure()

    def _create_default_structure(self):
        home = VFSNode("home", "directory")
        user = VFSNode("user", "directory")
        etc = VFSNode("etc", "directory")

        self.root.add_child(home)
        home.add_child(user)
        self.root.add_child(etc)

        readme = VFSNode("readme.txt", "file", "Welcome to VFS!")
        user.add_child(readme)

    def load_from_xml(self, xml_path):
        try:
            if not os.path.exists(xml_path):
                raise FileNotFoundError(f"VFS file not found: {xml_path}")

            tree = ET.parse(xml_path)
            root = tree.getroot()

            if root.tag != 'vfs':
                raise ValueError("Invalid VFS format")

            self._parse_directory(self.root, root)
            self.loaded = True
            return True

        except Exception as e:
            raise ValueError(f"Error loading VFS: {e}")

    def _parse_directory(self, parent, xml_element):
        for child in xml_element:
            if child.tag == 'directory':
                dir_name = child.get('name')
                dir_node = VFSNode(dir_name, 'directory')
                parent.add_child(dir_node)
                self._parse_directory(dir_node, child)
            elif child.tag == 'file':
                file_name = child.get('name')
                content = child.text.strip() if child.text else ""
                file_node = VFSNode(file_name, 'file', content)
                parent.add_child(file_node)

    def resolve_path(self, path):
        if not path or path == '/':
            return self.root

        if path.startswith('/'):
            current = self.root
            path_parts = [p for p in path[1:].split('/') if p]
        else:
            current = self.current_directory
            path_parts = [p for p in path.split('/') if p]

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

    def list_directory(self, path=None):
        target = self.resolve_path(path) if path else self.current_directory
        if not target or target.type != 'directory':
            return None, "Directory not found"

        items = []
        for name, node in target.children.items():
            if node.type == 'directory':
                items.append(f"{name}/")
            else:
                items.append(name)

        return sorted(items), None

    def change_directory(self, path):
        target = self.resolve_path(path)
        if not target:
            return f"Directory not found: {path}"
        if target.type != 'directory':
            return f"Not a directory: {path}"

        self.current_directory = target
        return None

    def get_current_path(self):
        return self.current_directory.get_path()

    def read_file(self, path):
        file_node = self.resolve_path(path)
        if not file_node:
            return None, f"File not found: {path}"
        if file_node.type != 'file':
            return None, f"Not a file: {path}"
        return file_node.content, None

    def __init__(self, config):
        # ... существующий код ...
        self.start_time = time.time()

    def get_uptime(self):
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return 0, hours, minutes, seconds

    def get_who_info(self):
        return [
            {"user": "user", "terminal": "tty1", "login_time": "10:30"},
            {"user": "root", "terminal": "pts/0", "login_time": "09:15", "host": "192.168.1.100"}
        ]

    def list_directory(self, path=None, detailed=False):
        target = self.resolve_path(path) if path else self.current_directory
        if not target or target.type != 'directory':
            return None, "Directory not found"

        if detailed:
            items = []
            for name, node in target.children.items():
                item_type = "d" if node.type == 'directory' else "-"
                items.append(f"{item_type}rw-r--r-- 1 user user 4096 Dec 10 12:00 {name}")
            return items, None
        else:
            items = []
            for name, node in target.children.items():
                if node.type == 'directory':
                    items.append(f"{name}/")
                else:
                    items.append(name)
            return sorted(items), None