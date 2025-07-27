# window.py
#
# Copyright 2024 Cabral
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdk
import sys
import os
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)
from .fb_editor import FunctionBlockEditor
from .project_editor import ProjectEditor
from .xmlParser import *

@Gtk.Template(resource_path='/com/lapas/Fbe/window.ui')
class FbeWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'FbeWindow'

    vpaned = Gtk.Template.Child()
    vbox_window = Gtk.Template.Child()
    labels_box = Gtk.Template.Child()
    tool_frame = Gtk.Template.Child()
    notebook = Gtk.Template.Child()
    add_fb_btn = Gtk.Template.Child()
    connect_fb_btn = Gtk.Template.Child()
    move_fb_btn = Gtk.Template.Child()
    remove_fb_btn = Gtk.Template.Child()
    edit_fb_btn = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.maximize()

        # Creation of the "new project" action
        new_file_action = Gio.SimpleAction(name="new-project")
        new_file_action.connect("activate", self.new_file_dialog)
        self.add_action(new_file_action)

        # Creation of the "open project" action
        open_action = Gio.SimpleAction(name="open-project")
        open_action.connect("activate", self.open_file_sys_dialog)
        self.add_action(open_action)

        # Creation of the "close project" action
        delete_proj_action = Gio.SimpleAction(name="close-project")
        delete_proj_action.connect("activate", self.close_project)
        self.add_action(delete_proj_action)

        # Creation of the "add type" action
        add_type_action = Gio.SimpleAction(name="add-type")
        add_type_action.connect("activate", self.add_fb_dialog)
        self.add_action(add_type_action)

        # ---------- Make tool frame's border square ---------- #
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b".squared {border-radius: 0;}")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        self.tool_frame.get_style_context().add_class("squared")
        # ---------------------------------------------------- #

        # self.menu = Gtk.PopoverMenuBar().new_from_model(self.menubar)
        # self.vbox_window.append(self.menu)
        self.selected_tool = None
        self.library = None  # Library path to load nested elements
        self.notebook.connect('create-window', self.on_notebook_create_window)
        self.notebook.connect('page-removed', self.close_project)
        self.add_fb_btn.connect('clicked', self.add_fb_dialog)
        self.edit_fb_btn.connect('clicked',self.inspect_function_block)
        self.connect_fb_btn.connect('clicked', self.connect_function_block)
        self.move_fb_btn.connect('clicked', self.move_function_block)
        self.remove_fb_btn.connect('clicked', self.remove_function_block)

        self.directory_list = Gtk.DirectoryList.new(
            attributes=Gio.FILE_ATTRIBUTE_STANDARD_NAME)

        self.vbox_separator = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=5)
        
        # Create a GtkSingleSelection model
        self.selection_model = Gtk.SingleSelection.new(self.directory_list)

        if self.selection_model.get_autoselect():
            self.selection_model.set_autoselect(False)

        # Create a ListView to display the files
        self.list_view = Gtk.ListView.new(model=self.selection_model, factory=self.create_list_factory())

        # Create a GestureClick to add fb from the imported library
        self.gesture_press = Gtk.GestureClick.new()

        self.scrolled_window = Gtk.ScrolledWindow(margin_top=5)
        self.scrolled_window.set_child(self.list_view)
        self.scrolled_window.set_min_content_width(190)
        self.scrolled_window.set_vexpand(True)
        
        self.vbox_expander = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.library_expander = Gtk.Expander(margin_top=10, margin_start=5, expanded=True)
        self.library_expander.set_label("Imported library")
        self.library_expander.set_child(self.scrolled_window)
        self.library_expander.set_vexpand(True)

        self.choose_button = Gtk.Button(label="Load library")
        self.choose_button.connect("clicked", self.on_choose_button_clicked)

        self.refresh_button = Gtk.Button(label="Refresh library")
        self.refresh_button.connect("clicked", self.on_refresh_button_clicked)

        self.vpaned.set_end_child(self.vbox_separator)
        self.vbox_separator.append(self.vbox_expander)
        self.vbox_separator.append(self.choose_button)      
        self.vbox_separator.append(self.refresh_button)
        self.vbox_expander.append(self.library_expander)

        self.gesture_press.connect("pressed", self.on_add_library_fb)
        self.list_view.add_controller(self.gesture_press)

        self.library = "/home/taques/fbe3_gnome/src/models/fb_library/"
        self.actual_folder = None

    def create_list_factory(self):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_factory_setup)
        factory.connect("bind", self.on_factory_bind)
        return factory

    # ------------------ Load Library Methods ---------------------
    def load_files(self, directory):
        directory = Gio.File.new_for_path(directory)
        self.directory_list.set_file(directory)

    def on_choose_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Choose Directory",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.set_transient_for(self)
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK
        )
        dialog.connect("response", self.on_file_dialog_response)
        dialog.show()

    def on_file_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            selected_folder = dialog.get_file().get_path()
            self.actual_folder = selected_folder
            self.load_files(selected_folder)
            self.imported_library = True
        dialog.destroy()

    # Method to refresh the library
    def on_refresh_button_clicked(self, widget):
        if self.actual_folder:
            self.load_files(self.actual_folder)
        else:
            print("No imported folder")

    # --Methods to setup the Gtk.SignalListItemFactory--
    def on_factory_setup(self, factory, list_item):
        label = Gtk.Label()
        list_item.set_child(label)

    def on_factory_bind(self, factory, list_item):
        file_info = list_item.get_item()
        label = list_item.get_child()
        if file_info:
            return label.set_text(file_info.get_name())
    # --------------------------------------------------

    # Method to create a project
    def new_file_dialog(self, action, param=None):
        self.notebook.set_visible(True)
        self.labels_box.set_visible(False)
        system = System(name='Untitled')
        system.application_create()
        window = self.get_ancestor(Gtk.Window)
        fb_project = ProjectEditor(window, system, current_tool=self.selected_tool, library=self.library)
        self.add_tab_editor(fb_project, system.name, None)

    # --------------- Methods to open an existing project ------------
    def open_file_sys_dialog(self, action, parameter):
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filter_fbt = Gtk.FileFilter()
        filter_fbt.set_name("sys Files")
        filter_fbt.add_pattern("*.sys")
        filters.append(filter_fbt)
        native = Gtk.FileDialog()
        native.set_filters(filters)
        native.open(self, None, self.on_open_project_response)

    def get_current_tab_widget(self):
        _id = self.notebook.get_current_page()
        return self.notebook.get_nth_page(_id)

    def on_open_project_response(self, dialog, result):
        file = dialog.open_finish(result)
        file_name = file.get_path()
        current_page = self.notebook.get_current_page()
        sys_name = file_name.split("/")[-1]
        contents = file.load_contents_finish(result)

        # If the user selected a file...
        if file is not None:
            self.notebook.set_visible(True)
            self.labels_box.set_visible(False)
            window = self.get_ancestor(Gtk.Window)
            system = convert_xml_system(file_name, self.library)

            if system is None:
                if current_page < 0:
                    self.labels_box.set_visible(True)
                    toast = Adw.Toast.new(f"Unable to open: {sys_name}")
                    toast_overlay = Adw.ToastOverlay.new()
                    toast_overlay.add_toast(toast)
                    self.vbox_window.append(toast_overlay)
                else:
                    toast = Adw.Toast.new(f"Unable to open: {sys_name}")
                    toast_overlay = Adw.ToastOverlay.new()
                    toast_overlay.add_toast(toast)
                    self.vbox_window.append(toast_overlay)

            else:
                fb_project = ProjectEditor(window, system, current_tool=self.selected_tool, library=self.library)
                self.add_tab_editor(fb_project, system.name, None)

    # Method to import a resource (not yet implemented)
    def on_import_resource_response(self, type_name):
        resource = convert_xml_resource(self.library+type_name+'.res')
        return resource

    # Method to add a function block to the application
    def add_fb_dialog(self, action, param=None):
        # Create a new file selection dialog, using the "open" mode
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filter_fbt = Gtk.FileFilter()
        filter_fbt.set_name("fbt Files")
        filter_fbt.add_pattern("*.fbt")
        filters.append(filter_fbt)
        native = Gtk.FileDialog()
        native.set_filters(filters)
        native.open(self, None, self.on_add_response)

    def on_add_response(self, dialog, result):
        self.selected_tool = 'add'
        file = dialog.open_finish(result)
        file_name = file.get_path()
        toast = Adw.ToastOverlay()
        toast.set_parent(self.vbox_window)
        self.vbox_window.append(toast)
        # If the user selected a file...
        if file is not None:
            fb_choosen, _  = convert_xml_basic_fb(file_name, self.library)
            if isinstance(self.get_current_tab_widget().current_page, FunctionBlockEditor):
                fb_editor = self.get_current_tab_widget().current_page
                fb_editor.selected_fb = fb_choosen
            else:
                print('not fb editor')
                toast.add_toast(Adw.Toast(title="Must be inside application editor to add type", timeout=3))
                self.selected_tool = None

    # Method to add a function block to the application from the imported library
    def on_add_library_fb(self, gesture, n_press, x, y):
        self.selected_tool = 'add'
        toast_overlay = Adw.ToastOverlay.new()
        toast_overlay.set_parent(self.vbox_window)
        self.vbox_window.append(toast_overlay)


        selected_item_index = self.selection_model.get_selected()
        print('SELECTED_ITEM_INDEX')
        print(selected_item_index)
        print('\n')
        if selected_item_index == Gtk.INVALID_LIST_POSITION:
            toast = Adw.Toast(title="No selected item.", timeout=3)
            toast_overlay.add_toast(toast)
            return

        file_info = self.selection_model.get_selected_item()
        print('FILE_INFO')
        print(file_info)
        print('\n')
        if not file_info:
            toast = Adw.Toast(title="Cannot open the file.", timeout=3)
            toast_overlay.add_toast(toast)
            return

        file_name_short = file_info.get_name()
        print('FILE_NAME_SHORT')
        print(file_name_short)
        print('\n')

        if not self.library:
            toast = Adw.Toast(title="No library path defined.", timeout=3)
            toast_overlay.add_toast(toast)
            return

        full_file_path = os.path.join(self.library, file_name_short)
        print('FULL_FILE_PATH')
        print(full_file_path)
        print('\n')

        fb_choosen, _  = convert_xml_basic_fb(full_file_path, self.library)
        if isinstance(self.get_current_tab_widget().current_page, FunctionBlockEditor):
            fb_editor = self.get_current_tab_widget().current_page
            fb_editor.selected_fb = fb_choosen
        else:
            print('not fb editor')
            toast = Adw.Toast(title="Must be inside application editor to add type", timeout=3)
            toast_overlay.add_toast(toast)
            self.selected_tool = None


    # ---------------------- Function Blocks Tools -----------------------

    def remove_function_block(self, widget):
        self.selected_tool = 'remove'
        print("fb removed")

    def connect_function_block(self, widget):
        self.selected_tool = 'connect'
        print("connect selected")

    def move_function_block(self, widget):
        self.selected_tool = 'move'
        print('move selected')

    def inspect_function_block(self, widget):
        self.selected_tool = 'inspect'
        print('inspect selected')

    def get_selected_tool(self):
        return self.selected_tool

    # --------------------- Project Tabs Methods ----------------------------

    def on_notebook_create_window(self,notebook,widget,x,y):
        # handler for dropping outside of notebook
        new_window = self.props.application.add_window()

        new_window.move(x, y)
        new_window.show_all()
        new_window.present()
        return new_window.notebook

    def set_tab_label_color(self, widget, color = 'label-black'):
        label = self.notebook.get_tab_label(widget)
        self.add_default_css_provider(label, color)

    def add_tab_editor(self, editor, label, fb_chosen):
        already_open_in = None
        if already_open_in is None:
            self.add_tab(editor, label)
        else:
            tab_id, window = already_open_in
            window.notebook.set_current_page(tab_id)
            window.present()

    def add_tab(self, widget, title):
        notebook = self.notebook.insert_page(widget, Gtk.Label.new(title), -1)
        self.notebook.set_current_page(notebook)
        self.notebook.set_tab_detachable(widget, True)
        return notebook

    # ---------------- Methods to close a project tab ---------------

    def on_close_project_response(self, dialog, response, project_widget):
        if response == "close":
            # Close the project tab
            page_num = self.notebook.page_num(project_widget)
            self.notebook.remove_page(page_num)
            current_page = self.notebook.get_current_page()
            if current_page < 0:
                self.labels_box.set_visible(True)

    def close_project(self, action, param):
        # Delete the actual project opened in the tab
        current_page = self.notebook.get_current_page()
        if current_page < 0:
            toast = Adw.ToastOverlay()
            toast.set_parent(self.vbox_window)
            self.vbox_window.append(toast)
            toast.add_toast(Adw.Toast(title="No tabs open", timeout=3))
        else:
            # Get the widget of the current tab
            current_widget = self.notebook.get_nth_page(current_page)

            # Verify if is a project editor
            if isinstance(current_widget, ProjectEditor):
                # Create confirmation dialog
                dialog = Adw.MessageDialog(
                    transient_for=self,
                    heading="Close Project",
                    body="Are you sure you want to close this project?",
                    close_response="cancel"
                )

                dialog.add_response("cancel", "Cancel")
                dialog.add_response("close", "Close")
                dialog.set_response_appearance("close", Adw.ResponseAppearance.DESTRUCTIVE)

                dialog.connect("response", self.on_close_project_response, current_widget)
                dialog.present()

