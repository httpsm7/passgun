#!/bin/bash
echo "Installing PassGun dependencies..."
apt update -qq
apt install -y python3 python3-pip python3-venv -qq
python3 -m venv venv
source venv/bin/activate
pip install flask
echo "✅ Setup complete!"
echo "Run: source venv/bin/activate && python3 passgen.py --web"
