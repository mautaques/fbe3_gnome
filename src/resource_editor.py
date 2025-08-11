from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdk
from .base import PageMixin
from .fb_editor import FunctionBlockEditor
from .system_renderer import SystemRenderer

import gi
import math
import cairo

class ResourceEditor(PageMixin, Gtk.Box):
    def __init__(self, system, project, current_tool=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.system = system
        self.project = project
        self.current_tool = current_tool
    
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

        self.gesture_press.connect("pressed", self.button_press)
        self.gesture_release.connect("released", self.button_release)
        self.event_controller.connect("motion", self.motion_notify)
        self.system_render.add_controller(self.gesture_press)
        self.system_render.add_controller(self.gesture_release)
        self.system_render.add_controller(self.event_controller)
        
        self.system_render.set_draw_func(self.on_draw, None)

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
            self.system.device_remove(device)
                
        elif tool == 'inspect':
            resource = self.system_render.get_resource_at(x, y)
            if resource is not None:

                self.system_render.queue_draw()

    def button_release(self, e, data, x, y):
        window = self.get_ancestor_window()
        tool_name = window.get_selected_tool()

        if tool_name == 'move':
            self.update_scrolled_window()
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
