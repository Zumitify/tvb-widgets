# -*- coding: utf-8 -*-
#
# "TheVirtualBrain - Widgets" package
#
# (c) 2022-2023, TVB Widgets Team
#
import collections

from tvb.basic.neotraits._attr import NArray
from tvbwidgets.ui.base_widget import TVBWidget
from IPython.core.display_functions import display
import ipywidgets as widgets


class PSELauncher(TVBWidget):

    def __init__(self, simulator):
        # type: (Simulator) -> None
        super().__init__()
        self.simulator = simulator
        self.params_dict = {}
        self.create_dict()
        self.param_1 = None
        self.param_2 = None
        self.warning = None
        self.metrics = None
        self.min_range1 = None
        self.max_range1 = None
        self.step1 = None
        self.min_range2 = None
        self.max_range2 = None
        self.step2 = None
        self.create_warning_text()
        self.create_metrics()
        widget = self.create_params()
        display(widget)

    def create_dict(self):
        # TODO still need to take the params for connectivity and conduction_speed

        for elem in type(self.simulator.model).declarative_attrs:
            attribute = getattr(type(self.simulator.model), elem)
            if isinstance(attribute, NArray) and attribute.domain is not None:
                param_name = "model." + elem
                self.params_dict[param_name] = [attribute.domain.lo, attribute.domain.hi, attribute.domain.step]

        for elem in type(self.simulator.coupling).declarative_attrs:
            attribute = getattr(type(self.simulator.coupling), elem)
            if isinstance(attribute, NArray) and attribute.domain is not None:
                param_name = "coupling." + elem
                self.params_dict[param_name] = [attribute.domain.lo, attribute.domain.hi, attribute.domain.step]

        cond_speed_default_value = self.simulator.conduction_speed
        self.params_dict["conduction_speed"] = [0, 10*cond_speed_default_value, cond_speed_default_value]

    def create_metrics(self):
        self.metrics = widgets.SelectMultiple(
            options=["Example_1", "Example_2", "Example_3", "Example_4", "Example_5"],
            description=f"<b>Metrics</b>",
            value=["Example_1"],
            disabled=False, layout=widgets.Layout(margin="30px 0px 10px 25px", height="100px"))

        def metrics_changed(change):
            if change['type'] != 'change' or change['name'] != 'value':
                return

        self.metrics.observe(metrics_changed)

    def create_warning_text(self):
        self.warning = widgets.HTML(value="", layout=widgets.Layout(margin="0px 0px 0px 65px"))

    def create_params(self):
        self.param_1 = widgets.Dropdown(
            options=sorted(self.params_dict.keys()),
            description=f"<b>PSE param1</b>",
            value=list(sorted(self.params_dict.keys()))[0],
            disabled=False
        )
        self.param_2 = widgets.Dropdown(
            options=sorted(self.params_dict.keys()),
            description=f"<b>PSE param2</b>",
            value=list(sorted(self.params_dict.keys()))[1],
            disabled=False
        )

        def param_changed(change):
            if change['type'] != 'change' or change['name'] != 'value':
                return

            if self.param_1.value != self.param_2.value:
                self.warning.value = ""
            else:
                self.warning.value = f"<b><font color='red'>The parameters should be different!</b>"

            if self.param_1.value == change['new'] and self.param_1.value != self.param_2.value:
                self.change_range_param(True)
            elif self.param_2.value == change['new'] and self.param_1.value != self.param_2.value:
                self.change_range_param(False)
            else:
                self.change_range_param(True)
                self.change_range_param(False)

        self.param_1.observe(param_changed)
        self.param_2.observe(param_changed)

        return self.pse_params_range()

    def change_range_param(self, param1):
        if param1:
            self.min_range1.value = self.params_dict[self.param_1.value][0]
            self.max_range1.value = self.params_dict[self.param_1.value][1]
            self.step1.value = self.params_dict[self.param_1.value][2]
        else:
            self.min_range2.value = self.params_dict[self.param_2.value][0]
            self.max_range2.value = self.params_dict[self.param_2.value][1]
            self.step2.value = self.params_dict[self.param_2.value][2]

    def pse_params_range(self):
        self.set_range(True)
        self.set_range(False)

        def range_changed(change):
            if change['type'] != 'change' or change['name'] != 'value':
                return

        self.min_range1.observe(range_changed)
        self.max_range1.observe(range_changed)
        self.step1.observe(range_changed)
        self.min_range2.observe(range_changed)
        self.max_range2.observe(range_changed)
        self.step2.observe(range_changed)

        range1 = widgets.VBox(children=[widgets.HBox(children=[self.min_range1, self.max_range1]), self.step1],
                              layout=widgets.Layout(margin="0px 0px 0px 60px"))
        range2 = widgets.VBox(children=[widgets.HBox(children=[self.min_range2, self.max_range2]), self.step2],
                              layout=widgets.Layout(margin="0px 0px 0px 60px"))
        box1 = widgets.HBox(children=[self.param_1, range1], layout=widgets.Layout(margin="40px 50px 50px 50px"))
        box2 = widgets.HBox(children=[self.param_2, range2], layout=widgets.Layout(margin="40px 50px 30px 50px"))
        return widgets.VBox(children=[box1, box2, self.warning, self.metrics],
                            layout=widgets.Layout(margin="40px 50px 50px 50px"))

    def set_range(self, param1):
        if param1:
            self.min_range1 = widgets.FloatText(
                value=self.params_dict[self.param_1.value][0],
                description=f"<b><font color='gray'>Min range</b>",
                disable=False
            )

            self.max_range1 = widgets.FloatText(
                value=self.params_dict[self.param_1.value][1],
                description=f"<b><font color='gray'>Max range</b>",
                disable=False
            )

            self.step1 = widgets.FloatText(
                value=self.params_dict[self.param_1.value][2],
                description=f"<b><font color='gray'>Step</b>",
                disable=False
            )
        else:
            self.min_range2 = widgets.FloatText(
                value=self.params_dict[self.param_2.value][0],
                description=f"<b><font color='gray'>Min range</b>",
                disable=False
            )

            self.max_range2 = widgets.FloatText(
                value=self.params_dict[self.param_2.value][1],
                description=f"<b><font color='gray'>Max range</b>",
                disable=False
            )

            self.step2 = widgets.FloatText(
                value=self.params_dict[self.param_2.value][2],
                description=f"<b><font color='gray'>Step</b>",
                disable=False
            )
