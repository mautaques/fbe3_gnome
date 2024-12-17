from gi.repository import Gtk
import gi
import math
import cairo

gi.require_version('Gtk', '3.0')

class EccRenderer(Gtk.DrawingArea):
    TEXT_GAP = 8
    ACTION_TEXT_GAP = 2
    ACTION_SPACE_GAP = 1
    ARROW_LENGTH = 7
    ARROW_MID_HEIGHT = 2.5
    def __init__(self, fb, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fb = fb
        self.ecc = self.fb.get_ecc()
        self.state_dimensions = dict()  # state_dimensions[state] = (radius, width, height) -> Dimension refers to the state name dimension
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
    
    def reset_dimensions_dict(self):        
        self.state_dimensions = dict()      
    
    def state_txt_radius(self, width, height):
        return math.sqrt((width/2)**2 + (height/2)**2)
        
    def maximum_radius(self, cr, state):
        max_radius_alg = 0
        max_radius_event = 0
        max_height = 0
        for action in state.actions:
            if action.algorithm:
                text_alg = action.algorithm.name
                _ , _, width, height, _, _ = cr.text_extents(text_alg)
                min_radius_algo = self.state_txt_radius(width, height) + self.TEXT_GAP
                if min_radius_algo > max_radius_alg:
                    max_radius_alg = min_radius_algo
                if height > max_height:
                    max_height = height
            if action.output_event:    
                text_event = action.output_event.name
                _ , _, width, height, _, _ = cr.text_extents(text_event)
                min_radius_event = self.state_txt_radius(width, height) + self.TEXT_GAP
                if min_radius_event > max_radius_event:
                    max_radius_event = min_radius_event
                if height > max_height:
                    max_height = height
        return max_radius_alg, max_radius_event, max_height
            
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
        min_radius = self.state_txt_radius(width, height) + self.TEXT_GAP
        # print(f'name[{text}] -> W:{width} H:{height} R: {min_radius}')
        return min_radius, width, height
    
    def write_action_txt(self, cr, text, x, y,
                  font_size=15, font_family='Sans',
                  font_slant=cairo.FONT_SLANT_NORMAL,
                  font_weight=cairo.FONT_WEIGHT_NORMAL
                  ):
        cr.select_font_face(font_family, font_slant, font_weight)
        cr.set_font_size(font_size)
        xbearing , ybearing, width, height, _, _ = cr.text_extents(text)
        cr.move_to(x + self.ACTION_TEXT_GAP, y - height/2 - ybearing)
        cr.show_text(text)
        cr.stroke()
        min_radius = self.state_txt_radius(width, height) + self.TEXT_GAP
        return min_radius, width, height

    def draw_state(self, cr, wid, state, txt_color=(0, 0, 0), rec_color=(0, 0, 0)):
        #state.print_state_actions()
        cr.set_source_rgb(*txt_color)
        state_x, state_y = self.get_state_position(state)
        radius, width, height = self.write_txt(cr, state.name, state_x, state_y)    
        self.state_dimensions[state] = (radius, width, height)
        cr.set_source_rgb(*rec_color)
        cr.rectangle(state_x - radius, state_y, radius*2, height*2)
        cr.stroke()
        if state.is_initial:
            cr.set_source_rgb(50/255, 130/255, 210/255)
            cr.rectangle(state_x - radius, state_y, radius*2, height*2)
            cr.fill()
            cr.set_source_rgb(255/255, 255/255, 255/255)
            radius, width, height = self.write_txt(cr, state.name, state_x, state_y, font_weight=cairo.FONT_WEIGHT_BOLD) 
            self.state_dimensions[state] = (radius, width, height)  
            cr.stroke()
        x, y = 0, 0
        if state.actions:
            cr.set_source_rgb(170/255, 190/255, 255/255)
            cr.move_to(state_x + radius, state_y + height)
            cr.rel_line_to(25, 0)
            x, y = cr.get_current_point()
            cr.stroke()
        return x, y

    def draw_action(self, cr, wid, state, action, x, y, max_radius_algo, max_radius_event, max_height, txt_color=(0, 0, 0), rec_color=(0, 0, 0)):
        # print(f'ALG = {action.algorithm.name}')
        if action.algorithm.name != '':
            cr.set_source_rgb(65/255, 146/255, 75/255)
            radius, width, height = self.write_action_txt(cr, action.algorithm.name, x, y)
            cr.set_source_rgb(135/255, 226/255, 147/255)
            cr.rectangle(x, y - max_height, max_radius_algo*2, max_height*2)
        else:
            cr.set_source_rgb(135/255, 226/255, 147/255)
            cr.rectangle(x - self.ACTION_SPACE_GAP, y - max_height - self.ACTION_SPACE_GAP, max_radius_algo*2 + self.ACTION_TEXT_GAP, max_height*2 + self.ACTION_SPACE_GAP)
            cr.fill()
        cr.stroke()
        x += max_radius_algo*2
        if action.output_event.name != '':
            cr.set_source_rgb(*txt_color)
            radius, width, height = self.write_action_txt(cr, action.output_event.name, x, y)
            cr.set_source_rgb(*rec_color)
            cr.rectangle(x, y - max_height, max_radius_event*2, max_height*2)
        else:
            cr.set_source_rgb(*rec_color)
            cr.rectangle(x - self.ACTION_SPACE_GAP, y - max_height - self.ACTION_SPACE_GAP, max_radius_event*2 + self.ACTION_TEXT_GAP, max_height*2 + self.ACTION_SPACE_GAP)
            cr.fill()
        cr.stroke()
    
    def write_condition(self, cr, x, y, condition):
        if condition == '':
            return False
        cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(14)
        xbearing , ybearing, width, height, _, _ = cr.text_extents(condition)
        radius = self.state_txt_radius(width, height) + self.TEXT_GAP
        cr.set_source_rgba(107/255, 202/255, 226/255, 7*0.1) 
        cr.rectangle(x - width/2, y + height/2, width + 4, height + 4)
        cr.fill()
        cr.stroke()
        #cr.set_source_rgb(2/255, 132/255, 130/255)
        cr.set_source_rgb(255/255, 255/255, 255/255)
        cr.move_to(x - xbearing - width/2 + 2, y + height - ybearing/2 + 1)
        cr.show_text(condition)
        cr.stroke()
        cr.set_source_rgb(2/255, 132/255, 130/255)

    def draw_connections(self, cr, wid, h, data):
        cr.set_source_rgb(2/255, 132/255, 130/255)
        cr.set_line_width(1.2)
        
        connections_left = {}
        connections_right = {}
        connections_top = {}
        connections_bottom = {}
        for source_state in self.ecc.states:
            count_right, count_left, count_bottom, count_top = 0, 0, 0, 0
            source_radius, _, source_height = self.get_state_dimensions(source_state)
            for transition in source_state.out_transitions:
                destination_state = transition.to_state
                if source_state.x < destination_state.x:
                    count_right += 1
                else:
                    count_left += 1
            for transition in source_state.in_transitions:
                destination_state = transition.from_state
                # print(f'src {source_state.name}({source_state.y}) dest {destination_state.name}({destination_state.y})')
                if source_state.y < destination_state.y:
                    count_bottom += 1
                else:
                    count_top += 1 

            connections_left[source_state] = (source_height*2/(count_left+1), source_height*2/(count_left+1)) # State height/n_sections
            connections_right[source_state] = (source_height*2/(count_right+1), source_height*2/(count_right+1))
            connections_bottom[source_state] = (source_radius*2/(count_bottom+1), source_radius*2/(count_bottom+1))
            connections_top[source_state] = (source_radius*2/(count_top+1), source_radius*2/(count_top+1))
            # print(f'GAP State[{source_state.name}] = {source_height*2}/{count_left+1}')
            # print(f'GAP State[{source_state.name}] = {source_height*2}/{count_right+1}')
            # print(f'GAP State[{source_state.name}] = {source_radius*2}/{count_bottom+1}')
            # print(f'GAP State[{source_state.name}] = {source_radius*2}/{count_top+1}')


        for transition in self.ecc.transitions:
            print(f'From state[{transition.from_state.x, transition.from_state.y}]: {transition.from_state.name}\nTo state[{transition.to_state.x, transition.to_state.y}]: {transition.to_state.name}')
            source_state, destination_state = transition.from_state, transition.to_state
            source_x, source_y = source_state.x, source_state.y
            destination_x, destination_y = destination_state.x, destination_state.y
            source_radius, source_width, source_height = self.get_state_dimensions(source_state)
            destination_radius, destination_width, destination_height = self.get_state_dimensions(destination_state)
            cr.move_to(source_x, source_y)
            if source_x < destination_x:
                # print("xs < xd")
                cr.rel_move_to(source_radius, connections_right[source_state][0])
                cr.rel_line_to(self.TEXT_GAP, 0)
                x0, y0 = cr.get_current_point()
                connections_right[source_state] = (connections_right[source_state][0] + connections_right[source_state][1], connections_right[source_state][1])
                # print(f'State[{source_state.name}] = {source_y}T {connections_right[source_state]}B')
                if source_y <= destination_y:
                    # print("ys < yd")
                    cr.line_to(destination_x - destination_radius + connections_top[destination_state][0], destination_y - self.TEXT_GAP*2)
                    x1, y1 = cr.get_current_point()
                    cr.rel_line_to(0, self.TEXT_GAP*2)
                    connections_top[destination_state] = (connections_top[destination_state][0] + connections_top[destination_state][1], connections_top[destination_state][1])
                    tip_x, tip_y = cr.get_current_point()
                    cr.stroke()
                    cr.line_to(tip_x-self.ARROW_MID_HEIGHT, tip_y-self.ARROW_LENGTH)
                    cr.line_to(tip_x+self.ARROW_MID_HEIGHT, tip_y-self.ARROW_LENGTH)
                    cr.line_to(tip_x, tip_y)
                    cr.fill()
                    cr.stroke()
                    mid_x, mid_y = (x1+x0)/2, (y1+y0)/2
                    condition = transition.convert_condition_xml()
                    self.write_condition(cr, mid_x, mid_y, condition)
                else:
                    # print("ys > yd")
                    cr.line_to(destination_x - destination_radius + connections_bottom[destination_state][0], destination_y + destination_height*2 + self.TEXT_GAP*2)
                    x1, y1 = cr.get_current_point()
                    cr.move_to(x1, y1)
                    cr.rel_line_to(0, -self.TEXT_GAP*2)
                    connections_bottom[destination_state] = (connections_bottom[destination_state][0] + connections_bottom[destination_state][1], connections_bottom[destination_state][1])
                    tip_x, tip_y = cr.get_current_point()
                    cr.stroke()
                    cr.line_to(tip_x-self.ARROW_MID_HEIGHT, tip_y+self.ARROW_LENGTH)
                    cr.line_to(tip_x+self.ARROW_MID_HEIGHT, tip_y+self.ARROW_LENGTH)
                    cr.line_to(tip_x, tip_y)
                    cr.fill()
                    cr.stroke()
                    mid_x, mid_y = (x1+x0)/2, (y1+y0)/2
                    condition = transition.convert_condition_xml()
                    self.write_condition(cr, mid_x, mid_y, condition)
            else:
                # print("xs > xd")
                cr.rel_move_to(-source_radius, connections_left[source_state][0])
                cr.rel_line_to(-self.TEXT_GAP, 0)
                x0, y0 = cr.get_current_point()
                connections_left[source_state] = (connections_left[source_state][0]  + connections_left[source_state][1], connections_left[source_state][1])
                # print(f'State[{source_state.name}] = {source_y}T {connections_left[source_state]}B')
                if source_y <= destination_y:
                    # print("ys < yd")
                    cr.line_to(destination_x - destination_radius + connections_top[destination_state][0], destination_y - self.TEXT_GAP*2)
                    x1, y1 = cr.get_current_point()
                    cr.rel_line_to(0, self.TEXT_GAP*2)
                    connections_top[destination_state] = (connections_top[destination_state][0] + connections_top[destination_state][1], connections_top[destination_state][1])
                    tip_x, tip_y = cr.get_current_point()
                    cr.stroke()
                    cr.line_to(tip_x-self.ARROW_MID_HEIGHT, tip_y-self.ARROW_LENGTH)
                    cr.line_to(tip_x+self.ARROW_MID_HEIGHT, tip_y-self.ARROW_LENGTH)
                    cr.line_to(tip_x, tip_y)
                    cr.fill()
                    cr.stroke()
                    mid_x, mid_y = (x1+x0)/2, (y1+y0)/2
                    condition = transition.convert_condition_xml()
                    self.write_condition(cr, mid_x, mid_y, condition)
                else:
                    # print("ys > yd")
                    cr.line_to(destination_x - destination_radius + connections_bottom[destination_state][0], destination_y + destination_height*2 + self.TEXT_GAP*2)
                    x1, y1 = cr.get_current_point()
                    cr.rel_line_to(0, -self.TEXT_GAP*2)
                    connections_bottom[destination_state] = (connections_bottom[destination_state][0] + connections_bottom[destination_state][1], connections_bottom[destination_state][1])
                    tip_x, tip_y = cr.get_current_point()
                    cr.stroke()
                    cr.line_to(tip_x-self.ARROW_MID_HEIGHT, tip_y+self.ARROW_LENGTH)
                    cr.line_to(tip_x+self.ARROW_MID_HEIGHT, tip_y+self.ARROW_LENGTH)
                    cr.line_to(tip_x, tip_y)
                    cr.fill()   
                    cr.stroke()
                    mid_x, mid_y = (x1+x0)/2, (y1+y0)/2
                    condition = transition.convert_condition_xml()
                    self.write_condition(cr, mid_x, mid_y, condition)
            # print(f'State L[{source_state.name}] = {connections_left[source_state]}')
            # print(f'State R[{source_state.name}] = {connections_right[source_state]}')
                    
            cr.stroke()        

    def get_state_at(self, x, y):
        for state in self.ecc.states:
            radius, _, height = self.get_state_dimensions(state)
            if x >= state.x - radius and y >= state.y and x <= state.x + radius and y <= state.y + height*2:
                return state
        return None


    def draw(self, area, cr, wid, h, data):
        self.draw_grid(cr)
        # cr.set_source_rgb(1, 1, 1)  
        # cr.paint()
        for state in self.ecc.states:
            if state.is_initial:
                x, y = self.draw_state(cr, wid, state, rec_color=(20/255, 80/255, 250/255))
            else:
                x, y = self.draw_state(cr, wid, state, txt_color=(81/255, 165/255, 186/255), rec_color=(107/255, 202/255, 226/255))
            if state.actions:
                max_radius_algo, max_radius_event, max_height = self.maximum_radius(cr, state)
                for action in state.actions:
                    self.draw_action(cr, wid, state, action, x, y, max_radius_algo, max_radius_event, max_height, txt_color=(255/255, 81/255, 81/255), rec_color=(255/255, 138/255, 128/255))
                    y += max_height*2
        self.draw_connections(cr, wid, h, data)

    def get_state_position(self, state):
        return state.x + self.offset_x, state.y + self.offset_y
    
    def get_state_dimensions(self, state):
        return self.state_dimensions[state][0], self.state_dimensions[state][1], self.state_dimensions[state][2]  # Returns radius, width and height
  
    def renderer_set_size_request(self, scrolled_allocation, margin=50):
        width, height = 0, 0
        delta_x, delta_y = 0, 0
        old_offset_x, old_offset_y = self.offset_x, self.offset_y
        self.offset_x, self.offset_y = 0, 0

        if not self.ecc.states:
            return delta_x, delta_y
        
        x_values, y_values = zip(*[self.get_state_position(state) for state in self.ecc.states])
        min_x, min_y = min(x_values), min(y_values)
        max_x, max_y = max(x_values), max(y_values)

        if min_x <= margin:
            delta_x = margin - min_x - old_offset_x
            self.offset_x = margin - min_x 
        if min_y <= margin:
            delta_y = margin - min_y - old_offset_y
            self.offset_y = margin - min_y 

        x_values, y_values = zip(*[self.get_state_position(state) for state in self.ecc.states])
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
    