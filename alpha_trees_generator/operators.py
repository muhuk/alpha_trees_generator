import bpy
import os
import time
import webbrowser
from bpy.props import FloatProperty, IntProperty, BoolProperty
from . import gen_functions, imp_functions, sys_functions
from .sys_functions import get_system_vars

# Generator


class ALPHATREE_OT_set_up_scene(bpy.types.Operator):
    """Set up scene for rendering"""
    bl_label = "Set up scene"
    bl_idname = "alpha_tree.set_up_scene"
    bl_description = "Set up scene for rendering"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        gen_functions.setup_scene(self, context)

        return {"FINISHED"}


class ALPHATREE_OT_set_up_tree(bpy.types.Operator):
    """Set up tree for rendering"""
    bl_label = "Set up tree"
    bl_idname = "alpha_tree.set_up_tree"
    bl_description = "Set up tree for rendering"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        if not bpy.context.selected_objects:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}

        gen_functions.scale_to_height()
        gen_functions.set_render_border(context)
        gen_functions.transparent_normal(self, context)

        return {"FINISHED"}


class ALPHATREE_OT_render_maps(bpy.types.Operator):
    """render all maps"""
    bl_label = "Render maps"
    bl_idname = "alpha_tree.render_maps"
    bl_description = "render all maps"
    bl_description = "render all maps"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cscene = scene.cycles
        layout.scale_y = 1.3
        layout.prop(cscene, "samples", text="samples (50 max.)")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        if not bpy.context.selected_objects:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}

        gen_functions.render_maps(self, context)

        return {"FINISHED"}


class ALPHATREE_OT_open_folder(bpy.types.Operator):
    """open the renders folder"""
    bl_label = "Open renders folder"
    bl_idname = "alpha_tree.open_folder"
    bl_description = "Open renders folder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        at = bpy.context.scene.alpha_trees
        if at.open_leaf_folder == "leaves":
            script_path = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_path, "maps", "leaf_maps", "")
            path = bpy.path.abspath(script_path)
        else:
            path = bpy.path.abspath(at.render_filepath)
        print("Opening: " + path)
        webbrowser.open('file:///' + path)
        return {"FINISHED"}


class ALPHATREE_OT_execute_all(bpy.types.Operator):
    """Execute all operators"""
    bl_label = "Execute all"
    bl_idname = "alpha_tree.execute_all"
    bl_description = "Execute all operators"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cscene = scene.cycles
        layout.scale_y = 1.3
        layout.prop(cscene, "samples", text="samples (50 max.)")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        if not bpy.context.selected_objects:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}

        start = time.time()
        at = bpy.context.scene.alpha_trees

        print("Scaling object")
        gen_functions.scale_to_height()
        print("Rendering normal image")
        gen_functions.transparent_normal(self, context)
        print("Rendering maps")
        gen_functions.render_maps(self, context)
        if at.open_renders_folder:
            print("Opening folder")
            bpy.ops.alpha_tree.open_folder()

        total_time = round(time.time() - start, 2)

        print(f"Done in {total_time} seconds")

        return {"FINISHED"}

# Importer


class ALPHATREE_OT_import_tree(bpy.types.Operator):
    """Import a tree from the available library"""
    bl_label = "Import Tree"
    bl_idname = "alpha_tree.import_tree"
    bl_description = "Import a tree from the available library"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    for_psystem: BoolProperty(
        default = False
    )

    def execute(self, context):

        path = os.path.dirname(os.path.abspath(__file__))

        if self.for_psystem:
            item = sys_functions.get_system_vars(self, context)[-1]
            imp_functions.import_tree(os.path.join(path, "maps", "rendered_maps", item.selected_tree))

        else:    
            at = context.scene.alpha_trees
            print("")
            print("Importing " + at.alpha_trees_previews[:-19])
            imp_functions.import_tree(os.path.join(path, "maps", "rendered_maps", at.alpha_trees_previews))

        return {"FINISHED"}


class ALPHATREE_OT_reload_previews(bpy.types.Operator):
    """Reload the previews to inculde new trees"""
    bl_label = "Reload previews"
    bl_idname = "alpha_tree.reload_previews"
    bl_description = "Reload the previews to inculde new trees"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        at = context.scene.alpha_trees
        at.reload_previews = True
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=0)
        at.reload_previews = False

        return {"FINISHED"}


