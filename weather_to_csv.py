"""
Legacy entrypoint.

Mantém compatibilidade com `python weather_to_csv.py ...` enquanto o código vive em
`howmanydegrees/`.
"""

# Wrapper fino: o código real (CLI) mora em `howmanydegrees/cli.py`.
from howmanydegrees.cli import main, run  # noqa: F401


if __name__ == "__main__":
    run()
