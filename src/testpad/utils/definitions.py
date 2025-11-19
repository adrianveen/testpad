import sys
from pathlib import Path

ROOT_LOGGER_NAME = "debug.log"
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

if getattr(sys, "frozen", False):
    print("Running as frozen application")
    SRC_DIR = Path(sys.executable).parent
    ROOT_DIR = SRC_DIR
else:
    SRC_DIR = Path(__file__).parent
    ROOT_DIR = Path(SRC_DIR).parent
