
![Logo](./images/logo.jpg)

### What is Interactive Tools?
Interactive Tools is a collection of tools for Blender that aims to provide intuitive, context sensitive tools.

Due to its design these tools work better when used with hotkeys.

### Documentation:
You can find the documentation for the tools and how to install them [here](https://maxivz.github.io/interactivetoolsblenderdocs.github.io/).

### License
Interactive Tools uses the GPL 3.0 license

### Reporting a bug
When it comes to reporting bugs, please submit them on Github [here](https://github.com/maxivz/interactivetoolsblender/issues).

Please include a description of the problem and if possible the circustances in which it happends, as more detailed reports makes it easier to fix bugs.


### 1.5.0 - Blender 5.x compatibility update
This is an unofficial compatibility update of version 1.4.1 for Blender 4.2 up to 5.3.

**Fixed**
- **Smart Loop / Smart Ring / Step Loop** no longer fail with `Calling operator "bpy.ops.mesh.loop_multi_select" error, could not be found`. Edge loops and rings are now walked directly on the mesh, so selection does not depend on that operator existing. Works in vertex, edge and face mode.
- **Quick Rotate UV 90** read `BMLoopUV.select`, which was removed in Blender 5.0.
- **New Object pie** crashed because `object.gpencil_add` (legacy Grease Pencil) is gone, it uses `object.grease_pencil_add` now.
- **Transform Options pie / Snap Presets / Target Weld** read snapping properties that were reorganised in 4.0 (`snap_elements`, `use_snap_project`), these go through a compatibility layer now.
- Context overrides built from `bpy.context.copy()` (Transform Mode Cycle, CS Move/Rotate/Scale) are replaced with a minimal window/area/region override.
- **Smart Extrude Modal** called an undefined `SmartDelete` and passed `None` into macro properties.
- **Quick Align** passed a point instead of a direction to `Scene.ray_cast`, and failed on redo.
- Menu entry pointing at a non existent operator (`mesh.transform_orientation_pie_pie`).
- Object mode selection helper called `select_set` on a list instead of each object.
- Keymap cleanup (`unregister_keymaps`) used an attribute that does not exist.
- Preferences id is derived from the full package name, so the addon also works when installed as an extension.
- Reading preferences with dict style access (removed for `bpy.props` in 5.0).

**More robust**
- F2, LoopTools, Set Flow, QBlocker and TexTools are detected by whether their operators exist right now, instead of by a one time check at startup. F2 and LoopTools features fall back to built in behaviour when those addons are not enabled.
- Icons that do not exist in the running Blender fall back to no icon instead of breaking the whole panel or pie.
- Menus that no longer exist are skipped, and a class that fails to register no longer stops the rest of the addon from registering.
- Bmesh lookup tables are made valid before element indices are used.
- Grease Pencil v3 (`GREASEPENCIL`, `EDIT_GREASE_PENCIL`) is handled in the mode switching.
