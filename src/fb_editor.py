from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdk
from .base import PageMixin
from .fb_renderer import FunctionBlockRenderer
from .ecc_editor import EccEditor
import copy

@Gtk.Template(resource_path='/com/lapas/Fbe/menu.ui')
class FunctionBlockEditor(PageMixin, Gtk.Box):
    __gtype_name__ = 'FunctionBlockEditor'
    
    fb_menu = Gtk.Template.Child()
    mapping_menu = Gtk.Template.Child()
    mapping_submenu = Gtk.Template.Child()
    
    def __init__(self, app=None, fb_diagram=None, project=None, selected_fb=None, current_tool=None, window=None, inspected_block=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        self.fb_diagram = fb_diagram
        self.project = project
        self.window = window
        self.selected_fb = selected_fb
        self.selected_event = None
        self.selected_variable = None
        self.selected_connection = None
        self.previous_selected = None
        self.current_tool = current_tool
        self.inspected_block = inspected_block
        self.fb_count = 0
        if self.fb_diagram is None:
            self.fb_diagram = app.subapp_network

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.paned = Gtk.Paned(wide_handle=True)
        
        self.scrolled = Gtk.ScrolledWindow.new()
        self.fb_render = FunctionBlockRenderer(self.fb_diagram, self.inspected_block)
        self.sidebox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, valign=Gtk.Align.FILL)
        self.gesture_press = Gtk.GestureClick.new()
        self.gesture_release = Gtk.GestureClick.new()
        self.event_controller = Gtk.EventControllerMotion.new()
              
        self.append(self.paned)
        self.paned.set_vexpand(True)
        self.paned.set_hexpand(True)
        self.paned.set_start_child(self.scrolled)
        self.paned.set_resize_start_child(True)
        self.paned.set_shrink_start_child(False)
        self.paned.set_end_child(self.sidebox)
        self.paned.set_resize_end_child(False)
        self.paned.set_shrink_end_child(False)
        self.scrolled.set_child(self.fb_render)
        self.fb_render.renderer_set_size_request(self.scrolled.get_allocation())

        
         # ---------- Make tool frame's border square ---------- #  
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b".squared {border-radius: 0;}")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        
        # ---------------------------------------------------- #
    
        # self.sidebox.append(self.fb_menu)
        # self.popover = Gtk.PopoverMenu().new_from_model(self.mapping_menu)
        # self.popover.set_parent(self.fb_render)
        # self.popover.set_has_arrow(False)
        # self.popover.set_halign(Gtk.Align.START)
        
        # self.click_on_fb = Gtk.GestureClick.new()
        # self.click_on_fb.connect("pressed", self.on_right_click_app)
        # self.click_on_fb.set_button(3)
        # self.fb_render.add_controller(self.click_on_fb)
        
        # self.fb_menu.set_popover(self.popover)
        # self.fb_menu.set_visible(False)

        self.fb_render.set_draw_func(self.on_draw, None)
        
        self.gesture_press.connect("pressed", self.button_press)
        self.gesture_release.connect("released", self.button_release)
        self.event_controller.connect("motion", self.motion_notify)
        self.fb_render.add_controller(self.gesture_press)
        self.fb_render.add_controller(self.gesture_release)
        self.fb_render.add_controller(self.event_controller)

        self.build_treeview()

    def build_treeview(self):
        self.events_liststore = Gtk.ListStore(str, bool, bool, object)

        self.events_treeview = Gtk.TreeView(model=self.events_liststore)
        self.events_treeview_selection  = self.events_treeview.get_selection()
        self.events_treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.events_treeview.set_enable_search(False)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property('editable', True)
        renderer_editabletext.connect('edited', self.event_text_edited)
        column_editabletext = Gtk.TreeViewColumn("Events", renderer_editabletext, text=0)
        self.events_treeview.append_column(column_editabletext)

        renderer_toggle_1 = Gtk.CellRendererToggle()
        renderer_toggle_1.connect('toggled', self.events_toggle_active)
        column_toggle_1 = Gtk.TreeViewColumn('Active', renderer_toggle_1, active=1)
        self.events_treeview.append_column(column_toggle_1)

        renderer_toggle_2 = Gtk.CellRendererToggle()
        renderer_toggle_2.connect('toggled', self.events_toggle_input)
        column_toggle_2 = Gtk.TreeViewColumn('Input', renderer_toggle_2, active=2)
        self.events_treeview.append_column(column_toggle_2)

        self.events_treeview.set_vexpand(True)
        self.events_treeview.set_hexpand(True)
        self.sidebox.append(self.events_treeview)

        self.add_button = Gtk.Button(label = "Add Event")
        self.add_button.connect('clicked', self.event_add)
        self.sidebox.append(self.add_button)

        self.delete_button = Gtk.Button(label = "Remove Event")
        self.delete_button.connect('clicked', self.event_remove)
        self.sidebox.append(self.delete_button)

        self.vars_liststore = Gtk.ListStore(str, bool, str, object)

        renderer_editabletext1 = Gtk.CellRendererText()
        renderer_editabletext1.set_property('editable', True)
        renderer_editabletext1.connect('edited', self.variable_text_edited)

        self.vars_treeview = Gtk.TreeView(model=self.vars_liststore)
        self.vars_treeview_selection  = self.vars_treeview.get_selection()
        self.vars_treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.vars_treeview.set_enable_search(False)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property('editable', True)
        renderer_editabletext.connect('edited', self.variable_text_edited)

        column_editabletext = Gtk.TreeViewColumn("Variable", renderer_editabletext, text=0)
        self.vars_treeview.append_column(column_editabletext)

        renderer_toggle_1 = Gtk.CellRendererToggle()
        renderer_toggle_1.connect('toggled', self.variable_toggle_input)
        column_toggle_1 = Gtk.TreeViewColumn('Input', renderer_toggle_1, active=1)
        self.vars_treeview.append_column(column_toggle_1)

        renderer_text_1 = Gtk.CellRendererText()
        renderer_text_1.set_property('editable', True)
        renderer_text_1.connect('edited', self.variable_text_type)
        column_text_1 = Gtk.TreeViewColumn("Type", renderer_text_1, text=2)
        self.vars_treeview.append_column(column_text_1)

        self.vars_treeview.set_vexpand(True)
        self.vars_treeview.set_hexpand(True)
        self.sidebox.append(self.vars_treeview)

        self.add_button = Gtk.Button(label = "Add Variable")
        self.add_button.connect('clicked', self.variable_add)
        self.sidebox.append(self.add_button)

        self.delete_button = Gtk.Button(label = "Remove Variable")
        self.delete_button.connect('clicked', self.variable_remove)
        self.sidebox.append(self.delete_button)

        self.map_frame = Gtk.Frame(vexpand=True)
        self.map_frame.get_style_context().add_class("squared")
        self.map_label = Gtk.Label(label="Map to", margin_top=2, margin_bottom=2)
        self.map_label_frame = Gtk.Frame()
        self.map_label_frame.set_child(self.map_label)
        self.map_label_frame.get_style_context().add_class("squared")
        self.map_list = Gtk.ListBox()
        self.map_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.map_list.set_show_separators(True)
        self.build_mapping_list(self.map_list)
        self.test_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.test_vbox.append(self.map_label_frame)
        self.test_vbox.append(self.map_list)
        self.map_frame.set_child(self.test_vbox)
        self.sidebox.append(self.map_frame)
        
        self.map_button = Gtk.Button(label = "Map to resource")
        self.map_button.connect('clicked', self.map_to_resource)
        self.sidebox.append(self.map_button)

        if self.selected_fb is not None:
            self.update_treeview()

    def update_treeview(self):
        cursor_path, cursor_focus_column = self.events_treeview.get_cursor()
        current_fb = None
        if self.selected_fb is None:
            current_fb = self.previous_selected
        else:
            current_fb = self.selected_fb

        self.events_liststore.clear()
        self.vars_liststore.clear()
        events_rows = list()
        vars_rows = list()

        for event in current_fb.events:
            events_rows.append([event.name, event.active, event.is_input, event])

        events_rows.sort(key=lambda row: row[0])

        for row in events_rows:
            self.events_liststore.append(row)

        cursor_path, cursor_focus_column = self.vars_treeview.get_cursor()

        for var in current_fb.variables:
            vars_rows.append([var.name, var.is_input, var.type, var])

        vars_rows.sort(key=lambda row: row[0])

        for row in vars_rows:
            self.vars_liststore.append(row)

        if cursor_path:
            self.events_treeview.set_cursor(cursor_path, cursor_focus_column, False)
            self.vars_treeview.set_cursor(cursor_path, cursor_focus_column, False)

    def build_mapping_list(self, listbox):
        system = self.project.system
        for device in system.devices:
            for resource in device.resources:
                label = f'[{device.name}]{resource.name}'
                self.add_row(listbox, label)

    def add_row(self, listbox, label, margin=0):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=label, halign=Gtk.Align.START, margin_start=5+margin, margin_end=5)
        row.set_child(label)
        listbox.append(row)
        return row
    
    def map_to_resource(self, widget):
        row = self.map_list.get_selected_row()
        if row is not None:
            label = row.get_child().get_label()
            device_name, resource_name = self.extract_strings(label)
            system = self.project.system
            device = system.device_get(device_name)
            resource = device.resource_get(resource_name)
            source = (self.app, self.previous_selected)
            destination = (device, resource, self.previous_selected)
            system.mapping_add((source, destination))
            fb_copy = copy.deepcopy(self.previous_selected)
            fb_copy.connections.clear()
            for variable in fb_copy.variables:
                variable.connections.clear()
            for event in fb_copy.events:
                event.connections.clear()
            resource.fb_network.add_function_block(fb_copy)
    
    def extract_strings(self, label):
        start = label.find('[')
        end = label.find(']')
        
        if start != -1 and end != -1:
            inside_brackets = label[start+1:end]
            outside_brackets = label[end+1:].strip()
            return inside_brackets, outside_brackets
        else:
            return None, None

    def event_text_edited(self, widget, path, event_name):
        event = self.events_liststore[path][3]
        self.previous_selected.event_rename(event, event_name)
        self.update_treeview()
        self.trigger_change()

    def events_toggle_active(self, widget, path):
        event = self.events_liststore[path][3]
        event.active = not event.active
        self.update_treeview()
        self.trigger_change()

    def events_toggle_input(self, widget, path):
        event = self.events_liststore[path][3]
        event.is_input = not event.is_input
        event.connection_remove_all_same_type()
        self.update_treeview()
        self.trigger_change()

    def event_add(self, widget):
        self.previous_selected.event_add(name="new_Event")
        self.update_treeview()
        self.trigger_change()

    def event_remove(self, widget):
        _, tree_path_list = self.events_treeview_selection.get_selected_rows()
        for tree_path in tree_path_list:
            tree_iter = self.events_liststore.get_iter(tree_path)
            event = self.events_liststore.get(tree_iter, 3)[0]
            self.previous_selected.event_remove(event)
        self.update_treeview()
        self.trigger_change()

    def variable_text_edited(self, widget, path, var_name):
        var = self.vars_liststore[path][3]
        self.previous_selected.variable_rename(var, var_name)
        self.update_treeview()
        self.trigger_change()

    def variable_toggle_input(self, widget, path):
        variable = self.vars_liststore[path][3]
        variable.is_input = not variable.is_input
        variable.is_output = not variable.is_output
        variable.connection_remove_all_same_type()
        self.update_treeview()
        self.trigger_change()

    def variable_text_type(self, widget, path, type_name):
        var = self.vars_liststore[path][3]
        self.previous_selected.variable_type_rename(var, type_name)
        self.update_treeview()
        self.trigger_change()

    def variable_add(self, widget):
        self.previous_selected.variable_add(name="new_Var", fb=self.previous_selected)
        self.update_treeview()
        self.fb_render.queue_draw()
        self.trigger_change()

    def variable_remove(self, widget):
        _, tree_path_list = self.vars_treeview_selection.get_selected_rows()
        for tree_path in tree_path_list:
            tree_iter = self.vars_liststore.get_iter(tree_path)
            var = self.vars_liststore.get(tree_iter, 3)[0]
            self.previous_selected.variable_remove(var)
        self.update_treeview()
        self.trigger_change()

    def diagram_add(self, fb):
        self.fb_diagram.add_function_block(fb)
        self.update_treeview()
        self.fb_render.queue_draw()
        self.trigger_change()

    def on_draw(self, area, cr, wd, h, data):
        self.fb_render.draw(area, cr, wd, h, data)

    def save(self, file_path_name=None):
        status = self.selected_fb.save(file_path_name)
        if status == True:
            self._changes_to_save = False
        return status

    def has_file_path_name(self):
        return self.selected_fb.get_file_path_name() is not None

    def trigger_change(self):
        self._changes_to_save = True
        self.fb_render.queue_draw()

    def get_tab_name(self):
        if self.selected_fb is not None:
            return self.selected_fb.get_name()
        return self

    def _create_action(self, action_name, callback, *args):
        action = Gio.SimpleAction.new(action_name, None)
        if not args:
            action.connect("activate", callback)
            self.window.add_action(action)
        else:
            action.connect("activate", callback, args)
            self.window.add_action(action)  

    def on_right_click_app(self, gesture, n, x, y):
        rect = self.fb_menu.get_allocation()
        rect.width = 0
        rect.height = 0
        rect.x = x
        rect.y = y
        self.popover.set_pointing_to(rect)
        self.popover.popup()

    def on_map_resource(self, action, param=None):
        print("map")

    def on_my_app(self):
        print('app')

    def on_system_config(self):
        print('config')

    def motion_notify(self, data, x, y):
        window = self.get_ancestor_window()
        tool_name = window.get_selected_tool()

        if tool_name == 'move':
            if not self.selected_fb is None:
                #print(self.selected_fb.x)
                self.selected_fb.x = x-self.fb_render.offset_x
                self.selected_fb.y = y-self.fb_render.offset_y
                self.trigger_change()
                self.update_treeview()
                self.update_scrolled_window()

    def button_press(self, e, data, x, y):
        '''
        Erro
        '''
        # print("000000")
        # print(x,y)
        print(self.selected_fb)
        window = self.get_ancestor_window()
        tool = window.get_selected_tool()
        if tool != 'add':
            fb = self.fb_render.get_fb_at(x, y)
        #if fb is not None:
            #print(fb.name)

        if tool == 'add':
            new_fb = self.selected_fb
            new_fb.x = x
            new_fb.y = y
            self.fb_render.fb_diagram.add_function_block(new_fb)
            self.fb_count = self.fb_count + 1
            self.update_treeview()
            self.trigger_change()
            self.project.update_system_editor()
            self.selected_fb = None
            
        elif tool == 'connect':
            selected_event = None
            selected_variable = None
            selected_event, selected_variable = self.fb_render.detect_data(x, y)
            if self.previous_selected == None:
                if selected_event == None:
                    self.previous_selected = selected_variable
                else:
                    self.previous_selected = selected_event
            else:
                if selected_event is not None:
                    self.fb_render.fb_diagram.connect_events(self.previous_selected, selected_event)
                    self.previous_selected = None
                else:
                    self.fb_render.fb_diagram.connect_variables(self.previous_selected, selected_variable)
                    self.previous_selected = None
            self.selected_fb = None
            
        elif tool == 'move':
            self.selected_fb = fb
            
        elif tool =='remove':
            self.fb_render.detect_connection(x,y)
            if fb is not None:
                self.fb_render.fb_diagram.remove_function_block(fb)
                self.fb_count = self.fb_count - 1
            if self.fb_render.selected_connection is not None:
                self.fb_render.selected_connection[0].connections.remove(self.fb_render.selected_connection[1])
            self.project.update_system_editor()
            
        elif tool == 'inspect':
            self.selected_fb = fb
            fb_diagram = fb.get_fb_network()
            if fb_diagram != None:
                fb_editor = FunctionBlockEditor(fb_diagram=fb_diagram, inspected_block=fb, project=self.project)
                self.project.last_page = self.project.current_page
                self.project.last_page_label = self.project.current_page_label.get_label()
                self.project.current_page = fb_editor
                self.project.vpaned.set_end_child(fb_editor)
                self.project.current_page_label.set_label('Inspecting: ' + fb.name)
            elif fb.is_basic():
                ecc_editor = EccEditor(fb, self.current_tool)
                self.project.last_page = self.project.current_page
                self.project.last_page_label = self.project.current_page_label.get_label()
                self.project.current_page = ecc_editor
                self.project.vpaned.set_end_child(ecc_editor)
                self.project.current_page_label.set_label('ECC: ' + fb.name)
                # window.add_tab(ecc_editor, 'ECC: ' + fb.name)
            self.update_treeview()
            self.trigger_change()


        self.fb_render.queue_draw()

    def button_release(self, e, data, x, y):
        window = self.get_ancestor_window()
        tool_name = window.get_selected_tool()

        if tool_name == 'move':
            self.update_scrolled_window()
            self.update_treeview()
            self.previous_selected = self.selected_fb
            self.selected_fb = None

    def update_scrolled_window(self):
        hadj = self.scrolled.get_hadjustment()
        vadj = self.scrolled.get_vadjustment()

        delta_x, delta_y = self.fb_render.renderer_set_size_request(self.scrolled.get_allocation())

        hadj.set_value(hadj.get_value() + delta_x)
        vadj.set_value(vadj.get_value() + delta_y)
        self.scrolled.set_hadjustment(hadj)
        self.scrolled.set_vadjustment(vadj)
