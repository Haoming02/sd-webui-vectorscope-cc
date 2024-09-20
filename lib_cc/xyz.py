from modules import scripts


def _grid_reference():
    for data in scripts.scripts_data:
        if data.script_class.__module__ in (
            "scripts.xyz_grid",
            "xyz_grid.py",
        ) and hasattr(data, "module"):
            return data.module

    raise SystemError("Could not find X/Y/Z Plot...")


def xyz_support(cache: dict):

    def apply_field(field):
        def _(p, x, xs):
            cache.update({field: x})

        return _

    def choices_bool():
        return ["False", "True"]

    def choices_method():
        return [
            "Disabled",
            "Straight",
            "Straight Abs.",
            "Cross",
            "Cross Abs.",
            "Ones",
            "N.Random",
            "U.Random",
            "Multi-Res",
            "Multi-Res Abs.",
        ]

    def choices_scaling():
        return ["Flat", "Cos", "Sin", "1 - Cos", "1 - Sin"]

    xyz_grid = _grid_reference()

    extra_axis_options = [
        xyz_grid.AxisOption(
            "[Vec.CC] Enable", str, apply_field("Enable"), choices=choices_bool
        ),
        xyz_grid.AxisOption(
            "[Vec.CC] Alt.", str, apply_field("Alt"), choices=choices_bool
        ),
        xyz_grid.AxisOption("[Vec.CC] Brightness", float, apply_field("Brightness")),
        xyz_grid.AxisOption("[Vec.CC] Contrast", float, apply_field("Contrast")),
        xyz_grid.AxisOption("[Vec.CC] Saturation", float, apply_field("Saturation")),
        xyz_grid.AxisOption("[Vec.CC] R", float, apply_field("R")),
        xyz_grid.AxisOption("[Vec.CC] G", float, apply_field("G")),
        xyz_grid.AxisOption("[Vec.CC] B", float, apply_field("B")),
        xyz_grid.AxisOption(
            "[Adv.CC] Proc. H.Fix", str, apply_field("DoHR"), choices=choices_bool
        ),
        xyz_grid.AxisOption(
            "[Adv.CC] Method", str, apply_field("Method"), choices=choices_method
        ),
        xyz_grid.AxisOption(
            "[Adv.CC] Scaling", str, apply_field("Scaling"), choices=choices_scaling
        ),
        xyz_grid.AxisOption("[Adv.CC] Randomize", int, apply_field("Random")),
    ]

    xyz_grid.axis_options.extend(extra_axis_options)
