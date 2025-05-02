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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # print(cur_path)

        # Creation of the "new project" action
        new_file_action = Gio.SimpleAction(name="new-project")
        new_file_action.connect("activate", self.new_file_dialog)
        self.add_action(new_file_action)

        # Creation of the "open project" action
        open_action = Gio.SimpleAction(name="open-project")
        open_action.connect("activate", self.open_file_sys_dialog)
        self.add_action(open_action)

        # Creation of the "delete project" action
        delete_proj_action = Gio.SimpleAction(name="delete-project")
        delete_proj_action.connect("activate", self.on_close_tab)
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
        self.notebook.connect('page-removed', self.on_notebook_page_removed)
        self.add_fb_btn.connect('clicked', self.add_fb_dialog)
        self.edit_fb_btn.connect('clicked',self.inspect_function_block)
        self.connect_fb_btn.connect('clicked', self.connect_function_block)
        self.move_fb_btn.connect('clicked', self.move_function_block)
        self.remove_fb_btn.connect('clicked', self.remove_function_block)

        self.directory_list = Gtk.DirectoryList.new(
            attributes=Gio.FILE_ATTRIBUTE_STANDARD_NAME,
            file=Gio.File.new_for_path(".")
        )

        self.vbox_separator = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=5)
        
        # Create a GtkSingleSelection model
        self.selection_model = Gtk.SingleSelection.new(self.directory_list)

        # Create a ListView to display the files
        self.list_view = Gtk.ListView.new(model=self.selection_model, factory=self.create_list_factory())

        self.scrolled_window = Gtk.ScrolledWindow(margin_top=5)
        self.scrolled_window.set_child(self.list_view)
        self.scrolled_window.set_min_content_width(190)
        self.scrolled_window.set_vexpand(True)
        
        self.vbox_expander = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.library_expander = Gtk.Expander(margin_top=10, margin_start=5, expanded=True)
        self.library_expander.set_label("Import library")
        self.library_expander.set_child(self.scrolled_window)
        self.library_expander.set_vexpand(True)

        self.choose_button = Gtk.Button(label="Load library")
        self.choose_button.connect("clicked", self.on_choose_button_clicked)

        self.refresh_button = Gtk.Button(label="Refresh library")
        self.refresh_button.connect("clicked", self.on_refresh_button_clicked)

        self.add_library_fb_btn = Gtk.Button(label="Add function block")
        self.add_library_fb_btn.connect("clicked", self.on_refresh_button_clicked)
        
        self.vpaned.set_end_child(self.vbox_separator)
        self.vbox_separator.append(self.vbox_expander)
        self.vbox_separator.append(self.choose_button)      
        self.vbox_separator.append(self.refresh_button)
        self.vbox_expander.append(self.library_expander)

        self.load_files()

    def create_list_factory(self):
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_factory_setup)
        factory.connect("bind", self.on_factory_bind)
        return factory

    def load_files(self, directory="Projects/fbe3_gnome/src/models/fb_library/"):
        self.library = directory
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
            self.load_files(selected_folder)
        dialog.destroy()

    def on_refresh_button_clicked(self, widget):
        self.load_files()

    def on_factory_setup(self, factory, list_item):
        label = Gtk.Label()
        list_item.set_child(label)

    def on_factory_bind(self, factory, list_item):
        file_info = list_item.get_item()
        label = list_item.get_child()
        if file_info:
            label.set_text(file_info.get_name())

    # Method to create a project
    def new_file_dialog(self, action, param=None):
        self.notebook.set_visible(True)
        self.labels_box.set_visible(False)
        system = System(name='Untitled')
        system.application_create()
        window = self.get_ancestor(Gtk.Window)
        fb_project = ProjectEditor(window, system, current_tool=self.selected_tool)
        self.add_tab_editor(fb_project, system.name, None)

    # Method to open an existing project
    def open_file_dialog(self, action, parameter):
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filter_fbt = Gtk.FileFilter()
        filter_fbt.set_name("fbt Files")
        filter_fbt.add_pattern("*.fbt")
        filters.append(filter_fbt)
        native = Gtk.FileDialog()
        native.set_filters(filters)
        native.open(self, None, self.on_open_response)
        
    def open_file_sys_dialog(self, action, parameter):
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filter_fbt = Gtk.FileFilter()
        filter_fbt.set_name("sys Files")
        filter_fbt.add_pattern("*.sys")
        filters.append(filter_fbt)
        native = Gtk.FileDialog()
        native.set_filters(filters)
        native.open(self, None, self.on_open_project_response)

    def on_open_project_response(self, dialog, result):
        file = dialog.open_finish(result)
        file_name = file.get_path()
        print(file_name)
        # If the user selected a file...
        if file is not None:
            self.notebook.set_visible(True)
            self.labels_box.set_visible(False)
            window = self.get_ancestor(Gtk.Window)
            system = convert_xml_system(file_name, self.library)
            fb_project = ProjectEditor(window, system, current_tool=self.selected_tool)
            self.add_tab_editor(fb_project, system.name, None)
    
    def on_open_response(self, dialog, result):
        file = dialog.open_finish(result)
        file_name = file.get_path()
        print(file_name)
        # If the user selected a file...
        if file is not None:
            # ... open it
            fb_choosen, _  = convert_xml_basic_fb(file_name, self.library)
            fb_diagram = Composite()
            fb_diagram.add_function_block(fb_choosen)
            self.add_tab_editor(fb_diagram, fb_choosen.name, fb_choosen)

    def on_import_resource_response(self, type_name):
        resource = convert_xml_resource(self.library+type_name+'.res')
        return resource

    def open_file(self, file):
        file.load_contents_async(None, self.open_file_complete)

    def open_file_complete(self, file, result):

        contents = file.load_contents_finish(result)
        if not contents[0]:
            path = file.peek_path()
            print(f"Unable to open {path}: {contents[1]}")
            return

        try:
            text = contents[1].decode('utf-8')
        except UnicodeError as err:
            path = file.peek_path()
            print(f"Unable to load the contents of {path}: the file is not encoded with UTF-8")
            return

    # Method to add a function block to the application from the library
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

    def on_add_library_fb(self, action, param=None):
        pass

    def on_add_response(self, dialog, result):
        self.selected_tool = 'add'
        file = dialog.open_finish(result)
        file_name = file.get_path()
        print(file_name)
        toast = Adw.ToastOverlay()
        toast.set_parent(self.vbox_window)
        self.vbox_window.append(toast)
        # If the user selected a file...
        if file is not None:
            fb_choosen,_  = convert_xml_basic_fb(file_name, self.library)
            if isinstance(self.get_current_tab_widget().current_page, FunctionBlockEditor):
                fb_editor = self.get_current_tab_widget().current_page
                fb_editor.selected_fb = fb_choosen
            else:
                print('not fb editor')
                toast.add_toast(Adw.Toast(title="Must be inside application editor to add type", timeout=3))
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

    # ---------------- Project Tabs Methods -----------------------

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

    # ------------------ Delete Project Methods ------------------------

    def remove_current_tab(self, *args):
        _id = self.notebook.get_current_page()
        self.remove_tab(_id)

    def remove_tabs(self):
        while self.notebook.get_n_pages() > 0:
            if self.remove_tab(0) == False:
                return False  # at least one tab canceled
        return True  # was able to close all tabs

    def get_current_tab_widget(self):
        _id = self.notebook.get_current_page()
        return self.notebook.get_nth_page(_id)

    def remove_tab(self, _id):
        if _id < 0:
            return False

        self.notebook.set_current_page(_id)

        widget = self.notebook.get_nth_page(_id)
        if widget.has_changes_to_save():
            result = self._popup(widget.get_tab_name())
            if result == Gtk.ResponseType.CANCEL:
                return False
            elif result == Gtk.ResponseType.APPLY:  # save
                if not widget.save():
                    if  not self._save_dialog(widget):
                        return False
        self.notebook.remove_page(_id)
        return True

    def on_notebook_page_removed(self, notebook, child, page):
        if notebook.get_n_pages() == 0:
            self.close()
        return True

    # Função chamada pela interface
    def on_close_tab(self, action, param):
        self.remove_current_tab()

    def get_selected_tool(self):
        return self.selected_tool

    # -----------------------------------------------------------------

    def on_delete_project_response(self, dialog, response, project_widget):
        if response == "delete":
            # Close the project tab
            page_num = self.notebook.page_num(project_widget)
            if page_num >= 0:
                self.notebook.remove_page(page_num)

            # Show notification
            toast = Adw.Toast.new("Project deleted successfully")
            toast_overlay = Adw.ToastOverlay.new()
            toast_overlay.add_toast(toast)
            self.vbox_window.append(toast_overlay)

    def delete_project(self, action, param):

        # Delete the actual project opened in the tab
        current_page = self.notebook.get_current_page()
        if current_page < 0:
            return  # No tabs open

        # Get the widget of the current tab
        current_widget = self.notebook.get_nth_page(current_page)

        # Verify if is a project editor
        if isinstance(current_widget, ProjectEditor):
            # Create confirmation dialog
            dialog = Adw.MessageDialog(
                transient_for=self,
                heading="Delete Project",
                body="Are you sure you want to delete this project? This action cannot be undone.",
                close_response="cancel"
            )

            dialog.add_response("cancel", "Cancel")
            dialog.add_response("delete", "Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

            dialog.connect("response", self.on_delete_project_response, current_widget)
            dialog.present()
