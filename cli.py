import importlib
import logging
from wcmatch.pathlib import Path
import sys
import toml
from typing import List, Optional

import click
import watchgod

from hiccup.config import HiccupConfig
from hiccup.logger import setup_logger
from hiccup.tasks import TaskList
from hiccup.utils import change_to_str
from hiccup.watcher import GlobWatcher


@click.group()
@click.option("-c", "--config", "config_filename", default="./hiccup_config.py")
@click.pass_context
def cli(ctx, config_filename):
    setup_logger()
    config = HiccupConfig(Path(config_filename))
    ctx.obj["config"] = config


@cli.command()
@click.option("-m", "--match-patterns", default=None, multiple=True)
@click.option("-s", "--skip-patterns", default=None, multiple=True)
@click.argument("watch_dir", nargs=1, default="./", type=Path)
@click.pass_context
def watch(ctx, match_patterns, skip_patterns, watch_dir):
    logging.info(f"Watching directory {watch_dir}")
    config = ctx.obj["config"]
    task_list = TaskList(
        tasks=config.watch_tasks, watch_dir=watch_dir, globals_=config.globals
    )
    watcher_kwargs = {
        "match_patterns": match_patterns if match_patterns else None,
        "skip_patterns": skip_patterns if skip_patterns else None,
    }
    for changes in watchgod.watch(
        watch_dir, watcher_cls=GlobWatcher, watcher_kwargs=watcher_kwargs
    ):
        for change_type, filepath in changes:
            filepath = Path(filepath)
            rel_filepath = filepath.relative_to(Path(watch_dir))
            logging.info(f"File {rel_filepath} {change_type.name}!")
            task_list.run_tasks(filepath, change_to_str(change_type))


@cli.command()
@click.option("-d", "--deep", is_flag=True)
@click.pass_context
def clean(ctx, deep):
    pass


if __name__ == "__main__":
    cli(obj={})
