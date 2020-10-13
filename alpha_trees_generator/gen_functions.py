import bpy
import os
import re
from pathlib import Path

# UI
# ----------------------------------------------------------------------------------------


def draw_info(layout):
    lines = [
        "Before you use this addon make sure that:",
        " 1. Your tree only has 2 materials:",
        "     1 for bark and 1 for leaves",
        " 2. The material names include the words:",
        "     'leaf' or 'leaves' and 'bark' or 'trunk'",
    ]
    for line in lines:
        layout.label(text=line)


def dropdown_operator(layout, context, name, operators, icons, operator_booleans=[], operator_boolean_strings=[], operator_settings=[], setttings_toggle=[]):
    at = bpy.context.scene.alpha_trees
    col = layout.column(align=True)
    box = col.box().column(align=True)
    botaniq_col = box.column()
    row = box.row(align=True)
    row.scale_y = 1.2
    row.scale_x = 1.13
    botaniq_row = botaniq_col.row()
    botaniq_row.alignment = "CENTER"
    botaniq_row.label(text="Operators")
    botaniq_row.prop(at, "show_info", text="", icon="INFO", emboss=False)
    info_col = botaniq_col.column(align=True)
    info_col.scale_y = 0.5
    if at.show_info:
        draw_info(info_col)

    # check for botaniq
    for addon in bpy.context.preferences.addons:
        if addon.module == "botaniq_full":
            botaniq_col.operator("material.biq_spawn_asset",
                                 icon="OUTLINER_DATA_VOLUME", text="Plant tree")

    for operator in operators:

        box.scale_y = 1.4
        current_index = operators.index(operator)
        col = box.column(align=True)
        row = col.row(align=True)
        row.scale_x = 1.2
        row.operator(operator, icon=icons[current_index])
        if operator_booleans[current_index] and operator_settings[current_index] != []:
            row.prop(
                at, operator_boolean_strings[current_index], text="", icon='PREFERENCES')
            setting_list = operator_settings[current_index]
            settting_toggle = setttings_toggle[current_index]
            boxcol = col.box().column(align=True)

            if operator == "alpha_tree.render_maps":
                scene = context.scene
                cscene = scene.cycles
                row = boxcol.row(align=True)
                row.scale_y = 0.8
                row.prop(cscene, "samples", text="samples (50 max.)")

            for setting_index in range(len(setting_list)):
                row = boxcol.row(align=True)
                row.scale_y = 0.8
                if settting_toggle:
                    row.prop(at, setting_list[setting_index],
                             toggle=settting_toggle[setting_index])
                else:
                    row.prop(at, setting_list[setting_index],)

        elif operator_settings[current_index] != []:
            row.prop(
                at, operator_boolean_strings[current_index], text="", icon='PREFERENCES')


def operator_settings(layout, context, bool, bool_string, operator, settings, settings_toggle, icon, scale):
    at = bpy.context.scene.alpha_trees
    col = layout.column(align=True)
    row = col.row(align=True)
    row.scale_x = 1.33
    row.scale_y = scale
    row.operator(operator, icon=icon)
    row.prop(at, bool_string, text="", icon="PREFERENCES")

    if bool:
        box = col.box()
        index = 0
        for setting in settings:
            if type(setting) == list:
                box = col.box()
                row = box.row()
                boxcol = box.column(align=True)
                row.scale_y = 0.9
                row.alignment = "CENTER"
                row.label(text=setting[0])

                if setting[0] == "Rendering":
                    scene = context.scene
                    cscene = scene.cycles
                    boxcol.prop(cscene, "samples", text="samples (50 max.)")
            else:
                boxcol.prop(at, setting, toggle=settings_toggle[index])
            index += 1

# UTILS
# ----------------------------------------------------------------------------


def rename_output(path, format=".png"):
    # vars
    frame = str(bpy.context.scene.frame_current)
    zero_length = 4 - len(frame)

    full_frame = ""
    for i in range(zero_length):
        full_frame += "0"
    full_frame += str(frame)

    if path.endswith(format):
        path = path[: - len(format)]

    if os.path.isfile(path + format):
        os.remove(path + format)

    os.rename(path + full_frame + format,
              path + format)


def check_botaniq_ob(object_name):
    name_up = object_name.upper()
    letters = ["_A_", "_B_", "_C_", "_D_", "_E_", "_F_"]
    seasons = ["SPRING", "SUMMER", "AUTUMN", "WINTER"]
    if "TREE_" in name_up and any(x in name_up for x in letters) and any(x in name_up for x in seasons):
        try:
            tree_name = object_name.split("_")
            name = tree_name[1]
            return True
        except IndexError:
            return False
    else:
        return False


def make_tree_editable():
    object = bpy.context.active_object
    if object.type == "EMPTY":
        empty_name = object.name
        bpy.ops.material.biq_make_selection_editable()
        bpy.ops.object.make_local(type='ALL')

        # remove empty
        name_regex = re.compile(r".\d\d\d")
        mo = name_regex.search(empty_name)
        if mo:
            if mo.group():
                for object in bpy.context.scene.objects:
                    if empty_name[:-3] in object.name:
                        tree = object
                        break
        else:
            tree = bpy.data.objects[empty_name + ".001"]
        tree.name = empty_name
        tree.select_set(True)
        bpy.context.view_layer.objects.active = tree
    else:
        tree = object

    return(tree)


