import importlib
import logging
from wcmatch.pathlib import Path
import shutil
import sys
import time
import toml
from typing import List, Optional

import click
import watchgod

from .config import HiccupConfig
from .generate_config import TEMPLATE
from .logger import setup_logger
from .tasks import TaskList
from .utils import change_to_str
from .watcher import GlobWatcher


@click.group()
@click.option(
    "-c", "--config", "config_filename", default="./hiccup_config.py", type=Path
)
@click.pass_context
def cli(ctx, config_filename):
    setup_logger()
    ctx.obj["config_filename"] = config_filename


@cli.command()
@click.option("-m", "--match-patterns", default=None, multiple=True)
@click.option("-s", "--skip-patterns", default=None, multiple=True)
@click.argument("watch_dir", nargs=1, default="./", type=Path)
@click.pass_context
def watch(ctx, match_patterns, skip_patterns, watch_dir):
    logging.info(f"Watching directory {watch_dir}")
    config = HiccupConfig(ctx.obj["config_filename"])
    task_ctx = {"__globals": config.globals, "__root": watch_dir}
    task_list = TaskList(tasks=config.watch_tasks, ctx=task_ctx)
    watcher_kwargs = {
        "match_patterns": match_patterns if match_patterns else None,
        "skip_patterns": skip_patterns if skip_patterns else None,
    }
    for changes in watchgod.watch(
        watch_dir, watcher_cls=GlobWatcher, watcher_kwargs=watcher_kwargs
    ):
        for change_type, filepath in changes:
            filepath = Path(filepath)
            logging.info(f"File {filepath} {change_type.name}!")
            task_list.run_tasks(filepath, change_to_str(change_type))


@cli.command()
@click.option("-d", "--deep", is_flag=True)
@click.pass_context
def clean(ctx, deep):
    config = HiccupConfig(ctx.obj["config_filename"])
    task_ctx = {"__globals": config.globals, "__root": ""}
    task_list = TaskList(tasks=config.clean_tasks, ctx=task_ctx)
    logging.info("Running clean tasks")
    task_list.run_tasks()


@cli.command()
@click.option("-c", "--clean", is_flag=True)
@click.pass_context
def run(ctx, clean):
    config = HiccupConfig(ctx.obj["config_filename"])
    task_ctx = {"__globals": config.globals, "__root": ""}
    if clean:
        logging.info("Running tasks")
        TaskList(tasks=config.clean_tasks, ctx=task_ctx).run_tasks()
    task_list = TaskList(tasks=config.run_tasks, ctx=task_ctx)
    logging.info("Running tasks")
    task_list.run_tasks()


@cli.command()
@click.option("-p", "--path", type=Path, default="hiccup_config.py")
@click.option("-f", "--force", is_flag=True)
def generate_config(path, force):
    if force and path.exists():
        ts = str(int(time.time()))
        backup_path = path.parent / (path.stem + ts + path.suffix)
        logging.info(
            f"Config file at {path} already exists, backing up to {backup_path}"
        )
        shutil.copy2(path, backup_path)
        logging.info(f"Writing new config template to {path}")
    elif force or not path.exists():
        logging.info(f"Writing new config template to {path}")
    else:
        raise FileExistsError(
            f"Config file already exists at {path}. Use hiccup generate-config --force to overwrite it."
        )
    with open(path, "w") as f:
        f.write(TEMPLATE)


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
