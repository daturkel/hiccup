from collections import OrderedDict

import hiccup.functions as fn
from hiccup.tasks import Task


md_task = Task(
    match_patterns="**/*.md",
    change_types="change",
    steps=[
        (fn.parse_markdown_with_template, {"template_dir": "./src/templates"}),
        (
            fn.write_text_to_file,
            {"ext": ".html", "text": "__output", "out_dir": "./dist"},
        ),
    ],
    name="parse markdown",
    skip_patterns="ext/**/*",
)

WATCH_TASKS = [
    Task(
        match_patterns="templates/**/*.j2",
        change_types="change",
        steps=[(fn.run_task_on_matches, {"task": md_task, "match_pattern": "**/*.md"})],
        name="recreate all pages",
        skip_patterns=None,
    ),
    md_task,
    Task(
        match_patterns=["sass/**/*.sass", "sass/**/*.scss"],
        change_types="change",
        steps=[(fn.compile_sass, {"in_dir": "sass", "out_dir": "./dist/css"})],
        name="compile sass",
        skip_patterns=None,
    ),
]

CLEAN_TASKS = []

GLOBALS = {
    "pages": [
        {"file_name": "index.html", "title": "Home"},
        {"file_name": "about.html", "title": "About"},
        {"file_name": "photo.html", "title": "Photo"},
        {"file_name": "code.html", "title": "Code"},
    ]
}
