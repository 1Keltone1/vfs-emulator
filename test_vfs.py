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


if __name__ == "__main__":
    test_vfs()