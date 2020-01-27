from copy import deepcopy
import logging
from typing import Dict, Union, Optional, List, Tuple
from watchgod import Change
from wcmatch.pathlib import Path, GLOBSTAR

from .utils import listify


class Task:
    def __init__(
        self,
        steps: List[Tuple],
        name: str,
        change_types: Optional[Union[str, List[str]]] = None,
        match_patterns: Optional[Union[str, List[str]]] = None,
        skip_patterns: Optional[Union[str, List[str]]] = None,
    ):
        self.steps = steps
        self.num_steps = len(self.steps)
        self.name = name
        if change_types == "any" or change_types is None:
            self.change_types = ["add", "modify", "delete"]
        elif change_types == "change":
            self.change_types = ["add", "modify"]
        else:
            self.change_types = listify(change_types)
        if match_patterns is None:
            self.match_patterns = ["**/*"]
        else:
            self.match_patterns = listify(match_patterns)
        self.skip_patterns = listify(skip_patterns)
        self._sanitize_patterns()

    def _sanitize_patterns(self):
        self.match_patterns = [str(Path(pattern)) for pattern in self.match_patterns]
        self.skip_patterns = [str(Path(pattern)) for pattern in self.skip_patterns]

    def _match(self, filepath: Path, patterns: List[str]) -> bool:
        return any(filepath.globmatch(pattern, flags=GLOBSTAR) for pattern in patterns)

    def should_run(
        self, filepath: Optional[Path], change_type: Optional[str] = None
    ) -> bool:
        if filepath is not None:
            match_ok = self._match(filepath, self.match_patterns)
            skip_ok = not self._match(filepath, self.skip_patterns)
        else:
            match_ok = skip_ok = True
        change_ok = change_type is None or change_type in self.change_types
        return change_ok and match_ok and skip_ok

    def _run_step(self, filepath: Path, step: Tuple, ctx: Dict) -> Dict:
        step_fn, step_args = step
        expected_argcount = step_fn.__code__.co_argcount
        step_fn_expected_args = step_fn.__code__.co_varnames[:expected_argcount]
        args = {"ctx": ctx}
        for arg in step_fn_expected_args:
            if arg == "ctx":
                pass
            elif arg == "filepath":
                if "__filepath" in step_args:
                    args[arg] = Path(step_args["__filepath"])
                else:
                    args[arg] = filepath
            elif arg in step_args:
                if isinstance(step_args[arg], str) and step_args[arg][0:2] == "__":
                    ctx_key = step_args[arg][2:]
                    args[arg] = ctx[ctx_key]
                else:
                    args[arg] = step_args[arg]
            elif arg in ctx:
                args[arg] = ctx[arg]
        return step_fn(**args)

    def run(
        self,
        ctx: dict,
        filepath: Optional[Path] = None,
        change_type: Optional[str] = None,
        skip_checks: bool = False,
    ):
        if skip_checks or self.should_run(filepath, change_type):
            for j, step in enumerate(self.steps):
                if ctx.get("__skip_remaining_steps", False):
                    logging.info(f"   Skipping remaining steps for task {self.name}.")
                    ctx["__skip_remaining_steps"] = False
                    break
                logging.info(f"   Step {j+1} of {self.num_steps}: {step[0].__name__}")
                ctx = self._run_step(filepath, step, deepcopy(ctx))

        return ctx


class TaskList:
    def __init__(self, tasks: List[Task], ctx: Dict):
        self.tasks = tasks
        self.num_tasks = len(self.tasks)
        self.ctx = ctx

    def run_tasks(
        self,
        filepath: Optional[Path] = None,
        change_type: Optional[str] = None,
        skip_checks: bool = False,
    ):
        to_run = [
            task
            for task in self.tasks
            if skip_checks or task.should_run(filepath, change_type)
        ]
        if to_run:
            logging.info(f" Running tasks for {filepath}:")
            num_to_run = len(to_run)
            for i, task in enumerate(to_run):
                if self.ctx.get("__skip_remaining_tasks", False):
                    logging.info(f"  Skipping remaining tasks for {filepath}.")
                    break
                logging.info(f"  Task {i+1} of {num_to_run}: {task.name}")
                self.ctx = task.run(deepcopy(self.ctx), filepath)
            logging.info(f"Done with tasks for {filepath}!")
