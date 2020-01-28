from importlib import import_module
import logging
import os
from pathlib import Path
import sys


class HiccupConfig:
    def __init__(self, config_filename: Path):
        sys.path.append(os.getcwd())
        config_filename = Path(config_filename.with_suffix(""))
        self.config_module = import_module(str(config_filename))
        self.watch_tasks = self.config_module.WATCH_TASKS
        self.clean_tasks = self.config_module.CLEAN_TASKS
        self.run_tasks = self.config_module.RUN_TASKS
        self.globals = self.config_module.GLOBALS
