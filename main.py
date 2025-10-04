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

# Обновите класс VFSEmulator:
class VFSEmulator:
    def __init__(self, config):
        self.config = config
        self.current_directory = "/"
        self.running = True
        self.script_runner = ScriptRunner(self)

        # Выполнить стартовый скрипт если указан
        if config.startup_script:
            self.script_runner.execute_script(config.startup_script)

def main():
    emulator = VFSEmulator()
    emulator.run()

if __name__ == "__main__":
    main()