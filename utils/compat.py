"""
Compatibility helpers so Interactive Tools keeps working across Blender 4.2 -> 5.x.

Nothing in here is specific to one tool; it is the small set of "does this
exist / does this work on the running Blender" checks the rest of the addon
uses instead of assuming that an operator, property or icon is available.
"""
import bpy


def version_at_least(*version):
    """True if the running Blender is at least the given (major, minor, patch)."""
    return tuple(bpy.app.version) >= tuple(version)


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------
def op_exists(idname):
    """
    True if the operator "module.name" is registered in the running Blender.

    hasattr(bpy.ops.x, 'y') is not reliable (it always returns True), the
    failure only shows up when the operator is called. get_rna_type() raises
    for operators that are not registered, which is what we use here. Because
    nothing is cached, enabling or disabling another addon is picked up
    immediately.
    """
    try:
        module_name, op_name = idname.split('.', 1)
        getattr(getattr(bpy.ops, module_name), op_name).get_rna_type()
        return True
    except Exception:
        return False


def run_op(idname, *args, **kwargs):
    """
    Call an operator by id if it exists.
    Returns the operator result set, or None if the operator is not available.
    """
    if not op_exists(idname):
        return None

    module_name, op_name = idname.split('.', 1)
    return getattr(getattr(bpy.ops, module_name), op_name)(*args, **kwargs)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
_icon_cache = None


def _icon_names():
    global _icon_cache

    if _icon_cache is None:
        try:
            names = set(bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items.keys())
        except Exception:
            names = set()

        if names:
            _icon_cache = names
        else:
            return names

    return _icon_cache


def safe_icon(name, fallback='NONE'):
    """
    Icon names get renamed or removed between releases and an unknown icon
    raises inside draw(), which takes the whole panel or pie down with it.
    This returns the fallback instead when the icon does not exist.
    """
    names = _icon_names()

    if not names or name in names:
        return name

    return fallback


class _NullProps:
    """Stands in for operator properties of an operator that is not available."""

    def __setattr__(self, key, value):
        pass

    def __getattr__(self, key):
        return None


def ui_operator(layout, idname, **kwargs):
    """
    layout.operator() that does not blow up when the operator (usually one that
    belongs to an optional third party addon) is missing.

    Returns the operator properties like layout.operator does, or a dummy
    object that accepts and ignores attribute assignment, so that code like
    ui_operator(row, "x.y", text="Z").angle = 1.0 keeps working.
    """
    if 'icon' in kwargs:
        kwargs['icon'] = safe_icon(kwargs['icon'])

    if op_exists(idname):
        return layout.operator(idname, **kwargs)

    row = layout.row()
    row.enabled = False
    row.label(text=kwargs.get('text', idname) + " (not available)")
    return _NullProps()


# ---------------------------------------------------------------------------
# View3D context overrides
# ---------------------------------------------------------------------------
def view3d_override(context, area=None):
    """
    Keyword arguments for context.temp_override() that target a 3D viewport.

    Only window, screen, area, region and space_data are overridden. Copying
    the whole of bpy.context into temp_override works on some versions and
    raises on others, so it is not done here.
    """
    window = context.window
    screen = context.screen or (window.screen if window else None)

    if area is None:
        if context.area is not None and context.area.type == 'VIEW_3D':
            area = context.area
        elif screen is not None:
            area = next((a for a in screen.areas if a.type == 'VIEW_3D'), None)

    if area is None:
        return None

    override = {'area': area}

    if window is not None:
        override['window'] = window

    if screen is not None:
        override['screen'] = screen

    region = next((r for r in area.regions if r.type == 'WINDOW'), None)
    if region is not None:
        override['region'] = region

    return override


def set_select_tool(context, area=None):
    """Make the active workspace tool the Select Box tool for a 3D viewport."""
    override = view3d_override(context, area)

    if override is None:
        return False

    try:
        with context.temp_override(**override):
            bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
        return True

    except Exception as error:
        print("Interactive Tools: could not set the select tool:", error)
        return False


# ---------------------------------------------------------------------------
# Tool settings (snapping and friends changed shape in 4.0 and later)
# ---------------------------------------------------------------------------
def ts_has(tool_settings, name):
    return name in tool_settings.bl_rna.properties.keys()


def ts_get(tool_settings, name, default=None):
    try:
        return getattr(tool_settings, name)
    except AttributeError:
        return default


def ts_set(tool_settings, name, value):
    """Set a tool setting, silently skipping ones this Blender does not have."""
    try:
        setattr(tool_settings, name, value)
        return True
    except (AttributeError, TypeError, ValueError):
        return False


def _enum_keys(tool_settings, name):
    if not ts_has(tool_settings, name):
        return set()

    return set(tool_settings.bl_rna.properties[name].enum_items.keys())


def get_snap_elements(tool_settings):
    """Every enabled snap element, however this Blender splits them up."""
    elements = set()

    for name in ('snap_elements', 'snap_elements_base', 'snap_elements_individual'):
        value = ts_get(tool_settings, name)

        if value:
            elements |= set(value)

    return elements


def set_snap_elements(tool_settings, elements):
    """
    Set the snap elements. Blender 4.0 split snap_elements into
    snap_elements_base and snap_elements_individual, this writes to
    whichever of those exist.
    """
    elements = set(elements)

    if ts_has(tool_settings, 'snap_elements_base'):
        base = _enum_keys(tool_settings, 'snap_elements_base')
        individual = _enum_keys(tool_settings, 'snap_elements_individual')

        # 'FACE' used to cover face projection as well
        if 'FACE' in elements and 'FACE' not in base and 'FACE_PROJECT' in individual:
            elements.discard('FACE')
            elements.add('FACE_PROJECT')

        ts_set(tool_settings, 'snap_elements_base', elements & base)

        if individual:
            ts_set(tool_settings, 'snap_elements_individual', elements & individual)

    else:
        ts_set(tool_settings, 'snap_elements', elements)


def get_snap_project(tool_settings):
    """'Project Individual Elements', which moved from a bool to an element."""
    value = ts_get(tool_settings, 'use_snap_project')

    if value is not None:
        return bool(value)

    return 'FACE_PROJECT' in get_snap_elements(tool_settings)


def set_snap_project(tool_settings, enabled):
    if ts_has(tool_settings, 'use_snap_project'):
        ts_set(tool_settings, 'use_snap_project', enabled)
        return

    elements = get_snap_elements(tool_settings)

    if enabled:
        elements.add('FACE_PROJECT')
    else:
        elements.discard('FACE_PROJECT')

    set_snap_elements(tool_settings, elements)
