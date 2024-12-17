from gi.repository import Gtk
import gi
import math
import cairo

gi.require_version('Gtk', '3.0')

class SystemRenderer(Gtk.DrawingArea):
    TEXT_GAP = 8
    
    def __init__(self, system, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system = system
        self.device_dimensions = dict()
        self.resource_positions = dict()  # Saves resource position drawn inside device
        self.resource_dimensions = dict()
        self.offset_x, self.offset_y = 0, 0
    
    def draw_grid(self, cr):
        allocation = self.get_allocation()
        width = allocation.width
        height = allocation.height

        cr.set_source_rgba(1, 1, 1, 0.1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        cr.set_source_rgba(0, 0, 0, 0.15)
        grid_size = 20
        dot_spacing = 2 
        cr.set_dash([2.5, 2.5], 0) 
        cr.set_line_width(1.0)
        grid_size = 20
        for i in range(0, width, grid_size):
            cr.move_to(i, 0)
            cr.line_to(i, height)
            cr.stroke()

        for j in range(0, height, grid_size):
            cr.move_to(0, j)
            cr.line_to(width, j)
            cr.stroke()
        
        cr.set_dash((), 0.0)
        cr.set_line_width(2.0)
        
    def maximum_radius(self, cr, device):
        max_radius_resource = 0
        max_height = 0
        _, _, width, height, _, _ = cr.text_extents(device.name)
        min_radius = self.device_txt_radius(width, height) + self.TEXT_GAP
        if min_radius > max_radius_resource:
                max_radius_resource = min_radius
        if height > max_height:
            max_height = height
        for resource in device.resources:
            _, _, width, height, _, _ = cr.text_extents(resource.name)
            min_radius_resource = self.device_txt_radius(width, height) + self.TEXT_GAP
            if min_radius_resource > max_radius_resource:
                max_radius_resource = min_radius_resource
            if height > max_height:
                max_height = height
        return max_radius_resource, max_height
        
    def write_txt(self, cr, text, x, y,
                  font_size=15, font_family='Sans',
                  font_slant=cairo.FONT_SLANT_NORMAL,
                  font_weight=cairo.FONT_WEIGHT_NORMAL
                  ):
        cr.select_font_face(font_family, font_slant, font_weight)
        cr.set_font_size(font_size)
        xbearing , ybearing, width, height, _, _ = cr.text_extents(text)
        cr.move_to(x - xbearing - width/2, y + height - ybearing/2)
        cr.show_text(text)
        cr.stroke()
        min_radius = self.device_txt_radius(width, height) + self.TEXT_GAP
        return min_radius, width, height
        
    def draw_device(self, cr, wid, device, txt_color=(0, 0, 0), rec_color=(0, 0, 0)):
        cr.set_source_rgb(*txt_color)
        device_x, device_y = self.get_device_position(device)
        radius, width, height = self.write_txt(cr, device.name, device_x, device_y)    
        resource_gap = len(device.resources)*25
        cr.set_source_rgb(*rec_color)
        cr.set_source_rgb(40/255, 180/255, 180/255)
        max_radius, max_height = self.maximum_radius(cr, device)    
        self.device_dimensions[device] = (max_radius, width, max_height, resource_gap)
        cr.rectangle(device_x - max_radius, device_y, max_radius*2, max_height*2.5+resource_gap)
        cr.fill()
        cr.stroke()
        cr.set_source_rgb(250/255, 250/255, 250/255)
        radius, width, height = self.write_txt(cr, device.name, device_x, device_y, 14, 
                                               font_weight=cairo.FONT_WEIGHT_BOLD)
        gap = 25
        for resource in device.resources:
            radius, width, height = self.write_txt(cr, resource.name, device_x, device_y+gap, 13, font_slant=cairo.FONT_SLANT_ITALIC)
            self.resource_positions[resource] = (device_x, device_y+gap)
            self.resource_dimensions[resource] = (radius, width, height)
            gap += 25
    
    def get_device_at(self, x, y):
        for device in self.system.devices:
            radius, _, height, resource_gap = self.get_device_dimensions(device)
            if x >= device.x - radius and y >= device.y and x <= device.x + radius and y <= device.y + height*2.5+resource_gap:
                return device
        return None

    def get_resource_at(self, x, y):
        for device in self.system.devices:
            for resource in device.resources:
                radius, width, height = self.get_resource_dimensions(resource)
                res_x, res_y = self.get_resource_positions(resource)
                if x >= res_x - radius and y >= res_y and x <= res_x + radius and y <= res_y + height:
                    return resource
        return None

    def draw(self, area, cr, wid, h, data):
        self.draw_grid(cr)
        for dev in self.system.devices:
            self.draw_device(cr, wid, dev, rec_color=(0/255, 0/255, 0/255))

    def get_device_dimensions(self, device):
        return self.device_dimensions[device][0], self.device_dimensions[device][1], self.device_dimensions[device][2], self.device_dimensions[device][3]  # Returns radius, width, height and resource gap 

    def get_resource_dimensions(self, resource):
        return self.resource_dimensions[resource][0], self.resource_dimensions[resource][1], self.resource_dimensions[resource][2]  # Returns radius, width and height        
    
    def get_resource_positions(self, resource):
        return self.resource_positions[resource][0], self.resource_positions[resource][1] # Returns x and y of resource inside a device        

    def get_device_position(self, device):
        return device.x + self.offset_x, device.y + self.offset_y
    
    def device_txt_radius(self, width, height):
        return math.sqrt((width/2)**2 + (height/2)**2)
            
    def renderer_set_size_request(self, scrolled_allocation, margin=50):
        width, height = 0, 0
        delta_x, delta_y = 0, 0
        old_offset_x, old_offset_y = self.offset_x, self.offset_y
        self.offset_x, self.offset_y = 0, 0

        if not self.system.devices:
            return delta_x, delta_y
        
        x_values, y_values = zip(*[self.get_device_position(device) for device in self.system.devices])
        min_x, min_y = min(x_values), min(y_values)
        max_x, max_y = max(x_values), max(y_values)

        if min_x <= margin:
            delta_x = margin - min_x - old_offset_x
            self.offset_x = margin - min_x 
        if min_y <= margin:
            delta_y = margin - min_y - old_offset_y
            self.offset_y = margin - min_y 

        x_values, y_values = zip(*[self.get_device_position(device) for device in self.system.devices])
        min_x, min_y = min(x_values), min(y_values)
        max_x, max_y = max(x_values), max(y_values)

        width = max_x + 300
        height = max_y + 300
        if scrolled_allocation.width > width:
            width = scrolled_allocation.width
        if scrolled_allocation.height > height:
            height = scrolled_allocation.height
        
        self.set_size_request(width, height)
        return delta_x, delta_y