def set_render_border(context):
    object = context.active_object
    at = context.scene.alpha_trees
    context.scene.render.use_border = True
    object = make_tree_editable()

    size_x = object.dimensions[0]
    size_y = object.dimensions[2]

    context.scene.render.border_min_x = 0.5-size_x/20-at.border_padding
    context.scene.render.border_min_y = 0
    context.scene.render.border_max_x = 0.5+size_x/20+at.border_padding
    context.scene.render.border_max_y = size_y/10 + at.border_padding/2


def get_materials():
    object = bpy.context.active_object
    index = 0

    if len(object.material_slots) < 2:
        print("Not enough materials!")
        return None, None

    bark_material, leaf_material = None, None
    for slot in object.material_slots:
        if "BARK" in slot.material.name.upper() or "TRUNK" in slot.material.name.upper():
            bark_material = [slot.material, index]
        if "LEAF" in slot.material.name.upper() or "LEAV" in slot.material.name.upper():
            leaf_material = [slot.material, index]
        index += 1
    index = 0

    # both not found
    if not bark_material and not leaf_material:
        for slot in object.material_slots:
            for node in slot.material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    if node.image:
                        if "BARK" or "TRUNK" in node.image.name.upper():
                            bark_material = [slot.material, index]
                        elif "LEAF" or "LEAV" in node.image.name.upper():
                            leaf_material = [slot.material, index]
                        elif bark_material and bark_material:
                            break
            index += 1
        # blind attempt
        else:
            bark_material = [object.material_slots[0], 0]
            leaf_material = [object.material_slots[1], 1]

    # one not found
    elif not bark_material:
        for slot in object.material_slots:
            for node in slot.material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    if node.image:
                        if "BARK" or "TRUNK" in node.image.name.upper():
                            bark_material = [slot.material, index]
                        elif bark_material:
                            break
            index += 1
        else:
            bark_material = [object.material_slots[0], 0]

    elif not leaf_material:
        for slot in object.material_slots:
            for node in slot.material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    if "LEAF" or "LEAV" in node.image.name.upper():
                        leaf_material = [slot.material, index]
                    elif leaf_material:
                        break
            index += 1
        else:

            leaf_material = [object.material_slots[1], 1]

    return bark_material, leaf_material


def get_tree_maps(context, material):
    script_path = os.path.dirname(os.path.abspath(__file__))
    found = [False, False]
    use_opacity_map = False
    #check node images
    for node in material.node_tree.nodes:
        if found[0] and use_opacity_map == True:
            break
        if node.type == "TEX_IMAGE":
            if node.image:
                image = node.image
                image_up = image.name.upper()

                if "NOR" in image_up and "TNORMAL" not in image_up:
                    normal_image = image
                    found[0] = True
                elif "DIFF" in image_up and not use_opacity_map:
                    diffuse_image = image
                    found[1] = True
                elif "OPAC" in image_up:
                    diffuse_image = image
                    found[1] = True
                    use_opacity_map = True

    #check likely nodes
    if not found[0] and not found[0]:
        for node in material.node_tree.nodes:
            if found[0] and use_opacity_map == True:
                break
            if node.type == 'BSDF_PRINCIPLED':
                #opacity
                if node.inputs[18].links:
                    from_node = node.inputs[18].links[0].from_node
                    if from_node.type == "TEX_IMAGE":
                        if from_node.image:
                            if node.inputs[18].links[0].from_socket.name == "Color":
                                diffuse_image = from_node.image
                                found[1] = True
                                use_opacity_map = True
                #diffuse
                if node.inputs[0].links and not use_opacity_map:
                    from_node = node.inputs[0].links[0].from_node
                    if from_node.type == "TEX_IMAGE":
                        if from_node.image:
                            diffuse_image = from_node.image
                            found[1] = True
            
            elif node.type == 'BSDF_DIFFUSE' and not use_opacity_map:
                #diffuse
                if node.inputs[0].links:
                    from_node = node.inputs[0].links[0].from_node
                    if from_node.type == "TEX_IMAGE":
                        if from_node.image:
                            diffuse_image = from_node.image
                            found[1] = True
            
            elif node.type == 'NORMAL_MAP':
                #normal
                if node.inputs[1].links:
                    from_node = node.inputs[1].links[0].from_node
                    if from_node.type == "TEX_IMAGE":
                        if from_node.image:
                            normal_image = from_node.image
                            found[0] = True
            
            elif node.type == 'MIX_SHADER':
                for input in node.inputs:
                    if input.links:
                        if input.links[0].from_node.type == 'BSDF_TRANSPARENT':
                            if node.inputs[0].links:
                                from_node = node.inputs[0].links[0].from_node
                                if from_node.type == "TEX_IMAGE":
                                    #opacity
                                    if node.inputs[0].links[0].from_socket.name == "Color":
                                        if from_node.image:
                                            diffuse_image = from_node.image
                                            found[1] = True
                                            use_opacity_map = True
                                    #diffuse
                                    elif node.inputs[0].links[0].from_socket.name == "Alpha" and not use_opacity_map:
                                        if from_node.image:
                                            diffuse_image = from_node.image
                                            found[1] = True


    if not found[0] or not found[1]:
        normal_image = bpy.data.images.load(
            os.path.join(script_path, "TNormal.png"), check_existing=True)
    if not found[1]:
        diffuse_image = bpy.data.images.load(
            os.path.join(script_path, "alpha_trees_diffuse.png"), check_existing=True)
    
    return normal_image,diffuse_image,use_opacity_map


