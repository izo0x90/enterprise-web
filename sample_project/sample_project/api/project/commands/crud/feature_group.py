from enterprise_web.api.feature import FeatureGroup

crud_commands = FeatureGroup('crud')
in_between = FeatureGroup('in_between')
crud_commands2 = FeatureGroup('crud2')

in_between.add_command_group(crud_commands2)
crud_commands.add_command_group(in_between)
