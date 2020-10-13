import bpy
from . import gen_functions, imp_functions, sys_functions, operators, settings
from .operators import (
    ALPHATREE_OT_change_tree,
    ALPHATREE_OT_reload_previews,
    ALPHATREE_OT_multi_import,
    ALPHATREE_OT_sys_list_actions,
    ALPHATREE_OT_new_settings)

class AlphaTreesPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    show_extra_operators: bpy.props.BoolProperty(
        name="Show extra operators",
        default = True,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_extra_operators")

# class PreviewMenu(bpy.types.Menu):
#     bl_idname = "ALPHATREE_MT_preview_options"
#     bl_label = "Previews"

#     def draw(self, context):
#         layout = self.layout

#         layout.operator(ALPHATREE_OT_multi_import.bl_idname, text="Multi import", icon = "DOCUMENTS")

class ALPHATREE_UL_SystemList(bpy.types.UIList):
    """UIlist for the particle systems"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        custom_icon = 'PARTICLES'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align = True)
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)
            
            if item.show_viewport:
                row.prop(item, "show_viewport", text="", emboss=False, icon="RESTRICT_VIEW_OFF")
            else:
                row.prop(item, "show_viewport", text="", emboss=False, icon="RESTRICT_VIEW_ON")
            
            if item.show_render:
                row.prop(item, "show_render", text="", emboss=False, icon="RESTRICT_RENDER_OFF")
            else:
                row.prop(item, "show_render", text="", emboss=False, icon="RESTRICT_RENDER_ON")
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

class ALPHATREE_PT_import_panel(bpy.types.Panel):
    """Import panel"""
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "Alpa trees importer"
    bl_category = "Alpha Trees"

    def draw(self, context):
        layout = self.layout
        at = bpy.context.scene.alpha_trees

        row = layout.row(align=True)
        row.prop(at,"import_type",expand = True,)

        if at.import_type == "PARTICLE":

            if context.object:
                sys_list, sys_settings, index, psystems, item = sys_functions.get_system_vars(self,context)

                row = layout.row(align = True)
                row.template_list("ALPHATREE_UL_SystemList", "The_List", context.object, "sys_list", context.object.sys_settings, "index")
                column = row.column()
                col = column.column(align=True)
                actions_name = ALPHATREE_OT_sys_list_actions.bl_idname
                col.operator(actions_name, text="", icon="ADD").action = "ADD"
                row = col.row(align = True)
                if not sys_list:
                    row.enabled = False
                row.operator(actions_name, text="", icon="REMOVE").action = "REMOVE"
                
                if sys_list:
                    if len(sys_list) >= 2:
                        col = column.column(align=True)
                        col.operator(actions_name, text="", icon="TRIA_UP").action = "UP"
                        col.operator(actions_name, text="", icon="TRIA_DOWN").action = "DOWN"

                    #settings row
                    row = layout.row()
                    row.label(text=item.sys_name)

                    row = layout.row(align=True)
                    if item.particle_settings == "NONE":
                        row.prop(item, "particle_settings", text="", icon="SETTINGS", icon_only=True)
                        row.operator(ALPHATREE_OT_new_settings.bl_idname, text="New settings", icon="ADD")
                        return

                    row.prop(item, "particle_settings", text="", icon="SETTINGS")
                    row.operator(ALPHATREE_OT_new_settings.bl_idname, text="", icon="ADD")
                    row.operator(operators.ALPHATREE_OT_remove_settings.bl_idname, text="", icon="REMOVE")

                    box = layout.box()
                    boxcol = box.column(align=True)
                    boxcol.template_icon_view(item, "selected_tree", scale=6, scale_popup=7, show_labels=True)

                    col = layout.column(align = True)
                    boxcol = col.box().column()
                    row = boxcol.row()

                    #particle settings
                    if at.show_particle_settings:
                        row.prop(at, "show_particle_settings", text = "", icon = "TRIA_DOWN")
                        row.label(text="Settings")

                        psettings = bpy.data.particles[item.particle_settings]
                        psys = psystems[psystems.find(item.sys_name)]

                        boxcol = col.box().column()
                        boxcol.use_property_split = True
                        boxcol.prop(psys, "seed")
                        boxcol.prop(psettings, "count")
                        boxcol.prop(psettings, "particle_size", text="Size")
                        boxcol.prop(psettings, "size_random")
                        boxcol.prop(item, "random_rotation", slider=True)
                        boxcol.prop(psettings, "display_percentage", text="Viewport")
                    else:
                        row.prop(at, "show_particle_settings", text = "", icon = "TRIA_RIGHT")
                        row.label(text="Settings")
                    
                    #materials
                    if item.selected_tree != "default.png":

                        col = layout.column(align = True)
                        boxcol = col.box().column()
                        row = boxcol.row()

                        if at.show_material_settings:
                            row.prop(at, "show_material_settings", text = "", icon = "TRIA_DOWN")
                            row.label(text="Material")
                            boxcol = col.box().column()

                            object = bpy.data.collections[item.particle_settings].objects[item.particle_settings.replace("AT_PSYSTEM_","")]
                            control_node = object.material_slots[0].material.node_tree.nodes["Alpha trees control"]
                            imp_functions.draw_material_settings(context, boxcol, control_node)
                        else:
                            row.prop(at, "show_material_settings", text = "", icon = "TRIA_RIGHT")
                            row.label(text="Material")

        else:
            
            imp_functions.draw_preview_enum(
                self,
                context,
                layout,
                [ALPHATREE_OT_change_tree, ALPHATREE_OT_reload_previews, ALPHATREE_OT_multi_import],
                at,
                "alpha_trees_previews"
                )
            
            #row = layout.row()
            #row.alignment = "CENTER"
            #row.label(text = at.alpha_trees_previews[:-19])

            row = layout.row()
            row.scale_y = 1.8
            row.operator("alpha_tree.import_tree", icon="VOLUME_DATA", text = "Import:  " + at.alpha_trees_previews[:-19])


class ALPHATREE_PT_overall_settings(bpy.types.Panel):
    """Overall settings panel"""
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "Overall settings"
    bl_category = "Alpha Trees"
    bl_parent_id = "ALPHATREE_PT_import_panel"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        at = context.scene.alpha_trees
        return at.import_type == "PARTICLE"
    
    def draw(self, context):
        layout = self.layout
        at = context.scene.alpha_trees

        col = layout.column(align=True)
        col.use_property_split = True
        col.prop(at,"particle_rotation")

class ALPHATREE_PT_material_settings(bpy.types.Panel):
    """Material settings panel"""
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "Material settings"
    bl_category = "Alpha Trees"
    bl_parent_id = "ALPHATREE_PT_import_panel"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        object = context.object

        if context.scene.alpha_trees.import_type == "PARTICLE":
            return False

        if not object:
            return False

        elif not object.material_slots:
            return False
        
        elif not object.material_slots[0].material:
            return False
        
        elif not object.material_slots[0].material.use_nodes:
            return False
        
        elif not object.material_slots[0].material.node_tree.nodes:
            return False

        try:
            _ = object.material_slots[0].material.node_tree.nodes["Alpha trees control"]
        except KeyError:
            return False
        
        return True

    def draw(self, context):
        layout = self.layout
        object = context.active_object
        control_node = object.material_slots[0].material.node_tree.nodes["Alpha trees control"]

        col = layout.column(align = True)
        imp_functions.draw_material_settings(context,col, control_node)


class ALPHATREE_PT_gen_panel(bpy.types.Panel):
    """Generator panel"""
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "Alpa trees generator"
    bl_category = "Alpha Trees"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        at = bpy.context.scene.alpha_trees
        layout = self.layout
        if prefs.show_extra_operators:
            gen_functions.dropdown_operator(
                layout,
                context,
                name="  Alpha Trees",
                operators=["alpha_tree.set_up_tree","alpha_tree.render_maps", "alpha_tree.open_folder", ],
                icons=["SORT_DESC","RESTRICT_RENDER_OFF", "FILEBROWSER", ],
                operator_booleans=[at.show_setup_tree_settings,at.show_render_settings, at.show_open_folder_settings, ],
                operator_boolean_strings=["show_setup_tree_settings", "show_render_settings", "show_open_folder_settings", ],
                operator_settings=[["border_padding"], [
                    "resolution", "render_filepath", "diff_render", "nor_render", "mask_render", "overwrite", "remove_extra_masks", ], ["open_leaf_folder"]],
                setttings_toggle=[[], [False, False,True, True, True, False, False], []]
            )
        
        # else:
        #     row = layout.row()
        #     row.alignment = "RIGHT"
        #     row.prop(at, "show_info", text="", icon="INFO", emboss=False)
        #     col = layout.column()
        #     col.scale_y = 0.8
        #     if at.show_info:
        #         functions.draw_info(col)

        gen_functions.operator_settings(
            layout,
            context,
            bool=at.show_exec_all_settings,
            bool_string="show_exec_all_settings",
            operator="alpha_tree.execute_all",
            settings=[["Render border"], "border_padding", ["Rendering"],
                    "resolution", "render_filepath", "diff_render", "nor_render", "mask_render",  "overwrite", "remove_extra_masks",["Open renders folder"], "open_renders_folder"],
            settings_toggle = [False,False,False,False,False,True,True,True,False,False,False,False,],
            icon="DRIVER",
            scale=1.75)

classes = [
    ALPHATREE_PT_import_panel,
    ALPHATREE_PT_gen_panel,
    ALPHATREE_PT_material_settings,
    ALPHATREE_PT_overall_settings,
    ALPHATREE_UL_SystemList,
    AlphaTreesPrefs,
    #PreviewMenu,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