class ALPHATREE_OT_multi_import(bpy.types.Operator):
    """Import multiple trees from the library"""
    bl_label = "Multi import"
    bl_idname = "alpha_tree.multi_import"
    bl_description = "Import multiple trees from the library"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    tree_search: bpy.props.StringProperty(
        name="",
        default="",
        description="Import trees whose name contains these words",
    )

    def draw(self, context):
        layout = self.layout
        pcoll = imp_functions.preview_collections["alpha_trees_previews"]

        layout.label(text="Import trees containing the words:")
        layout.prop(self, "tree_search")
        layout.separator()
        layout.label(text="Trees found:")
        i = 0
        row = layout.row(align=True)
        col = row.column(align=True)
        col.scale_y = 0.3

        matches = [map for map in imp_functions.get_diff_maps(
        )[1] if self.tree_search.upper() in map.upper() or self.tree_search == ""]

        for i, map in enumerate(matches):
            if i == int(len(matches)/2) + 1:
                col = row.column(align=True)
                col.scale_y = 0.3
            trow = col.row(align=True)
            trow.scale_x = 10
            trow.template_icon(icon_value=pcoll[map].icon_id, scale=8)
            tcol = trow.column(align=True)
            tcol.scale_y = 5
            tcol.separator()
            tcol.label(text=map[:-19])
            i += 1

        if i == 1:
            col = row.column(align=True)
            col.template_icon(icon_value=101, scale=8)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        at = context.scene.alpha_trees
        diff_maps = imp_functions.get_diff_maps()[1]
        trees = []
        pos = 0

        for map in diff_maps:
            if self.tree_search.upper() in map.upper() or self.tree_search == "":
                at.alpha_trees_previews = map
                bpy.ops.alpha_tree.import_tree()
                trees.append(context.active_object)

        if trees == []:
            self.report({"WARNING"}, "No trees found")
            return{"CANCELLED"}

        def get_size(object):
            return object.dimensions[2]

        trees.sort(key=get_size)
        total_len = 0
        for tree in trees:
            total_len += tree.dimensions[0]

        for tree in trees:
            pos += tree.dimensions[0]/2
            tree.location[0] = pos - total_len/2
            pos += tree.dimensions[0]/2

        return {"FINISHED"}


class ALPHATREE_OT_change_tree(bpy.types.Operator):
    """Switch to the next/previous tree"""
    bl_idname = 'alpha_tree.change_tree'
    bl_label = 'Next/Previous'
    bl_options = {'INTERNAL'}

    forward: bpy.props.BoolProperty()

    def execute(self, context):
        at = context.scene.alpha_trees
        diff_maps = imp_functions.get_diff_maps()[1]

        for i, map in enumerate(diff_maps):
            if map == at.alpha_trees_previews:
                break

        if diff_maps[i] == diff_maps[0] and not self.forward:
            at.alpha_trees_previews = diff_maps[-1]
            return {"FINISHED"}
        elif diff_maps[i] == diff_maps[-1] and self.forward:
            at.alpha_trees_previews = diff_maps[0]
            return {"FINISHED"}
        else:
            at.alpha_trees_previews = diff_maps[i +
                                                1] if self.forward else diff_maps[i - 1]
        return {"FINISHED"}


class ALPHATREE_OT_sys_list_actions(bpy.types.Operator):
    """Manipulate list items, either: move up, move down, add or remove"""
    bl_label = "List actions"
    bl_idname = "alpha_tree.sys_list_actions"
    bl_description = "Manipulate list items, either: move up, move down, add or remove"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER"}

    action: bpy.props.EnumProperty(
        items=(
            ("ADD", "Add", "Add item"),
            ("REMOVE", "Remove", "Remove item"),
            ("UP", "Up", "Move item up"),
            ("DOWN", "Down", "Move item down"),
        )
    )

    def execute(self, context):
        sys_list, sys_settings, index, psystems, item = get_system_vars(self, context)

        if self.action == "ADD":

            bpy.ops.object.particle_system_add()
            psys = psystems.active
            orig_psettings = psys.settings

            basic_psetting = sys_functions.get_basic_psystem(self,context)

            psys.settings = basic_psetting
            psys.seed = len(sys_list)
            bpy.data.particles.remove(orig_psettings)

            sys_list.add()
            new_item = sys_list[len(sys_list)-1]
            new_item.name = "Untitled " + str(len(sys_list) - 1)
            psys.name = new_item.name
            new_item.sys_name = psys.name
            sys_settings.index = len(sys_list) - 1

            return {"FINISHED"}

        elif self.action == "REMOVE":

            pindex = psystems.find(sys_list[index].sys_name)
            psystems.active_index = pindex
            bpy.ops.object.particle_system_remove()

            sys_list.remove(index)
            sys_settings.index = min(max(0, index - 1), len(sys_list) - 1)

            return {"FINISHED"}

        elif self.action == "UP" or "DOWN":
            up = (self.action == "UP")
            length = len(sys_list) - 1
            new_index = index + (-1 if up else 1)

            sys_list.move(new_index, index)
            sys_settings.index = max(0, min(new_index, length))

        return {"FINISHED"}


