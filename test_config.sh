#!/bin/bash
echo "Testing VFS Emulator Configuration"

echo "1. Basic help:"
python main.py --help

echo "2. Debug mode:"
python main.py --debug << EOF
pwd
exit
EOF

echo "3. With startup script:"
python main.py --script startup_demo.txt

echo "Testing completed"