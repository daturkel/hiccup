from copy import deepcopy
import logging
from typing import Dict, Union, Optional, List, Tuple
from watchgod import Change
from wcmatch.pathlib import Path, GLOBSTAR

from .utils import listify


class Task:
    def __init__(
        self,
        match_patterns: Union[str, List[str]],
        change_types: Union[str, List[str]],
        steps: List[Tuple],
        name: str,
        skip_patterns: Optional[Union[str, List[str]]] = None,
    ):
        self.match_patterns = listify(match_patterns)
        if change_types == "change":
            self.change_types = ["add", "modify"]
        elif change_types == "any":
            self.change_types = ["add", "modify", "delete"]
        else:
            self.change_types = listify(change_types)
        self.steps = steps
        self.num_steps = len(self.steps)
        self.name = name
        self.skip_patterns = listify(skip_patterns)

    def _match(self, filepath: Path, patterns: List[str]) -> bool:
        return any(filepath.globmatch(pattern, flags=GLOBSTAR) for pattern in patterns)

    def should_run(
        self, filepath: Path, change_type: str, skip_change_type=False
    ) -> bool:
        return (
            self._match(filepath, self.match_patterns)
            and not self._match(filepath, self.skip_patterns)
            and (change_type in self.change_types or skip_change_type)
        )

    def _run_step(self, filepath: Path, step: Tuple, ctx: Dict) -> Dict:
        step_fn, step_args = step
        expected_argcount = step_fn.__code__.co_argcount
        step_fn_expected_args = step_fn.__code__.co_varnames[:expected_argcount]
        args = {"filepath": filepath, "ctx": ctx}
        for arg in step_fn_expected_args:
            if arg in ("filepath", "ctx"):
                pass
            elif arg in step_args:
                if isinstance(step_args[arg], str) and step_args[arg][0:2] == "__":
                    ctx_key = step_args[arg][2:]
                    args[arg] = ctx[ctx_key]
                else:
                    args[arg] = step_args[arg]
            elif arg in ctx:
                args[arg] = ctx[arg]
        return step_fn(**args)

    def run(self, filepath: Path, ctx: dict):
        for j, step in enumerate(self.steps):
            if ctx.get("__skip_remaining_steps", False):
                logging.info(f"   Skipping remaining steps for task {self.name}.")
                ctx["__skip_remaining_steps"] = False
                break
            logging.info(f"   Step {j+1} of {self.num_steps}: {step[0].__name__}")
            ctx = self._run_step(filepath, step, deepcopy(ctx))
        return ctx


class TaskList:
    def __init__(self, tasks: List[Task], watch_dir: Path, globals_: Dict):
        self.tasks = tasks
        self.num_tasks = len(self.tasks)
        self.watch_dir = watch_dir
        self.ctx = {"__watch_dir": watch_dir, "__globals": globals_}

    def run_tasks(self, filepath: Path, change_type: str):
        rel_filepath = filepath.relative_to(self.ctx["__watch_dir"])
        to_run = [
            task for task in self.tasks if task.should_run(rel_filepath, change_type)
        ]
        if to_run:
            logging.info(f" Running tasks for {rel_filepath}:")
            num_to_run = len(to_run)
            for i, task in enumerate(to_run):
                if self.ctx.get("__skip_remaining_tasks", False):
                    logging.info(f"  Skipping remaining tasks for {rel_filepath}.")
                    break
                logging.info(f"  Task {i+1} of {num_to_run}: {task.name}")
                self.ctx = task.run(filepath, deepcopy(self.ctx))
            logging.info(f"Done with tasks for {rel_filepath}!")
