from collections import OrderedDict

import hiccup.functions as fn
from hiccup.tasks import Task


md_task = Task(
    steps=[
        (fn.parse_markdown_with_template, {"template_dir": "./src/templates"}),
        (
            fn.write_text_to_file,
            {"ext": ".html", "text": "__output", "out_dir": "./dist"},
        ),
    ],
    name="parse markdown",
    change_types="change",
    match_patterns="./src/**/*.md",
    skip_patterns="./src/ext/**/*",
)

img_task = Task(
    steps=[(fn.copy_files, {"out_dir": "./dist"})],
    name="copy images",
    change_types="change",
    match_patterns=["./src/img/**/*"],
)

j2_task = Task(
    steps=[
        (fn.run_task_on_matches, {"task": md_task, "match_pattern": "./src/**/*.md"})
    ],
    name="recreate all pages",
    change_types="change",
    match_patterns="./src/templates/**/*.j2",
    skip_patterns=None,
)

sass_task = Task(
    steps=[(fn.compile_sass, {"in_dir": "./src/sass", "out_dir": "./dist/css"})],
    name="compile sass",
    change_types="change",
    match_patterns=["./src/sass/**/*.sass", "./src/sass/**/*.scss"],
    skip_patterns=None,
)

WATCH_TASKS = [j2_task, md_task, sass_task, img_task]

CLEAN_TASKS = [
    Task(
        steps=[(fn.empty_directory, {"directory": "./dist"})], name="clean dist folder"
    )
]

RUN_TASKS = [
    j2_task,
    sass_task,
    Task(
        steps=[(fn.copy_files, {"__filepath": "./src/img", "out_dir": "./dist"})],
        name="copy all images",
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
