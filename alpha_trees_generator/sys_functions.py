# <pep8-80 compliant>

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
        imp_functions
    ]:
        importlib.reload(mod)
else:
    import os
    import bpy
    from . import (
        imp_functions
    )


def get_system_vars(self, context):
    sys_list = context.object.sys_list
    sys_settings = context.object.sys_settings
    index = sys_settings.index
    if context.object:
        if context.object.sys_list:
            item = sys_list[index]
        else:
            item = None

    psystems = context.object.particle_systems

    return sys_list, sys_settings, index, psystems, item


def get_item_psystem(self, context, item):
    psystems = context.object.particle_systems
    pindex = psystems.find(item.sys_name)
    psystem = psystems[pindex]

    return psystem, pindex


def get_previews_from_files(self, context):
    # This is pretty much just straight from the template scipt "Ui Previews Dynamic Enum"
    # so thanks blender devs :)
    """EnumProperty callback"""
    enum_items = []
    at = bpy.context.scene.alpha_trees

    #enum_items.append(("NONE", "Default", "Default tree", "VOLUME_DATA", 0))

    if context is None:
        return enum_items

    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(script_dir, "maps", "rendered_maps", "")

    # Get the preview collection (defined in register func).
    pcoll = imp_functions.preview_collections["alpha_trees_system_previews"]

    diff_maps = ["default.png"]
    for map in os.listdir(directory):
        if "diff_leaf" in map:
            diff_maps.append(map)
    
    #diff_maps.append(map for map in os.listdir(directory) if "diff_leaf" in map)

    if directory == pcoll.my_previews_dir and not at.reload_previews:
        return pcoll.my_previews

    print("Scanning directory: %s" % directory)

    # Scan the directory for files
    for i, name in enumerate(diff_maps):
        # generates a thumbnail preview for a file.
        filepath = os.path.join(directory, name)
        icon = pcoll.get(name)
        if not icon:
            thumb = pcoll.load(name, filepath, 'IMAGE')
        else:
            thumb = pcoll[name]
        label = name[:-19]
        enum_items.append((name, label, name, thumb.icon_id, i))

    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory
    return pcoll.my_previews


def get_settings_enum_items():
    at_settings = [
        setting.name for setting in bpy.data.particles if "AT_PSYSTEM" in setting.name and not "AT_PSYSTEM_basic" in setting.name]
    return at_settings


def get_default_obj(self, context):
    
        for obj in bpy.data.objects:
            if "AT_PSYSTEM_default_obj" in obj.name:
                default_plane = obj
                break
        else:
            bpy.ops.mesh.primitive_plane_add()
            default_plane = bpy.context.active_object
            default_plane.name = "AT_PSYSTEM_default_obj"

            verts = default_plane.data.vertices
            size = 0.05
            verts[0].co = (-size, 0, 0)
            verts[1].co = (size, 0, 0)
            verts[2].co = (-size, 0, (1 / size) * size)
            verts[3].co = (size, 0, (1 / size) * size)

            default_plane.track_axis = "POS_Z"
            default_plane.location = (0,0,0)
            context.scene.collection.objects.unlink(default_plane)
        
        return default_plane


def get_basic_psystem(self, context):
    for psetting in bpy.data.particles:
        if psetting.name == "AT_PSYSTEM_basic":
            basic_psetting = psetting
            break
    else:
        basic_psetting = bpy.data.particles.new("AT_PSYSTEM_basic")
        basic_psetting.type = "HAIR"
        basic_psetting.count = 100
    
    return basic_psetting

def get_default_psystem(self, context):
    for psetting in bpy.data.particles:
        if psetting.name == "AT_PSYSTEM_basic":
            default_psetting = psetting
            break
    else:
        default_psetting = bpy.data.particles.new("AT_PSYSTEM_basic")
        default_psetting.type = "HAIR"
        default_psetting.count = 100
    
    return default_psetting


def particle_index_update(self, context):

    psystems, item = get_system_vars(self, context)[3:]

    if psystems:
        pindex = psystems.find(item.sys_name)
        psystems.active_index = pindex
        if pindex == -1:
            print("can't find psystem")

def show_viewport_update(self, context):
    psys = context.object.particle_systems[self.sys_name]

    for mod in context.object.modifiers:
        if mod.type == "PARTICLE_SYSTEM":
            if mod.particle_system == psys:
                mod.show_viewport = self.show_viewport

def show_render_update(self, context):
    psys = context.object.particle_systems[self.sys_name]

    for mod in context.object.modifiers:
        if mod.type == "PARTICLE_SYSTEM":
            if mod.particle_system == psys:
                mod.show_render = self.show_render

