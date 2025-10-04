#!/usr/bin/env python3
"""
VFS Testing Script - Stage 3
"""

from vfs_core import VFSConfig, VirtualFileSystem


def test_vfs():
    config = VFSConfig()
    config.vfs_path = "minimal_vfs.xml"

    vfs = VirtualFileSystem(config)
    vfs.load_from_xml("minimal_vfs.xml")

    print("VFS Loaded Successfully!")
    print(f"Current path: {vfs.get_current_path()}")

    items, error = vfs.list_directory("/")
    print(f"Root contents: {items}")

    content, error = vfs.read_file("/home/user/readme.txt")
    print(f"File content: {content}")

    # Test touch command
    print("\n=== Testing touch command ===")

    # Test creating new file
    error = vfs.touch("newfile.txt")
    if error:
        print(f"Error creating file: {error}")
    else:
        print("File created successfully")

    # Test updating existing file
    error = vfs.touch("newfile.txt")
    if error:
        print(f"Error updating file: {error}")
    else:
        print("File timestamp updated successfully")

    # Test invalid filename
    error = vfs.touch("invalid/name.txt")
    if error:
        print(f"Expected error for invalid name: {error}")

    # List directory to verify
    items, error = vfs.list_directory()
    print(f"Directory contents after touch: {items}")


if __name__ == "__main__":
    test_vfs()