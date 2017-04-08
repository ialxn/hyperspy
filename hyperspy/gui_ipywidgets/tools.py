import ipywidgets
import traitlets

from hyperspy.gui_ipywidgets.utils import (
    labelme, labelme_sandwich, enum2dropdown, add_display_arg,
    register_ipy_widget, string_to_html)
from hyperspy.misc.link_traits import link_traits
from hyperspy.gui_ipywidgets.custom_widgets import OddIntSlider
from hyperspy.signal_tools import SPIKES_REMOVAL_INSTRUCTIONS


@register_ipy_widget(toolkey="interactive_range_selector")
@add_display_arg
def interactive_range_ipy(obj, **kwargs):
    # Define widgets
    axis = obj.axis
    left = ipywidgets.FloatText(disabled=True)
    right = ipywidgets.FloatText(disabled=True)
    units = ipywidgets.Label()
    help = ipywidgets.HTML(
        "Click on the signal figure and drag to the right to select a signal "
        "range. Press `Apply` to perform the operation or `Close` to cancel.",)
    help = ipywidgets.Accordion(children=[help])
    help.set_title(0, "Help")
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove span selector from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Perform the operation using the selected range.")

    # Connect
    link_traits((obj, "ss_left_value"), (left, "value"))
    link_traits((obj, "ss_right_value"), (right, "value"))
    link_traits((axis, "units"), (units, "value"))

    def on_apply_clicked(b):
        obj = obj
        if obj.ss_left_value != obj.ss_right_value:
            obj.span_selector_switch(False)
            for method, cls in obj.on_close:
                method(cls, obj.ss_left_value, obj.ss_right_value)
            obj.span_selector_switch(True)
    apply.on_click(on_apply_clicked)

    box = ipywidgets.VBox([
        ipywidgets.HBox([left, units, ipywidgets.Label("-"), right, units]),
        help,
        ipywidgets.HBox((apply, close))
    ])

    def on_close_clicked(b):
        obj.span_selector_switch(False)
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.calibrate")
@add_display_arg
def calibrate_ipy(obj, **kwargs):
    # Define widgets
    axis = obj.axis
    left = ipywidgets.FloatText(disabled=True)
    right = ipywidgets.FloatText(disabled=True)
    offset = ipywidgets.FloatText(disabled=True)
    scale = ipywidgets.FloatText(disabled=True)
    new_left = ipywidgets.FloatText(disabled=False)
    new_right = ipywidgets.FloatText(disabled=False)
    units = ipywidgets.Label()
    help = ipywidgets.HTML(
        "Click on the signal figure and drag to the right to select a signal "
        "range. Set the new left and right values and press `Apply` to update "
        "the calibration of the axis with the new values or press "
        " `Close` to cancel.",)
    help = ipywidgets.Accordion(children=[help])
    help.set_title(0, "Help")
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove span selector from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Set the axis calibration with the `offset` and `scale` values "
        "above.")

    # Connect
    link_traits((obj, "ss_left_value"), (left, "value"))
    link_traits((obj, "ss_right_value"), (right, "value"))
    link_traits((obj, "left_value"), (new_left, "value"))
    link_traits((obj, "right_value"), (new_right, "value"))
    link_traits((axis, "units"), (units, "value"))
    link_traits((axis, "offset"), (offset, "value"))
    link_traits((axis, "scale"), (scale, "value"))

    def on_apply_clicked(b):
        axis.scale = obj.scale
        axis.offset = obj.offset
        obj.span_selector_switch(on=False)
        obj.signal._plot.signal_plot.update()
        obj.span_selector_switch(on=True)
    apply.on_click(on_apply_clicked)

    box = ipywidgets.VBox([
        labelme_sandwich("New left", new_left, units),
        labelme_sandwich("New right", new_right, units),
        labelme_sandwich("Left", left, units),
        labelme_sandwich("Right", right, units),
        labelme_sandwich("Scale", scale, ""),  # No units, but padding
        labelme_sandwich("Offset", offset, units),
        help,
        ipywidgets.HBox((apply, close))
    ])

    def on_close_clicked(b):
        obj.span_selector_switch(False)
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.smooth_savitzky_golay")
@add_display_arg
def smooth_savitzky_golay_ipy(obj, **kwargs):
    window_length = OddIntSlider(
        value=3, step=2, min=3, max=max(int(obj.axis.size * 0.25), 3))
    polynomial_order = ipywidgets.IntSlider(value=3, min=1,
                                            max=window_length.value - 1)
    # Polynomial order must be less than window length

    def update_bound(change):
        polynomial_order.max = change.new - 1
    window_length.observe(update_bound, "value")
    differential_order = ipywidgets.IntSlider(value=0, min=0, max=10)
    color = ipywidgets.ColorPicker()
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove the smoothed line from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Perform the operation using the selected range.")
    link_traits((obj, "polynomial_order"), (polynomial_order, "value"))
    link_traits((obj, "window_length"), (window_length, "value"))
    link_traits((obj, "differential_order"), (differential_order, "value"))
    # Differential order must be less or equal to polynomial_order
    link_traits((polynomial_order, "value"), (differential_order, "max"))
    link_traits((obj, "line_color_ipy"), (color, "value"))
    box = ipywidgets.VBox([
        labelme("Window length", window_length),
        labelme("polynomial order", polynomial_order),
        labelme("Differential order", differential_order),
        labelme("Color", color),
        ipywidgets.HBox((apply, close))
    ])

    def on_apply_clicked(b):
        obj.apply()
    apply.on_click(on_apply_clicked)

    def on_close_clicked(b):
        obj.close()
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.smooth_lowess")
@add_display_arg
def smooth_lowess_ipy(obj, **kwargs):
    smoothing_parameter = ipywidgets.FloatSlider(min=0, max=1)
    number_of_iterations = ipywidgets.IntText()
    color = ipywidgets.ColorPicker()
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove the smoothed line from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Perform the operation using the selected range.")
    link_traits((obj, "smoothing_parameter"), (smoothing_parameter, "value"))
    link_traits((obj, "number_of_iterations"), (number_of_iterations, "value"))
    link_traits((obj, "line_color_ipy"), (color, "value"))
    box = ipywidgets.VBox([
        labelme("Smoothing parameter", smoothing_parameter),
        labelme("Number of iterations", number_of_iterations),
        labelme("Color", color),
        ipywidgets.HBox((apply, close))
    ])

    def on_apply_clicked(b):
        obj.apply()
    apply.on_click(on_apply_clicked)

    def on_close_clicked(b):
        obj.close()
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.smooth_total_variation")
@add_display_arg
def smooth_tv_ipy(obj, **kwargs):
    smoothing_parameter = ipywidgets.FloatSlider(min=0.1, max=1000)
    smoothing_parameter_max = ipywidgets.FloatText(
        value=smoothing_parameter.max)
    color = ipywidgets.ColorPicker()
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove the smoothed line from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Perform the operation using the selected range.")
    link_traits((obj, "smoothing_parameter"), (smoothing_parameter, "value"))
    link_traits((smoothing_parameter_max, "value"),
                (smoothing_parameter, "max"))
    link_traits((obj, "line_color_ipy"), (color, "value"))
    box = ipywidgets.VBox([
        labelme("Weight", smoothing_parameter),
        labelme("Weight max", smoothing_parameter_max),
        labelme("Color", color),
        ipywidgets.HBox((apply, close))
    ])

    def on_apply_clicked(b):
        obj.apply()
    apply.on_click(on_apply_clicked)

    def on_close_clicked(b):
        obj.close()
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.smooth_butterworth")
@add_display_arg
def smooth_butterworth(obj, **kwargs):
    cutoff = ipywidgets.FloatSlider(min=0.01, max=1.)
    order = ipywidgets.IntText()
    type_ = ipywidgets.Dropdown(options=("low", "high"))
    color = ipywidgets.ColorPicker()
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove the smoothed line from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Perform the operation using the selected range.")
    link_traits((obj, "cutoff_frequency_ratio"), (cutoff, "value"))
    link_traits((obj, "type"), (type_, "value"))
    link_traits((obj, "order"), (order, "value"))
    box = ipywidgets.VBox([
        labelme("Cutoff frequency ration", cutoff),
        labelme("Type", type_),
        labelme("Order", order),
        ipywidgets.HBox((apply, close))
    ])

    def on_apply_clicked(b):
        obj.apply()
    apply.on_click(on_apply_clicked)

    def on_close_clicked(b):
        obj.close()
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.contrast_editor")
@add_display_arg
def image_constast_editor_ipy(obj, **kwargs):
    left = ipywidgets.FloatText(disabled=True)
    right = ipywidgets.FloatText(disabled=True)
    help = ipywidgets.HTML(
        "Click on the histogram figure and drag to the right to select a"
        "range. Press `Apply` to set the new contrast limits, `Reset` to reset "
        "them or `Close` to cancel.",)
    help = ipywidgets.Accordion(children=[help])
    help.set_title(0, "Help")
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove span selector from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Perform the operation using the selected range.")
    reset = ipywidgets.Button(
        description="Reset",
        tooltip="Reset the contrast to the previous value.")

    # Connect
    link_traits((obj, "ss_left_value"), (left, "value"))
    link_traits((obj, "ss_right_value"), (right, "value"))

    def on_apply_clicked(b):
        obj.apply()
    apply.on_click(on_apply_clicked)

    def on_reset_clicked(b):
        obj.reset()
    reset.on_click(on_reset_clicked)

    box = ipywidgets.VBox([
        labelme("vmin", left),
        labelme("vmax", right),
        help,
        ipywidgets.HBox((apply, reset, close))
    ])

    def on_close_clicked(b):
        obj.close()
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.remove_background")
@add_display_arg
def remove_background_ipy(obj, **kwargs):
    fast = ipywidgets.Checkbox()
    help = ipywidgets.HTML(
        "Click on the signal figure and drag to the right to select a"
        "range. Press `Apply` to remove the background in the whole dataset. "
        "If fast is checked, the background parameters are estimated using a "
        "fast (analytical) method that can compromise accuray. When unchecked "
        "non linear least squares is employed instead.",)
    help = ipywidgets.Accordion(children=[help])
    help.set_title(0, "Help")
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove span selector from the signal figure.")
    apply = ipywidgets.Button(
        description="Apply",
        tooltip="Remove the background in the whole dataset.")

    polynomial_order = ipywidgets.IntSlider(min=1, max=10)
    labeled_polyorder = labelme("Polynomial order", polynomial_order)
    background_type = enum2dropdown(obj.traits()["background_type"])

    def enable_poly_order(change):
        if change.new == "Polynomial":
            for child in labeled_polyorder.children:
                child.layout.display = ""
        else:
            for child in labeled_polyorder.children:
                child.layout.display = "none"
    background_type.observe(enable_poly_order, "value")
    link_traits((obj, "background_type"), (background_type, "value"))
    # Trigger the function that controls the visibility of poly order as
    # setting the default value doesn't trigger it.

    class Dummy:
        new = background_type.value
    enable_poly_order(change=Dummy())
    link_traits((obj, "polynomial_order"), (polynomial_order, "value"))
    link_traits((obj, "fast"), (fast, "value"))
    box = ipywidgets.VBox([
        labelme("Background type", background_type),
        labeled_polyorder,
        labelme("Fast", fast),
        help,
        ipywidgets.HBox((apply, close)),
    ])

    def on_apply_clicked(b):
        obj.apply()
        box.close()
    apply.on_click(on_apply_clicked)

    def on_close_clicked(b):
        obj.span_selector_switch(False)
        box.close()
    close.on_click(on_close_clicked)
    return box


