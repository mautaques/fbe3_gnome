from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdk
from .base import PageMixin


class SystemEditor(PageMixin, Gtk.Box):
    __gtype_name__ = 'SystemEditor'
    
    
    def __init__(self, window, project, system=None, current_tool=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.system = system
        self.project = project
        self.current_tool = current_tool
        self.rgt_click_app = None  # Which application was right clicked on
        self.rgt_click_row = None
        self.window = window
        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b".squared {border-radius: 0;}")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_margin_start(5)
        self.set_margin_top(5)
        self.set_margin_end(5)
        self.set_margin_bottom(5)
        self.set_homogeneous(True)
        self.set_vexpand(True)
        self.info_vbox_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.info_vbox_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.info_vbox_left.set_homogeneous(True)
        self.info_vbox_right.set_homogeneous(True)
        self.append(self.info_vbox_left)
        self.append(self.info_vbox_right)
        
        self.sys_identification_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=10, margin_top=10, margin_end=10, margin_bottom=10)
        self.sys_version_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=10, margin_top=10, margin_end=10, margin_bottom=10)
        self.sys_config_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=10, margin_top=10, margin_end=10, margin_bottom=10)
        self.apps_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=10, margin_top=10, margin_end=10, margin_bottom=10)
      
        self.sys_iden_expander = Gtk.Expander(label="Identification", margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        self.sys_iden_expander.set_child(self.sys_identification_vbox)
        self.sys_iden_expander.set_expanded(True)
        
        self.sys_version_expander = Gtk.Expander(label="Version Info", margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        self.sys_version_expander.set_child(self.sys_version_vbox)
        self.sys_version_expander.set_expanded(True)
        
        self.sys_config_expander = Gtk.Expander(label="System Configuration", margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        self.sys_config_expander.set_child(self.sys_config_vbox)
        self.sys_config_expander.set_expanded(True)
        
        self.apps_expander = Gtk.Expander(label="Applications", margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        self.apps_expander.set_child(self.apps_vbox)
        self.apps_expander.set_expanded(True)
        
        self.apps_scrolled = Gtk.ScrolledWindow()
        self.apps_scrolled.set_child(self.apps_expander)
        
        self.sys_config_scrolled = Gtk.ScrolledWindow()
        self.sys_config_scrolled.set_child(self.sys_config_expander)
        
        self.sys_iden_frame = Gtk.Frame(margin_start=5, margin_top=5, margin_end=5, margin_bottom=5, halign=Gtk.Align.FILL)
        self.sys_iden_frame.set_child(self.sys_iden_expander)
        self.sys_iden_frame.get_style_context().add_class("squared")
        
        self.sys_version_frame = Gtk.Frame(margin_start=5, margin_top=5, margin_end=5, margin_bottom=5, halign=Gtk.Align.FILL)
        self.sys_version_frame.set_child(self.sys_version_expander)
        self.sys_version_frame.get_style_context().add_class("squared")
        
        self.sys_config_frame = Gtk.Frame(margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        self.sys_config_frame.set_child(self.sys_config_scrolled)
        self.sys_config_frame.get_style_context().add_class("squared")
        
        self.apps_frame = Gtk.Frame(margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        self.apps_frame.set_child(self.apps_scrolled)
        self.apps_frame.get_style_context().add_class("squared")
        
        self.info_vbox_left.append(self.sys_iden_frame)
        self.info_vbox_left.append(self.apps_frame)
        self.info_vbox_right.append(self.sys_version_frame)
        self.info_vbox_right.append(self.sys_config_frame)
        
        # ------------- System Identification ---------------- #
        
        self._create_entry(self.sys_identification_vbox, 'Standard: ', system.identification.standard)       
        self._create_entry(self.sys_identification_vbox, 'Classification: ', system.identification.classification)
        self._create_entry(self.sys_identification_vbox, 'Function: ', system.identification.function)
        self._create_entry(self.sys_identification_vbox, 'Type: ', system.identification.type)
        self._create_entry(self.sys_identification_vbox, 'Description: ', system.identification.description)
        
        # -------------- System Version Info ---------------- #
        
        self._create_entry(self.sys_version_vbox, 'Version: ', system.version_info.version)
        self._create_entry(self.sys_version_vbox, 'Organization: ', system.version_info.organization)
        self._create_entry(self.sys_version_vbox, 'Author: ', system.version_info.author)
        self._create_entry(self.sys_version_vbox, 'Date: ', system.version_info.date)
        self._create_entry(self.sys_version_vbox, 'Remarks: ', system.version_info.remarks)
        
        # --------------- Gesture Handling ------------------ #
        
        gesture_click_applications = Gtk.GestureClick()
        gesture_click_applications.set_button(1)  # Set to listen to left-click
        gesture_click_applications.connect("pressed", self.on_gesture_click_applications)  # Connect event handler
        
        gesture_click_sys_device = Gtk.GestureClick()
        gesture_click_sys_device.set_button(1)  # Set to listen to left-click
        gesture_click_sys_device.connect("pressed", self.on_gesture_click_device)  # Connect event handler
       
        gesture_click_sys_resource = Gtk.GestureClick()
        gesture_click_sys_resource.set_button(1)  # Set to listen to left-click
        gesture_click_sys_resource.connect("pressed", self.on_gesture_click_resource)  # Connect event handler
        
        # ------------- Applications List ---------------- #
        
        self.apps_listbox = Gtk.ListBox()
        self.apps_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.apps_vbox.append(self.apps_listbox)
        self.build_application_list()
                
        # ---------------- System Config ------------------- #
        
        self.sys_config_listbox = Gtk.ListBox()
        self.sys_config_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sys_config_vbox.append(self.sys_config_listbox)

        for dev in self.system.devices:
            if dev.resources:
                dev_expander = Gtk.Expander(label=dev.name)
                device_listbox = Gtk.ListBox()
                device_listbox.set_show_separators(True)
                device_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
                device_listbox.add_controller(gesture_click_sys_resource)
                dev_expander.set_child(device_listbox)
                self.sys_config_listbox.append(dev_expander)
                for res in dev.resources:
                    self.add_row(device_listbox, res.name)
            else:
                self.add_row(self.sys_config_listbox, dev.name)
                
                
        # -------------- Popover menu ---------------- #
        
        self._create_action('new-app', self.on_new_app)
        self._create_action('rename-app', self.on_rename_app)
        self._create_action('delete-app', self.on_delete_app)
        self.menu = Gio.Menu()
        self.menu.append('Create', 'win.new-app')
        self.menu.append('Rename', 'win.rename-app')
        self.menu.append('Delete', 'win.delete-app')
        self.popover = Gtk.PopoverMenu().new_from_model(self.menu)
        self.popover.set_parent(self.apps_expander)
        self.popover.set_has_arrow(False)
        self.popover.set_halign(Gtk.Align.START)
        self.menu_button = Gtk.MenuButton()
        self.info_vbox_left.append(self.menu_button)
        self.click_on_app = Gtk.GestureClick.new()
        self.click_on_app.connect("pressed", self.on_right_click_app)
        self.click_on_app.set_button(3)
        self.apps_expander.add_controller(self.click_on_app)
        self.menu_button.set_popover(self.popover)
        self.menu_button.set_visible(False)

        self.apps_listbox.add_controller(gesture_click_applications)  # Add to the list box
        self.sys_config_listbox.add_controller(gesture_click_sys_device)  # Add to the list box                
    
    def build_application_list(self):
        for app in self.system.applications:
            if app.subapp_network.function_blocks:
                app_expander = Gtk.Expander(label=app.name, margin_start=4)
                fb_listbox = Gtk.ListBox()
                fb_listbox.set_show_separators(True)
                fb_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
                app_expander.set_child(fb_listbox)
                self.apps_listbox.append(app_expander)
                for fb in app.subapp_network.function_blocks:
                    self.add_row(fb_listbox, fb.name, 10)
            else:
                self.add_row(self.apps_listbox, app.name)
    
    def update_application_list(self):
        self.apps_listbox.remove_all()
        self.build_application_list()

    # ------------ Methods to rename the application -----------------
    
    def app_rename_dialog(self, label):
        dialog = Gtk.Dialog(title="Rename app", transient_for=self.window, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        dialog.set_default_size(120, 80)
        dialog.set_resizable(False)
        dialog.add_button("_CANCEL", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)
        
        content_area = dialog.get_content_area()
        toast = Adw.ToastOverlay()
        toast.set_parent(self.project.vbox)
        app = self.system.application_get(label)
        buffer = Gtk.EntryBuffer(text=label)
        entry = Gtk.Entry(buffer=buffer, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        content_area.append(entry)
        #toast.set_child(entry)
        self.project.vbox.append(toast)

        # content_area = dialog.get_content_area()
        # toast = Adw.ToastOverlay()
        # toast.set_parent(content_area)
        # app = self.system.application_get(label)
        # buffer = Gtk.EntryBuffer(text=label)
        # entry = Gtk.Entry(buffer=buffer, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        # toast.set_child(entry)
        # content_area.append(toast)
        
        def destroy_dialog(parent, widget, app):
            buffer = None
            if(widget == -5):
                new_name = entry.get_buffer().get_text()
                if self.system.application_rename(app, new_name):
                    if " " in new_name:
                        toast.add_toast(Adw.Toast(title="The app's name cannot contain spaces!", timeout=3))

                    else:
                        if self.rgt_click_row is not None:
                            label = self.rgt_click_row.get_child()
                            label.set_label(new_name)
                        else:
                            label = self.apps_listbox.get_selected_row().get_child()
                            label.set_label(new_name)
                        self.project._action_append_menu(self.project.apps_submenu, app, '-app', self.project.on_application_editor)
                        self.project.update_application_menu()
                        self.rgt_click_app = None
                        self.rgt_click_row = None
                        toast.add_toast(Adw.Toast(title="Application renamed", timeout=3))
                        dialog.destroy()
                else:
                    toast.add_toast(Adw.Toast(title="There's an app with the same name already!", timeout=3))
            else:
                dialog.destroy()
            
        dialog.connect("response", destroy_dialog, app)

        dialog.show()

    def on_rename_app(self, action, param=None, app=None):
        selected_row = self.apps_listbox.get_selected_row()
        if selected_row:
            label = selected_row.get_child()
            app = self.system.application_get(label.get_label())
            self.app_rename_dialog(app.name)
        elif self.rgt_click_app is not None:
            self.app_rename_dialog(self.rgt_click_app.name)

    # ----------------------------------------------------------

    def _create_action(self, action_name, callback, *args):
        action = Gio.SimpleAction.new(action_name, None)
        if not args:
            action.connect("activate", callback)
            self.window.add_action(action)
        else:
            action.connect("activate", callback, args)
            self.window.add_action(action)  
              
    def _create_entry(self, section, entry_type, entry):
        hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        section.append(hbox)
        label = Gtk.Label(label=entry_type)
        buffer = Gtk.EntryBuffer(text=entry)
        entry = Gtk.Entry(buffer=buffer)
        entry.set_hexpand(True)
        label.set_width_chars(13)
        hbox.append(label)
        hbox.append(entry)
        
    def on_right_click_app(self, gesture, n, x, y):
        self.rgt_click_row = self.apps_listbox.get_selected_row()
        if self.rgt_click_row is not None:
            label = self.rgt_click_row.get_child().get_label()
            app = self.system.application_get(label)
            self.rgt_click_app = app
        rect = self.menu_button.get_allocation()
        rect.width = 0
        rect.height = 0
        rect.x = x
        rect.y = y
        self.popover.set_pointing_to(rect)
        self.popover.popup()
    
    def on_gesture_click_applications(self, gesture, n_press, x, y):
        if n_press == 2:
            target = gesture.get_widget().get_selected_row()
            if isinstance(target, Gtk.ListBoxRow):
                app = target.get_child()
                application = self.system.application_get(app.get_label())
                self.project.on_application_editor(None, app=application)
    
    def on_gesture_click_device(self, gesture, n_press, x, y):
        if n_press == 2: 
            target = gesture.get_widget().get_selected_row()
            if isinstance(target, Gtk.ListBoxRow):
                dev = target.get_child()
                if isinstance(dev, Gtk.Expander):
                    device = self.system.device_get(dev.get_label())
                    print(device.name)
                elif isinstance(dev, Gtk.Label):
                    device = self.system.device_get(dev.get_label())
                    print(device.name)
    
    def on_gesture_click_resource(self, gesture, n_press, x, y):
        self.sys_config_listbox.unselect_all()
        if n_press == 2:
            target = gesture.get_widget().get_selected_row()
            if isinstance(target, Gtk.ListBoxRow):
                res = target.get_child()
                while(not isinstance(target, Gtk.Expander)):
                    target = target.get_parent()
                dev = self.system.device_get(target.get_label())
                resource = dev.resource_get(res.get_label())
                print(resource.name)
    
    def on_new_app(self, action, param=None):
        toast = Adw.ToastOverlay()
        toast.set_parent(self.project.vbox)
        self.project.vbox.append(toast)
        toast.add_toast(Adw.Toast(title="Application created", timeout=1.5))
        if not self.system.applications:
            self.apps_frame.remove_controller(self.click_on_app)
            self.apps_expander.add_controller(self.click_on_app)
        app = self.system.application_create()
        row = self.add_row(self.apps_listbox, app.name)
        self.project._action_append_menu(self.project.apps_submenu, app, '-app', self.project.on_application_editor)
        self.project.update_application_menu()
        self.apps_listbox.unselect_all()
            
    def on_delete_app(self, action, param=None, app=None):
        toast = Adw.ToastOverlay()
        toast.set_parent(self.project.vbox)
        self.project.vbox.append(toast)
        selected_row = self.apps_listbox.get_selected_row()
        if selected_row:
            label = selected_row.get_child()
            app = self.system.application_get(label.get_label())
            self.rgt_click_app = None
            self.system.application_remove(app)
            self.project.update_application_menu()
            self.apps_listbox.unselect_all()
            self.apps_listbox.remove(selected_row)
            if not self.system.applications:
                self.apps_expander.remove_controller(self.click_on_app)
                self.apps_frame.add_controller(self.click_on_app)
            self.rgt_click_row = None
            toast.add_toast(Adw.Toast(title="Application deleted", timeout=1.5))
            
        elif self.rgt_click_app is not None:
            app = self.rgt_click_app
            self.rgt_click_app = None
            self.system.application_remove(app)
            self.project.update_application_menu()
            self.apps_listbox.unselect_all()
            self.apps_listbox.remove(self.rgt_click_row)
            if not self.system.applications:
                self.apps_expander.remove_controller(self.click_on_app)
                self.apps_frame.add_controller(self.click_on_app)
            self.rgt_click_row = None
            toast.add_toast(Adw.Toast(title="Application deleted", timeout=1.5))
    
    def add_row(self, listbox, label, margin=0):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=label, halign=Gtk.Align.START, margin_start=20+margin)
        row.set_child(label)
        listbox.append(row)
        return row

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

    def on_my_app(self):
        print('app')

    def on_system_config(self):
        print('config')