def separate_materials(self,context):
    # separate object
    object = context.active_object
    bark_material, leaf_material = get_materials()
    if not bark_material:
        self.report({"ERROR"}, "Could not find bark material")
        bpy.data.scenes.remove(bpy.data.scenes["alpha_trees_scene"])
        bpy.ops.object.mode_set(mode="OBJECT")
        return None,None
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    object.active_material_index = leaf_material[1]
    bpy.ops.object.material_slot_select()
    try:
        bpy.ops.mesh.separate(type='SELECTED')
    except RuntimeError as er:
        if "NOTHING SELECTED" in str(er).upper():
            self.report({"ERROR"}, "Material is not applied to any geometry, cant split mesh")
        else:
            self.report({"ERROR"}, "Could not split mesh, please check that your materials are set up properly")
        bpy.data.scenes.remove(bpy.data.scenes["alpha_trees_scene"])
        bpy.ops.object.mode_set(mode="OBJECT")
        return None,None
    bpy.ops.object.mode_set(mode="OBJECT")
    bark_object = object
    for obj in context.selected_objects:
        if obj != bark_object:
            leaf_object = obj
    return bark_object, leaf_object


def unlink_file_output_nodes(node_tree):
    bpy.context.scene.use_nodes = True
    for node in node_tree.nodes:
        if node.type == "OUTPUT_FILE":
            for input in node.inputs:
                if input.links:
                    node_tree.links.remove(input.links[0])


def unlink_output_node(compositor=True, material=None):
    # unlink composite node
    output_link = None
    composite_link = None
    if compositor:
        node_tree = bpy.context.scene.node_tree
        for node in node_tree.nodes:
            if node.type == "COMPOSITE":
                if node.inputs[0].links:
                    output = node.inputs[0].links[0]
                    output_link = output.from_socket
                    composite_link = output.to_socket
                    node_tree.links.remove(output)
    else:
        mat_output_node = material.node_tree.nodes.new(
            "ShaderNodeOutputMaterial")
        for node in material.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                node.is_active_output = False
        mat_output_node.is_active_output = True

    if compositor:
        return output_link, composite_link
    else:
        return mat_output_node


def fast_render():
    render = bpy.context.scene.render
    x_res = render.resolution_x
    y_res = render.resolution_y
    orig_settings = [x_res, y_res, render.engine]
    render.resolution_x = 4
    render.resolution_y = 4
    render.engine = "BLENDER_WORKBENCH"

    bpy.ops.render.render(use_viewport=True)

    render.resolution_x = orig_settings[0]
    render.resolution_y = orig_settings[1]
    render.engine = orig_settings[2]


def get_settings():
    render = bpy.context.scene.render
    view_settings = bpy.context.scene.view_settings
    display = bpy.context.scene.display
    shading = display.shading
    settings = [
        bpy.context.scene.use_nodes,

        # render settings
        render.engine,
        render.filepath,
        render.film_transparent,
        render.resolution_percentage,
        render.resolution_x,
        render.resolution_y,
        render.use_border,
        render.use_crop_to_border,
        render.use_file_extension,
        render.use_overwrite,
        render.use_stamp,
        render.pixel_aspect_x,
        render.pixel_aspect_y,
        render.use_single_layer,
        render.use_compositing,
        render.use_sequencer,
        render.image_settings.file_format,
        render.image_settings.quality,

        # color management settings
        view_settings.exposure,
        view_settings.gamma,
        view_settings.look,
        view_settings.use_curve_mapping,
        view_settings.view_transform,
        bpy.context.scene.display_settings.display_device,
        bpy.context.scene.sequencer_colorspace_settings.name,

        # workbench settings
        display.render_aa,
        shading.show_cavity,
        shading.show_backface_culling,
        shading.show_object_outline,
        shading.show_shadows,
        shading.show_specular_highlight,
        shading.show_xray,
        shading.use_dof,
        shading.light,
        shading.studio_light,
        shading.color_type,

    ]
    return settings