@register_ipy_widget(toolkey="Signal1D.spikes_removal_tool")
@add_display_arg
def spikes_removal_ipy(obj, **kwargs):
    threshold = ipywidgets.FloatText()
    add_noise = ipywidgets.Checkbox()
    default_spike_width = ipywidgets.IntText()
    interpolator_kind = enum2dropdown(obj.traits()["interpolator_kind"])
    spline_order = ipywidgets.IntSlider(min=1, max=10)
    progress_bar = ipywidgets.IntProgress(max=len(obj.coordinates) - 1)
    help = ipywidgets.HTML(value=string_to_html(SPIKES_REMOVAL_INSTRUCTIONS))
    help = ipywidgets.Accordion(children=[help])
    help.set_title(0, "Help")

    show_diff = ipywidgets.Button(
        description="Show derivative histogram",
        tooltip="This figure is useful to estimate the threshold.",
        layout=ipywidgets.Layout(width="auto"))
    close = ipywidgets.Button(
        description="Close",
        tooltip="Close widget and remove span selector from the signal figure.")
    next = ipywidgets.Button(
        description="Find next",
        tooltip="Find next spike")
    previous = ipywidgets.Button(
        description="Find previous",
        tooltip="Find previous spike")
    remove = ipywidgets.Button(
        description="Remove spike",
        tooltip="Remove spike and find next one.")

    def on_show_diff_clicked(b):
        obj._show_derivative_histogram_fired()
    show_diff.on_click(on_show_diff_clicked)

    def on_next_clicked(b):
        obj.find()
    next.on_click(on_next_clicked)

    def on_previous_clicked(b):
        obj.find(back=True)
    previous.on_click(on_previous_clicked)

    def on_remove_clicked(b):
        obj.apply()
    remove.on_click(on_remove_clicked)
    labeled_spline_order = labelme("Spline order", spline_order)

    def enable_interpolator_kind(change):
        if change.new == "Spline":
            for child in labeled_spline_order.children:
                child.layout.display = ""
        else:
            for child in labeled_spline_order.children:
                child.layout.display = "none"
    interpolator_kind.observe(enable_interpolator_kind, "value")
    link_traits((obj, "interpolator_kind"), (interpolator_kind, "value"))
    link_traits((obj, "threshold"), (threshold, "value"))
    link_traits((obj, "add_noise"), (add_noise, "value"))
    link_traits((obj, "default_spike_width"), (default_spike_width, "value"))
    link_traits((obj, "spline_order"), (spline_order, "value"))
    link_traits((obj, "index"), (progress_bar, "value"))
    # Trigger the function that controls the visibility  as
    # setting the default value doesn't trigger it.

    class Dummy:
        new = interpolator_kind.value
    enable_interpolator_kind(change=Dummy())
    advanced = ipywidgets.Accordion((
        ipywidgets.VBox([
            labelme("Add noise", add_noise),
            labelme("Interpolator kind", interpolator_kind),
            labelme("Default spike width", default_spike_width),
            labelme("Spline order", spline_order), ]),))

    advanced.set_title(0, "Advanced settings")
    box = ipywidgets.VBox([
        ipywidgets.VBox([
            show_diff,
            labelme("Threshold", threshold),
            labelme("Progress", progress_bar), ]),
        advanced,
        help,
        ipywidgets.HBox([previous, next, remove, close])
    ])

    def on_close_clicked(b):
        obj.span_selector_switch(False)
        box.close()
    close.on_click(on_close_clicked)
    return box
