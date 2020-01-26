from collections import OrderedDict

import hiccup.functions as fn
from hiccup.tasks import Task


def get_out_dir(filepath: str, ctx: dict, text: str):
    if ctx["template"] == "post":
        out_dir = "./dist/posts"
    elif ctx["template"] == "page":
        out_dir = "./dist"
    else:
        out_dir = "./dist"
    ctx["out_dir"] = out_dir
    ctx["text"] = text
    return ctx


OLD_TASKS = OrderedDict(
    {
        ("**/*.md", "change", "a"): [
            (fn.parse_markdown_with_template, {"template_dir": "./src/templates"}),
            (get_out_dir, {"text": "__output"}),
            (fn.write_text_to_file, {"ext": ".html"}),
        ],
        ("sass/**/*.sass", "change"): [
            (fn.compile_sass, {"in_dir": "./src/sass", "out_dir": "./dist/scss"})
        ],
    }
)

md_task = Task(
    match_patterns="**/*.md",
    change_types="change",
    steps=[
        (fn.parse_markdown_with_template, {"template_dir": "./src/templates"}),
        (get_out_dir, {"text": "__output"}),
        (fn.write_text_to_file, {"ext": ".html"}),
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

GLOBALS = {
    "pages": [
        {"file_name": "index.html", "title": "Home"},
        {"file_name": "about.html", "title": "About"},
        {"file_name": "photo.html", "title": "Photo"},
        {"file_name": "code.html", "title": "Code"},
    ]
}