def set_active_nodes(bark_material, leaf_material):
    for node in leaf_material.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            if node.image:
                if "TNORMAL" in node.image.name.upper():
                    leaf_material.node_tree.nodes.active = node
                    break
    for node in bark_material.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            if node.image:
                if "NOR" in node.image.name.upper():
                    node.image.colorspace_settings.name = "Non-Color"
                    bark_material.node_tree.nodes.active = node
                    break
    else:
        script_path = os.path.dirname(os.path.abspath(__file__))
        nor_image = bpy.data.images.load(
            os.path.join(script_path, "TNormal.png"), check_existing=True)
        nor_image.colorspace_settings.name = "Non-Color"

        # check if already exists
        for node in bark_material.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                if node.image:
                    if node.image.name == "TNormal.png":
                        nor_node = node
                        break
        else:
            nor_node = bark_material.node_tree.nodes.new("ShaderNodeTexImage")

        nor_node.image = nor_image
        nor_image.pixels = (0.5, 0.5, 1, 1)
        bark_material.node_tree.nodes.active = nor_node


def set_general_settings():
    render = bpy.context.scene.render
    view_settings = bpy.context.scene.view_settings
    display = bpy.context.scene.display
    shading = display.shading
    at = bpy.context.scene.alpha_trees

    bpy.context.scene.use_nodes = True

    # render settings
    render.film_transparent = True
    render.resolution_percentage = 100
    render.resolution_x = at.resolution
    render.resolution_y = at.resolution
    render.use_border = True
    render.use_crop_to_border = True
    render.use_file_extension = True
    render.use_overwrite = at.overwrite
    render.use_stamp = False
    render.pixel_aspect_x = 1
    render.pixel_aspect_y = 1
    render.use_single_layer = True
    render.use_compositing = True
    render.use_sequencer = False
    render.image_settings.file_format = "JPEG"
    render.image_settings.quality = 85

    # color management settings
    view_settings.exposure = 0
    view_settings.gamma = 1
    view_settings.look = "None"
    view_settings.use_curve_mapping = False
    view_settings.view_transform = "Standard"
    bpy.context.scene.display_settings.display_device = "sRGB"
    bpy.context.scene.sequencer_colorspace_settings.name = "Filmic Log"

    # workbench settings
    display.render_aa = "32"
    shading.show_cavity = False
    shading.show_backface_culling = False
    shading.show_object_outline = False
    shading.show_shadows = False
    shading.show_specular_highlight = False
    shading.show_xray = False
    shading.use_dof = False


def reset_settings(settings):
    render = bpy.context.scene.render
    view_settings = bpy.context.scene.view_settings
    display = bpy.context.scene.display
    shading = display.shading
    i = 0

    bpy.context.scene.use_nodes = settings[i]
    i += 1

    # render settings
    render.engine = settings[i]
    i += 1
    render.filepath = settings[i]
    i += 1
    render.film_transparent = settings[i]
    i += 1
    render.resolution_percentage = settings[i]
    i += 1
    render.resolution_x = settings[i]
    i += 1
    render.resolution_y = settings[i]
    i += 1
    render.use_border = settings[i]
    i += 1
    render.use_crop_to_border = settings[i]
    i += 1
    render.use_file_extension = settings[i]
    i += 1
    render.use_overwrite = settings[i]
    i += 1
    render.use_stamp = settings[i]
    i += 1
    render.pixel_aspect_x = settings[i]
    i += 1
    render.pixel_aspect_y = settings[i]
    i += 1
    render.use_single_layer = settings[i]
    i += 1
    render.use_compositing = settings[i]
    i += 1
    render.use_sequencer = settings[i]
    i += 1
    render.image_settings.file_format = settings[i]
    i += 1
    render.image_settings.quality = settings[i]
    i += 1

    # color management settings
    view_settings.exposure = settings[i]
    i += 1
    view_settings.gamma = settings[i]
    i += 1
    view_settings.look = settings[i]
    i += 1
    view_settings.use_curve_mapping = settings[i]
    i += 1
    view_settings.view_transform = settings[i]
    i += 1
    bpy.context.scene.display_settings.display_device = settings[i]
    i += 1
    bpy.context.scene.sequencer_colorspace_settings.name = settings[i]
    i += 1

    # workbench settings
    display.render_aa = settings[i]
    i += 1
    shading.show_cavity = settings[i]
    i += 1
    shading.show_backface_culling = settings[i]
    i += 1
    shading.show_object_outline = settings[i]
    i += 1
    shading.show_shadows = settings[i]
    i += 1
    shading.show_specular_highlight = settings[i]
    i += 1
    shading.show_xray = settings[i]
    i += 1
    shading.use_dof = settings[i]
    i += 1
    shading.light = settings[i]
    i += 1
    shading.studio_light = settings[i]
    i += 1
    shading.color_type = settings[i]
    i += 1


def load_image(file_name, img_path, name, format=".jpg"):
    # load
    for image in bpy.data.images:
        if image.name == name + file_name + format:
            bpy.data.images.remove(image)
    image = bpy.data.images.load(img_path + file_name + format)
    return image


def load_nor_image(file_name, img_path, format=".jpg"):
    # load
    for image in bpy.data.images:
        if image.name == file_name + format:
            bpy.data.images.remove(image)
    image = bpy.data.images.load(img_path + file_name + format)
    return image

# OPERATORS
# ----------------------------------------------------------------------------------------

