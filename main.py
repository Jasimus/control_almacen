#!/usr/bin/env python3
"""Control de Almacen — Entry Point"""
import sys
from tui.app import ControlAlmacenApp
from tui.excel import ExcelStore
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <usuario>")
        sys.exit(1)

    user = sys.argv[1]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    file = f"deposito_{timestamp}.xlsx"

    store = ExcelStore(file)
    app = ControlAlmacenApp(store, user)
    app.run()


if __name__ == "__main__":
    main()
