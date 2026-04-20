"""
Legacy entrypoint.

Mantém compatibilidade com `python weather_gui.py` enquanto o código vive em
`howmanydegrees/`.
"""

from pathlib import Path

from howmanydegrees.gui import main


if __name__ == "__main__":
    # Fixamos o `project_root` para garantir que `out/` seja criado ao lado do projeto,
    # mesmo se a GUI for executada por IDE/atalhos (onde o diretório atual pode variar).
    main(project_root=Path(__file__).resolve().parent)