def setup_scene(self, context):
    objects = context.selected_objects

    for scene in bpy.data.scenes:
        if scene.name == "alpha_trees_scene":
            context.window.scene = scene
            scene = context.scene
            break
    else:
        bpy.ops.scene.new(type='EMPTY')
        scene = context.scene
        scene.name = "alpha_trees_scene"

    at = scene.alpha_trees
    script_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_path, "base_scene.blend")

    already_created = [] 
    with bpy.data.libraries.load(file_path) as (data_from, data_to):
        for object in data_from.objects:
            data_to.objects.append(object)
        for object in data_from.objects:
            for data_object in bpy.data.objects:
                if object == data_object.name:
                    data_to.objects.remove(object)
                    already_created.append(data_object)


        for world in bpy.data.worlds:
            if world.name == "alpha_trees_world":
                bpy.context.scene.world = world
                break
        else:
            data_to.worlds.append("alpha_trees_world")

    try:
        collection = bpy.context.scene.collection.children["alpha_generator_objects"]
    except KeyError:
        collection = bpy.data.collections.new("alpha_generator_objects")
        bpy.context.scene.collection.children.link(collection)

    for object in already_created:
        try:
            collection.objects.link(object)
        except RuntimeError:
            continue

    for object in data_to.objects:
        collection.objects.link(object)

    if data_to.worlds:
        bpy.context.scene.world = data_to.worlds[0]

    for object in context.scene.objects:
        if object.type == "CAMERA":
            context.scene.camera = object
            break
    else:
        camera = bpy.data.cameras.new("alpha_trees_camera")
        cam_obj = bpy.data.objects.new("camera_object", camera)
        context.scene.collection.objects.link(cam_obj)
        context.scene.camera = cam_obj
    
    for object in objects:
        try:
            context.scene.collection.objects.link(object)
            context.view_layer.objects.active = object
        except RuntimeError:
            continue

    scene.render.resolution_x = at.resolution
    scene.render.resolution_y = at.resolution


def scale_to_height():
    object = bpy.context.active_object
    at = bpy.context.scene.alpha_trees
    target = 10
    padding = 0.03
    bpy.context.scene.use_nodes = True

    # if linked
    object = make_tree_editable()

    # check if needed
    if round(object.dimensions[2]) == round(target - padding):
        return

    dimensions = object.dimensions
    if dimensions[0] > dimensions[2]:
        z_scale = target/dimensions[0] - padding
    else:
        z_scale = target/dimensions[2] - padding

    object.scale = [z_scale*object.scale[0], z_scale *
                    object.scale[1], z_scale*object.scale[2]]


def transparent_normal(self,context):
    if bpy.context.active_object == None:
        return {'CANCELLED'}
    
    cam_obj = None
    for object in context.scene.objects:
        if object.type == "CAMERA":
            context.scene.camera = object
            break
    else:
        camera = bpy.data.cameras.new("alpha_trees_camera")
        cam_obj = bpy.data.objects.new("camera_object", camera)
        context.scene.collection.objects.link(cam_obj)
        context.scene.camera = cam_obj

    at = bpy.context.scene.alpha_trees
    object = bpy.context.active_object
    node_tree = bpy.context.scene.node_tree
    script_path = os.path.dirname(os.path.abspath(__file__))
    path = bpy.path.abspath(os.path.join(script_path,"maps","leaf_maps",""))
    bark_material, leaf_material = get_materials()
    bpy.context.scene.use_nodes = True
    unlink_file_output_nodes(node_tree)

    make_tree_editable()

    object.active_material_index = leaf_material[1]

    # names
    object_name = object.name
    # check if botaniq tree
    if check_botaniq_ob(object_name):
        tree_name = object_name.split("_")
        name = tree_name[1]
    else:
        name = object_name

    normal_img_path = path + "Leaf_" + name + "_TNormal.png"

    normal_image,diffuse_image,use_opacity_map = get_tree_maps(context,leaf_material[0])

    # make nodes
    bpy.context.scene.use_nodes = True
    diff_map = node_tree.nodes.new('CompositorNodeImage')
    nor_map = node_tree.nodes.new('CompositorNodeImage')
    translate_node = node_tree.nodes.new('CompositorNodeTranslate')
    normal_mix_node = node_tree.nodes.new('CompositorNodeMixRGB')
    set_alpha_node = node_tree.nodes.new('CompositorNodeSetAlpha')
    output_node = node_tree.nodes.new('CompositorNodeOutputFile')

    # node settings
    nor_map.image = normal_image
    diff_map.image = diffuse_image
    # translate node to tile image if normal map not provided
    translate_node.wrap_axis = "BOTH"
    normal_mix_node.inputs[0].default_value = 1

    output_node.base_path = path
    output_node.format.file_format = "PNG"
    output_node.format.color_mode = "RGBA"
    output_node.file_slots.clear()
    output_node.file_slots.new("Leaf_" + name + "_TNormal")

    # links
    node_tree.links.new(nor_map.outputs[0], translate_node.inputs[0])
    node_tree.links.new(translate_node.outputs[0], normal_mix_node.inputs[2])
    node_tree.links.new(diff_map.outputs[0], normal_mix_node.inputs[1])
    node_tree.links.new(diff_map.outputs[1], normal_mix_node.inputs[0])
    node_tree.links.new(normal_mix_node.outputs[0], set_alpha_node.inputs[0])
    print(use_opacity_map)
    print(diffuse_image)
    if use_opacity_map:
        output_index = 0
    else:
        output_index = 1
    node_tree.links.new(diff_map.outputs[output_index], set_alpha_node.inputs[1])
    node_tree.links.new(set_alpha_node.outputs[0], output_node.inputs[0])

    # rendering
    fast_render()

    # remove nodes
    nodes = [diff_map, nor_map, normal_mix_node,
             output_node, translate_node, set_alpha_node, ]
    for node in nodes:
        node_tree.nodes.remove(node)

    rename_output(normal_img_path)

    # shader nodes
    shader_node_tree = object.active_material.node_tree

    nodes_exist = {
        "nor": False,
        "output": False
    }

    # get/make shader nodes
    for node in shader_node_tree.nodes:
        if node.type == "OUTPUT_MATERIAL":
            nodes_exist["output"] = True
            mat_output_node = node
        elif node.type == "TEX_IMAGE":
            if node.image:
                if "Leaf_" + name + "_TNormal" in node.image.name:
                    nodes_exist["nor"] = True
                    nor_img_node = node
        elif nodes_exist["nor"] and nodes_exist["output"]:
            break

    final_normal_image = load_nor_image(
        "Leaf_" + name + "_TNormal", path, ".png")
    final_normal_image.colorspace_settings.name = "Non-Color"

    if nodes_exist["output"]:
        location = mat_output_node.location
    else:
        location = (0, 0)

    if not nodes_exist["nor"]:
        nor_img_node = shader_node_tree.nodes.new("ShaderNodeTexImage")

    # locations
    nor_img_node.location = location
    nor_img_node.location[1] -= 150
    shader_node_tree.nodes.active = nor_img_node

    nor_img_node.image = final_normal_image
    object.data.uv_layers.active_index = 0

    if cam_obj:
        bpy.data.objects.remove(cam_obj)


