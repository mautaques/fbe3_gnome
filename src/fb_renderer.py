from gi.repository import Gtk
import sys
import gi
import os
import math
import cairo
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

class FunctionBlockRenderer(Gtk.DrawingArea):

    def __init__(self, fb_diagram, inspected_block, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fb_diagram = fb_diagram
        self.inspected_block = inspected_block
        self.selected_connection = None
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
            
        # for i in range(0, width, grid_size):
        #     for j in range(0, height, dot_spacing*2):
        #         cr.rectangle(i, j, dot_spacing, dot_spacing)
        #         cr.fill()

        # for j in range(0, height, grid_size):
        #     for i in range(0, width, dot_spacing*2):
        #         cr.rectangle(i, j, dot_spacing, dot_spacing)
        #         cr.fill()
        
        cr.set_dash((), 0.0)

    def draw_function_block(self, cr, wid, fb, gain):
        if self.inspected_block is not None:
            max_x, _ = self.fb_diagram.find_max_cord()
            pos_x = 40.0
            pos_y = 40.0
            count_pos = 0.0
            for event in self.inspected_block.events:
                if event.is_input:
                    count_pos += 20.0
                    # print("Name = " + event.name + "\npos_x = " +
                    # str(pos_x) + "\npos_y = " + str(pos_y+count_pos))
                    self.write_txt(wid, cr, event.name, pos_x, pos_y+count_pos,
                                   1, 0, font_size=14, font_family='sans')
                    event.x = pos_x+(len(event.name)+2)*5.5
                    event.y = pos_y+count_pos-4
            for var in self.inspected_block.variables:
                if var.is_input:
                    count_pos += 20.0
                    # print("Name = " + var.name + "\npos_x = " +
                    # str(pos_x) + "\npos_y = " + str(pos_y+count_pos))
                    self.write_txt(wid, cr, var.name, pos_x, pos_y+count_pos,
                                   0, 1, font_size=14, font_family='sans')
                    var.x = pos_x+(len(var.name)+2)*5.5
                    var.y = pos_y+count_pos-4
            pos_x = max_x + 250
            pos_y = 40.0
            count_pos = 0.0
            for event in self.inspected_block.events:
                if not event.is_input:
                    count_pos += 20.0
                    # print("Name = " + event.name + "\npos_x = "
                    #       + str(pos_x) + "\npos_y = " + str(pos_y+count_pos))
                    self.write_txt(wid, cr, event.name, pos_x, pos_y+count_pos,
                                   1, 0, font_size=14, font_family='sans')
                    event.x = pos_x-(len(event.name)+2)*5.5
                    event.y = pos_y+count_pos-4
            for var in self.inspected_block.variables:
                if not var.is_input:
                    count_pos += 20.0
                    # print("Name = " + var.name + "\npos_x = " +
                    #       str(pos_x) + "\npos_y = " + str(pos_y+count_pos))
                    self.write_txt(wid, cr, var.name, pos_x, pos_y+count_pos,
                                   0, 1, font_size=14, font_family='sans')
                    var.x = pos_x-(len(var.name)+2)*4
                    var.y = pos_y+count_pos-4

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2.3)
        i_pos_x = fb.x
        i_pos_y = fb.y
        # print("FB = " + fb.name + "\nX = " + str(i_pos_x)
        #       + "\nY = " + str(i_pos_y))

        h_length, t_vlength, b_vlength = self.get_measurements(fb, gain)
        b_neck_width = h_length/6
        b_neck_height = t_vlength/2

        cr.move_to(i_pos_x, i_pos_y)
        cr.line_to(i_pos_x, i_pos_y + t_vlength)
        cr.line_to(i_pos_x + b_neck_width, i_pos_y + t_vlength)
        cr.line_to(i_pos_x + b_neck_width, i_pos_y +
                   t_vlength + b_neck_height)
        cr.line_to(i_pos_x, i_pos_y + t_vlength + b_neck_height)
        cr.line_to(i_pos_x, i_pos_y + t_vlength +
                   b_neck_height + b_vlength)
        cr.line_to(i_pos_x + h_length, i_pos_y + t_vlength +
                   b_neck_height + b_vlength)
        cr.line_to(i_pos_x + h_length, i_pos_y + t_vlength + b_neck_height)
        cr.line_to(i_pos_x + h_length - b_neck_width, i_pos_y +
                   t_vlength + b_neck_height)
        cr.line_to(i_pos_x + h_length - b_neck_width, i_pos_y + t_vlength)
        cr.line_to(i_pos_x + h_length, i_pos_y + t_vlength)
        cr.line_to(i_pos_x + h_length, i_pos_y)
        cr.line_to(i_pos_x, i_pos_y)
        cr.stroke()

        print(fb.get_category() + fb.type)
        self.write_txt(wid, cr, fb.name,
                       i_pos_x + h_length/2 - (8.3*len(fb.name))/2, i_pos_y - 4,
                       font_family='sans', font_weight=cairo.FONT_WEIGHT_BOLD)
        self.write_txt(wid, cr, fb.get_category() + fb.type,
                       i_pos_x + h_length/2 - (7*(len(fb.type) + len(fb.get_category()))/2),
                       gain/2 + i_pos_y+t_vlength+b_neck_height,
                       font_family='sans', font_slant=cairo.FONT_SLANT_ITALIC)

        i = 0
        j = 0
        for event in fb.events:

            if event.is_selected:
                fst_selected = 1
            else:
                fst_selected = 0
            if event.active:
                snd_selected = 1
            else:
                snd_selected = 0
            event_offset = len(event.name) + 15

            if event.is_input:
                self.write_txt(wid, cr, event.name, i_pos_x + 3,
                               13 + i_pos_y + i*gain,
                               fst_selected=fst_selected,
                               snd_selected=snd_selected)
                event.x = i_pos_x + 3
                event.y = 13 + i_pos_y + i*gain
                i = i+1
            else:
                self.write_txt(wid, cr, event.name,
                               i_pos_x + h_length - 7*len(event.name) - 3,
                               13 + i_pos_y + j*gain,
                               fst_selected=fst_selected,
                               snd_selected=snd_selected)
                event.x = i_pos_x + h_length - 7*len(event.name) - 3
                event.y = 13 + i_pos_y + j*gain
                j = j+1

        i = 0
        j = 0
        for var in fb.variables:
            if var.is_input:
                if var.is_selected:
                    fst_selected = 1
                else:
                    fst_selected = 0
                self.write_txt(wid, cr, var.name, i_pos_x + 3,
                               13 + i_pos_y + i*gain +
                               t_vlength + b_neck_height + gain,
                               fst_selected=fst_selected)
                var.x = i_pos_x + 3
                var.y = (13 + i_pos_y + i*gain +
                         t_vlength + b_neck_height + gain)
                i = i+1
                # print('var '+ var.name+' x = '+str(var.x))
            else:
                self.write_txt(wid, cr, var.name,
                               i_pos_x + h_length - 7*len(var.name) - 3,
                               13 + i_pos_y + j*gain
                               + t_vlength + b_neck_height + gain,
                               fst_selected=fst_selected)
                var.x = i_pos_x + h_length - 7*len(var.name) - 3
                var.y = (13 + i_pos_y + j*gain +
                         t_vlength + b_neck_height + gain)
                j = j+1

    def draw_connections(self, cr, wid, h, data, gain=20, is_selected=0):
        # cr.set_source_rgb(is_selected, 0, 0)
        cr.set_line_width(1.2)

        for fb in self.fb_diagram.function_blocks:
            for var in fb.variables:
                for connection in var.connections:
                    # print('Tuple('+var.name+'['+str(var.is_input)+', '+str(var.x)+', '+str(var.y)+'],'+connection.name+'['+str(connection.is_input)+', '+str(connection.x)+', '+str(connection.y)+'])')
                    # if self.selected_connection == (var, connection):
                    #     cr.set_source_rgb(1,0,0)
                    # else:
                    cr.set_source_rgb(47/255,141/255,255/255) # blue color
                    h_length, t_vlength, b_vlength = self.get_measurements(var.fb, gain=20)
                    con_offset = len(connection.name) + 15
                    cr.move_to(var.fb.x, var.y)
                    if self.inspected_block is not None and\
                        (var.fb.name == self.inspected_block.name or
                         connection.fb.name == self.inspected_block.name):
                        print('Tuple('+var.name+'['+str(var.is_input)+', '+str(var.x)+', '+str(var.y)+'],'+connection.name+'['+str(connection.is_input)+', '+str(connection.x)+', '+str(connection.y)+'])')
                        if var.x > connection.x:
                            if var.is_input:
                                cr.line_to(connection.x + con_offset + 20, var.y)
                            else:
                                cr.line_to(var.fb.x + 7*len(var.name)+h_length, var.y) # Draws line from border to white space
                            print("1")
                            print(var.fb.name)
                            print(connection.fb.name)
                            if var.y > connection.y: # Var is below the composite block's var
                                print("2")
                                if var.is_input:
                                    print("3")
                                    cr.line_to(connection.x + con_offset + 20, connection.y)
                                    cr.line_to(connection.x + con_offset - 5, connection.y)
                                    # cr.line_to(var.fb.x - 7*len(var.name), connection.y)
                                    # cr.line_to(connection.x + 7*con_offset, connection.y)
                                else:
                                    cr.line_to(var.fb.x + 7*len(var.name), b_vlength+t_vlength)
                            else:
                                if var.is_input:
                                    print("4")
                                    cr.line_to(connection.x + con_offset, connection.y)
                                    cr.line_to(connection.x + con_offset, connection.y)
                                else:
                                    print("5")
                                    cr.line_to(var.fb.x + 7*len(var.name), t_vlength+b_vlength)
                                    cr.line_to(connection.x + 7*con_offset, connection.y)

                        else:
                            if var.is_input:
                                print("6")
                            else:
                                print("7")
                                print(var.fb.name)
                                print(connection.fb.name)
                                print(connection.x)
                                print(con_offset)
                                print(connection.y)
                                cr.move_to(var.fb.x + h_length, var.y)
                                cr.line_to(connection.x - con_offset, var.y)
                                cr.line_to(connection.x - con_offset, connection.y)
                                cr.line_to(connection.x + 10, connection.y)

                    else:
                        if var.x > connection.x:
                            print("here1" + var.name)
                            cr.move_to(var.fb.x + h_length, var.y) # Moves to the border at the output variable
                            cr.line_to(len(var.name)*7 + var.fb.x + h_length, var.y) # Draws line from border to white space
                            if var.y < connection.y:
                                _, t_vlength, b_vlength = self.get_measurements(connection.fb, gain=20)
                                cr.line_to(len(var.name)*7 + var.fb.x + h_length,
                                        connection.fb.y + t_vlength + b_vlength + t_vlength/2 + gain)  # Draws line from the side to bottom of the destination block
                                cr.line_to(connection.fb.x - len(var.name)*7,
                                        connection.fb.y + t_vlength + b_vlength + t_vlength/2 + gain)
                            else:
                                print("here6" + var.name)
                                cr.line_to(len(var.name)*7 + var.fb.x + h_length,
                                        var.fb.y + t_vlength + b_vlength + t_vlength/2 + gain) # Draws line from the side to bottom of the block
                                cr.line_to(connection.fb.x - len(var.name)*7,
                                        var.fb.y + t_vlength + b_vlength + t_vlength/2 + gain) # Draws line from the bottom side of fst block to bottom side of the other

                            print("here7" + var.name)
                            cr.line_to(connection.fb.x - 7*len(var.name), connection.y) # Draws line from bottom to the side of the variable
                            cr.line_to(connection.x, connection.y) # Draws line from side to variable

                        else:
                            cr.move_to(var.fb.x + h_length, var.y)
                            cr.line_to((connection.fb.x - var.fb.x - h_length)/2 + var.fb.x + h_length, var.y) # Draws straight line/lines from one to another
                            cr.line_to((connection.fb.x- var.fb.x - h_length)/2 + var.fb.x + h_length, connection.y) # (it doesnt need to contour any fb)
                            cr.line_to(connection.fb.x, connection.y)
                            
                    cr.stroke()

            for event in fb.events:
                for connection in event.connections:
                    # if self.selected_connection == (event, connection):
                    #     cr.set_source_rgb(1,0,0)
                    # else:
                    cr.set_source_rgb(220/255, 20/255, 60/255)
                    h_length, b_vlength, t_vlength = self.get_measurements(event.fb, gain=20)
                    print('Tuple(' + event.name + '[' + str(event.is_input)
                                                + ', ' + str(event.x) + ', '
                                                + str(event.y) + '],'
                                                + connection.name + '['
                                                + str(connection.is_input)
                                                + ', ' + str(connection.x)
                                                + ', ' + str(connection.y)
                                                + '])')
                    cr.move_to(event.fb.x, event.y)
                    con_offset = len(connection.name) + 15
                    event_offset = len(event.name) + 15
                    if self.inspected_block is not None and\
                        (event.fb.name == self.inspected_block.name or
                         connection.fb.name == self.inspected_block.name):
                        if event.x > connection.x:  # fb is to the right of parent
                            print("1")
                            if event.is_input:
                                print("2")
                                cr.line_to(connection.x + con_offset + 20, event.y)  # Draws a straight line from the block to parent's x
                            else:
                                print("3")
                                cr.move_to(event.fb.x + h_length, event.y)
                                cr.line_to(event.fb.x + h_length + event_offset, event.y)  # Draws a small offset from fb's border to white space
                            print(event.fb.name)
                            print(connection.fb.name)
                            if event.y > connection.y:  # fb is to the right and below parent
                                print("4")
                                if event.is_input:
                                    print("5")
                                    cr.line_to(connection.x + con_offset + 20, connection.y)  # Draws a vertical line to parent's y
                                    cr.line_to(connection.x + con_offset - 5, connection.y)  # Draws a line connecting to parent's event
                                else:
                                    print("6")
                                    cr.line_to(event.fb.x + h_length + event_offset, event.y - t_vlength)
                                    cr.line_to(connection.x - con_offset, event.y - t_vlength)
                                    cr.line_to(connection.x - con_offset, connection.y)
                                    cr.line_to(connection.x + 10, connection.y)
                            else:  # fb is to the right and above parent
                                if event.is_input:
                                    print("7")
                                    cr.line_to(connection.x + con_offset + 20, connection.y)  # Draws
                                    cr.line_to(connection.x + con_offset - 5, connection.y)
                                else:
                                    print("8")
                                    cr.line_to(event.fb.x + event_offset, t_vlength+b_vlength)
                                    cr.line_to(connection.x + 7*con_offset, connection.y)

                        else:  # fb is to the left of parent
                            if event.is_input:
                                print("9")
                            else:
                                print("10")
                                print(event.fb.name)
                                print(connection.fb.name)
                                print(connection.x)
                                print(con_offset)
                                print(connection.y)
                                cr.move_to(event.fb.x + h_length, event.y)
                                doContour, _ = self.doContourBlock(event.x, connection.x, connection.fb)
                                if doContour:
                                    cr.line_to(event.fb.x + h_length + event_offset, event.y)
                                    cr.line_to(event.fb.x + h_length + event_offset, event.y - t_vlength)
                                    cr.line_to(connection.x - con_offset, event.y - t_vlength)
                                    cr.line_to(connection.x - con_offset, connection.y)
                                    cr.line_to(connection.x + 10, connection.y)
                                else:
                                    cr.line_to(connection.x - con_offset, event.y)
                                    cr.line_to(connection.x - con_offset, connection.y)
                                    cr.line_to(connection.x + 10, connection.y)
                    else:
                        con_offset = len(connection.name)/1.5 + 10
                        event_offset = len(event.name)/1.5 + 10
                        if event.x > connection.x:
                            cr.move_to(event.fb.x + h_length, event.y)
                            cr.line_to(event.fb.x + h_length + event_offset + con_offset/1.5, event.y)
                            if event.y > connection.y:
                                doContour, _ = self.doContourBlock(event.x, connection.x, connection.fb)
                                if doContour:
                                    cr.line_to(event.fb.x + h_length + event_offset + con_offset/1.5, event.y)
                                    _, b_vlength, t_vlength = self.get_measurements(connection.fb, gain=20)
                                    cr.line_to(event.fb.x + h_length + event_offset + con_offset/1.5, b_vlength + t_vlength + connection.fb.y + event_offset*1.5 + con_offset*1.5) # Goes down
                                    cr.line_to(connection.x - con_offset - event_offset, b_vlength + t_vlength + connection.fb.y + event_offset*1.5 + con_offset*1.5)
                                    # cr.line_to(connection.x - con_offset, connection.y)
                                    # cr.line_to(connection.fb.x, connection.y)
                                else:
                                    cr.line_to(event.fb.x + h_length + event_offset + con_offset/1.5, connection.fb.y - event_offset*1.5 - con_offset*1.5 + (connection.y-connection.fb.y) - gain) # Goes up
                                    cr.line_to(connection.fb.x - con_offset - event_offset, connection.fb.y - event_offset*1.5 - con_offset*1.5 + (connection.y-connection.fb.y) - gain)
                            else:
                                cr.line_to(event.fb.x + h_length + event_offset + con_offset/1.5, event.fb.y - event_offset*1.5 - con_offset*1.5 + (connection.y-connection.fb.y) - gain)
                                cr.line_to(connection.fb.x - con_offset - event_offset, event.fb.y - event_offset*1.5 - con_offset*1.5 + (connection.y-connection.fb.y) - gain)

                            cr.line_to(connection.fb.x - con_offset - event_offset, connection.y)
                            cr.line_to(connection.fb.x, connection.y)

                        else:
                            if event.is_input:
                                print("todo")
                            else:
                                cr.move_to(event.fb.x + h_length, event.y)
                                doContour, _ = self.doContourBlock(event.x, connection.x, connection.fb)
                                _, snd_fb_base_vlen, snd_fb_t_vlen = self.get_measurements(connection.fb, gain=20)
                                if doContour:
                                    cr.line_to(event.fb.x + h_length + event_offset, event.y)
                                    cr.line_to(event.fb.x + h_length + event_offset,
                                               snd_fb_base_vlen+snd_fb_t_vlen + connection.fb.y + snd_fb_t_vlen/2 + gain)
                                    cr.line_to(connection.x - con_offset,
                                               snd_fb_base_vlen+snd_fb_t_vlen + connection.fb.y + snd_fb_t_vlen/2 + gain)
                                    cr.line_to(connection.x - con_offset,
                                               connection.y)
                                    cr.line_to(connection.fb.x, connection.y)
                                else:
                                    cr.line_to((connection.fb.x - event.fb.x - h_length)/2 + event.fb.x + h_length, event.y)
                                    cr.line_to((connection.fb.x - event.fb.x - h_length)/2 + event.fb.x + h_length, connection.y)
                                    cr.line_to(connection.fb.x, connection.y)
                                    
                    cr.stroke()

    def draw(self, area, cr, wid, h, data):
        print(cr.get_dash())
        self.draw_grid(cr)
        # cr.set_source_rgb(1, 1, 1)
        # cr.paint()
        for fb in self.fb_diagram.function_blocks:
            self.draw_function_block(cr, wid, fb, gain=20)
        self.draw_connections(cr, wid, h, data, gain=20)


    def write_txt(self, wid, cr, name, i_pos_x, i_pos_y,
                  fst_selected=0, snd_selected=0,
                  font_size=11, font_family='Helvetica',
                  font_slant=cairo.FONT_SLANT_NORMAL,
                  font_weight=cairo.FONT_WEIGHT_NORMAL
                  ):
        cr.set_source_rgb(fst_selected, 0, snd_selected)
        cr.select_font_face(font_family, font_slant, font_weight)
        cr.set_font_size(font_size)
        cr.move_to(i_pos_x, i_pos_y)
        print(f"nome:{name}")
        cr.show_text(name)

    def get_fb_position(self, fb):
        return fb.x + self.offset_x, fb.y + self.offset_y

    def get_fb_at(self, x, y):
        for fb in self.fb_diagram.function_blocks:
            h_length, t_vlength, b_vlength = self.get_measurements(fb, gain=20)
            b_neck_height = t_vlength/2
            fb_x, fb_y = self.get_fb_position(fb)
            if (x - h_length) <= fb_x and (y - t_vlength - b_neck_height - b_vlength) <= fb_y and x >= fb_x and y >= fb_y:
                fb.is_selected = True
                return fb
            else:
                fb.is_selected = False
        return None

    def detect_fb(self, x, y):
        selected_fb = None

        for fb in self.fb_diagram.function_blocks:
            h_length, t_vlength, b_vlength = self.get_measurements(fb, gain=20)
            b_neck_height = t_vlength/2
            if (x - h_length) <= fb.x and (y - t_vlength - b_neck_height - b_vlength) <= fb.y and\
                    x >= fb.x and y >= fb.y:
                selected_fb = fb
                fb.is_selected = True
            else:
                fb.is_selected = False

        return selected_fb

    def detect_data(self, x, y):
        selected_event = None
        selected_var = None
        fb = self.detect_fb(x, y)

        if fb is not None:
            for event in fb.events:
                event_offset = len(event.name) + 15
                obj_length = event_offset + 3
                obj_height = 13
                if (x-obj_length) <= event.x and\
                    (y+obj_height) >= event.y and\
                        x >= event.x and y <= event.y:
                    selected_event = event
                    event.is_selected = True
                    # print("here")
                else:
                    event.is_selected = False
                    # print("here1")

            if selected_event is None:
                # print("here2")
                for var in fb.variables:
                    # print("here3")
                    obj_length = 7*len(var.name) + 3
                    obj_height = 13
                    if (x-obj_length) <= var.x and (y+obj_height) >= var.y and\
                        x >= var.x and y <= var.y:
                        # print("here4")
                        selected_var = var
                        var.is_selected = True
                    else:
                        # print("here5")
                        var.is_selected = False
            else: # clears selection
                # print("here6")
                for var in fb.variables:
                    var.is_selected = 0
        # print("here7")

        return selected_event, selected_var

    def detect_connection(self, x, y, z=7, gain=20):
        self.selected_connection is None
        for fb in self.fb_diagram.function_blocks:
            for event in fb.events:
                event.selected_connection = False
                for connection in event.connections:
                    connection.selected_connection = False

        for fb in self.fb_diagram.function_blocks:
            if self.selected_connection is not None:
                break
            for event in fb.events:
                for connection in event.connections:
                    event_offset = len(event.name) + 15
                    h_length,_,_ = self.get_measurements(event.fb, gain=20)
                    mid = (connection.x - event.fb.x - h_length)/2 + event.fb.x + h_length
                    if connection.x > event.x:
                        if x < mid and x > (event.fb.x+h_length):
                            if  y<(event.y + z) and y>(event.y-z):
                                self.selected_connection = (event, connection)
                                event.selected_connection = True
                                connection.selected_connection = True
                        if x<(mid+z) and x>(mid-z):
                            if event.y < connection.y:
                                if y>=event.y and y<=connection.y:
                                    self.selected_connection = (event, connection)
                                    event.selected_connection = True
                                    connection.selected_connection = True
                            else:
                                if y<=event.y and y>=connection.y:
                                    self.selected_connection = (event, connection)
                                    event.selected_connection = True
                                    connection.selected_connection = True
                        elif x>mid and x<connection.x:
                            if y>=connection.y - z and y<=connection.y + z:
                                self.selected_connection = (event, connection)
                                event.selected_connection = True
                                connection.selected_connection = True
                    else:
                        if connection.y < event.y:
                            if x > event.x and x < (14*len(event.name)+event.x):
                                if y > (event.y - z) and y < (event.y + z):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if x > (event.x + 14*len(event.name) - z) and x < (event.x + 14*len(event.name) + z):
                                if y < event.y and y > (connection.fb.y - gain):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if y > (connection.fb.y - gain - z) and y < (connection.fb.y - gain + z):
                                if x < (event.x + 14*len(event.name)) and x > (connection.x - 14*len(event.name)):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if y > (connection.fb.y - gain) and y < (connection.y):
                                if x < (connection.x - event_offset + z) and x > (connection.x - event_offset - z):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if y > (connection.y - z) and y < (connection.y + z):
                                if x > (connection.x - event_offset) and x < (connection.x):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                        else:
                            if x > event.x and x < (14*len(event.name)+event.x):
                                if y > (event.y - z) and y < (event.y + z):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if x > (event.x + 14*len(event.name) - z) and x < (event.x + 14*len(event.name) + z): ####AQUIII
                                if y < event.name.y and y > (event.fb.y - gain):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if y > (event.fb.y - gain - z) and y < (event.fb.y - gain + z):
                                if x < (event.x + 14*len(event.name)) and x > (connection.x - 14*len(event.name)):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if y > (event.fb.y - gain) and y < (connection.y):
                                if x < (connection.x - event_offset + z) and x > (connection.x - event_offset - z):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)
                            if y > (connection.y - z) and y < (connection.y + z):
                                if x > (connection.x - event_offset) and x < (connection.x):
                                    event.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (event, connection)


            if self.selected_connection != None:
                break
            for var in fb.variables:
                var.selected_connection = False
                for connection in var.connections:
                    connection.selected_connection = False
                    h_length,t_vlength,b_vlength = self.get_measurements(var.fb, gain=20)
                    mid = (connection.x - var.fb.x - h_length)/2 + var.fb.x + h_length
                    if connection.x > var.x:
                        if x<mid and x>(var.fb.x+h_length):
                            if  y<(var.y + z) and y>(var.y-z):
                                self.selected_connection = (var, connection)
                                var.selected_connection = True
                                connection.selected_connection = True
                        if x<(mid+z) and x>(mid-z):
                            if var.y < connection.y:
                                if y>=var.y and y<=connection.y:
                                    self.selected_connection = (var, connection)
                                    var.selected_connection = True
                                    connection.selected_connection = True
                            else:
                                if y<=var.y and y>=connection.y:
                                    self.selected_connection = (var, connection)
                                    var.selected_connection = True
                                    connection.selected_connection = True
                        if x>mid and x<connection.x:
                            if y>=connection.y - z and y<=connection.y + z:
                                self.selected_connection = (var, connection)
                                var.selected_connection = True
                                connection.selected_connection = True
                    else:
                        if connection.y > var.y:
                            h = b_vlength + 3/2*t_vlength
                            if x > var.x and x < (14*len(var.name)+var.x):
                                if y > (var.y - z) and y < (var.y + z):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if x > (var.x + 14*len(var.name) - z) and x < (var.x + 14*len(var.name) + z):
                                if y > var.y and y < (connection.fb.y + h  + gain):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if y > (connection.fb.y + h + gain - z) and y < (connection.fb.y +h + gain + z):
                                if x < (var.x + 14*len(var.name)) and x > (connection.x - 14*len(var.name)):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if y < (connection.fb.y + h + gain) and y > (connection.y):
                                if x < (connection.x - 7*len(var.name) + z) and x > (connection.x - 7*len(var.name) - z):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if y > (connection.y - z) and y < (connection.y + z):
                                if x > (connection.x - 7*len(var.name)) and x < (connection.x):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                        else:
                            _,t_vlength, b_vlength = self.get_measurements(var.fb, gain)
                            h = b_vlength + 3/2*t_vlength
                            if x > var.x and x < (14*len(var.name)+var.x):
                                if y > (var.y - z) and y < (var.y + z):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if x > (var.x + 14*len(var.name) - z) and x < (var.x + 14*len(var.name) + z):
                                if y > var.y and y < (var.fb.y + h + gain):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if y > (var.fb.y +h + gain - z) and y < (var.fb.y + h + gain + z):
                                if x < (var.x + 14*len(var.name)) and x > (connection.x - 14*len(var.name)):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if y < (var.fb.y + h + gain) and y > (connection.y):
                                if x < (connection.x - 7*len(var.name) + z) and x > (connection.x - 7*len(var.name) - z):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)
                            if y > (connection.y - z) and y < (connection.y + z):
                                if x > (connection.x - 7*len(var.name)) and x < (connection.x):
                                    var.selected_connection = True
                                    connection.selected_connection = True
                                    self.selected_connection = (var, connection)

    def doContourBlock(self,fst_x, snd_x, snd_fb):
        h_length,_,_ = self.get_measurements(snd_fb, gain=20)
        border_dist = fst_x - snd_x
        if border_dist >= -50 and border_dist <= h_length:
            return True, border_dist
        return False, border_dist


    def get_measurements(self, fb, gain):
        in_events = list()
        out_events = list()
        in_vars = list()
        out_vars = list()
        z = list()
        for event in fb.events:

            if event.is_input:
                in_events.append(event.name)
            else:
                out_events.append(event.name)

        for var in fb.variables:
            if var.is_input:
                in_vars.append(var.name)
            else:
                out_vars.append(var.name)

        for index, elem in enumerate(in_events):
            try:
                z.append(in_events[index]+out_events[index])
            except:
                try:
                    z.append(in_events[index])
                except:
                    z.append(out_events[index])
        if len(in_events) == 0:
            for index, elem in enumerate(out_events):
                z.append(out_events[index])
        for index, elem in enumerate(in_vars):
            try:
                z.append(in_vars[index]+out_vars[index])
            except:
                try:
                    z.append(in_vars[index])
                except:
                    z.append(out_vars[index])
        if len(in_vars) == 0:
            for index, elem in enumerate(out_vars):
                z.append(out_vars[index])
        try:
            h_length = gain*(int(math.ceil(0.2*len(max(z, key=len))))+6)
            t_vlength = gain*max(len(in_events), len(out_events))
            b_vlength = gain*(max(len(in_vars), len(out_vars))+1)
        except:
            h_length = 9*len(fb.name) + gain
            t_vlength = gain
            b_vlength = gain*2

        if h_length <= 9*len(fb.name):
            h_length = 9*len(fb.name) + gain

        return h_length, t_vlength, b_vlength


    def renderer_set_size_request(self, scrolled_allocation, margin=50):
        width, height = 0, 0
        delta_x, delta_y = 0, 0
        old_offset_x, old_offset_y = self.offset_x, self.offset_y
        self.offset_x, self.offset_y = 0, 0

        if not self.fb_diagram.function_blocks:
            return delta_x, delta_y

        x_values, y_values = zip(*[self.get_fb_position(fb) for fb in self.fb_diagram.function_blocks])
        min_x, min_y = min(x_values), min(y_values)
        max_x, max_y = max(x_values), max(y_values)

        if min_x <= margin:
            delta_x = margin - min_x - old_offset_x
            self.offset_x = margin - min_x
        if min_y <= margin:
            delta_y = margin - min_y - old_offset_y
            self.offset_y = margin - min_y

        x_values, y_values = zip(*[self.get_fb_position(fb) for fb in self.fb_diagram.function_blocks])
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

