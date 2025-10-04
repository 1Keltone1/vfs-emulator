#!/usr/bin/env python3
"""
VFS Emulator - Stage 1: REPL
Базовая структура с командами-заглушками
"""

import sys
import argparse
import os


class VFSConfig:
    def __init__(self):
        self.vfs_path = None
        self.startup_script = None
        self.debug_mode = False

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='VFS Emulator')
        parser.add_argument('--vfs', dest='vfs_path', help='Path to VFS XML file')
        parser.add_argument('--script', dest='startup_script', help='Path to startup script')
        parser.add_argument('--debug', action='store_true', help='Enable debug output')

        args = parser.parse_args()
        self.vfs_path = args.vfs_path
        self.startup_script = args.startup_script
        self.debug_mode = args.debug

        if self.debug_mode:
            print("=== VFS Configuration ===")
            print(f"VFS Path: {self.vfs_path}")
            print(f"Startup Script: {self.startup_script}")
            print("=========================")

        return self

class ScriptRunner:
    def __init__(self, emulator):
        self.emulator = emulator

    def execute_script(self, script_path):
        if not os.path.exists(script_path):
            print(f"Error: Script file not found: {script_path}")
            return False

        try:
            with open(script_path, 'r') as file:
                lines = file.readlines()

            print(f"=== Executing script: {script_path} ===")

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                print(f"$ {line}")
                self.emulator.execute_command(line)
                print()

            print(f"=== Script completed ===")
            return True

        except Exception as e:
            print(f"Error executing script: {e}")
            return False


class VFSEmulator:
    def __init__(self, config):
        self.config = config
        self.vfs = VirtualFileSystem(config)
        self.current_directory = "/"
        self.running = True
        self.script_runner = ScriptRunner(self)

        # Load VFS if specified
        if config.vfs_path:
            try:
                self.vfs.load_from_xml(config.vfs_path)
                print(f"VFS loaded from: {config.vfs_path}")
            except Exception as e:
                print(f"Error loading VFS: {e}")

        # Execute startup script if specified
        if config.startup_script:
            self.script_runner.execute_script(config.startup_script)

    def run(self):
        print("VFS Emulator v4.0 - Core UNIX Commands")
        print("=" * 50)

        while self.running:
            try:
                current_path = self.vfs.get_current_path()
                command = input(f"{current_path}$ ").strip()
                self.execute_command(command)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break

    def execute_command(self, command_string):
        """Execute command with enhanced UNIX functionality"""
        if not command_string:
            return

        parts = command_string.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if command == "exit":
            print("Exiting VFS Emulator...")
            self.running = False

        elif command == "help":
            self.show_help()

        elif command == "pwd":
            print(self.vfs.get_current_path())

        elif command == "ls":
            detailed = False
            path = None

            # Parse arguments for ls command
            for arg in args:
                if arg == '-l':
                    detailed = True
                elif not arg.startswith('-'):
                    path = arg

            items, error = self.vfs.list_directory(path, detailed)
            if error:
                print(f"ls: {error}")
            else:
                if detailed:
                    # Detailed listing
                    print(f"total {len(items)}")
                    for item in items:
                        print(item)
                else:
                    # Simple listing
                    print('  '.join(items))

        elif command == "cd":
            path = args[0] if args else None
            error = self.vfs.change_directory(path)
            if error:
                print(f"cd: {error}")

        elif command == "cat":
            if not args:
                print("cat: missing file operand")
            else:
                content, error = self.vfs.read_file(args[0])
                if error:
                    print(f"cat: {error}")
                else:
                    print(content)

        elif command == "uptime":
            days, hours, minutes, seconds = self.vfs.get_uptime()
            if days > 0:
                print(f" up {days} day(s), {hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                print(f" up {hours:02d}:{minutes:02d}:{seconds:02d}")

        elif command == "who":
            users = self.vfs.get_who_info()
            for user_info in users:
                line = f"{user_info['user']:8} {user_info['terminal']:8} {user_info['login_time']:5}"
                if user_info.get('host'):
                    line += f" ({user_info['host']})"
                print(line)

        elif command == "config":
            print("Current configuration:")
            print(f"  VFS Path: {self.config.vfs_path or 'Not specified'}")
            print(f"  Startup Script: {self.config.startup_script or 'Not specified'}")
            print(f"  Debug Mode: {self.config.debug_mode}")
            print(f"  VFS Loaded: {self.vfs.loaded}")

        elif command == "vfsinfo":
            if self.vfs.loaded:
                print("VFS Information:")
                print(f"  Source: {self.config.vfs_path}")
                # Count files and directories
                file_count = sum(1 for node in self._traverse_vfs(self.vfs.root) if node.type == 'file')
                dir_count = sum(1 for node in self._traverse_vfs(self.vfs.root) if node.type == 'directory')
                print(f"  Directories: {dir_count}")
                print(f"  Files: {file_count}")
            else:
                print("VFS: Default structure")

        elif command == "echo":
            print(' '.join(args))

        else:
            print(f"Error: Unknown command '{command}'")

    def _traverse_vfs(self, node):
        """Helper method to traverse VFS tree"""
        yield node
        if node.type == 'directory' and node.children:
            for child in node.children.values():
                yield from self._traverse_vfs(child)

    def show_help(self):
        """Show enhanced help with new commands"""
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
"""
        print(help_text)

def main():
    emulator = VFSEmulator()
    emulator.run()

if __name__ == "__main__":
    main()