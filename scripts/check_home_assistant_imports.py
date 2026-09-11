"""Import every integration module against an installed Home Assistant version."""

from __future__ import annotations

import importlib
import pkgutil

PACKAGE_NAME = "custom_components.remko_http"


def main() -> None:
    """Import the integration package and all of its direct modules."""
    package = importlib.import_module(PACKAGE_NAME)
    module_names = sorted(
        module.name
        for module in pkgutil.iter_modules(package.__path__, f"{PACKAGE_NAME}.")
    )
    for module_name in module_names:
        importlib.import_module(module_name)


if __name__ == "__main__":
    main()
