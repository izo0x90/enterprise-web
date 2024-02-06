from enterprise_web.api.feature import ApiFeature

from .commands.crud.feature_group import crud_commands

project_feature = ApiFeature("project")

project_feature.add_command_group(crud_commands)
