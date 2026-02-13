import sys
import os
import platform

print(f"--- 実行環境情報 ---")
print(f"Pythonパス: {sys.executable}")             # Miniconda等のパスが表示されます
print(f"OS情報: {platform.platform()}")            # WSLなら 'Linux-...-microsoft-standard-WSL2' と出ます
print(f"OS名: {os.name}")
print(f"現在のディレクトリ: {os.getcwd()}")
print(f"仮想環境(CONDA_DEFAULT_ENV): {os.environ.get('CONDA_DEFAULT_ENV', 'Not Conda')}")