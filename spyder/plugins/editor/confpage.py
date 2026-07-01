# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Editor config page."""

from qtpy.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from spyder.api.config.decorators import on_conf_change
from spyder.api.config.mixins import SpyderConfigurationObserver
from spyder.api.preferences import PluginConfigPage
from spyder.api.translations import _
from spyder.config.manager import CONF
from spyder.plugins.editor.widgets.mouse_shortcuts import MouseShortcutEditor


NUMPYDOC = "https://numpydoc.readthedocs.io/en/latest/format.html"
GOOGLEDOC = (
    "https://sphinxcontrib-napoleon.readthedocs.io/en/latest/"
    "example_google.html"
)
SPHINXDOC = (
    "https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html"
)
DOCSTRING_SHORTCUT = CONF.get('shortcuts', 'editor/docstring')


class EditorConfigPage(PluginConfigPage, SpyderConfigurationObserver):

    def __init__(self, plugin, parent):
        PluginConfigPage.__init__(self, plugin, parent)
        SpyderConfigurationObserver.__init__(self)

        self.removetrail_box = None
        self.add_newline_box = None
        self.remove_trail_newline_box = None
        self.tabwidth_spin = None
        self.indent_char_box = None

        self.apply_callback = self.set_indent_chars

    def setup_page(self):
        newcb = self.create_checkbox

        # ---- Display tab
        # -- Interface group
        interface_group = QGroupBox(_("Interface"))
        showtabbar_box = newcb(
            _("Show tab bar"),
            'show_tab_bar',
            tip=_(
                "Shows a tab for each open file.<br>The file switcher, "
                "Outline pane, and Ctrl-Tab are always available to navigate "
                "between files."
            ),
        )
        show_filename_box = newcb(
            _("Show full file path above editor"),
            'show_filename_toolbar',
            tip=_(
                "Shows the full path of the current file above the editor.<br>"
                "The path is always available by hovering over the file's tab."
            ),
        )
        showclassfuncdropdown_box = newcb(
            _("Show class/function selector"),
            'show_class_func_dropdown',
            tip=_(
                "Shows a selector to go to the file's classes and functions"
            ),
        )
        scroll_past_end_box = newcb(
            _("Allow scrolling past file end"), 'scroll_past_end'
        )

        interface_layout = QVBoxLayout()
        interface_layout.addWidget(showtabbar_box)
        interface_layout.addWidget(show_filename_box)
        interface_layout.addWidget(showclassfuncdropdown_box)
        interface_layout.addWidget(scroll_past_end_box)
        interface_group.setLayout(interface_layout)

        # -- Helpers group
        helpers_group = QGroupBox(_("Helpers"))
        showindentguides_box = newcb(_("Show indent guides"), 'indent_guides')
        showcodefolding_box = newcb(
            _("Show code folding"),
            "code_folding",
            tip=_(
                "Shows arrows in the margin to fold and unfold "
                "code by indent level"
            ),
        )
        linenumbers_box = newcb(_("Show line numbers"), 'line_numbers')
        breakpoints_box = newcb(
            _("Show debugger breakpoints"),
            'editor_debugger_panel',
            section='debugger',
        )
        todolist_box = newcb(
            _("Show code annotations"),
            'todo_list',
            tip=_(
                "Shows a marker to the left of line numbers when the "
                "following annotations appear at the beginning of a "
                "comment:<br><code>TODO, FIXME, XXX, HINT, TIP, @todo, HACK, "
                "BUG, OPTIMIZE, !!!, ???</code> (and their lowercase variants)"
            ),
        )

        helpers_layout = QVBoxLayout()
        helpers_layout.addWidget(showindentguides_box)
        helpers_layout.addWidget(showcodefolding_box)
        helpers_layout.addWidget(linenumbers_box)
        helpers_layout.addWidget(breakpoints_box)
        helpers_layout.addWidget(todolist_box)
        helpers_group.setLayout(helpers_layout)

        # -- Highlight group
        highlight_group = QGroupBox(_("Highlight"))
        currentline_box = newcb(
            _("Highlight current line"), 'highlight_current_line'
        )
        currentcell_box = newcb(
            _("Highlight current cell"), 'highlight_current_cell'
        )
        occurrence_box = newcb(
            _("Highlight occurrences of selected text after (ms):"),
            'occurrence_highlighting',
        )
        occurrence_spin = self.create_spinbox(
            "",
            None,
            'occurrence_highlighting/timeout',
            min_=100,  # 0.1 seconds
            max_=60_000,  # 1 minute
            step=100,  # 0.1 seconds
        )

        occurrence_box.checkbox.toggled.connect(
            occurrence_spin.spinbox.setEnabled
        )
        occurrence_spin.spinbox.setEnabled(
            self.get_option('occurrence_highlighting')
        )

        occurrence_glayout = QGridLayout()
        occurrence_glayout.addWidget(occurrence_box, 0, 0)
        occurrence_glayout.addWidget(occurrence_spin.spinbox, 0, 1)

        occurrence_layout = QHBoxLayout()
        occurrence_layout.addLayout(occurrence_glayout)
        occurrence_layout.addStretch(1)

        highlight_layout = QVBoxLayout()
        highlight_layout.addWidget(currentline_box)
        highlight_layout.addWidget(currentcell_box)
        highlight_layout.addLayout(occurrence_layout)
        highlight_group.setLayout(highlight_layout)

        # ---- Source code tab
        # -- Automatic changes group
        automatic_group = QGroupBox(_("Automatic editing"))
        closepar_box = newcb(
            _("Insert closing parentheses, brackets, and braces"),
            'close_parentheses',
            tip=_("Closes parentheses, brackets, and braces as you type"),
        )
        close_quotes_box = newcb(
            _("Insert closing quotes"),
            'close_quotes',
            tip=_("Closes quotes as you type"),
        )
        add_colons_box = newcb(
            _("Insert colons after block keywords"),
            "add_colons",
            tip=_(
                "Adds a colon at the end of block keywords, such as "
                "<code>if</code> or <code>for</code>"
            ),
        )
        autounindent_box = newcb(
            _("Align block keywords"),
            'auto_unindent',
            tip=_(
                "Aligns block keywords such as <code>else</code> or "
                "<code>elif</code> with their block"
            ),
        )

        automatic_layout = QVBoxLayout()
        automatic_layout.addWidget(closepar_box)
        automatic_layout.addWidget(close_quotes_box)
        automatic_layout.addWidget(add_colons_box)
        automatic_layout.addWidget(autounindent_box)
        automatic_group.setLayout(automatic_layout)

        # -- Trailing whitespace group
        whitespace_group = QGroupBox(_("Trailing whitespace"))
        self.removetrail_box = newcb(
            _("Strip all trailing whitespaces on save"),
            'always_remove_trailing_spaces',
            default=False,
        )
        strip_mode_box = newcb(
            _("Strip trailing whitespaces on edited lines"),
            'strip_trailing_spaces_on_modify',
            default=True,
            tip=_(
                "Remove trailing whitespace from edited line as you leave "
                "them, except inside strings.<br>When off, only whitespace "
                "that Spyder itself added is stripped."
            ),
        )
        self.add_newline_box = newcb(
            _("Add a final newline on save"),
            'add_newline',
            default=False,
            tip=_(
                "Adds a newline at the end of the file if it doesn't have "
                "one, following standard text file conventions"
            ),
        )
        self.remove_trail_newline_box = newcb(
            _("Strip blank lines at end of file on save"),
            'always_remove_trailing_newlines',
            default=False,
            tip=_(
                "Removes blank lines at the end of the file, keeping a single "
                "final newline"
            ),
        )

        # Disable the fix-on-save options if autoformatting is enabled
        format_on_save = CONF.get(
            'completions',
            ('provider_configuration', 'lsp', 'values', 'format_on_save'),
            False,
        )
        self.on_format_save_state(format_on_save)

        whitespace_layout = QVBoxLayout()
        whitespace_layout.addWidget(self.removetrail_box)
        whitespace_layout.addWidget(strip_mode_box)
        whitespace_layout.addWidget(self.add_newline_box)
        whitespace_layout.addWidget(self.remove_trail_newline_box)
        whitespace_group.setLayout(whitespace_layout)

        # -- Identation group
        indentation_group = QGroupBox(_("Indentation"))
        self.tabwidth_spin = self.create_spinbox(
            _("Tab width (spaces):"),
            None,
            "tab_stop_width_spaces",
            default=4,
            min_=1,
            max_=16,
            step=1,
        )
        self.indent_char_box = newcb(
            _("Indent with spaces instead of tabs"),
            'indent_with_spaces',
            default=True,
            tip=_(
                "Inserts the set number of spaces when you press Tab,"
                "instead of a tab"
            ),
        )
        ibackspace_box = newcb(
            _("Intelligent backspace"),
            'intelligent_backspace',
            tip=_(
                "Removes a full indentation level with a single backspace, "
                "instead of one space at a time"
            ),
            default=True,
        )
        tab_mode_box = newcb(
            _("Tab always indents"),
            'tab_always_indent',
            default=False,
            tip=_(
                "Always indents when you press Tab, even mid-line. "
                "You can still trigger code completion with Ctrl+Space."
            ),
        )

        indent_tab_grid_layout = QGridLayout()
        indent_tab_grid_layout.addWidget(self.tabwidth_spin.plabel, 0, 0)
        indent_tab_grid_layout.addWidget(self.tabwidth_spin.spinbox, 0, 1)

        indent_tab_layout = QHBoxLayout()
        indent_tab_layout.addLayout(indent_tab_grid_layout)
        indent_tab_layout.addStretch(1)

        indentation_layout = QVBoxLayout()
        indentation_layout.addLayout(indent_tab_layout)
        indentation_layout.addWidget(self.indent_char_box)
        indentation_layout.addWidget(ibackspace_box)
        indentation_layout.addWidget(tab_mode_box)
        indentation_group.setLayout(indentation_layout)

        # -- EOL group
        eol_group = QGroupBox(_("End-of-line characters"))
        fix_eol_box = newcb(
            _("Normalize mixed end-of-line characters"),
            'check_eol_chars',
            default=True,
            tip=_(
                "Normalizes mixed end-of-line characters to system EOL when "
                "opening a file. Recommended for Windows, as mixed characters "
                "can cause syntax errors in the console."
            ),
        )
        convert_eol_on_save_box = newcb(
            _("Convert end-of-line characters on save to:"),
            'convert_eol_on_save',
            default=False,
        )
        eol_combo_choices = (
            (_("LF (Linux/macOS)"), 'LF'),
            (_("CRLF (Windows)"), 'CRLF'),
            (_("CR (legacy Mac)"), 'CR'),
        )
        convert_eol_on_save_combo = self.create_combobox(
            "",
            eol_combo_choices,
            'convert_eol_on_save_to',
        )

        convert_eol_on_save_box.checkbox.toggled.connect(
            convert_eol_on_save_combo.setEnabled
        )
        convert_eol_on_save_combo.setEnabled(
            self.get_option('convert_eol_on_save')
        )

        eol_on_save_layout = QHBoxLayout()
        eol_on_save_layout.addWidget(convert_eol_on_save_box)
        eol_on_save_layout.addWidget(convert_eol_on_save_combo)

        eol_layout = QVBoxLayout()
        eol_layout.addWidget(fix_eol_box)
        eol_layout.addLayout(eol_on_save_layout)
        eol_group.setLayout(eol_layout)

        # ---- Advanced tab
        # -- Template group
        template_group = QGroupBox(_("Template"))
        template_button = self.create_button(
            text=_("Edit new file template"),
            callback=self.plugin.edit_template,
            set_modified_on_click=True,
        )

        template_layout = QVBoxLayout()
        template_layout.addSpacing(3)
        template_layout.addWidget(template_button)
        template_group.setLayout(template_layout)

        # -- Autosave group
        autosave_group = QGroupBox(_("Autosave"))
        autosave_checkbox = newcb(
            _("Save a backup copy of unsaved files"),
            "autosave_enabled",
            tip=_(
                "Periodically saves a copy of unsaved files. If Spyder closes "
                "unexpectedly, you can recover your work on the next launch."
            ),
        )
        autosave_spinbox = self.create_spinbox(
            _("Autosave interval (s):"),
            None,
            'autosave_interval',
            min_=1,
            max_=3600,
        )

        autosave_checkbox.checkbox.toggled.connect(autosave_spinbox.setEnabled)

        autosave_layout = QVBoxLayout()
        autosave_layout.addWidget(autosave_checkbox)
        autosave_layout.addWidget(autosave_spinbox)
        autosave_group.setLayout(autosave_layout)

        # -- Docstring group
        docstring_group = QGroupBox(_("Docstring style"))
        numpy_url = "<a href='{}'>NumPy</a>".format(NUMPYDOC)
        googledoc_url = "<a href='{}'>Google</a>".format(GOOGLEDOC)
        sphinx_url = "<a href='{}'>Sphinx</a>".format(SPHINXDOC)
        docstring_label = QLabel(
            _(
                "Spyder can generate a docstring when you press "
                "<kbd>{shortcut}</kbd> after a function, method, or class "
                "declaration. The {numpy}, {google}, and {sphinx} style are "
                "available."
            ).format(
                numpy=numpy_url,
                google=googledoc_url,
                sphinx=sphinx_url,
                shortcut=DOCSTRING_SHORTCUT,
            ),
        )
        docstring_label.setOpenExternalLinks(True)
        docstring_label.setWordWrap(True)
        docstring_combo_choices = (
            ("NumPy", 'Numpydoc'),
            ("Google", 'Googledoc'),
            ("Sphinx", 'Sphinxdoc'),
        )
        docstring_combo = self.create_combobox(
            _("Style:"),
            docstring_combo_choices,
            'docstring_type',
        )

        docstring_layout = QVBoxLayout()
        docstring_layout.addWidget(docstring_label)
        docstring_layout.addWidget(docstring_combo)
        docstring_group.setLayout(docstring_layout)

        # -- Multi-cursor group
        multicursor_group = QGroupBox(_("Multi-cursor"))
        multicursor_box = newcb(
            _("Enable multi-cursor support"),
            'multicursor_support',
            tip=_(
                "Lets you add extra cursors, or column of cursors, "
                "for simultaneous editing"
            ),
        )

        multicursor_layout = QVBoxLayout()
        multicursor_layout.addWidget(multicursor_box)
        multicursor_group.setLayout(multicursor_layout)

        # -- Multi-cursor paste group
        multicursor_paste_group = QGroupBox(_("Multi-cursor paste behavior"))
        multicursor_paste_bg = QButtonGroup(multicursor_paste_group)
        entire_clip_radio = self.create_radiobutton(
            _("Paste the entire clipboard at each cursor"),
            "multicursor_paste/always_full",
            button_group=multicursor_paste_bg,
        )
        conditional_spread_radio = self.create_radiobutton(
            _("Paste one line per cursor when possible"),
            "multicursor_paste/conditional_spread",
            tip=_(
                "When the lines and cursors counts match, "
                "pastes one line per cursor; otherwise, pastes the entire "
                "clipboard at each cursor"
            ),
            button_group=multicursor_paste_bg,
        )
        always_spread_radio = self.create_radiobutton(
            _("Always paste one line per cursor"),
            "multicursor_paste/always_spread",
            tip=_(
                "Pastes one line per cursor even if the line and cursor "
                "counts differ. Extra lines are dropped; extra cursors "
                "receive nothing."
            ),
            button_group=multicursor_paste_bg,
        )

        multicursor_box.checkbox.toggled.connect(
            multicursor_paste_group.setEnabled
        )
        multicursor_paste_group.setEnabled(
            self.get_option("multicursor_support")
        )

        multicursor_paste_layout = QVBoxLayout()
        multicursor_paste_layout.addWidget(entire_clip_radio)
        multicursor_paste_layout.addWidget(conditional_spread_radio)
        multicursor_paste_layout.addWidget(always_spread_radio)
        multicursor_paste_group.setLayout(multicursor_paste_layout)

        # -- Mouse shortcuts group
        mouse_shortcuts_group = QGroupBox(_("Mouse shortcuts"))
        mouse_shortcuts_button = self.create_button(
            lambda: MouseShortcutEditor(self).exec_(),
            _("Edit modifiers…"),
        )

        mouse_shortcuts_layout = QVBoxLayout()
        mouse_shortcuts_layout.addWidget(mouse_shortcuts_button)
        mouse_shortcuts_group.setLayout(mouse_shortcuts_layout)

        # --- Tabs ---
        self.create_tab(
            _("Display"),
            [
                interface_group,
                helpers_group,
                highlight_group,
            ],
        )

        self.create_tab(
            _("Source code"),
            [
                automatic_group,
                whitespace_group,
                indentation_group,
                eol_group,
            ],
        )

        self.create_tab(
            _("Advanced"),
            [
                template_group,
                autosave_group,
                docstring_group,
                multicursor_group,
                multicursor_paste_group,
                mouse_shortcuts_group,
            ],
        )

    @on_conf_change(
        option=('provider_configuration', 'lsp', 'values', 'format_on_save'),
        section='completions',
    )
    def on_format_save_state(self, value):
        """
        Change options following the `format_on_save` completion option.

        Parameters
        ----------
        value : bool
            If the completion `format_on_save` option is enabled or disabled.

        Returns
        -------
        None.

        """
        options = [
            self.removetrail_box,
            self.add_newline_box,
            self.remove_trail_newline_box,
        ]
        for option in options:
            if option:
                if value:
                    option.setToolTip(
                        _(
                            "This option is disabled since the "
                            "<i>Autoformat files on save</i> option is active."
                        )
                    )
                else:
                    option.setToolTip("")
                option.setDisabled(value)

    def set_indent_chars(self):
        """Set the indent_chars config option per the two sub-options."""
        if (
            "tab_stop_width_spaces" not in self.changed_options
            and "indent_with_spaces" not in self.changed_options
        ):
            return

        indent_tab = not self.indent_char_box.checkbox.isChecked()
        indent_width = (
            1 if indent_tab else int(self.tabwidth_spin.spinbox.value())
        )
        indent_char = "\t" if indent_tab else " "
        indent_chars = "*{}*".format(indent_char * indent_width)

        self.set_option("indent_chars", indent_chars)
