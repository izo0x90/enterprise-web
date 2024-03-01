from enterprise_web.api.feature import ApiFeature

from .commands.crud.feature_group import crud_commands


class ProjectFeature(ApiFeature):
    name = "project"


project_feature = ProjectFeature(ProjectFeature.name)

project_feature.add_command_group(crud_commands)
