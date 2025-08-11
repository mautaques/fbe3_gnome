from gi.repository import Gio, Gdk, Gtk, Adw

gi.require_version('Gtk', '4.0')

class DeviceEditor(PageMixin, Gtk.Box):
    
    def __init__(self, device, current_tool=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.device = device
        self.current_tool = current_tool

