import gi

from .function_block import FunctionBlock, ExecutionControlChart, State, Transition
from .ecc_renderer import EccRenderer
from .base import PageMixin

gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gdk, Gtk

class EccEditor(PageMixin, Gtk.Box):
    fb : FunctionBlock
    ecc : ExecutionControlChart
    selected_state : State
    selected_transition : Transition
    def __init__(self, fb, current_tool=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fb = fb
        self.ecc = fb.get_ecc()
        self.current_tool = current_tool
        self.selected_state = None
        self.selected_action = None
        self.selected_transition = None
        self.enable_add = True

        self.paned = Gtk.Paned(wide_handle=False, orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.FILL)
        self.paned_side = Gtk.Paned(wide_handle=True, orientation=Gtk.Orientation.HORIZONTAL)
        self.scrolled = Gtk.ScrolledWindow.new()
        self.ecc_render = EccRenderer(self.fb)
        self.box_bottom = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        self.box_side = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, halign=Gtk.Align.FILL)
        self.gesture_press = Gtk.GestureClick.new()
        self.gesture_release = Gtk.GestureClick.new()
        self.event_controller = Gtk.EventControllerMotion.new()
        self.box_bottom.set_homogeneous(True)
        
        self.paned_side.set_vexpand(True)
        self.paned_side.set_hexpand(True)
        self.paned_side.set_start_child(self.paned)
        self.paned_side.set_resize_start_child(True)
        self.paned_side.set_shrink_start_child(False)
        self.paned_side.set_end_child(self.box_side)
        self.paned_side.set_resize_end_child(False)
        self.paned_side.set_shrink_end_child(True)
        self.append(self.paned)
        self.append(self.paned_side)
        self.paned.set_vexpand(True)
        self.paned.set_hexpand(True)
        self.paned.set_start_child(self.scrolled)
        self.paned.set_resize_start_child(True)
        self.paned.set_shrink_start_child(False)
        self.paned.set_end_child(self.box_bottom)
        self.paned.set_resize_end_child(False)
        self.paned.set_shrink_end_child(False)
        self.scrolled.set_child(self.ecc_render)
        self.ecc_render.renderer_set_size_request(self.scrolled.get_allocation())

        self.build_bottom_treeview()
        self.build_side_treeview()
        
        self.gesture_press.connect("pressed", self.button_press)
        self.gesture_release.connect("released", self.button_release)
        self.event_controller.connect("motion", self.motion_notify)
        self.ecc_render.add_controller(self.gesture_press)
        self.ecc_render.add_controller(self.gesture_release)
        self.ecc_render.add_controller(self.event_controller)
        self.cursor_crosshair = Gdk.Cursor.new_from_name("crosshair")
        self.ecc_render.set_cursor(self.cursor_crosshair)

        self.ecc_render.set_draw_func(self.on_draw, None)
        
    def build_side_treeview(self):
        
        #  | -------------- STATE --------------- |
        
        self.states_liststore = Gtk.ListStore(str, bool, object)
        
        self.states_treeview = Gtk.TreeView(model=self.states_liststore)
        self.states_treeview_selection = self.states_treeview.get_selection()
        self.states_treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.states_treeview.set_enable_search(False)
        
        #  | -------------- State -------------- |

        state_editabletext = Gtk.CellRendererText()
        state_editabletext.set_property('editable', True)
        state_editabletext.connect('edited', self.state_text_edited)

        state_column = Gtk.TreeViewColumn('State', state_editabletext, text=0)
        self.states_treeview.append_column(state_column)
        
        #  | ------------ Initial ------------- |

        renderer_toggle_1 = Gtk.CellRendererToggle()
        # renderer_toggle_1.connect('toggled', self.events_toggle_active)
        column_toggle_1 = Gtk.TreeViewColumn('Initial', renderer_toggle_1, active=1)
        self.states_treeview.append_column(column_toggle_1)   

        #  | ---------------------------------- |    

        self.states_treeview.set_vexpand(True)
        self.states_treeview.set_hexpand(True)
        self.box_side.append(self.states_treeview)

        #  | ----------- BUTTONS -------------- |
        
        self.state_add_button = Gtk.Button(label="Add State")
        self.state_add_button.connect('clicked', self.state_add)
        self.box_side.append(self.state_add_button)
        
        self.delete_button = Gtk.Button(label="Remove State")
        self.delete_button.connect('clicked', self.state_remove)
        self.box_side.append(self.delete_button)
        
        #  | --------------- ACTION ------------- |
        
        self.actions_liststore = Gtk.ListStore(str, str, str, object)

        self.actions_treeview = Gtk.TreeView(model=self.actions_liststore)
        self.actions_treeview_selection  = self.actions_treeview.get_selection()
        self.actions_treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.actions_treeview.set_enable_search(False)

        # | ---------------- Algorithm --------------- |

        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True)
        renderer_text_1.connect('edited', self.algorithm_change)

        column_text_1 = Gtk.TreeViewColumn("Algorithm", renderer_text_1, text=0)
        self.actions_treeview.append_column(column_text_1)

        #  | -------------- Output Event ------------- |
        
        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True)
        renderer_text_1.connect('edited', self.event_output_change)

        column_text_1 = Gtk.TreeViewColumn("Output Event", renderer_text_1, text=1)
        self.actions_treeview.append_column(column_text_1)

        #  | ----------------- State --------------- |

        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True)
        renderer_text_1.connect('edited', self.state_change)

        column_text_1 = Gtk.TreeViewColumn("State", renderer_text_1, text=2)
        self.actions_treeview.append_column(column_text_1)

        #  | -------------------------------------- |
        
        self.actions_treeview.set_vexpand(True)
        self.actions_treeview.set_hexpand(True)
        self.box_side.append(self.actions_treeview)

        #  | --------------- BUTTONS -------------- |
        
        self.action_add_button = Gtk.Button(label = "Add Action")
        self.action_add_button.connect('clicked', self.action_add)
        self.box_side.append(self.action_add_button)
        
        self.action_delete_button = Gtk.Button(label = "Remove Action")
        self.action_delete_button.connect('clicked', self.action_remove)
        self.box_side.append(self.action_delete_button)
        
        #  | ------------- ALGORITHMS -------------- |

        self.algorithm_liststore = Gtk.ListStore(str, str, object)

        self.algorithm_treeview = Gtk.TreeView(model=self.algorithm_liststore)
        self.algorithm_treeview_selection  = self.algorithm_treeview.get_selection()
        self.algorithm_treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.algorithm_treeview.set_enable_search(False)

        #  | -------------- Name ----------------- |
        
        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True) 
        renderer_text_1.connect('edited', self.algorithm_name_edited)

        column_text_1 = Gtk.TreeViewColumn("Name", renderer_text_1, text=0)
        self.algorithm_treeview.append_column(column_text_1)

        #  | ---------------- Algoritm ------------- |
        
        algorithm_text = Gtk.CellRendererText()
        algorithm_text.set_property('editable', True)
        algorithm_text.connect('edited', self.algorithm_str_edited)

        column_text_3 = Gtk.TreeViewColumn("Algorithm", algorithm_text, text=1)
        self.algorithm_treeview.append_column(column_text_3)

        #  | --------------------------------------- |
        
        self.algorithm_treeview.set_vexpand(True)
        self.algorithm_treeview.set_hexpand(True)
        self.box_side.append(self.algorithm_treeview)
        
        #  | --------------- BUTTONS -------------- |

        self.add_button = Gtk.Button(label = "Add Algorithm")
        self.add_button.connect('clicked', self.algorithm_add)
        self.box_side.append(self.add_button)

        self.delete_button = Gtk.Button(label = "Remove Algorithm")
        self.delete_button.connect('clicked', self.algorithm_remove)
        self.box_side.append(self.delete_button)

        #  | --------------------------------------- |

        if self.ecc is not None:
            self.update_side_treeview()
            
    def update_side_treeview(self):
        cursor_path, cursor_focus_column = self.states_treeview.get_cursor()

        self.states_liststore.clear()
        self.actions_liststore.clear()
        self.algorithm_liststore.clear()
        states_rows = list()   
        actions_rows = list()
        algorithms_rows = list()

        for state in self.ecc.states:
            states_rows.append([state.name, state.is_initial, state])

        for action in self.ecc.actions:
            print(action.output_event.name)
            # print(f'EDITOR = {action.state.name}')
            actions_rows.append([action.algorithm.name, action.output_event.name, action.state.name, action])

        for algorithm in self.fb.algorithms:
            algorithms_rows.append([algorithm.name, algorithm.algorithm_str, algorithm])

        states_rows.sort(key=lambda row: row[0])
        actions_rows.sort(key=lambda row: row[0])
        algorithms_rows.sort(key=lambda row: row[0])

        for row in states_rows:
            self.states_liststore.append(row) 
            
        for row in actions_rows:
            self.actions_liststore.append(row)        


        for row in algorithms_rows:
            self.algorithm_liststore.append(row) 

        if cursor_path:
            self.states_treeview.set_cursor(cursor_path, cursor_focus_column, False)
        
    def build_bottom_treeview(self):
        self.transitions_liststore = Gtk.ListStore(int, str, str, str, str, object)
        
        self.transitions_treeview = Gtk.TreeView(model=self.transitions_liststore)
        self.transitions_treeview_selection = self.transitions_treeview.get_selection()
        self.transitions_treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.transitions_treeview.set_enable_search(False)
        
        #  | -------------- Order --------------- |
        
        order_editabletext = Gtk.CellRendererText()
        order_editabletext.set_property('editable', False)

        order_column = Gtk.TreeViewColumn("Order", order_editabletext, text=0)
        self.transitions_treeview.append_column(order_column)
        
        #  | -------------- Destination --------------- |
        
        destination_editabletext = Gtk.CellRendererText()
        destination_editabletext.set_property('editable', True)
        destination_editabletext.connect('edited', self.destination_state_change)
        
        destination_column = Gtk.TreeViewColumn("Destination", destination_editabletext, text=1)
        self.transitions_treeview.append_column(destination_column)
        
        #  | -------------- Event --------------- |
        
        event_editabletext = Gtk.CellRendererText()
        event_editabletext.set_property('editable', True)
        event_editabletext.connect('edited', self.event_change)
        
        event_column = Gtk.TreeViewColumn("Event", event_editabletext, text=2)
        self.transitions_treeview.append_column(event_column)
        
        #  | -------------- Condition --------------- |
        
        condition_editabletext = Gtk.CellRendererText()
        condition_editabletext.set_property('editable', True)
        #condition_editabletext.connect('edited', self.condition_text_edited)
        
        condition_column = Gtk.TreeViewColumn("Condition", condition_editabletext, text=3)
        self.transitions_treeview.append_column(condition_column)
        
        #  | -------------- Comment --------------- |
        
        comment_editabletext = Gtk.CellRendererText()
        comment_editabletext.set_property('editable', True)
        comment_editabletext.connect('edited', self.comment_text_edited)
        
        comment_column = Gtk.TreeViewColumn("Comment", comment_editabletext, text=4)
        self.transitions_treeview.append_column(comment_column)
        
        #  | -------------------------------------- |
        
        self.transitions_treeview.set_vexpand(True)
        self.transitions_treeview.set_hexpand(True)
        self.box_bottom.append(self.transitions_treeview)
        
        # if self.selected_state is not None:
        self.update_bottom_treeview()
        
    def update_bottom_treeview(self):
        cursor_path, cursor_focus_column = self.transitions_treeview.get_cursor()

        self.transitions_liststore.clear()
        transitions_rows = list()   

        if self.selected_state is not None:
            for index, transition in enumerate(self.selected_state.out_transitions):
                condition = transition.condition_convert_str()
                print(transition.event.name)
                transitions_rows.append([index+1, transition.to_state.name, transition.event.name, condition, transition.comment, transition])

        transitions_rows.sort(key=lambda row: row[0])

        for row in transitions_rows:
            self.transitions_liststore.append(row) 

        if cursor_path:
            self.transitions_treeview.set_cursor(cursor_path, cursor_focus_column, False)
    
    def destination_state_change(self, widget, path, destination_name):
        transition = self.transitions_liststore[path][5]
        destination_state = self.ecc.state_get(destination_name)
        if destination_state is None:
            return False
        self.selected_state.transition_destination_change(transition, destination_state)
        self.update_bottom_treeview()
        self.trigger_change()
        
    def event_change(self, widget, path, event_name):
        transition = self.transitions_liststore[path][5]
        new_event = self.fb.event_get(event_name)
        if new_event is None:
            return False
        self.selected_state.transition_event_change(transition, new_event)
        self.update_bottom_treeview()
        self.trigger_change()
        
    def condition_text_edited(self, widget, path, new_condition):
        transition = self.transitions_liststore[path][5]
        self.selected_state.transition_condition_change(transition, new_condition)
        self.update_bottom_treeview()
        self.trigger_change()

    def comment_text_edited(self, widget, path, new_comment):
        transition = self.transitions_liststore[path][5]
        self.selected_state.transition_event_change(transition, new_comment)
        self.update_bottom_treeview()
        self.trigger_change()

     # | ----------- STATE ------------- |
        
    def state_text_edited(self, widget, path, state_name):
        state = self.states_liststore[path][2]
        self.ecc.state_rename(state, state_name)
        self.update_side_treeview()
        self.update_bottom_treeview()
        self.trigger_change()

    def state_add(self, widget):
        if self.enable_add:
            window = self.get_ancestor_window()
            window.selected_tool = 'add'
            new_state = self.ecc.state_add(name="new_State")
            self.selected_state = new_state
            self.enable_add = False
        else:
            print("Previous added state needs to be drawn before adding a new state")
        # self.update_side_treeview()
        # self.trigger_change()

    def state_remove(self, widget):
        _, tree_path_list = self.states_treeview_selection.get_selected_rows()
        for tree_path in tree_path_list:
            tree_iter = self.states_liststore.get_iter(tree_path)
            state = self.states_liststore.get(tree_iter, 2)[0]
            self.ecc.state_remove(state)
        if self.selected_state == state:
            self.selected_state = self.ecc.states[0]
        self.update_side_treeview()
        self.update_bottom_treeview()
        self.trigger_change()

    def state_change(self, widget, path, state_name):
        action = self.actions_liststore[path][3]
        old_state = action.state
        old_state.action_remove(action)
        new_state = self.ecc.state_get(state_name)
        if new_state is None:
            return False
        action.state = new_state
        new_state.actions.append(action)
        self.update_side_treeview()
        self.update_bottom_treeview()
        self.trigger_change()

    #  | ---------------- ACTION -------------- |

    def action_add(self, widget):
        self.ecc.action_add()
        self.update_side_treeview()
        self.trigger_change()

    def action_remove(self, widget):
        _, tree_path_list = self.actions_treeview_selection.get_selected_rows()
        for tree_path in tree_path_list:
            tree_iter = self.actions_liststore.get_iter(tree_path)
            action = self.actions_liststore.get(tree_iter, 3)[0]
            self.ecc.action_remove(action)
        self.update_side_treeview()
        self.update_bottom_treeview()
        self.trigger_change()

    def algorithm_change(self, widget, path, algorithm_name):
        action = self.actions_liststore[path][3]
        if algorithm_name == '':
            action.algorithm = self.fb.algorithm_create_blank()
        else:
            new_algorithm = self.fb.algorithm_get(algorithm_name)
            if new_algorithm is None:
                return False
            action.algorithm = new_algorithm
        self.update_side_treeview()
        self.update_bottom_treeview()
        self.trigger_change()

    def event_output_change(self, widget, path, event_output_name):
        action = self.actions_liststore[path][3]
        if event_output_name == '':
            action.output_event = self.fb.event_create_blank()
        else:
            new_event = self.fb.event_get(event_output_name)
            if new_event is None:
                return False
            action.output_event = new_event
        self.update_side_treeview()
        self.update_bottom_treeview()
        self.trigger_change()

    # | ----------- ALGORITHM ------------- |

    def algorithm_add(self, widget):
        self.fb.algorithm_add(name="new_Algorithm")    
        self.update_side_treeview()
        self.trigger_change()
        
    def algorithm_name_edited(self, widget, path, algorithm_name):
        algorithm = self.algorithm_liststore[path][2]
        self.fb.algorithm_rename(algorithm, algorithm_name)
        self.update_side_treeview()
        self.trigger_change()      
        
    def algorithm_str_edited(self, widget, path, algorithm_text):
        algorithm = self.algorithm_liststore[path][2]
        self.fb.algorithm_change(algorithm, algorithm_text)
        self.update_side_treeview()
        self.trigger_change()
        
    def algorithm_remove(self, widget):
        _, tree_path_list = self.algorithm_treeview_selection.get_selected_rows()
        for tree_path in tree_path_list:
            tree_iter = self.algorithm_liststore.get_iter(tree_path)
            algorithm = self.algorithm_liststore.get(tree_iter, 2)[0]
            self.selected_state.algorithm_remove(algorithm)
        self.update_side_treeview()
        self.trigger_change()
    
    #  | ------------------------------------- |

        
    def on_draw(self, area, cr, wd, h, data):
        self.ecc_render.draw(area, cr, wd, h, data)
        
    def trigger_change(self):
        self._changes_to_save = True
        self.ecc_render.queue_draw()
        
    def motion_notify(self, data, x, y):
        window = self.get_ancestor_window()
        tool_name = window.get_selected_tool()

        if tool_name == 'move':
            if not self.selected_state is None:
                #print(self.selected_state.x)
                self.selected_state.x = x-self.ecc_render.offset_x
                self.selected_state.y = y-self.ecc_render.offset_y
                self.trigger_change()
                self.update_scrolled_window()
                
    def button_press(self, e, data, x, y):
        window = self.get_ancestor_window()
        tool = window.get_selected_tool()
        print(f'tool = {tool}')
        if tool != 'add':
            state = self.ecc_render.get_state_at(x, y) 

        if tool == 'add':
            # print('1')
            new_state = self.selected_state
            new_state.x = x
            new_state.y = y
            #self.ecc.state_add(new_state)
            self.update_side_treeview()
            self.update_bottom_treeview()
            self.trigger_change()
            self.selected_state = None
            self.enable_add = True
        elif tool == 'move':
            # print('2')
            self.selected_state = state
            self.update_bottom_treeview()
        elif tool == 'connect':
            if state is None:
                self.selected_state = None
                # print('3')
            else:
                if self.selected_state is None:
                    self.selected_state = state
                    # print(f'SELECTED = {self.selected_state.name}')
                    # print('4')
                else:
                    # print('5')
                    transition = Transition(self.selected_state, state)
                    self.ecc.transition_add(transition)
                    self.selected_state.transition_out_add(transition)
                    state.transition_in_add(transition)
                    self.trigger_change()
                    self.update_bottom_treeview()
                    self.selected_state = None
        elif tool == 'inspect':
            self.selected_state = state
            self.update_bottom_treeview()


    def button_release(self, e, data, x, y):
        window = self.get_ancestor_window()
        tool_name = window.get_selected_tool()

        if tool_name == 'move':
            self.update_scrolled_window()
            self.selected_state = None
                
    def update_scrolled_window(self):
        hadj = self.scrolled.get_hadjustment()
        vadj = self.scrolled.get_vadjustment()

        delta_x, delta_y = self.ecc_render.renderer_set_size_request(self.scrolled.get_allocation())

        hadj.set_value(hadj.get_value() + delta_x)
        vadj.set_value(vadj.get_value() + delta_y)
        self.scrolled.set_hadjustment(hadj)
        self.scrolled.set_vadjustment(vadj)