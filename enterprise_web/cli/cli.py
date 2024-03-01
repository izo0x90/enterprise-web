# TODO: (Hristo) Break cli into modules

from contextlib import contextmanager
from dataclasses import dataclass
import pathlib
import importlib
import inspect

# from rich import print  # TODO: (Hristo) Remove as "real" UI/CLI develops ?
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from rich.theme import Theme
from tomlkit import dumps, parse, table
import typer
import jinja2

LIB_IDENTIFIER = "enterprise_web"

cli_theme = Theme(
    {
        "error": "bold red",
    }
)

error_console = Console(stderr=True, theme=cli_theme)
console = Console(theme=cli_theme)

app = typer.Typer()
info_app = typer.Typer()
add_app = typer.Typer()
app.add_typer(info_app, name="info")
app.add_typer(add_app, name="add")


# Utils
def print_err(msg):
    error_console.print(msg, style="error")


def print(msg):
    console.print(msg)


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
    project = importlib.import_module(f"{package_name}.main", package=package_name)
    return project


def extract_project_info(config):
    package_name = config["tool"][LIB_IDENTIFIER]["project_name"]
    return {"project_name": package_name}


## Entity utils
def extract_entities_info(project_obj):
    entities = {}
    for entity_name, repo_type in project_obj.repo.repo_types.items():
        entities[entity_name] = {
            "name": entity_name,
            "class": repo_type.ENTITY_CLS,
            "repo": repo_type,
            "datastore_type": repo_type.DATA_STORE_TYPE,
        }

    return entities


GENERIC_ENTITY_SUFFIX = "Entity"
ENTITY_DIR_NAME = "domain"
ENTITY_FILE_SUFFIX = "_entity.py"


def make_entity_names(entity_name_prefix):
    entity_class_prefix = entity_name_prefix.capitalize()
    entity_name = f"{entity_class_prefix}{GENERIC_ENTITY_SUFFIX}"
    entity_directory_name = ENTITY_DIR_NAME
    entity_file_name = f"{entity_name_prefix}{ENTITY_FILE_SUFFIX}"
    return entity_name, entity_class_prefix, entity_directory_name, entity_file_name


# Entity utils END


def extract_features_info(project_obj):
    features = {}
    for feature in project_obj.app.features:
        name = feature.name
        path = inspect.getfile(type(feature))
        command_groups = feature.command_groups
        features[name] = {
            "path": path,
            "class": type(feature),
            "command_groups": command_groups,
        }
    return features


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


## Entity commands
class EntityAlreadyExists(Exception):
    pass


@dataclass
class NewEntityData:
    entity_name: str
    entity_file_path: str
    entity_file_content: str


def create_entity_command(feature_name: str, entity_name_prefix: str):
    path = pathlib.Path(__file__).parent / "templates"
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    template = jinja_env.get_template("entity.jinja2")
    (
        entity_name,
        class_prefix,
        entity_directory_name,
        entity_file_name,
    ) = make_entity_names(entity_name_prefix)

    config = read_project_config()
    project_obj = import_project(config)
    entitities = extract_entities_info(project_obj)

    if entity_name in entitities:
        raise EntityAlreadyExists

    features = extract_features_info(project_obj)
    if feature_name not in features:
        raise ValueError(f"Feature `{feature_name}` does not exist!")

    feature = features[feature_name]

    feature_path = pathlib.Path(feature["path"]).parent
    entity_file_path = feature_path / entity_directory_name / entity_file_name

    entity_code = template.render(
        entity_name_prefix=class_prefix, entity_name=entity_name
    )

    return NewEntityData(
        entity_name=entity_name,
        entity_file_path=entity_file_path,
        entity_file_content=entity_code,
    )


## Entity commands

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
    exitsting_entities = extract_entities_info(project_obj)
    console.rule()
    for entity_name, entity_meta in exitsting_entities.items():
        print(f"Entity name: {entity_name}, class: {entity_meta.get('class')}")


@info_app.command()
def features():
    console.rule("Loading project ...")
    config = read_project_config()
    project_obj = import_project(config)
    project_info = extract_project_info(config)
    features = extract_features_info(project_obj)
    console.rule()

    table = Table(title=f"Project `{project_info['project_name']}` features")
    table.add_column("Feature name")
    table.add_column("Path")
    table.add_column("Class")
    for name, meta in features.items():
        table.add_row(name, meta["path"], str(meta["class"]))

    print(table)


@add_app.command()
def entity(feature_name: str, entity_name_prefix: str, yes: bool = False):
    console.rule("Loading project ...")
    new_entity_data = create_entity_command(feature_name, entity_name_prefix)
    # TODO: (hristo) Generate datamodel data, lol
    # TODO: (hristo) Generate repo data
    console.rule("New entity name:")
    print(new_entity_data.entity_name)
    console.rule("Path to entity file: ")
    print(new_entity_data.entity_file_path)
    console.rule("Generated entity code:")
    print(new_entity_data.entity_file_content)
    console.rule()
    if not yes:
        yes = Confirm.ask("Create entity ?", console=console)

    if yes:
        # TODO: (Hristo) Create entity, repo and data model
        print(
            "Entity created! (Not actually we are just pretending for now :kissing_cat_face:)"
        )
    else:
        print("Entity create operation aborted :cross_mark:")


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
