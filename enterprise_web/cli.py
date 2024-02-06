# TODO: (Hristo) Break cli into modules

from contextlib import contextmanager
import importlib

from rich import print  # TODO: (Hristo) Remove as "real" UI/CLI develops ?
from rich.console import Console
from rich.theme import Theme
from tomlkit import dumps, parse, table
import typer

LIB_IDENTIFIER = "enterprise_web"

cli_theme = Theme(
    {
        "error": "bold red",
    }
)

error_console = Console(stderr=True, theme=cli_theme)

app = typer.Typer()
info_app = typer.Typer()
app.add_typer(info_app, name="info")


# Utils
def print_err(msg):
    error_console.print(msg, style="error")


class ProjectAlreadyInit(Exception):
    pass


@contextmanager
def open_project_config():
    with open("pyproject.toml", "r+") as project_config_file:
        yield project_config_file


def read_project_config():
    with open_project_config() as project_config_file:
        config = parse(project_config_file.read())
        return config


def write_project_config(config):
    with open_project_config() as project_config_file:
        content = dumps(config)
        project_config_file.seek(0)
        project_config_file.write(content)


def import_project(config):
    package_name = config["tool"][LIB_IDENTIFIER]["project_name"]
    return importlib.import_module(f"{package_name}.main", package=package_name)


# Utils END


# Commands
def init_command(project_name: str):
    config = read_project_config()

    tool_table = config.get("tool")

    if not tool_table:
        tool_table = table()

    if LIB_IDENTIFIER in tool_table:
        raise ProjectAlreadyInit

    ew_table = table()
    ew_table.add("project_name", project_name)

    tool_table.add(LIB_IDENTIFIER, ew_table)

    write_project_config(config)


def extract_entities_info(project_obj):
    return project_obj.repo.repo_types


# Commands END

# UI
# TODO: (Hristo) Add ui for managing project using Textual
# UI END


# Command line interface
@info_app.command()
def overview():
    print("Loading project ...")
    config = read_project_config()
    m = import_project(config)
    print("Project overview: ")
    print(m.app)
    print(m.repo.repo_types)


@info_app.command()
def entities():
    print("Loading project ...")
    config = read_project_config()
    project_obj = import_project(config)
    entitities = extract_entities_info(project_obj)
    print("Project entities: ")
    print(entitities)


@app.command()
def init(project_name: str):
    try:
        init_command(project_name)
    except ProjectAlreadyInit:
        print_err("Project is already initialized!")
    except FileNotFoundError:
        print_err("Python project with a `pyproject.toml` file is required!")


# Command line interface END

if __name__ == "__main__":
    app()
