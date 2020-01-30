from importlib import import_module
import logging
import os
from pathlib import Path
import sys

from . import __version__


class HiccupConfig:
    def __init__(self, config_filename: Path):
        sys.path.append(os.getcwd())
        config_filename = str(Path(config_filename.with_suffix("")))
        self.config_module = import_module(config_filename)
        self.version = self.config_module.VERSION
        if self.version.split(".")[0] != __version__.split(".")[0]:
            logging.warning(
                f"hiccup config version mismatch: hiccup version {__version__} vs config file version {self.version}.\n Check docs for possible API changes before changing the VERSION specified in {config_filename}."
            )
        self.watch_tasks = self.config_module.WATCH_TASKS
        self.clean_tasks = self.config_module.CLEAN_TASKS
        self.run_tasks = self.config_module.RUN_TASKS
        self.globals = self.config_module.GLOBALS
