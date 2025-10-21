"""Entry point for running testpad as a module.

This allows the package to be run using:
  python -m testpad

Which is equivalent to running:
  python src/testpad/testpad_main.py
"""

from testpad.testpad_main import main

if __name__ == "__main__":
    main()
