from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdk
from .base import PageMixin


class ExportWindow(Gtk.Box, PageMixin):
    def __init__(self, system, window, **kwargs):
        super().__init__(**kwargs)
        
        self.system = system
        self.window = window
        self.elements = list()
        self.export_list = list()
        self.current_selected_row = None
        
        self.vbox_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, width_request=400)   
        self.vbox_middle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, width_request=70, valign=Gtk.Align.CENTER)   
        self.vbox_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, width_request=400)
    
        self.set_vexpand(True)
        self.set_margin_top(5)
        self.set_margin_end(5)
        self.set_margin_start(5)
        self.set_margin_bottom(5)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        
        self.append(self.vbox_left)
        self.append(self.vbox_middle)
        self.append(self.vbox_right)
        
        self.vbox_left.set_homogeneous(True)
        self.vbox_right.set_homogeneous(True)

        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b".squared {border-radius: 0;}")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        
        self.elements.append(self.system)
        
        # ----------------------- Sytem box --------------------- #
        
        self.system_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=10, margin_top=10, margin_end=10, margin_bottom=10)
        self.system_listbox = Gtk.ListBox()
        self.system_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.system_box.append(self.system_listbox)
        
        self.system_frame = Gtk.Frame(margin_start=5, margin_top=5, margin_end=5, margin_bottom=5, halign=Gtk.Align.FILL)
        self.system_frame.set_child(self.system_box)
        self.system_frame.get_style_context().add_class("squared")
        
        self.vbox_left.append(self.system_frame)
        
        self.system_listbox = Gtk.ListBox()
        self.system_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.system_expander = Gtk.Expander(label=self.system.name, margin_start=4)
        self.system_listbox.append(self.system_expander)
        
        # ------------------ Buttons box --------------------- #
        
        right_arrow = Gio.ThemedIcon.new("big_right_arrow")
        right_arrow_renderer = Gtk.Image.new_from_gicon(right_arrow)
        right_arrow_renderer.set_pixel_size(32)
        
        left_arrow = Gio.ThemedIcon.new("big_left_arrow")
        left_arrow_renderer = Gtk.Image.new_from_gicon(left_arrow)
        left_arrow_renderer.set_pixel_size(32)
        
        self.right_button = Gtk.Button()
        self.right_button.set_child(right_arrow_renderer)
        self.left_button = Gtk.Button()
        self.left_button.set_child(left_arrow_renderer)

        self.right_button.set_has_frame(False)
        self.left_button.set_has_frame(False)
        
        self.right_button.connect("clicked", self.on_export_right_button)
        self.left_button.connect("clicked", self.on_export_left_button)
        
        self.vbox_middle.append(self.right_button)
        self.vbox_middle.append(self.left_button)
        
        # ------------------- Export box --------------------- #
        
        self.export_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=5, margin_top=5, margin_end=5, margin_bottom=5)
        self.export_listbox = Gtk.ListBox(height_request=600)
        self.export_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.export_box.append(self.export_listbox)
        self.export_path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.selected_path_btn = Gtk.Button(icon_name='directory', has_frame=False)
        self.selected_path_btn.connect("clicked", self.on_choose_button_clicked)
        self.export_path_box.append(self.selected_path_btn)
        self.export_box.append(self.export_path_box)
        self.path_buffer = Gtk.EntryBuffer(text="")
        self.selected_path_text = Gtk.Entry(placeholder_text="No path selected", hexpand=True)
        self.export_path_box.append(self.selected_path_text)
        self.export_btn = Gtk.Button(label="EXPORT", margin_top=8)
        self.export_btn.connect("clicked", self.on_export_button)
        self.export_box.append(self.export_btn)
        

        self.export_frame = Gtk.Frame(margin_start=5, margin_top=5, margin_end=5, margin_bottom=5, halign=Gtk.Align.FILL)
        self.export_frame.set_child(self.export_box)
        self.export_frame.get_style_context().add_class("squared")

        self.vbox_right.append(self.export_frame)
        
        self.system_listbox.connect("row-selected", self.on_row_selected)
        
        self.build_system_list()
        
    def build_system_list(self):
        self.app_listbox = Gtk.ListBox()
        self.app_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.app_listbox.connect("row-selected", self.on_row_selected)
        self.system_expander.set_child(self.app_listbox)
        self.system_box.append(self.system_listbox)
        for app in self.system.applications:
            if app.subapp_network.function_blocks:
                self.elements.append(app)
                app_expander = Gtk.Expander(label=app.name)
                fb_listbox = Gtk.ListBox()
                fb_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
                fb_listbox.connect("row-selected", self.on_row_selected)
                app_expander.set_child(fb_listbox)
                self.app_listbox.append(app_expander)
                for fb in app.subapp_network.function_blocks:
                    self.elements.append(fb)
                    self.add_row(fb_listbox, fb.name, 10)
            else:
                self.elements.append(app)
                self.add_row(self.app_listbox, app.name)
        for dev in self.system.devices:
            if dev.resources:
                self.elements.append(dev)
                dev_expander = Gtk.Expander(label=dev.name)
                device_listbox = Gtk.ListBox()
                device_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
                device_listbox.connect("row-selected", self.on_row_selected)
                dev_expander.set_child(device_listbox)
                self.app_listbox.append(dev_expander)
                for res in dev.resources:
                    self.elements.append(res)
                    self.add_row(device_listbox, res.name)
            else:
                self.elements.append(dev)
                self.add_row(self.app_listbox, dev.name)

    def build_fb_list(self):
        pass
                    
    def on_row_selected(self, listbox, row):
        if row is not None:
            self.current_selected_row = row.get_child().get_label()
    
    def add_row(self, listbox, label, margin=0):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=label, halign=Gtk.Align.START, margin_start=20+margin)
        row.set_child(label)
        listbox.append(row)
        return row
        
    def on_choose_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Choose Directory",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.set_transient_for(self.window)
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK
        )
        dialog.connect("response", self.on_file_dialog_response)
        dialog.show()

    def on_file_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            selected_folder = dialog.get_file().get_path()
            self.update_selected_path(selected_folder)
        dialog.destroy()

    def update_selected_path(self, new_path):
        self.path_buffer.set_text(new_path, len(new_path))
        self.selected_path_text.set_buffer(self.path_buffer)
        
    def on_export_right_button(self, widget):
        self.add_row(self.export_listbox, self.current_selected_row, -5)
        self.export_list.append(self.current_selected_row)
        
    def on_export_left_button(self, widget):
       row = self.export_listbox.get_selected_row()
       self.export_listbox.remove(row)
       self.export_list.remove(self.current_selected_row)
       
    def on_export_button(self, widget):
        path = self.path_buffer.get_text()
        for element in self.export_list:
            for elem in self.elements:
                if elem.name == element:
                    elem.save(path)


