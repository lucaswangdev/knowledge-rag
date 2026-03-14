## uv 搭建Python开发环境，Python版本 3.12，Python版本 3.12，Python版本 3.12（重要）

uv manages project dependencies and environments, with support for lockfiles, workspaces, and more, similar to rye or poetry:


uv init example


cd example

uv add ruff








uv run ruff check


uv lock


uv sync


See the project guide to get started.

uv also supports building and publishing projects, even if they're not managed with uv. See the packaging guide to learn more.

Scripts
uv manages dependencies and environments for single-file scripts.

Create a new script and add inline metadata declaring its dependencies:


echo 'import requests; print(requests.get("https://astral.sh"))' > example.py

uv add --script example.py requests

Then, run the script in an isolated virtual environment:


uv run example.py



See the scripts guide to get started.