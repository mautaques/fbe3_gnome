from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdk
from .base import PageMixin
from .system_renderer import SystemRenderer
from .fb_editor import FunctionBlockEditor
from .xmlParser import *

class SystemConfigEditor(PageMixin, Gtk.Box):
    def __init__(self, system, project, current_tool=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.system = system
        self.project = project
        self.enable_add = True
        self.current_tool = current_tool
        self.selected_device = None
        self.last_selected_device = None
        self.selected_resource = None
        
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.hpaned = Gtk.Paned(wide_handle=True)
        self.system_render = SystemRenderer(self.system)
        self.scrolled = Gtk.ScrolledWindow.new()
        self.sidebox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, valign=Gtk.Align.FILL)
        self.gesture_press = Gtk.GestureClick.new()
        self.gesture_release = Gtk.GestureClick.new()
        self.event_controller = Gtk.EventControllerMotion.new()
              
        self.append(self.hpaned)
        self.hpaned.set_vexpand(True)
        self.hpaned.set_hexpand(True)
        self.hpaned.set_start_child(self.scrolled)
        self.hpaned.set_resize_start_child(True)
        self.hpaned.set_shrink_start_child(False)
        self.hpaned.set_end_child(self.sidebox)
        self.hpaned.set_resize_end_child(False)
        self.hpaned.set_shrink_end_child(False)
        self.scrolled.set_child(self.system_render)
        self.system_render.renderer_set_size_request(self.scrolled.get_allocation())
        self.build_treeview()

        self.gesture_press.connect("pressed", self.button_press)
        self.gesture_release.connect("released", self.button_release)
        self.event_controller.connect("motion", self.motion_notify)
        self.system_render.add_controller(self.gesture_press)
        self.system_render.add_controller(self.gesture_release)
        self.system_render.add_controller(self.event_controller)
        
        self.system_render.set_draw_func(self.on_draw, None)

        # self.sidebox.add_controller(self.criar_scroll_controller())

        # self.zoom = 1.0

    def build_treeview(self):
        
        #  | -------------- Resource --------------- |
        
        self.resources_liststore = Gtk.ListStore(str, str, str, object)
        
        self.resources_treeview = Gtk.TreeView(model=self.resources_liststore)
        self.resources_treeview_selection = self.resources_treeview.get_selection()
        self.resources_treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.resources_treeview.set_enable_search(False)
        
        #  | -------------- Resource -------------- |

        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True)
        renderer_text_1.connect('edited', self.resource_text_edited)

        column_text_1 = Gtk.TreeViewColumn("Resource", renderer_text_1, text=0)
        self.resources_treeview.append_column(column_text_1)
        
        #  | ------------- Type ---------------- |
        
        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True)
        renderer_text_1.connect('edited', self.type_text_edited)

        column_text_1 = Gtk.TreeViewColumn("Type", renderer_text_1, text=1)
        self.resources_treeview.append_column(column_text_1)
        
        #  | ------------- Comment ---------------- |
        
        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True)
        renderer_text_1.connect('edited', self.comment_text_edited)

        column_text_1 = Gtk.TreeViewColumn("Comment", renderer_text_1, text=2)
        self.resources_treeview.append_column(column_text_1)
        
        # | -------------------------------------- |
                
        self.resources_treeview.set_vexpand(True)
        self.resources_treeview.set_hexpand(True)
        self.sidebox.append(self.resources_treeview)
        
        #  | ----------- BUTTONS -------------- |
        
        self.resource_add_btn = Gtk.Button(label="Add Resource")
        self.resource_add_btn.connect('clicked', self.resource_add)
        self.sidebox.append(self.resource_add_btn)
        
        self.resource_delete_btn = Gtk.Button(label="Remove Resource")
        self.resource_delete_btn.connect('clicked', self.resource_remove)
        self.sidebox.append(self.resource_delete_btn)
        
        if self.selected_device is not None:
            self.update_treeview()
    
    def update_treeview(self):
        cursor_path, cursor_focus_column = self.resources_treeview.get_cursor()
        current_device = None
        if self.selected_device is None:
            current_device = self.last_selected_device
        else:
            current_device = self.selected_device

        self.resources_liststore.clear()
        resources_rows = list()
      
        for resource in current_device.resources:
            print(resource.name)
            resources_rows.append([resource.name, resource.type, resource.comment, resource])

        resources_rows.sort(key=lambda row: row[0])

        for row in resources_rows:
            self.resources_liststore.append(row)
            
        if cursor_path:
            self.resources_treeview.set_cursor(cursor_path, cursor_focus_column, False)
            
    def resource_add(self, widget):
        if self.selected_device is None:
            self.last_selected_device._resource_add_(name="new_resource")
        else:
            self.selected_device._resource_add_(name="new_resource")
        self.update_treeview()
        self.trigger_change()

    def resource_remove(self, widget):
        _, tree_path_list = self.resources_treeview_selection.get_selected_rows()
        for tree_path in tree_path_list:
            tree_iter = self.resources_liststore.get_iter(tree_path)
            resource = self.resources_liststore.get(tree_iter, 3)[0]
            if self.selected_device is None:
                self.last_selected_device.resource_remove(resource)
            else:
                self.selected_device.resource_remove(resource)
        self.update_treeview()
        self.trigger_change()        
    
    def resource_text_edited(self, widget, path, resource_name):
        resource = self.resources_liststore[path][3]
        if self.selected_device is None:
            self.last_selected_device.resource_rename(resource, resource_name)            
        else:
            self.selected_device.resource_rename(resource, resource_name)
        self.update_treeview()
        self.trigger_change()
        
    def type_text_edited(self, widget, path, new_type):
        resource = self.resources_liststore[path][3]
        new_resource = convert_xml_resource('tqs/fbe3_gnome/src/models/fb_library/'+new_type+'.res')
        if self.selected_device is None:
            self.last_selected_device.resource_change_type(resource, new_type, new_resource)            
        else:
            self.selected_device.resource_change_type(resource, new_typem, new_resource)
        self.update_treeview()
        self.trigger_change()
        
    def comment_text_edited(self, widget, path, new_comment):
        resource = self.resources_liststore[path][3]
        if self.selected_device is None:
            self.last_selected_device.resource_change_comment(resource, new_comment)            
        else:
            self.selected_device.resource_change_comment(resource, new_comment)
        self.update_treeview()
        self.trigger_change()
    
    def on_draw(self, area, cr, wd, h, data):
        self.system_render.draw(area, cr, wd, h, data)

    def motion_notify(self, data, x, y):
        window = self.get_ancestor_window()
        tool_name = window.get_selected_tool()

        if tool_name == 'move':
            if not self.selected_device is None:
                self.selected_device.x = x-self.system_render.offset_x
                self.selected_device.y = y-self.system_render.offset_y
                self.trigger_change()
                self.update_treeview()
                self.update_scrolled_window()

    def button_press(self, e, data, x, y):
        window = self.get_ancestor_window()
        tool = window.get_selected_tool()
        print(f'TOOL {tool}')
        # device = self.system_render.get_device_at(x, y)

        if tool != 'add':
            device = self.system_render.get_device_at(x, y) 

        if tool == 'add':
            new_device = self.selected_device
            new_device.x = x
            new_device.y = y
            self.trigger_change()
            self.selected_device = None
            self.enable_add = True
            
        elif tool == 'move':
            self.selected_device = device

        elif tool == 'connect':
            print("not possible")
            
        elif tool =='remove':
            self.system._device_remove_(device)
                
        elif tool == 'inspect':
            resource = self.system_render.get_resource_at(x, y)
            if resource is not None:
                fb_editor = FunctionBlockEditor(fb_diagram=resource.fb_network, project=self.project)
                self.project.last_page = self.project.current_page
                self.project.last_page_label = self.project.current_page_label.get_label()
                self.project.current_page = fb_editor
                self.project.vpaned.set_end_child(fb_editor)
                self.project.current_page_label.set_label('Resource: ' + resource.name)
                

        self.system_render.queue_draw()

    def button_release(self, e, data, x, y):
        window = self.get_ancestor_window()
        tool_name = window.get_selected_tool()

        if tool_name == 'move':
            self.update_scrolled_window()
            self.last_selected_device = self.selected_device
            self.selected_device = None

    def trigger_change(self):
        self._changes_to_save = True
        self.system_render.queue_draw()

    def update_scrolled_window(self):
        hadj = self.scrolled.get_hadjustment()
        vadj = self.scrolled.get_vadjustment()

        delta_x, delta_y = self.system_render.renderer_set_size_request(self.scrolled.get_allocation())

        hadj.set_value(hadj.get_value() + delta_x)
        vadj.set_value(vadj.get_value() + delta_y)
        self.scrolled.set_hadjustment(hadj)
        self.scrolled.set_vadjustment(vadj)
    
    def update_scrolled_window(self):
        hadj = self.scrolled.get_hadjustment()
        vadj = self.scrolled.get_vadjustment()

        delta_x, delta_y = self.system_render.renderer_set_size_request(self.scrolled.get_allocation())

        hadj.set_value(hadj.get_value() + delta_x)
        vadj.set_value(vadj.get_value() + delta_y)
        self.scrolled.set_hadjustment(hadj)
        self.scrolled.set_vadjustment(vadj)
    '''
    def criar_scroll_controller(self):
        scroll = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll.connect("scroll", self.ao_scrollar)
        return scroll

    def ao_scrollar(self, controller, dx, dy):
        if dy < 0:
            self.zoom *= 1.1  # Zoom in
        elif dy > 0:
            self.zoom /= 1.1  # Zoom out

        # Limita o zoom
        self.zoom = max(0.1, min(self.zoom, 10))

        # Aplica o zoom (via escala no widget)
        self.label.set_scale_x(self.zoom)
        self.label.set_scale_y(self.zoom)

        return True
    '''