class ALPHATREE_OT_new_settings(bpy.types.Operator):
    """Add new settngs for this system"""
    bl_label = "Add settings"
    bl_idname = "alpha_tree.sys_new_settings"
    bl_description = "Add new settngs for this system"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER"}

    def execute(self, context):

        item = get_system_vars(self, context)[-1]
        at = context.scene.alpha_trees
        object = context.active_object
        selected = object.select_get()

        # collections
        collections = [col.name for col in context.scene.collection.children]
        parent_coll_name = "ALPHA_TREES_PARTICLE_COLLECTION"

        if parent_coll_name in collections:
            parent_coll = context.scene.collection.children[parent_coll_name]
        else:
            parent_coll = bpy.data.collections.new(parent_coll_name)
            context.scene.collection.children.link(parent_coll)
            layer_parent_coll = context.view_layer.layer_collection.children.get(
                parent_coll_name)
            layer_parent_coll.exclude = True

        i = -1
        for coll in parent_coll.children:
            num = ""
            if "AT_PSYSTEM_default" in coll.name:
                for ch in coll.name:
                    try:
                        int(ch)
                    except ValueError:
                        continue
                    num += (ch)
            if num:
                if int(num) > i:
                    i = int(num)
                elif int(num) == i:
                    i = int(num) + 1
        i += 1

        collection = bpy.data.collections.new(
            "AT_PSYSTEM_default" + "_" + str(i))
        parent_coll.children.link(collection)

        # placeholder ob
        default_plane = sys_functions.get_default_obj(self, context)

        collection.objects.link(default_plane)
        context.view_layer.objects.active = object

        # particle settings
        psetting = bpy.data.particles.new("AT_PSYSTEM_default" + "_" + str(i))

        psetting.type = "HAIR"
        psetting.use_advanced_hair = True
        psetting.render_type = 'COLLECTION'
        psetting.instance_collection = collection
        psetting.use_rotation_instance = False
        psetting.use_scale_instance = True
        psetting.particle_size = 0.05
        psetting.size_random = 0.4
        psetting.distribution = 'RAND'
        psetting.use_modifier_stack = True
        psetting.use_rotations = True
        psetting.rotation_mode = 'GLOB_Z'
        psetting.rotation_factor_random = 0.025
        psetting.phase_factor = (2/360*at.particle_rotation)-1

        psystem, _ = sys_functions.get_item_psystem(self, context, item)
        psystem.settings = psetting
        psystem.seed = len(context.object.particle_systems)
        item.particle_settings = psetting.name
        #item.selected_tree = "default.png"
        object.select_set(selected)
        #item.psetting_name = "Untitled settings " + str(len(sys_functions.get_settings_enum_items()))

        return {'FINISHED'}


class ALPHATREE_OT_remove_settings(bpy.types.Operator):
    """Remove selected setting for this system"""
    bl_label = "Remove settings"
    bl_idname = "alpha_tree.sys_remove_settings"
    bl_description = "Remove selected setting for this system"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER"}

    def execute(self, context):

        sys_list,_,_,_,item = sys_functions.get_system_vars(self, context)
        psys, _ = sys_functions.get_item_psystem(self, context, item)

        for list_item in sys_list:
            if list_item != item:
                if list_item.particle_settings == item.particle_settings:
                    list_item.particle_settings = "NONE"

        basic_psetting = sys_functions.get_basic_psystem(self,context)

        psetting = psys.settings

        collection = context.scene.collection.children["ALPHA_TREES_PARTICLE_COLLECTION"].children[item.particle_settings]
        
        psys.settings = basic_psetting
        item.particle_settings = "NONE"
        bpy.data.collections.remove(collection)
        bpy.data.particles.remove(psetting)

        return {'FINISHED'}

classes = (
    ALPHATREE_OT_set_up_scene,
    ALPHATREE_OT_execute_all,
    ALPHATREE_OT_open_folder,
    ALPHATREE_OT_render_maps,
    ALPHATREE_OT_set_up_tree,
    ALPHATREE_OT_import_tree,
    ALPHATREE_OT_change_tree,
    ALPHATREE_OT_multi_import,
    ALPHATREE_OT_reload_previews,
    ALPHATREE_OT_sys_list_actions,
    ALPHATREE_OT_new_settings,
    ALPHATREE_OT_remove_settings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
