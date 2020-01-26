from importlib import import_module
from pathlib import Path


class HiccupConfig:
    def __init__(self, config_filename: Path):
        config_filename = str(config_filename.with_suffix(""))
        self.config_module = import_module(config_filename)
        self.watch_tasks = self.config_module.WATCH_TASKS
        self.globals = self.config_module.GLOBALS
