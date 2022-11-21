"""demonstrate how to extract metadata from package resources

e.g. for __version__
"""
import os

import pkg_resources  # type: ignore

try:
    package = pkg_resources.require("hagemt_template")
    version = package[0].version
except pkg_resources.DistributionNotFound:
    version = os.getenv("HAGEMT_TEMPLATE_VERSION", "development")

__all__ = (
    "package",
    "version",
)

__version__ = version
