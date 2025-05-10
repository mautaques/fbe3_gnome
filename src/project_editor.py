from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from .base import PageMixin
from .system_editor import SystemEditor
from .system_config_editor import SystemConfigEditor
from .fb_editor import FunctionBlockEditor
from .export import ExportWindow

@Gtk.Template(resource_path='/com/lapas/Fbe/menu.ui')
class ProjectEditor(PageMixin, Gtk.Box):
    __gtype_name__ = 'ProjectEditor'
    
    project_menu_button = Gtk.Template.Child()
    primary_menu = Gtk.Template.Child()
    sys_config_submenu = Gtk.Template.Child()
    apps_submenu = Gtk.Template.Child()
    popover_menubar = Gtk.Template.Child()
    
    def __init__(self, window, system=None, current_page=None, current_tool=None, system_editor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.window = window
        self.system = system
        self.editor_index = 0
        self.current_page = current_page 
        self.current_page_label = Gtk.Label()
        self.last_page = None
        self.last_page_label = None
        self.current_tool = current_tool
        self.system_editor = SystemEditor(self.window, self, self.system)
        self.system_configuration_editor = SystemConfigEditor(self.system, self)
        self.applications_editors = list()
        
        if current_page is None:
            self.current_page = self.system_editor  # Always open in system editor 
            self.current_page_label.set_label('System Information')
        
        self.open_menu = Gio.Menu.new()
        self.project_bar = Gtk.ActionBar(valign=Gtk.Align.START)
        self.vpaned = Gtk.Paned(wide_handle=False, orientation = Gtk.Orientation.VERTICAL)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.vpaned.set_start_child(self.project_bar)
        self.vpaned.set_resize_start_child(False)
        self.vpaned.set_end_child(self.current_page)
        self.vpaned.set_resize_end_child(True)
        self.vpaned.set_shrink_end_child(False)
        self.vbox.append(self.vpaned)
        self.vbox.set_vexpand(True)
        self.vbox.set_hexpand(True)
        self.append(self.vbox)
        
        self.project_menu_button.set_label('THIS PROJECT')
        
        self._create_action("export-project", self.on_export_project)
        # self._create_action("save-project", self.on_save_project)
        self._create_action("system-information", self.on_system_information)
        self._create_action("system-configuration", self.on_system_configuration)
        self._create_action("apps-swipe-left", self.on_apps_swipe_left)
        self._create_action("apps-swipe-right", self.on_apps_swipe_right)
        self._create_action("last-page", self.goto_last_page)
        
        self.build_application_menu()
        self.build_system_config_menu()
            
        self.project_bar.pack_start(self.project_menu_button)
        self.project_bar.pack_start(self.current_page_label)
          
    # -------------- Methods to create actions ----------------------
    def _create_action(self, action_name, callback, *args):
        action = Gio.SimpleAction.new(action_name, None)
        if not args:
            action.connect("activate", callback)
            self.window.add_action(action)
        else:
            action.connect("activate", callback, args)
            self.window.add_action(action)
    
    def _action_append_menu(self, menu, elem, suffix, callback):
        label = elem.name
        action_label = label+suffix
        self._create_action(action_label, callback, elem)
        menu.append(label, "win."+action_label)
    # ---------------------------------------------------------------

    # System configuration method
    def build_system_config_menu(self):
        for dev in self.system.devices:
            self._action_append_menu(self.sys_config_submenu, dev, '-dev', self.on_application_editor)
            # label = dev.name
            # label_action = label+"-dev"
            # self._create_action(label_action, self.on_application_editor)
            # self.sys_config_submenu.append(label, "win."+label_action)
            print('')
    
    def update_system_config_menu(self):
        self.sys_config_submenu.remove_all()
        for dev in self.system.devices:
            label = dev.name
            label_action = label+"-dev"
            self.sys_config_submenu.append(label, "win."+label_action)
            
    def build_application_menu(self):       
        for app in self.system.applications:
            self.applications_editors.append(FunctionBlockEditor(app, project=self, window=self.window))
            self._action_append_menu(self.apps_submenu, app, '-app', self.on_application_editor)
            # label = app.name
            # label_action = label+"-app"
            # self._create_action(label_action, self.on_application_editor, app)
            # self.apps_submenu.append(label, "win."+label_action) 
    
    def update_application_menu(self):
        self.applications_editors.clear()
        self.apps_submenu.remove_all()
        for app in self.system.applications:
            self.applications_editors.append(FunctionBlockEditor(app, project=self))
            label = app.name
            label_action = label+"-app"
            self.apps_submenu.append(label, "win."+label_action)
            
    def on_system_information(self, action, param=None):
        self.last_page = self.current_page
        self.last_page_label = self.current_page_label.get_label()
        self.current_page_label.set_label('System Information')
        self.current_page = self.system_editor
        self.vpaned.set_end_child(self.current_page)
        
    def on_system_configuration(self, action, param=None):
        self.last_page = self.current_page
        self.last_page_label = self.current_page_label.get_label()
        self.current_page_label.set_label('System Configuration')
        self.current_page = self.system_configuration_editor
        self.vpaned.set_end_child(self.current_page)
    
    def on_apps_swipe_left(self, action, param=None):
        if self.editor_index == 0:
            self.editor_index = len(self.applications_editors)-1
        else:
            self.editor_index -= 1
        self.last_page = self.current_page
        self.last_page_label = self.current_page_label.get_label()
        self.current_page_label.set_label(self.applications_editors[self.editor_index].app.name)
        self.current_page = self.applications_editors[self.editor_index]
        self.vpaned.set_end_child(self.current_page)
            
    def on_apps_swipe_right(self, action, param=None):
        self.editor_index += 1
        if self.editor_index == len(self.applications_editors):
            self.editor_index = 0
        self.last_page = self.current_page
        self.last_page_label = self.current_page_label.get_label()
        self.current_page_label.set_label(self.applications_editors[self.editor_index].app.name)
        self.current_page = self.applications_editors[self.editor_index]
        self.vpaned.set_end_child(self.current_page)

    def on_application_editor(self, action, param=None, app=None):
        if isinstance(app, tuple):
            app_editor = self.application_editor_get(app[0])
        else:
            app_editor = self.application_editor_get(app)
        self.last_page = self.current_page
        self.current_page_label.set_label(app_editor.app.name)
        self.current_page = app_editor
        self.vpaned.set_end_child(self.current_page)
    
    def application_editor_get(self, app):
        for editor in self.applications_editors:
            if editor.app.name == app.name:
                return editor
        return None

    def goto_last_page(self, action, param=None):
        if self.last_page is not None:
            current_page_label = self.current_page_label.get_label()
            current_page = self.current_page
            self.current_page = self.last_page
            self.current_page_label.set_label(self.last_page_label)
            self.last_page = current_page
            self.last_page_label = current_page_label
            self.vpaned.set_end_child(self.current_page)
            
    # Project exportation method
    def on_export_project(self, action, param=None):
        self.last_page = self.current_page
        self.last_page_label = self.current_page_label.get_label()
        self.current_page = ExportWindow(self.system, self.window)
        self.current_page_label.set_label("Export project")
        self.vpaned.set_end_child(self.current_page)
        
    def update_system_editor(self):
        self.system_editor.update_application_list()

    def save_file_dialog(self, action, _):
        self._native = Gtk.FileChooserNative(
            title="Save File As",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="_Save",
            cancel_label="_Cancel",
        )
        self._native.connect("response", self.on_save_response)
        self._native.show()

    def on_save_response(self, native, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.save_file(native.get_file())
        self._native = None

    def save_file(self, file):
        buffer = self.main_text_view.get_buffer()

        # Retrieve the iterator at the start of the buffer
        start = buffer.get_start_iter()
        # Retrieve the iterator at the end of the buffer
        end = buffer.get_end_iter()
        # Retrieve all the visible text between the two bounds
        text = buffer.get_text(start, end, False)

        # If there is nothing to save, return early
        if not text:
            return

        bytes = GLib.Bytes.new(text.encode('utf-8'))

        # Start the asynchronous operation to save the data into the file
        file.replace_contents_bytes_async(
            bytes,
            None,
            False,
            Gio.FileCreateFlags.NONE,
            None,
            self.save_file_complete
        )

    def save_file_complete(self, file, result):
        res = file.replace_contents_finish(result)
        info = file.query_info("standard::display-name",
                               Gio.FileQueryInfoFlags.NONE)
        if info:
            display_name = info.get_attribute_string("standard::display-name")
        else:
            display_name = file.get_basename()

        if not res:
            msg = f"Unable to save as “{display_name}”"
        else:
            msg = f"Saves as “{display_name}”"
        self.toast_overlay.add_toast(Adw.Toast(title=msg))

    def save(self, file_path_name=None):
        status = self.selected_fb.save(file_path_name)
        if status == True:
            self._changes_to_save = False
        return status

    def has_file_path_name(self):
        return self.selected_fb.get_file_path_name() is not None

    def get_tab_name(self):
        if self.selected_fb is not None:
            return self.selected_fb.get_name()
        return self

