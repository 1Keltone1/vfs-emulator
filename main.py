#!/usr/bin/env python3
"""
VFS Emulator - Stage 1: REPL
Базовая структура с командами-заглушками
"""

import sys


class VFSEmulator:
    def __init__(self):
        self.current_directory = "/"
        self.running = True

    def run(self):
        print("VFS Emulator v1.0 - Basic REPL")
        print("Type 'exit' to quit, 'help' for commands")
        print("-" * 50)

        while self.running:
            try:
                command = input(f"{self.current_directory}$ ").strip()
                self.execute_command(command)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break

    def execute_command(self, command_string):
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
            print(self.current_directory)
        elif command == "ls":
            print(f"Command: ls, Arguments: {args}")
            print("file1.txt  file2.txt  directory1/")
        elif command == "cd":
            print(f"Command: cd, Arguments: {args}")
            if args:
                print(f"Changed to directory: {args[0]}")
        else:
            print(f"Error: Unknown command '{command}'")

    def show_help(self):
        help_text = """
Available commands:
  ls [args]     - List directory contents (stub)
  cd [dir]      - Change directory (stub)  
  pwd           - Print current directory
  exit          - Exit the emulator
  help          - Show this help message
"""
        print(help_text)


def main():
    emulator = VFSEmulator()
    emulator.run()


if __name__ == "__main__":
    main()