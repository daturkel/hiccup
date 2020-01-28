import click
from pathlib import Path

TEMPLATE = """from collections import OrderedDict

import hiccup.functions as fn
from hiccup.tasks import Task

# Your hiccup config file is a plain old python file.
#
# It *must* contain four specific variables:
# - WATCH_TASKS: a list of tasks that are run, if triggered, with the `hiccup watch` command
# - CLEAN_TASKS: a list of tasks that are run with the `hiccup clean` command
# - RUN_TASKS: a list of tasks that are run with the `hiccup run` command
# - GLOBALS: a dictionary of arbitrary variables that can be used within tasks and steps
#
# A task is created using the Task class. The required arguments are `steps` and `name`.
# - steps is a list of tuples where each tuple is a function and a dictionary of keyword arguments to provide
# - name is a human-readable name for the task used during logging
#
# Tasks may also have several powerful optional arguments:
# - change_types is a string or list of strings indicating what types of file changes
#   (in watch mode) will trigger this task. The default value is None, which is interpreted
#   as "any":
#   - "add" means the file must be added
#   - "modify" means the file must be modified
#   - "delete" means the file must be deleted
#   - "change" is short-hand for ["add","modify"]
#   - "any" is short-hand for ["add","modify","delete"]
# - match_patterns is a string or list of strings indicating Unix glob-style patterns
#   that a file must match in order to trigger this step
# - skip_patterns is a string or list of strings indicating Unix glob-style patterns that a
#   file must *not* match in order to trigger this step
#

img_task = Task(
    steps=[(fn.copy_files, {"out_dir": "./dist"})],
    name="copy images",
    change_types="change",
    match_patterns=["./src/img/**/*"],
)

all_img_task = Task(
    steps=[(fn.copy_files, {"__filepath": "./src/img", "out_dir": "./dist"})],
    name="copy images",
    change_types="change",
)

WATCH_TASKS = [img_task]

CLEAN_TASKS = [
    Task(
        steps=[(fn.empty_directory, {"directory": "./dist"})], name="clean dist folder"
    )
]

RUN_TASKS = [all_img_task]

GLOBALS = {}
"""
