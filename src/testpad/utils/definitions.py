import os
import sys

ROOT_LOGGER_NAME = "debug.log"
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

if getattr(sys, "frozen", False):
    print("Running as frozen application")
    SRC_DIR = os.path.dirname(sys.executable)
    ROOT_DIR = SRC_DIR
else:
    SRC_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.dirname(SRC_DIR)
