from .markdown import parse_markdown_file_with_fm
from .tasks import Task

from copy import deepcopy
from glob import glob
from jinja2 import TemplateNotFound, Environment, FileSystemLoader
import logging
from wcmatch.pathlib import Path
import sass
from typing import Tuple, Optional

# functions for filenames


def noop(filepath: Path, ctx: dict):
    pass


def compile_sass(filepath: Path, ctx: dict, in_dir: str, out_dir: str):
    in_dir = ctx.get("__watch_dir", Path("")) / Path(in_dir)
    out_dir = Path(out_dir)
    sass.compile(dirname=(in_dir, out_dir), output_style="compressed")
    return ctx


def parse_markdown_with_template(filepath: Path, ctx: dict, template_dir: str):
    metadata, content = parse_markdown_file_with_fm(filepath)
    env = Environment(
        loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
    )
    env.globals = ctx.get("__globals", {})
    try:
        template_name = metadata.pop("__template")
    except KeyError as e:
        logging.error(f"File {filepath} does not specify a template.")
        raise e
    ctx["template"] = template_name
    try:
        template = env.get_template(template_name)
    except TemplateNotFound as e:
        logging.error(f"Could not locate template {template_name}.")
        raise e
    special_keys = [k[2:] for k in metadata.keys() if k[0:2] == "__"]
    for key in special_keys:
        ctx[key] = metadata.pop(key)
    output = template.render({**metadata, "content": content})
    filepath = filepath.with_suffix(".html")
    ctx.update({"output": output})
    return ctx


def write_text_to_file(
    filepath: Path, ctx: dict, text: str, out_dir: str, ext: Optional[str] = None
):
    filepath = filepath.relative_to(ctx.get("__watch_dir", ""))
    full_filepath = Path(out_dir) / filepath
    full_filepath.parent.mkdir(parents=True, exist_ok=True)
    if ext is not None:
        full_filepath = full_filepath.with_suffix(ext)
    with open(full_filepath, "w") as f:
        f.write(text)
    return ctx


def skip_remaining_steps(filepath: Path, ctx: dict):
    ctx["__skip_remaining_steps"] = True
    return ctx


def skip_remaining_tasks(filepath: Path, ctx: dict):
    ctx["__skip_remaining_tasks"] = True
    return ctx


def skip_remaining_steps_and_tasks(filepath: Path, ctx: dict):
    ctx["__skip_remaining_tasks"] = True
    ctx["__skip_remaining_steps"] = True
    return ctx


def run_task_on_matches(filepath: Path, ctx: dict, task: Task, match_pattern: str):
    for filepath_ in glob(str(match_pattern), recursive=True):
        filepath_ = Path(filepath_)
        rel_filepath = filepath_.relative_to(ctx["__watch_dir"])
        if task.should_run(rel_filepath, change_type="", skip_change_type=True):
            logging.info(f" Running task {task.name} on {filepath_}:")
            ctx = task.run(Path(filepath_), deepcopy(ctx))
    return ctx
