#!/bin/bash
set -e

python3 - <<END
import jinja2
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader("benchmarks/templates/"),
    autoescape=select_autoescape(),
)

template = env.get_template("bench_minimize.py")
for n in range(20):
    fnam = f"benchmarks/bench_minimize_{n:02}.py"
    with open(fnam, "w") as file:
        print("Generating %s . . . " % fnam)
        file.write(
            template.render(
                NUM=f"{n:02}"
            )
        )
END
