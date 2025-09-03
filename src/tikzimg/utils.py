import logging
import os
import subprocess
from pathlib import Path

def get_default_editor() -> str:
    return os.getenv("EDITOR", "vim")
