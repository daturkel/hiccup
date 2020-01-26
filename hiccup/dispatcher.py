from collections import OrderedDict
from copy import deepcopy
import glob
import logging
from wcmatch.pathlib import Path, GLOBSTAR
from typing import List, Tuple, Dict

from .config import HiccupConfig
from .functions import noop
from .tasks import TaskList
from .utils import change_to_str


class OldDispatcher:
    def __init__(self, config: HiccupConfig):
        self.tasks = config.tasks

    def dispatch(self, filename, change_type, watch_dir):
        filepath = Path(filename)
        watch_dir = Path(watch_dir)
        rel_filename = filepath.relative_to(watch_dir)
        logging.info(f"File {rel_filename} {change_type.name}!")
        to_execute = OrderedDict()
        for key, steps in self.tasks.items():
            pattern, task_change_type, *_ = key
            if change_to_str(change_type) == task_change_type and filepath.globmatch(
                pattern, flags=GLOBSTAR
            ):
                to_execute[key] = steps
        logging.info(f" Running tasks for {rel_filename}:")
        self._execute_tasks(filepath, to_execute, watch_dir)
        logging.info(f"Done with tasks for {rel_filename}!")

    def _execute_tasks(self, filepath: Path, task_dict: OrderedDict, watch_dir: Path):
        ctx = {"__watch_dir": watch_dir}
        num_tasks = len(task_dict)
        for i, (key, steps) in enumerate(task_dict.items()):
            if ctx.get("__skip_remaining_tasks", False):
                logging.info(f"  Skipping remaining tasks for this file.")
                break
            if num_tasks > 1:
                logging.info(f"  Task {i+1} of {num_tasks} {key}:")
            else:
                logging.info(f"  {key}:")
            num_steps = len(steps)
            for j, step in enumerate(steps):
                if ctx.get("__skip_remaining_steps", False):
                    logging.info("    Skipping remaining steps for this task.")
                    ctx["__skip_remaining_steps"] = False
                    break
                if num_steps > 1:
                    logging.info(f"    Step {j+1} of {num_steps}: {step[0].__name__}")
                else:
                    logging.info(f"    {step[0].__name__}")
                ctx = self._execute_step(filepath, step, deepcopy(ctx))

    def _execute_step(self, filepath: Path, step: Tuple, ctx: Dict):
        step_fn, step_args = step
        expected_argcount = step_fn.__code__.co_argcount
        step_fn_expected_args = step_fn.__code__.co_varnames[:expected_argcount]
        args = {"filepath": filepath, "ctx": ctx}
        for arg in step_fn_expected_args:
            if arg == "filepath":
                args[arg] = filepath
            elif arg == "ctx":
                args[arg] = ctx
            elif arg in step_args:
                if step_args[arg][0:2] == "__":
                    ctx_key = step_args[arg][2:]
                    args[arg] = ctx[ctx_key]
                else:
                    args[arg] = step_args[arg]
            elif arg in ctx:
                args[arg] = ctx[arg]
        logging.debug(
            f"     Calling {step_fn.__name__} with args {[key for key in args.keys()]}."
        )
        return step_fn(**args)


class Dispatcher:
    def __init__(self, config: HiccupConfig, watch_dir: Path):
        self.task_list = TaskList(config.tasks, watch_dir)

    def dispatch(self, filepath: Path, change_type: str, watch_dir: Path):
        self.task_list = TaskList(config.tasks, watch_dir)
        rel_filename = filepath.relative_to(watch_dir)
        logging.info(f"File {rel_filename} {change_type.name}!")
        self.task_list.run_tasks(filepath, change_type)
