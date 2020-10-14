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
        ui,
        settings,
        gen_functions,
        imp_functions,
        sys_functions,
        operators
    ]:
        importlib.reload(mod)
else:
    import bpy
    from . import (
        ui,
        settings,
        gen_functions,
        imp_functions,
        sys_functions,
        operators
    )


bl_info = {
    "name": "CardMate",
    "author": "Atamert Ölçgen",
    "description": "This project is forked from alpha_trees_generator.  "
                   "See: https://blenderartists.org/t/alpha-trees-wip-nature-addon/1250694/48",
    "blender": (2, 90, 0),
    "version": (0, 7, 0),
    "location": "",
    "tracker_url": "https://github.com/muhuk/cardmate",
    "warning": "",
    "category": "Image"
}


items = [
    imp_functions,
    settings,
    ui,
    operators,
]


if "bpy" in locals():
    import imp
    imp.reload(gen_functions)
    imp.reload(sys_functions)
    for item in items:
        imp.reload(item)


def register():
    for item in items:
        item.register()


def unregister():
    for item in reversed(items):
        item.unregister()