# def psetting_name_update(self, context):
#     item = get_system_vars(self, context)[-1]
#     i = 0
#     matches = 1

#     while i <= len(context.object.sys_list)
#         for list_item in context.object.sys_list:
#             if item.psetting_name == list_item.psetting_name:
#                 item.psetting_name += str(matches)
#                 matches +=1
#         i+=1

#     psetting = bpy.data.particles[item.particle_settings]
#     psetting.name = "AT_PSYSTEM_" + item.psetting_name


def psettings_update(self, context):
    item = self
    psys = get_item_psystem(self, context, item)[0]
    at = context.scene.alpha_trees

    if item.particle_settings == item.sys_name:
        return

    if item.particle_settings == "NONE":
        basic_psetting = get_basic_psystem(self,context)

        psys.settings = basic_psetting
        return
        
    elif "default_" not in item.particle_settings:
        object = bpy.data.collections[item.particle_settings].objects[0]
        node = object.material_slots[0].material.node_tree.nodes["leaf color"]
        if item.selected_tree != node.image.name:
            item.selected_tree = node.image.name

    setting = bpy.data.particles[item.particle_settings]
    psys.settings = setting
    at.update_selected_tree = False
    #item.psetting_name = "Untitled settings " + str(len(get_settings_enum_items()))


def selected_tree_update(self, context):
    item = get_system_vars(self, context)[-1]
    psys = get_item_psystem(self, context, item)[0]
    at = context.scene.alpha_trees
    orig_object = context.object
    selected = orig_object.select_get()
    users = bpy.data.particles[item.particle_settings].users
    at_psettings = get_settings_enum_items()

    #if using same settings as another system
    if users == 0 or at.update_selected_tree or "default_" in item.particle_settings:

        if item.selected_tree == "default.png":
            object = get_default_obj(self, context)
        else:
            bpy.ops.alpha_tree.import_tree(for_psystem=True)
            object = context.active_object
            object.location = (0,0,0)

        collection = context.scene.collection.children["ALPHA_TREES_PARTICLE_COLLECTION"].children[item.particle_settings]
        previous_obj = collection.objects[0]  #

        collection.objects.unlink(previous_obj)
        collection.objects.link(object)

        context.view_layer.objects.active = orig_object

        if item.selected_tree == "default.png":
            default_psetting = get_basic_psystem(self, context)
            psys.settings = default_psetting
            item.name = "Untitled " + str(len(context.object.sys_list) - 1)
            psys.name = item.name
        else:
            context.scene.collection.objects.unlink(object)

            #check if created before
            duplicates = 0
            for setting in at_psettings:
                if "AT_PSYSTEM_" + item.selected_tree[:-19] in setting:
                    duplicates += 1

            new_name = "AT_PSYSTEM_" + item.selected_tree[:-19] + "_" + str(duplicates)
                
            psys.settings.name = new_name
            psys.name = new_name
            collection.name = new_name
            object.name = new_name.replace("AT_PSYSTEM_","")

            #check if mat needs to copy
            material = object.material_slots[0].material
            if duplicates != 0:
                orig_mat = material
                material = material.copy()
                bpy.data.materials.remove(orig_mat)
                object.material_slots[0].material = material
            material.name = new_name

            #prevent update loop
            if item.particle_settings != new_name:
                item.particle_settings = new_name

            item.sys_name = new_name

            if "Untitled " in item.name:
                item.name = new_name.replace("AT_PSYSTEM_","")

            psys.settings.phase_factor = (2 / 360 * at.particle_rotation) - 1
    
    else:
        new_name = item.particle_settings + "_" + str(users)
        psys.name = new_name
        item.sys_name = new_name
        if "Untitled " in item.name:
                item.name = new_name.replace("AT_PSYSTEM_","")

    orig_object.select_set(selected)
    at.update_selected_tree = True

def random_rotation_update(self, context):
    bpy.data.particles[self.particle_settings].rotation_factor_random = self.random_rotation

def overall_particle_rotation_update(self, context):
    sys_list = get_system_vars(self,context)[0]
    if sys_list:
        for item in sys_list:
            if item != "NONE":
                psettings = bpy.data.particles[item.particle_settings]
                psettings.phase_factor = (2/360*self.particle_rotation)-1

def get_alpha_trees_psettings(self, context):
    items = [("NONE", "None", "None")]

    for setting in bpy.data.particles:
        if "AT_PSYSTEM" in setting.name and not "AT_PSYSTEM_basic" in setting.name:
            item = (setting.name, setting.name[11:],
                    "Settings to use for particle system")
            items.append(item)

    return items
