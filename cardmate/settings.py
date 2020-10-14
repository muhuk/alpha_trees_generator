# <pep8-80 compliant>

# CardMate is a Blender addon that helps with baking billboards.
# Copyright (C) 2020  Atamert Ölçgen
#
# This project is a fork of alpha_trees_generator.
# Copyright (C) 2020  Andrew Stevenson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

if "bpy" in locals():
    import importlib
    for mod in [
        imp_functions,
        sys_functions
    ]:
        importlib.reload(mod)
else:
    import os
    import bpy
    from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty, EnumProperty, CollectionProperty
    from . import (
        imp_functions,
        sys_functions
    )


class ATGeneratorSettings(bpy.types.PropertyGroup):

    # Show UI
    # ----------------------------------------------------------

    import_type: EnumProperty(
        items=(
            ("OBJECT", "Object", "Import trees to the viewport directly for use by the use","OBJECT_DATA",0),
            ("PARTICLE", "Particle", "Import trees into ready to use particle systems with easy settings","PARTICLE_DATA",1)
        )
    )

    show_info: BoolProperty(
        name="Info",
        description="Show info about how to use the addon",
        default=False
    )

    show_setup_tree_settings: BoolProperty(
        name="settings",
        description="Show setup settings",
        default=False
    )

    show_render_settings: BoolProperty(
        name="Show render settings",
        description="Show render settings",
        default=False,
    )

    show_open_folder_settings: BoolProperty(
        name="settings",
        description="Show Alpha trees operators",
        default=False,
    )

    show_exec_all_settings: BoolProperty(
        name="settings",
        description="Show Alpha trees operators",
        default=False,
    )

    # generator operator settings
    # ----------------------------------------------------------

    script_path = os.path.dirname(os.path.abspath(__file__))

    border_padding: FloatProperty(
        name="Render padding",
        default=0.03,
        description="Amount of extra space around object",
        soft_min=0,
        soft_max=0.2,
    )

    resolution: IntProperty(
        name="Resolution",
        default=1024,
        description="Max resolution of images",
        subtype="PIXEL"
    )

    render_filepath: StringProperty(
        name="",
        default=os.path.join(script_path,"maps","rendered_maps",""),
        description="Filepath to save rendered images to",
        subtype="FILE_PATH"
    )

    diff_render: BoolProperty(
        name="render diffuse map",
        default=True,
        description="render the diffuse map",
    )

    nor_render: BoolProperty(
        name="render normal map",
        default=True,
        description="render the normal map",
    )

    mask_render: BoolProperty(
        name="render mask map",
        default=True,
        description="render the mask map",
    )

    overwrite: BoolProperty(
        name="Overwrite",
        default=True,
        description="Overwrite images if they already exist",
    )

    remove_extra_masks: BoolProperty(
        name="delete extra masks",
        default=True,
        description="delete extra masks after combining (turn off for debug)",
    )

    open_renders_folder: BoolProperty(
        name="open renders folder on completion",
        default=False,
        description="open the renders folder on completion",
    )

    open_leaf_folder: EnumProperty(
        items=(
            ("renders", "Final renders", "Open renders folder"),
            ("leaves", "Leaf normals", "Open leaf normals folded (debug)")
        ),
        name="Folder",
        default="renders",
        description="Folder to open",
    )

    # importer operator settings
    # ----------------------------------------------------------

    alpha_trees_previews : EnumProperty(
        items=imp_functions.get_previews_from_files,
    )

    reload_previews : BoolProperty(
        name="Reload previews",
        default=False,
        description="Reload the previews to inculde new trees",
    )

    update_selected_tree : BoolProperty(
        default=True,
    )

    particle_rotation : IntProperty(
        name="Rotation",
        default=180,
        min=0,
        max=360,
        update=sys_functions.overall_particle_rotation_update,
        subtype="ANGLE"
    )

    # show importer settings
    # ----------------------------------------------------------

    show_particle_settings : BoolProperty(
        name="Show settings",
        default=True,
        description="Show settings",
    )

    show_material_settings : BoolProperty(
        name="Show settings",
        default=True,
        description="Show settings",
    )

class SystemSettings(bpy.types.PropertyGroup):

    # Particle system settings
    index: IntProperty(
        default=0,
        update = sys_functions.particle_index_update,
    )

class SystemListItem(bpy.types.PropertyGroup):

    sys_name : StringProperty(
        name="System name",
        description="particle system name",
        default="None"
        )

    #display

    name: StringProperty(
        name="Name",
        description="System display name name",
        default= "Untitled"
        )

    show_viewport : BoolProperty(
        name="Show viewport",
        default=True,
        description="Show system in the viewport",
        update = sys_functions.show_viewport_update
    )

    show_render : BoolProperty(
        name="Show rendered",
        default=True,
        description="Show system when rendered",
        update = sys_functions.show_render_update
    )

    particle_settings: EnumProperty(
        items = sys_functions.get_alpha_trees_psettings,
        name="Settings",
        description="Settings to use for this particle system",
        update=sys_functions.psettings_update,
        )

    selected_tree : EnumProperty(
        items=sys_functions.get_previews_from_files,
        update = sys_functions.selected_tree_update,
    )

    random_rotation: FloatProperty(
        name = "Random rotation",
        default=0.025,
        min=0,
        max=0.15,
        update = sys_functions.random_rotation_update
    )

    # psetting_name: StringProperty(
    #     name="Name",
    #     description="Settings name",
    #     default="Untitled",
    #     #update = sys_functions.psetting_name_update,
    #     )

classes = (
    ATGeneratorSettings,
    SystemListItem,
    SystemSettings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.alpha_trees = bpy.props.PointerProperty(type=ATGeneratorSettings)
    bpy.types.Object.sys_list = CollectionProperty(type = SystemListItem)
    #bpy.types.Object.sys_item = bpy.props.PointerProperty(type=SystemListItem)
    bpy.types.Object.sys_settings = bpy.props.PointerProperty(type=SystemSettings)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.alpha_trees
    del bpy.types.Object.sys_list
    #del bpy.types.Object.sys_item
    del bpy.types.Object.sys_settings
