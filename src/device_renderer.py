from gi.repository import Gtk
import gi
import math
import cairo

gi.require_version('Gtk', '4.0')

class DeviceRenderer(Gtk.DrawingArea):
    def __init__(self, device, *args, **kwargs):
        self.device = device       
        
    def draw_device(self, cr, wid, device, txt_color=(0, 0, 0), rec_color=(0, 0, 0)):
        cr.set_source_rgb(*rec_color)
        cr.rectangle(50, 50, 20, 15)
