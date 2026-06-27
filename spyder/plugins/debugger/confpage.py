# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Debugger Plugin Configuration Page."""

# Third party imports
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QVBoxLayout, QLabel

# Local imports
from spyder.api.preferences import PluginConfigPage
from spyder.api.translations import _


class DebuggerConfigPage(PluginConfigPage):

    def setup_page(self):
        newcb = self.create_checkbox

        # ---- Debug ----
        # Pdb run lines Group
        pdb_run_lines_group = QGroupBox(_("Run code while debugging"))
        pdb_run_lines_label = QLabel(
            _(
                "Spyder runs these statements automatically at each debugger "
                "prompt.<br>"
                "Enter them separated by semicolons, for example:<br>"
                "<code>import matplotlib.pyplot as plt; import numpy as "
                "np</code>"
            )
        )
        pdb_run_lines_label.setWordWrap(True)
        pdb_run_lines_edit = self.create_lineedit(
            _("Statements:"), 'startup/pdb_run_lines', '', alignment=Qt.Horizontal)

        pdb_run_lines_layout = QVBoxLayout()
        pdb_run_lines_layout.addWidget(pdb_run_lines_label)
        pdb_run_lines_layout.addWidget(pdb_run_lines_edit)
        pdb_run_lines_group.setLayout(pdb_run_lines_layout)

        # Debug Group
        debug_group = QGroupBox(_("Debugging"))
        debug_layout = QVBoxLayout()

        prevent_closing_box = newcb(
            _("Keep files open"),
            'pdb_prevent_closing',
            tip=_("Prevents accidentally closing a file while debugging"))
        debug_layout.addWidget(prevent_closing_box)

        continue_box = newcb(
            _("Break on first line in files with no breakpoints"),
            'pdb_stop_first_line')
        debug_layout.addWidget(continue_box)

        libraries_box = newcb(
            _("Skip Python libraries"),
            "pdb_ignore_lib",
            tip=_(
                "Skips Python libraries when stepping, so the debugger "
                "stays in your own code"
            ),
        )
        debug_layout.addWidget(libraries_box)

        execute_events_box = newcb(
            _("Process execute events"), 'pdb_execute_events',
            tip=_("Processes the 'execute events' after each prompt, such as "
                  "matplotlib <code>show</code> command."))
        debug_layout.addWidget(execute_events_box)

        exclamation_mark_box = newcb(
            _("Use exclamation mark prefix for Pdb commands"),
            "pdb_use_exclamation_mark",
            tip=_(
                "Prefixes Pdb commands with an exclamation mark to avoid "
                "confusion with Python code"
            ),
        )
        debug_layout.addWidget(exclamation_mark_box)

        debug_group.setLayout(debug_layout)

        filter_group = QGroupBox(_("Execution Inspector"))
        filter_data = [
            (
                "exclude_internal",
                _("Exclude internal frames when inspecting execution"),
            ),
        ]
        filter_boxes = [self.create_checkbox(text, option)
                        for option, text in filter_data]

        filter_layout = QVBoxLayout()
        for box in filter_boxes:
            filter_layout.addWidget(box)
        filter_group.setLayout(filter_layout)

        vlayout = QVBoxLayout()
        vlayout.addWidget(debug_group)
        vlayout.addWidget(pdb_run_lines_group)
        vlayout.addWidget(filter_group)
        vlayout.addStretch(1)
        self.setLayout(vlayout)
