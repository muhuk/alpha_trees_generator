import bpy
import os
import bpy.utils.previews


# UI
#--------------------------------------------------------------------------

def draw_material_settings(context, layout, node):
    inputs = [
        socket for socket in node.inputs if socket.enabled and not socket.is_linked]
    for input in inputs:
        col = layout.column(align=True)
        if input.hide_value:
            col = col.row()
            col.alignment = "CENTER"
        input.draw(context, col, node, input.name)


def draw_preview_enum(self, context, layout, operators : list, enum_data, enum_name):
    
    row = layout.row(align=True)
    col = row.column(align=True)
    cc = col.column(align=True)
    scale_y = 5
    cc.scale_y = scale_y
    cc.scale_x = 0.92
    cc.operator(operators[0].bl_idname, text="", icon="TRIA_LEFT").forward = False
    if len(operators) > 1:
        cc = col.column(align=True)
        cc.scale_y = 1
        cc.operator(operators[1].bl_idname, text="", icon="FILE_REFRESH")

    row.template_icon_view(enum_data, enum_name, scale=scale_y+1, scale_popup=7, show_labels=True)

    col = row.column(align=True)
    cc = col.column(align=True)
    cc.scale_y = scale_y
    cc.scale_x = 0.92
    cc.operator(operators[0].bl_idname, text="", icon="TRIA_RIGHT").forward = True
    if len(operators) > 2:
        cc = col.column(align=True)
        cc.scale_y = 1
        cc.operator(operators[2].bl_idname, text="", icon = "DOCUMENTS")


# Functions
#--------------------------------------------------------------------------


def get_previews_from_files(self, context):
    # This is pretty much just straight from the template scipt "Ui Previews Dynamic Enum"
    # so thanks blender devs :)
    """EnumProperty callback"""
    enum_items = []
    at = bpy.context.scene.alpha_trees

    if context is None:
        return enum_items

    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(script_dir, "maps", "rendered_maps", "")

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["alpha_trees_previews"]

    diff_maps = [map for map in os.listdir(directory) if "diff_leaf" in map]

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


def get_diff_maps():
    script_path = os.path.dirname(os.path.abspath(__file__))
    str_dir = os.path.join(script_path, "maps", "rendered_maps", "")
    dir = os.fsencode(str_dir)
    diff_maps = []
    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        if "diff_leaf" in str(filename):
            diff_maps.append(filename)
    return str_dir, diff_maps


def get_other_maps(images_path, diff_name):
    try:
        diff_trunk_image = bpy.data.images[diff_name.replace("leaf", "trunk")]
    except KeyError:
        diff_trunk_image = bpy.data.images.load(
            images_path + diff_name.replace("leaf", "trunk"))

    try:
        nor_leaf_image = bpy.data.images[diff_name.replace("diff", "nor")]
    except KeyError:
        nor_leaf_image = bpy.data.images.load(
            images_path + diff_name.replace("diff", "nor"))

    try:
        nor_trunk_image = bpy.data.images[diff_name.replace(
            "diff_leaf", "nor_trunk")]
    except KeyError:
        nor_trunk_image = bpy.data.images.load(
            images_path + diff_name.replace("diff_leaf", "nor_trunk"))

    try:
        mask_image = bpy.data.images[diff_name.replace(
            "diff_leaf.jpg", "mask.png")]
    except KeyError:
        mask_image = bpy.data.images.load(
            images_path + diff_name.replace("diff_leaf.jpg", "mask.png"))

    return diff_trunk_image, nor_leaf_image, nor_trunk_image, mask_image


def import_material(blend_path):
    with bpy.data.libraries.load(blend_path) as (data_from, data_to):
        data_to.materials.append("alpha_trees_material")
    return (data_to.materials[0])


def import_tree(image_path):
    diff_leaf_name = os.path.basename(image_path)
    images_path = image_path.replace(diff_leaf_name, "")

    for image in bpy.data.images:
        if image.name == diff_leaf_name:
            print("Found Image")
            diff_leaf_image = image
            break
    else:
        print("Loading Image")
        diff_leaf_image = bpy.data.images.load(image_path)

    ratio = diff_leaf_image.size[1]/diff_leaf_image.size[0]
    print("Ratio: " + str(ratio))
    bpy.ops.mesh.primitive_plane_add()
    plane = bpy.context.active_object
    plane.name = diff_leaf_name[:-19]

    verts = plane.data.vertices
    verts[0].co = (-1, 0, 0)
    verts[1].co = (1, 0, 0)
    verts[2].co = (-1, 0, 2*ratio)
    verts[3].co = (1, 0, 2*ratio)

    scale = float(diff_leaf_name[-18:-14])
    print("Scale: " + str(scale))
    plane.scale = (scale, scale, scale)
    plane.track_axis = "POS_Z"

    bpy.ops.object.material_slot_add()
    mat_slot = plane.material_slots[0]

    for material in bpy.data.materials:
        if material.name == "alpha_trees_material":
            print("Found Material")
            base_tree_material = material
            break
    else:
        print("Loading Material")
        script_path = os.path.dirname(os.path.abspath(__file__))
        blend_path = os.path.join(script_path, "base_scene.blend")
        base_tree_material = import_material(blend_path)
        base_tree_material

    for material in bpy.data.materials:
        if material.name == "AT_" + diff_leaf_name[:-19]:
            tree_material = material
            break
    else:
        tree_material = base_tree_material.copy()
        tree_material.name = "AT_" + diff_leaf_name[:-19]

    mat_slot.material = tree_material

    # Switch images
    diff_trunk_image, nor_leaf_image, nor_trunk_image, mask_image = get_other_maps(
        images_path, diff_leaf_name)

    nor_leaf_image.colorspace_settings.name = "Non-Color"
    nor_trunk_image.colorspace_settings.name = "Non-Color"

    nodes = tree_material.node_tree.nodes
    for node in nodes:
        if node.type == "TEX_IMAGE":
            if node.label == "leaf color":
                node.image = diff_leaf_image

            elif node.label == "trunk color":
                node.image = diff_trunk_image

            elif node.label == "leaf normal":
                node.image = nor_leaf_image

            elif node.label == "trunk normal":
                node.image = nor_trunk_image

            elif node.label == "mask":
                node.image = mask_image

    return plane


preview_collections = {}


def register():
    # register icons
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    preview_collections["alpha_trees_previews"] = pcoll

    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    preview_collections["alpha_trees_system_previews"] = pcoll


def unregister():
    # unregister icons
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
