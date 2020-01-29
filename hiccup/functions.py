from .markdown import parse_markdown_file_with_fm
from .tasks import Task

from copy import deepcopy
from glob import glob
from jinja2 import TemplateNotFound, Environment, FileSystemLoader
import logging
import sass
import shutil
from typing import Tuple, Optional
from wcmatch.pathlib import Path

# functions for filenames


def noop(filepath: Path, ctx: dict):
    pass


def compile_sass(filepath: Path, ctx: dict, in_dir: str, out_dir: str):
    in_dir = Path(in_dir)
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
    filepath: Path,
    ctx: dict,
    text: str,
    out_dir: str,
    ext: Optional[str] = None,
    relative_to: Optional[str] = None,
):
    if relative_to is not None:
        filepath = filepath.relative_to(relative_to)
    new_filepath = Path(out_dir) / filepath
    new_filepath.parent.mkdir(parents=True, exist_ok=True)
    if ext is not None:
        new_filepath = new_filepath.with_suffix(ext)
    with open(new_filepath, "w") as f:
        f.write(text)
    return ctx


def copy_files(
    filepath: Path, ctx: dict, out_dir: str, relative_to: Optional[str] = None
):
    out_dir = Path(out_dir)
    if relative_to is not None:
        new_filepath = Path(out_dir) / filepath.relative_to(relative_to)
    else:
        new_filepath = Path(out_dir) / filepath
    if filepath.is_file():
        new_filepath.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, new_filepath)
    elif filepath.is_dir():
        if new_filepath.exists():
            shutil.rmtree(new_filepath)
        shutil.copytree(filepath, new_filepath)
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
        if task.should_run(filepath_):
            logging.info(f" Running task {task.name} on {filepath_}:")
            ctx = task.run(deepcopy(ctx), filepath_)
    return ctx


def empty_directory(filepath: Path, ctx: dict, directory: str):
    directory = Path(directory)
    tmp_nm = directory.parent / ("__" + directory.name)
    directory.rename(tmp_nm)
    shutil.rmtree(tmp_nm)
    Path.mkdir(directory)
    return ctx