def render_maps(self, context):

    if len(context.selected_objects) == 2:
        bpy.ops.object.join()

    scene = context.scene
    setup_scene(self, context)

    for object in context.scene.objects:
        if object.type == "CAMERA":
            bpy.context.scene.camera = object
    
    set_render_border(context)

    settings = get_settings()
    at = bpy.context.scene.alpha_trees
    path = bpy.path.abspath(at.render_filepath)
    object = bpy.context.active_object
    ob_name = object.name

    #scaling
    scale = str(round(1 / object.scale[0], 2))
    while len(scale) < 4:
        scale+= "0"

    if check_botaniq_ob(ob_name):
        ob_name = object.name.split("_")
        name = ob_name[1] + "_" + ob_name[2] + "_" + \
            scale + "_"
            
    else:
        name = ob_name + "_" + scale + "_"

    img_path = path + name

    comp_nodes = []

    set_general_settings()
    bark_object, leaf_object = separate_materials(self, context)
    if not bark_object:
        return
    bark_material, leaf_material = get_materials()
    set_active_nodes(bark_material[0], leaf_material[0])

    node_tree = bpy.context.scene.node_tree
    unlink_file_output_nodes(node_tree)

    for node in node_tree.nodes:
        if node.type == "R_LAYERS":
            r_layers = node
            break
    else:
        r_layers = node_tree.nodes.new("CompositorNodeRLayers")

    output_link, composite_link = unlink_output_node()

    # file output
    output_node = node_tree.nodes.new("CompositorNodeOutputFile")
    comp_nodes.append(output_node)
    output_node.base_path = path
    output_node.format.file_format = "JPEG"
    output_node.format.quality = 100
    output_node.format.color_mode = "RGB"
    output_node.file_slots.clear()

    output_node.file_slots.new(name + "nor_leaf")  # 0
    output_node.file_slots.new(name + "nor_trunk")  # 1
    output_node.file_slots.new(name + "diff_leaf")  # 2
    output_node.file_slots.new(name + "diff_trunk")  # 3
    output_node.file_slots.new(name + "mask_leaf")  # 4
    output_node.file_slots.new(name + "mask_trunk")  # 5
    output_node.file_slots.new(name + "mask_shadow")  # 6
    output_node.file_slots.new(name + "mask")  # 7

    output_node.file_slots[7].use_node_format = False
    output_node.file_slots[7].format.file_format = "PNG"
    output_node.file_slots[7].format.compression = 100
    output_node.file_slots[7].format.color_depth = "8"
    output_node.file_slots[7].format.color_mode = "RGB"

    nor_leaf_exists = os.path.isfile(img_path + "nor_leaf.jpg")
    nor_trunk_exists = os.path.isfile(img_path + "nor_trunk.jpg")
    leaf_exists = os.path.isfile(img_path + "diff_leaf.jpg")
    trunk_exists = os.path.isfile(img_path + "diff_trunk.jpg")
    mask_exists = os.path.isfile(img_path + "mask.jpg")

    diff_trunk_img = None
    mask_leaf_img = None

    denoise_node = node_tree.nodes.new("CompositorNodeDenoise")
    comp_nodes.append(denoise_node)

    # N O R M A L
    if at.nor_render:
        if not nor_leaf_exists and not nor_trunk_exists or at.overwrite:
            print("RENDERING NORMAL")

            # set active nodes

            leaf_link = node_tree.links.new(
                r_layers.outputs["Image"], output_node.inputs[0])

            # nor settings
            render = bpy.context.scene.render
            shading = bpy.context.scene.display.shading
            render.engine = "BLENDER_WORKBENCH"
            render.filepath = img_path + "nor"
            shading.light = "MATCAP"
            shading.studio_light = "check_normal+y.exr"
            shading.color_type = "TEXTURE"

            bark_object.hide_render = True
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            bpy.ops.render.render()

            bark_object.hide_render = False
            leaf_object.hide_render = True
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            node_tree.links.remove(leaf_link)
            leaf_link = node_tree.links.new(
                r_layers.outputs["Image"], output_node.inputs[1])
            if at.mask_render:
                alpha_link = node_tree.links.new(
                    r_layers.outputs["Alpha"], output_node.inputs[5])

            bpy.ops.render.render()

            node_tree.links.remove(leaf_link)

            leaf_object.hide_render = False
            rename_output(img_path + "nor_leaf", format=".jpg")
            rename_output(img_path + "nor_trunk", format=".jpg")
            if at.mask_render:
                rename_output(img_path + "mask_trunk", format=".jpg")

            # load
            if at.mask_render:
                node_tree.links.remove(alpha_link)
                mask_trunk_img = load_image("mask_trunk", img_path, name)

        else:
            self.report({"WARNING"}, "Normal images already created")

    # D I F F U S E
    if at.diff_render:
        if not leaf_exists and not trunk_exists or at.overwrite:
            print("")
            print("RENDERING DIFFUSE:")
            print("Leaves...")
            print("")
            render = bpy.context.scene.render
            render.engine = "CYCLES"

            # denoise node
            bpy.context.view_layer.cycles.denoising_store_passes = True
            if at.mask_render:
                alpha_link = node_tree.links.new(
                    r_layers.outputs["Alpha"], output_node.inputs[4])
            node_tree.links.new(
                r_layers.outputs["Image"], denoise_node.inputs[0])
            node_tree.links.new(
                r_layers.outputs["Denoising Normal"], denoise_node.inputs[1])
            node_tree.links.new(
                r_layers.outputs["Denoising Albedo"], denoise_node.inputs[2])
            leaf_link = node_tree.links.new(
                denoise_node.outputs[0], output_node.inputs[2])

            # holdout bark
            mat_output_node = unlink_output_node(
                compositor=False, material=bark_material[0])
            holdout_node = bark_material[0].node_tree.nodes.new(
                "ShaderNodeHoldout")
            bark_material[0].node_tree.links.new(
                holdout_node.outputs[0], mat_output_node.inputs[0])
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            bpy.ops.render.render()

            # trunk
            print("")
            print("Trunk...")
            print("")
            node_tree.links.remove(leaf_link)
            node_tree.links.remove(alpha_link)

            trunk_link = node_tree.links.new(
                denoise_node.outputs[0], output_node.inputs[3])
            bark_material[0].node_tree.nodes.remove(mat_output_node)
            bark_material[0].node_tree.nodes.remove(holdout_node)
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            leaf_object.hide_render = True

            bpy.ops.render.render()

            leaf_object.hide_render = False
            node_tree.links.remove(trunk_link)

            rename_output(img_path + "diff_leaf", format=".jpg")
            rename_output(img_path + "diff_trunk", format=".jpg")
            rename_output(img_path + "mask_leaf", format=".jpg")

            if at.mask_render:
                mask_leaf_img = load_image("mask_leaf", img_path, name)
                diff_trunk_img = load_image("diff_trunk", img_path, name)
        else:
            self.report({"WARNING"}, "Diffuse images already created")

    # M A S K
    if at.mask_render:
        if not mask_exists or at.overwrite:
            print("")
            print("RENDERING MASKS:")
            mask_leaf_exists = os.path.isfile(img_path + "mask_leaf.jpg")
            mask_trunk_exists = os.path.isfile(img_path + "mask_trunk.jpg")
            mask_shadow_exists = os.path.isfile(img_path + "mask_shadow.jpg")
            render = bpy.context.scene.render

            # leaves
            if not mask_leaf_exists:
                print("Leaf mask...")
                print("")
                render.engine = "BLENDER_EEVEE"

                # holdout bark
                mat_output_node = unlink_output_node(
                    compositor=False, material=bark_material[0])
                holdout_node = bark_material[0].node_tree.nodes.new(
                    "ShaderNodeHoldout")
                bark_material[0].node_tree.links.new(
                    holdout_node.outputs[0], mat_output_node.inputs[0])
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

                alpha_link = node_tree.links.new(
                    r_layers.outputs["Alpha"], output_node.inputs[4])

                bpy.ops.render.render()

                for node in [mat_output_node, holdout_node]:
                    bark_material[0].node_tree.nodes.remove(node)
                node_tree.links.remove(alpha_link)
                rename_output(img_path + "mask_leaf", format=".jpg")

            # trunk mask
            if not mask_trunk_exists:
                print("Trunk mask...")
                print("")
                render.engine = "BLENDER_EEVEE"
                leaf_object.hide_render = True
                alpha_link = node_tree.links.new(
                    r_layers.outputs["Alpha"], output_node.inputs[5])

                bpy.ops.render.render()

                rename_output(img_path + "mask_trunk", format=".jpg")
                node_tree.links.remove(alpha_link)
                mask_trunk_exists = True

            # shadow
            if not mask_shadow_exists or at.overwrite:
                print("Shadow mask...")
                print("")
                render.engine = "CYCLES"
                collection = bpy.data.collections.new("leafcol")
                bpy.context.scene.collection.children.link(collection)
                collection.objects.link(leaf_object)
                layer_collection = bpy.context.view_layer.layer_collection.children[
                    collection.name]
                layer_collection.indirect_only = True

                node_tree.links.new(
                    r_layers.outputs["Image"], denoise_node.inputs[0])
                node_tree.links.new(
                    r_layers.outputs["Denoising Normal"], denoise_node.inputs[1])
                node_tree.links.new(
                    r_layers.outputs["Denoising Albedo"], denoise_node.inputs[2])
                node_tree.links.new(
                    denoise_node.outputs[0], output_node.inputs[6])

                bpy.ops.render.render()

                bpy.data.collections.remove(collection)
                rename_output(img_path + "mask_shadow", format=".jpg")
            mask_shadow_img = load_image("mask_shadow", img_path, name)

            if not mask_trunk_exists:
                rename_output(img_path + "mask_trunk", format=".jpg")
            mask_trunk_img = load_image("mask_trunk", img_path, name)

            # load masks
            if not mask_leaf_img:
                mask_leaf_img = load_image("mask_leaf", img_path, name)
            elif not diff_trunk_img:
                diff_trunk_img = load_image("diff_trunk", img_path, name)

            # combine masks
            print("Compositing final mask...")
            print("")
            # unlink all outputs
            for input in output_node.inputs:
                if input.links:
                    node_tree.links.remove(input.links[0])

            # make nodes
            diff_trunk_node = node_tree.nodes.new("CompositorNodeImage")
            mask_leaf_node = node_tree.nodes.new("CompositorNodeImage")
            mask_trunk_node = node_tree.nodes.new("CompositorNodeImage")
            mask_shadow_node = node_tree.nodes.new("CompositorNodeImage")
            bw_node = node_tree.nodes.new("CompositorNodeRGBToBW")
            multiply_node = node_tree.nodes.new("CompositorNodeMixRGB")
            combine_node = node_tree.nodes.new("CompositorNodeCombRGBA")

            # settings
            diff_trunk_node.image = diff_trunk_img
            mask_leaf_node.image = mask_leaf_img
            mask_trunk_node.image = mask_trunk_img
            mask_shadow_node.image = mask_shadow_img
            multiply_node.blend_type = "MULTIPLY"

            # links
            links = node_tree.links

            links.new(mask_shadow_node.outputs[0], bw_node.inputs[0])
            links.new(diff_trunk_node.outputs[0], multiply_node.inputs[1])
            links.new(bw_node.outputs[0], multiply_node.inputs[2])
            links.new(mask_trunk_node.outputs[0], combine_node.inputs[0])
            links.new(mask_leaf_node.outputs[0], combine_node.inputs[1])
            links.new(multiply_node.outputs[0], combine_node.inputs[2])
            links.new(combine_node.outputs[0], output_node.inputs[7])

            fast_render()

            # cleanup
            rename_output(img_path + "mask", format=".png")

            if at.remove_extra_masks:
                for image in ["mask_leaf", "mask_trunk", "mask_shadow"]:
                    os.remove(img_path + image + ".jpg")

            for node in [diff_trunk_node, mask_leaf_node, mask_trunk_node, mask_shadow_node, bw_node, multiply_node, combine_node, ]:
                comp_nodes.append(node)

        else:
            self.report({"WARNING"}, "Mask image already created")

    # remove nodes
    for node in comp_nodes:
        node_tree.nodes.remove(node)

    # relink composite node
    if output_link:
        node_tree.links.new(output_link, composite_link)

    # rejoin objects
    bpy.ops.object.select_all(action='DESELECT')
    bark_object.select_set(True)
    leaf_object.select_set(True)
    bpy.ops.object.join()

    reset_settings(settings)
    bpy.ops.object.delete()
    bpy.data.scenes.remove(bpy.data.scenes["alpha_trees_scene"])
    context.window.scene = scene





# Utils
# ------------------------------------------------------------------------------------

# useful for seeing through the mess of errors
def xprint(message, len=10):
    if type(message) == list:
        for item in message:
            for i in range(len):
                print(item)
    else:
        for i in range(len):
            print(message)
