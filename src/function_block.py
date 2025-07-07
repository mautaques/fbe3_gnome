import os
import sys
import copy
import datetime
import time

        
class Event():
    def __init__(self, name='', active=False, fb=None, is_input=False, comment="", x=0.0, y=0.0, *args, **kwargs):
        self.name = name
        self.comment = comment
        self.fb = fb
        self.x = x
        self.y = y
        self.active = active
        self.is_input = is_input
        self.is_selected = False
        self.selected_connection = False
        self.variables = list()  # For now this set is used for keeping the variable name connected to the event
        self.transitions = list()  
        self.connections = list()
        super().__init__(*args, **kwargs)
        
    def activate(self, active=False):
        self.active = active
        
    def variable_add(self, variable):
        self.variables.append(variable)
        
    def connection_add(self, connection):
        self.connections.append(connection)
        
    def variable_remove(self, variable):
        self.variables.discard(variable)
        
    def connection_remove_all_same_type(self):
        for con in self.connections:
            if con.is_input == self.is_input:
                self.connections.remove(con)
                con.connections.remove(self)

class Algorithm():
    def __init__(self, name='', algorithm_str=None, func=None, comment="", *args, **kwargs):
        self.name = name
        self.comment = comment  # Describe what algorithm does. e.g: count up, reset counter                
        self.func = func  # Algorithm function 
        self.algorithm_str = algorithm_str


class Action():
    algorithm_class = Algorithm
    
    def __init__(self, is_algorithm_executed=False, output_event=None, is_action_executed=False, state=None, *args, **kwargs):
        self.is_action_executed = is_action_executed
        self.is_algorithm_executed = is_algorithm_executed
        self.output_event = Event()
        self.state = State()
        self.algorithm = Algorithm()
        
    def run_action(self):
        self.is_algorithm_executed = self.algorithm.func()  # Function returns True if algorithm went fine
        if self.is_algorithm_executed == True:
            # print("Output event = "+ self.output_event.name)
            self.is_action_executed = True
            # Signal WORLD that output have been updated
            
    def algorithm_add(self, *args, **kwargs):
        algorithm = self.algorithm_class(*args, **kwargs)
        self.algorithm = algorithm
        return algorithm
    
    def __str__(self) -> str:
        if self.output_event is None:
            event = 'None'
        else:
            event = event = self.output_event.name
        if self.algorithm is None:
            algorithm = 'None'
        else:
            algorithm = self.algorithm.name
            
        return f'Event -> {event} | Algorithm -> {algorithm}\n '

            
class State():
    action_class = Action
    
    def __init__(self, name='', is_initial=False, x=50.0, y=0.0,
                 comment="",is_active=False, fb=None, 
                 *args, **kwargs
                 ):
        self.name = name
        self.comment = comment  # Usually states if the given state is initial
        self.is_initial = is_initial
        self.is_active = is_active
        self.in_transitions = list()
        self.out_transitions = list()
        self.map_transitions = dict()  # ???? - Maps a destination state given an event e.g: mp[event] = new_state
        self.actions = list()  # All actions must be executed
        self.x = x
        self.y = y
        self.fb = fb
        
    def run_actions(self):
        for action in self.actions:
            action.run_action()
            '''if action.is_action_executed == True:
                print("ok")
            else:
                print("execution error at " +action.output_event.name+ "!")
                return False'''
            
        return True      
    
    def transition_in_add(self, transition):
        self.in_transitions.append(transition) 
    
    def transition_out_add(self, transition):
        self.out_transitions.append(transition)  

    def transition_in_remove(self, transition):
        self.in_transitions.remove(transition)

    def transition_out_remove(self, transition):
        self.out_transitions.remove(transition)
        
    def transition_out_exists(self, transition_out):
        for transition in self.out_transitions:
            if transition.__eq__(transition_out):
                return True
        return False
        
    def transition_out_get(self, transition_out):
        for transition in self.out_transitions:
            if transition.event == transition_out.event and transition.condition == transition_out.condition:
                return transition
        return False
        
    def transition_destination_change(self, transition_out, new_state):
        if transition_out.to_state.name == new_state.name:
            return False
        transition_temp = copy.deepcopy(transition_out)
        transition_temp.to_state.name = new_state.name
        if self.transition_out_exists(transition_temp):
            return False
        transition_out.to_state = new_state
        
    def transition_event_change(self, transition_out, new_event):
        if transition_out.event.name == new_event.name:
            return False
        transition_temp = copy.deepcopy(transition_out)
        transition_temp.event.name = new_event.name
        if self.transition_out_exists(transition_temp):
            return False
        transition_out.event = new_event
    
    # TODO    
    def transition_condition_change(self, transition_out, new_condition):
        if transition_out.condition == new_condition:
            return False
        transition_temp = copy.deepcopy(transition_out)
        transition_temp.condition = new_condition
        if self.transition_out_exists(transition_temp):
            return False
        transition_out.condition = new_condition
        
    def transition_comment_change(self, transition_out, new_comment):
        if transition_out.comment == new_comment:
            return False
        transition_temp = copy.deepcopy(transition_out)
        transition_temp.comment = new_comment
        if self.transition_out_exists(transition_temp):
            return False
        transition_out.comment = new_comment
    
    def action_add(self, *args, **kwargs):
        action = self.action_class(*args, **kwargs)
        # print(action.state.name)
        self.actions.append(action)
        return action
    
    def action_get(self, algo_name):
        for action in self.actions:
            if action.algorithm_name == algo_name:
                return action
        return None
    
    def action_remove(self, action):
        if action not in self.actions:
            return False
        self.actions.remove(action)
        
    def set_initial_state(self):
        self.is_initial=True
        
    def get_event_output(self, event):
        return self.event.active

    def get_variable_value(self, variable):
        return self.variable.value

    def remove_event(self, name):
        delattr(self, name)	

    def remove_variable(self, name):
        delattr(self, name)

    def change_pos(self, pos_x, pos_y):
        self.x, self.y = pos_x, pos_y

    def maximum_algorithm_name(self):
        name = ''
        max_len = 0
        for action in self.actions:
            if len(action.algorithm.name) > max_len:
                name = action.algorithm.name
                max_len = len(action.algorithm.name)
        return name, max_len
        
    def print_state_actions(self):
        action_str = ''
        for action in self.actions:
            action_str += action.__str__()
        # print(f'{self.name} = {action_str}')

class Transition():
    def __init__(self, from_state, to_state, event=Event(), comment='', x=0.0, y=0.0, condition='', id=None, *args, **kwargs):
        self.comment = comment
        self.id = id
        self.from_state = from_state
        self.to_state = to_state
        self.event = event
        self.condition = condition # The tuple should give the elements in the following order (INPUT EVENT, VARIABLE, BOOLEAN OPERATOR, BOOLEAN OPERAND)
        self.x = x
        self.y = y        

    def add_event(self, event):
        self.event = event
        
    def strip_condition(self):
        op = {'&gt;': lambda x, y: x > y,  
              '&lt;': lambda x, y: x < y,
              '&gt;=': lambda x, y: x >= y,
              '&lt;=': lambda x, y: x <= y,
              '==': lambda x, y: x == y,
              '!=': lambda x, y: x != y,}
        if self.condition[0] != None and self.condition[1] == None:  # Only input event given e.g: R
            return 1
        if self.condition[0] == None and self.condition[3] == None:  # Unconditional e.g: 1
            return 1
        if op[self.condition[2]](self.condition[1].value,self.condition[1].type(self.condition[3])):  # [operator](variable.value, type cast at operand)
            return 1
        else:
            return 0
        
    def condition_convert_str(self):
        condition_str = '('
        for index, cond in enumerate(self.condition):
            if isinstance(cond, State) or isinstance(cond, Event) or isinstance(cond, Variable):
                condition_str += str(cond.name)
            else:
                condition_str += str(cond)
            if index != len(self.condition)-1:
                condition_str += ', '
        condition_str += ')'
        return condition_str
        
    def convert_condition_xml(self):
        print("CONDICAO COMECA AQUI")
        print(self.condition[0])
        print(self.condition[1])
        print(self.condition[2])
        print(self.condition[3])
        print("CONDICAO TERMINA AQUI")
        if self.condition == '':
            return self.condition
        condition_str=''
        if self.condition[0] == None and self.condition[3] == None:
            condition_str = "1"
        elif self.condition[0] != None and self.condition[1] == None:
            condition_str = self.condition[0].name
        elif self.condition[0] == None and self.condition[3] != None:
            condition_str = '['+self.condition[1].name + ' ' + self.condition[2] + ' ' + self.condition[3] +']'
        else:
            condition_str = self.condition[0].name+'['+self.condition[1].name + ' ' + self.condition[2] + ' ' + self.condition[3] +']'
            
        return condition_str    

    
    def __eq__(self, other):
        if isinstance(other, Transition):
            return self.from_state.name == other.from_state.name and self.to_state.name == other.to_state.name and\
                self.event.name == other.event.name and self.condition == other.condition
        return NotImplemented  


class Variable():
    def __init__(self, name, fb=None, comment="", is_selected = False, is_output=False, is_input=False, type=None, value=None, x=0.0, y=0.0, *args, **kwargs):
        self.name = name
        self.comment = comment
        self.fb = fb
        self.is_input = is_input
        self.is_output = is_output
        self.is_selected = is_selected
        self.selected_connection = False
        self.type = type  # BOOL, UINT, REAL...
        self.value = value # 13, True, 20.5...
        self.events = set() 
        self.connections = list()
        self.x = x
        self.y = y
        
    def event_add(self, event):
        self.events.add(event)
        
    def event_remove(self, event):
        self.events.discard(event)
        
    def connection_add(self, connection):
        self.connections.append(connection)

    def connection_remove_all_same_type(self):
        for con in self.connections:
            if con.is_input == self.is_input and con.is_output == self.is_output:
                self.connections.remove(con)
                con.connections.remove(self)

class ExecutionControlChart():
    state_class = State
    action_class = Action
    transition_class = Transition
    
    def __init__(self, fb=None, *args, **kwargs):
        self.fb = fb
        self.actions = set()
        self.states = list() 
        self.transitions = list()
        self.current_state = None
        
    # |--------------- STATE FUNCTIONS ---------------|
        
    def state_add(self, *args, **kwargs):
        state = self.state_class(*args, **kwargs)
        self.states.append(state)
        return state

    def state_remove(self, state):
        for transition in state.in_transitions:
            transition.from_state.transition_out_remove(transition)
            self.transition_remove(transition)
        for transition in state.out_transitions:
            transition.to_state.transition_in_remove(transition)
            self.transition_remove(transition)
        self.states.remove(state)

    def state_get(self, state_name):
        for state in self.states:
            if state.name == state_name:
                return state
        return None     
    
    def state_name_exists(self, state_name):
        return self.state_get(state_name) is not None
    
    def state_rename(self, state, new_name):
        if state.name == new_name:
            return False
        if self.state_name_exists(new_name):
            print("there's an state with same name")
            return False
        state.name = new_name
        #self.__str_event__()
        return True
    
    # |--------------- ACTION FUNCTIONS ---------------|
    
    def action_add(self, *args, **kwargs):
        action = self.action_class(*args, **kwargs)
        self.actions.add(action)

    def action_remove(self, action):
        action.state.action_remove(action)
        self.actions.discard(action)

    # |--------------- TRANSITION FUNCTIONS ---------------|

    def transition_add(self, transition):
        #transition = self.transition_class(*args, **kwargs)
        self.transitions.append(transition)

    def transition_remove(self, transition):
        # if transition not in self.transitions:
        #     return False
        self.transitions.remove(transition)

    def evalute_out_transitions(self):
        for transition in self.current_state.out_transitions:
            #if not transition.strip_condition():
                #print("transition "+ str(transition)+ " not valid")
            if transition.strip_condition():  
                    self.update_current_state(transition)
                    return

    def update_current_state(self, transition):
        self.current_state.is_active = False
        self.current_state = transition.to_state
        self.current_state.is_active = True
        #print("transition " +str(transition)+ " valid")

    def set_fb(self, fb):
        if fb is not None:
            self.fb = fb
            return True
        return False

class FunctionBlock():
    event_class = Event
    variable_class = Variable
    algorithm_class = Algorithm
    def __init__(self, name='', comment='', type=None, x=0.0, y=0.0,
                 service=None, fb_network=None, is_selected=False,
                 *args, **kwargs
                 ):
        self.name = name
        self.comment = comment
        self.type = type
        self.x = x
        self.y = y
        self.is_selected = is_selected
        self.service = service
        self.fb_network = fb_network  # If block is composite it receive a diagram of blocks (Composite)
        self.events = list()  # List since order matters
        self.variables = list()
        self.algorithms = set()
        self.map_algorithm_states = dict()  # Maps an algorithm to a list of states mp[algo] = [state1, state3]
        self.connections = list()  # Connections between function blocks. e.g: tuple = (source, destination)
        self.ecc = ExecutionControlChart()
        self.identificaton = Identification()
        self.version_info = VersionInfo()
        self._file_path_name = None
        self.events_unnamed = 0
        self.vars_unnamed = 0
        self.algorithms_unnamed = 0
        
    def get_ecc(self):
        if self.ecc is not None:
            return self.ecc
        return False
        
    def change_pos(self, pos_x, pos_y):
        self.x, self.y = pos_x, pos_y    
        
    def get_name(self):
        return self.name
        
    def connection_add(self, source, destination):
        if self.is_connection_valid(source, destination):
            self.connections.append((source, destination))
            # print(str(source.__class__.__name__)+" "+str(source.name)+" connected with "+str(destination.__class__.__name__)+" "+str(destination.name))
        else:
            print("invalid parameters for connection")
                
    def is_connection_valid(self, source, destination):          
        if isinstance(source, Event) and isinstance(destination, Event):
            if (source.is_input and not destination.is_input) or (not source.is_input and destination.is_input):
                return True
            return False
        elif isinstance(source, Variable) and isinstance(destination, Variable):
            if (source.is_input and not destination.is_input) or (not source.is_input and destination.is_input):
                return True
            return False
        
    # | -------------- EVENT FUCTIONS ---------------|
    
    def event_add(self, *args, **kwargs):
        event = self.event_class(*args, **kwargs) 
        if event.name == "new_Event":
            new_name = event.name + "_" + str(self.events_unnamed)
            self.inc_events_unnamed()
            self.event_rename(event, new_name)
        self.events.append(event)
        #self.__str_event__()
        return event
        
    def event_get(self, event_name):
        for event in self.events:
            if event.name == event_name:
                return event
        return None
    
    def event_remove(self, event):
        if event not in self.events:
            return False
        for var in list(event.variables):
            variable = self.variable_get(var) # Gets the variable list from fb using variable name
            variable.event_remove(event) # Remove event from variable's event set
        self.events.remove(event)
        #self.__str_event__()
        return True
    
    def event_name_exists(self, event_name):
        return self.event_get(event_name) is not None
    
    def _event_remove_(self, event_name):
        event = self.event_name_exists(event_name)
        if event is not None:
            return self.event_remove(event)
        return False
    
    def event_rename(self, event, new_name):
        if event.name == new_name:
            return False
        if self.event_name_exists(new_name):
            print("there's an event with same name")
            return False
        event.name = new_name
        #self.__str_event__()
        return True
    
    def event_create_blank(self):
        return Event()

    def __str_event__(self):
        for event in self.events:
            put = "Input Event" if event.is_input else "Output Event"
            print("Name:" + event.name + " -> " + put)          

    
    # | -------------- VARIABLE FUCTIONS ---------------|    
    
    def variable_add(self, *args, **kwargs):
        variable = self.variable_class(*args, **kwargs) 
        if variable.name == "new_Var":
            new_name = variable.name + "_" + str(self.vars_unnamed)
            self.inc_vars_unnamed()
            self.variable_rename(variable, new_name)
        self.variables.append(variable)
        return variable
        
    def variable_get(self, var_name):
        for var in self.variables:
            if var.name == var_name:
                return var
        return None

    def variable_remove(self, variable):
        if variable not in self.variables:
            return False
        for event in list(variable.events):
            event.variable_remove(variable) # Remove event from variable's event set
        self.variables.remove(variable)

    def _variable_remove_(self, variable_name):
        variable = self.variable_name_exists(variable_name)
        if variable is not None:
            return self.variable_remove(variable)
        return False
        
    def variable_rename(self, variable, new_name):
        if variable.name == new_name:
            return False
        if self.variable_name_exists(new_name):
            print("there's a variable with same name")
            return False
        variable.name = new_name
        return True    
        
    def variable_name_exists(self, variable_name):
        return self.variable_get(variable_name) is not None
    
    def variable_type_rename(self, variable, new_name):
        if variable.type == new_name:
            return False
        variable.type = new_name
        return True
    
    def __str_var__(self):
        for var in self.variables:
            put = "Input Var" if var.is_input else "Output Var"
            # print("Name:" + var.name + " -> " + put)
    
    # |------------------ ALGORITHM --------------------|
    
    def algorithm_add(self, *args, **kwargs):
        algorithm = self.algorithm_class(*args, **kwargs)
        if algorithm.name == 'new_Algorithm':
            new_name = algorithm.name + '_' + str(self.algorithms_unnamed)
            self.inc_algorithms_unnamed()
            self.algorithm_rename(algorithm, new_name)
        self.algorithms.add(algorithm)
        return algorithm
    
    #def _algorithm_add(self, algorithm):
    
    def algorithm_rename(self, algorithm, new_name):
        if algorithm.name == new_name:
            return False
        if self.algorithm_name_exists(new_name):
            print("there's an algorithm with same name")
            return False
        algorithm.name = new_name
        return True
    
    def algorithm_remove(self, algorithm):
        if algorithm not in self.algorithms:
            return False
        self.algorithms.discard(algorithm)

    def algorithm_create_blank(self):
        return Algorithm()
            
    def algorithm_get(self, algo_name):
        for algorithm in self.algorithms:
            if algorithm.name == algo_name:
                return algorithm
        return None    
    
    def algorithm_name_exists(self, algorithm_name):
        return self.algorithm_get(algorithm_name) is not None
    
    def algorithm_change(self, algorithm, new_algorithm):
        if algorithm.algorithm_str == new_algorithm:
            return False
        algorithm.algorithm_str = new_algorithm
        return True
    
    def algorithm_state_add(self, state, algorithm):
        if algorithm not in self.map_algorithm_states:
            self.map_algorithm_states[algorithm] = set()
        self.map_algorithm_states[algorithm].add(state)
        return True

    # | -------------- OTHER FUNCTIONS ------------ |

    def inc_events_unnamed(self):
        self.events_unnamed +=1
        
    def inc_vars_unnamed(self):
        self.vars_unnamed +=1

    def inc_algorithms_unnamed(self):
        self.algorithms_unnamed +=1
        
    def convert_type_py_to_xml(self, type):
        print(f'tipo : {type}')
        dict = {
            "BOOL": bool,
            "STRING": str,
            "REAL": float,
            "UINT": int,
            "ANY_ELEMENTARY" :int,
            "TIME" : float
        }
        return dict[type]
    
    def _str_service(self):
        if not self.service:
            return False
        # print("Comment= "+ self.service.comment + "\nInterfaces= " +str(self.service.interfaces))
        for seq in self.service.service_sequences.values():
            # print(" Name= " + seq.name + "\n Comment= " + seq.comment)
            for transaction in seq.service_transactions:
                print(" Input primitive" + str(transaction.input_primitive) + "\n Output primitive" + str(transaction.output_primitive) +"\n")
            
    def get_fb_network(self):
        if self.fb_network:
            return self.fb_network                   
        return None
        
    def is_basic(self):
        if self.fb_network is None and self.service is None:
            return True
        return False 
    
    def get_category(self):
        if self.fb_network is not None:
            return "[C]" 
        if self.service is not None:
            return "[SI]"
        return "[B]"
        
    # ---------------------------- FILE --------------------------- #
    
    def get_file_name(self):
        if self._file_path_name is not None:
            return os.path.basename(self._file_path_name)
        return None

    def get_file_path_name(self):
        return self._file_path_name

    def get_name(self):
        if self._file_path_name is not None:
            return self.get_file_name()
        elif self.name is not None:
            return self.name
        return 'Untitled'

    def set_file_path_name(self, file_path_name):
        self._file_path_name = file_path_name
        self._name = self.get_name()

    def clear_file_path_name(self):
        self._file_path_name = None

    def set_name(self, name):
        if self._file_path_name is None:
            self._name = name   
            
    # ------------------------------------------------------------- #         
        
    def save(self, file_path_name=None):
        if file_path_name is None:
            if self._file_path_name is None:
                return False
            file_path_name = self._file_path_name
        else:
            file_path_name += '/'+self.name+".fbt"
            self.set_file_path_name(file_path_name)
        
        f = open(file_path_name, 'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<FBType Name="{self.name}" Comment="{self.comment}">\n')
        f.write(f' <Identification Standard="{self.identification.standard}" Classification="{self.identification.classification}" ApplicationDomain="{self.identification.app_domain}" Function="{self.identification.function}" Type="{self.identification.type}" Description="{self.identification.description}">\n')
        f.write(f' </Identification>\n')
        f.write(f' <VersionInfo Organization="{self.version_info.organization}" Version="{self.version_info.version}" Author="{self.version_info.author}" Date="{datetime.date.today()}" Remarks="{self.version_info.remarks}">\n')
        f.write(f' </VersionInfo>\n')
        f.write(' <InterfaceList>\n')
        f.write('  <EventInputs>\n')
        for event in self.events:
            if event.is_input:
                if event.variables:
                    f.write(f'   <Event Name="{event.name}" Type="Event" Comment="{event.comment}">\n')
                    for var in event.variables:
                        f.write(f'    <With Var="{var}"/>\n')
                    f.write('   </Event>\n')
                else:
                    f.write(f'   <Event Name="{event.name}" Type="Event" Comment="{event.comment}"/>\n')
        f.write('  </EventInputs>\n')
        f.write('  <EventOutputs>\n')
        for event in self.events:
            if not event.is_input:
                f.write(f'   <Event Name="{event.name}" Type="Event" Comment="{event.comment}">\n')
                for var in event.variables:
                    f.write(f'    <With Var="{var}"/>\n')
                f.write('   </Event>\n')
        f.write('  </EventOutputs>\n')    
        f.write('  <InputVars>\n')
        for var in self.variables:
            if var.is_input:
                f.write(f'   <VarDeclaration Name="{var.name}" Type="{var.type}" Comment="{var.comment}"/>\n')
        f.write('  </InputVars>\n')
        f.write('  <OutputVars>\n')
        for var in self.variables:
            if var.is_output:
                f.write(f'   <VarDeclaration Name="{var.name}" Type="{var.type}" Comment="{var.comment}"/>\n')
        f.write('  </OutputVars>\n')
        f.write(' </InterfaceList>\n')
        if self.fb_network:
            f.write('   <FBNetwork>\n')
            for fb in self.fb_network.function_blocks:
                f.write(f'    <FB Name="{fb.name}" Type="{fb.type}" Comment="{fb.comment}" x="{fb.x}" y="{fb.y}">\n')
                for var in fb.variables:
                    if var.value is not None:
                        f.write(f'     <Parameter Name="{var.name}" Value="{var.value}"/>\n')
                f.write(f'    </FB>\n')
            f.write(f'    <EventConnections>\n')
            for connection in self.fb_network.event_connections:
                f.write(f'     <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
            f.write(f'    </EventConnections>\n')
            f.write(f'    <DataConnections>\n')
            for connection in self.fb_network.variable_connections:
                f.write(f'     <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
            f.write(f'    </DataConnections>\n')
            f.write('   </FBNetwork>\n')
        else:
            f.write(' <BasicFB>\n')
            f.write('  <ECC>\n')
            for state in self.ecc.states:
                if state.actions:
                    f.write(f'   <ECState Comment="{state.comment}" Name="{state.name}" x="{state.x}" y="{state.y}">\n')
                    for action in state.actions:
                        if action.output_event:
                            f.write(f'    <ECAction Algorithm="{action.algorithm.name}" Output="{action.output_event.name}"/>\n')  # It should be state.algorithm.name (missing name attr)
                        else:
                            f.write(f'    <ECAction Algorithm="{action.algorithm.name}"/>\n')
                    f.write('   </ECState>\n')  
                else:
                    f.write(f'   <ECState Comment="{state.comment}" Name="{state.name}" x="{state.x}" y="{state.y}"/>\n')

            for transition in self.ecc.transitions:
                f.write(f'   <ECTransition Comment="{transition.comment}" Condition="{transition.convert_condition_xml()}" Destination="{transition.to_state.name}" Source="{transition.from_state.name}" x="{transition.x}" y="{transition.y}"/>\n')    
            f.write('  </ECC>\n')  
            if self.algorithms:
                for algo in self.algorithms:
                    f.write(f'  <Algorithm Name="{algo.name}" Comment="{algo.comment}">\n')
                    f.write(f'   <ST Text="{algo.algorithm_str}"/>\n')
                    f.write(f'  </Algorithm>\n')  
            f.write(' </BasicFB>\n')
        f.write('</FBType>\n')
            
        return True
    
class Service():
    def __init__(self, interfaces=(None, None), comment='', *args, **kwargs):
        self.interfaces = interfaces
        self.service_sequences = dict()
        self.comment = comment

    def add_service_sequence(self, service_sequence):   
        self.service_sequences[service_sequence[0]] = service_sequence[1]
        

class ServiceSequence():
    def __init__(self, name='',comment='',*args, **kwargs):
        self.name = name
        self.comment = comment
        self.service_transactions = list()

    def add_service_transaction(self, *service_transactions):			
        for st in service_transactions:
            self.service_transactions.append(st)
            

class ServiceTransaction():
    def __init__(self, input_primitive=None, output_primitive=None, *args, **kwargs):
        self.input_primitive = input_primitive #(event, interface, parameters)
        self.output_primitive = output_primitive #(event, interface, parameters)
     
class Composite():
    def __init__(self):
        self.function_blocks = list()
        self.event_connections = list()  # A list of tuples: {((FB_A, IN1), (FB_B, OUT1))}
        self.variable_connections = list()
        
    def get_fb(self, fb_name):
        for fb in self.function_blocks:
            if fb.name == fb_name:
                return fb
        return None

    def add_function_block(self, fb):
        self.function_blocks.append(fb)
        
    def remove_function_block(self, fb):
        for fb in self.function_blocks:
            for event in fb.events:
                for connection in event.connections.copy():
                    if connection in fb.events:
                        event.connections.remove(connection)
            for var in fb.variables:
                for connection in var.connections.copy():
                    if connection in fb.variables:
                        var.connections.remove(connection)
        self.function_blocks.remove(fb)
        
    def event_connection_add(self, source_fb, source_event, destination_fb, destination_event):
        self.event_connections.append(((source_fb, source_event), (destination_fb, destination_event)))

    def variable_connection_add(self, source_fb, source_variable, destination_fb, destination_variable):
        self.variable_connections.append(((source_fb, source_variable), (destination_fb, destination_variable)))

    def read_through(self, fb, path):
        empty_block_flag = True
        for event in fb.events:
            for connection in event.connections:
                if connection != list():
                    empty_block_flag = False

        if empty_block_flag:
            self.paths.append(path)
            del path[-1]
        for event in fb.events:
            for in_event in event.connections:
                path.append(in_event)
                self.read_through(in_event.fb, path)

    def connect_events(self, in_event, out_event, is_basic=True):
        if type(in_event) is not Event or type(out_event) is not Event:
            print("Event type required")
        else:
            if ((in_event.is_input and out_event.is_input) or (in_event.is_input != True and out_event.is_input != True)) and is_basic:
                print("in_event with in_event or out_event with out_event")
            else:
                if in_event.is_input:
                    _in_event = in_event
                    _out_event = out_event
                else:
                    _in_event = out_event
                    _out_event = in_event
                _out_event.connection_add(_in_event)
                # _in_event.connection_add(_out_event)

    def connect_variables(self, in_var, out_var, is_basic=True):
        if type(in_var) is not Variable or type(out_var) is not Variable:
            print("Variable type required")
        else:
            if ((in_var.is_input and out_var.is_input) or (in_var.is_input != True and out_var.is_input != True)) and is_basic:
                print("in_var with in_var or out_var with out_var")
            else:		
                if in_var.is_input:
                    _in_var = in_var
                    _out_var = out_var
                else:
                    _in_var = out_var
                    _out_var = in_var
                _out_var.connection_add(_in_var)
   
    def find_max_cord(self):
        max_x = 0
        max_y = 0
        for fb in self.function_blocks:
            if fb.x > max_x:
                max_x = fb.x
            if fb.y > max_y:
                max_y = fb.y
        return max_x, max_y
    
    def save(self, path):
        print('not implemented')

class Identification():
    def __init__(self, standard='', classification='', app_domain='', function='', type='', description=''):
        self.standard = standard
        self.classification = classification
        self.app_domain = app_domain
        self.function = function
        self.type = type
        self.description = description

class VersionInfo():
    def __init__(self, version='', organization='', author='', date='', remarks=''):
        self.version = version
        self.organization = organization
        self.author = author
        self.date = date
        self.remarks = remarks
    
class Resource():
    def __init__(self, name, type='', comment='', x=0.0, y=0.0, fb_network=None):
        self.name = name
        self.type = type
        self.comment = comment
        self.version_info = VersionInfo()
        self.identification = Identification()
        self.x = x
        self.y = y
        self.fb_network = fb_network
        self.device = None
    
    def change_pos(self, pos_x, pos_y):
        self.x, self.y = pos_x, pos_y   

    # ---------------------------- FILE --------------------------- #
    
    def get_file_name(self):
        if self._file_path_name is not None:
            return os.path.basename(self._file_path_name)
        return None

    def get_file_path_name(self):
        return self._file_path_name

    def get_name(self):
        if self._file_path_name is not None:
            return self.get_file_name()
        elif self.name is not None:
            return self.name
        return 'Untitled'

    def set_file_path_name(self, file_path_name):
        self._file_path_name = file_path_name
        self._name = self.get_name()

    def clear_file_path_name(self):
        self._file_path_name = None

    def set_name(self, name):
        if self._file_path_name is None:
            self._name = name

    # ------------------------------------------------------------- #

    def save(self, file_path_name=None):
        if file_path_name is None:
            if self._file_path_name is None:
                return False
            file_path_name = self._file_path_name
        else:
            file_path_name += '/'+self.name+".res"
            self.set_file_path_name(file_path_name)

        f = open(file_path_name, 'w')
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        f.write('<!DOCTYPE ResourceType SYSTEM "http://www.holobloc.com/xml/LibraryElement.dtd">\n')
        f.write(f'<ResourceType Comment="{self.comment}" Name="{self.name}">\n')
        f.write(f' <Identification Description="{self.identification.description}">\n')
        f.write(f' <VersionInfo Author="{self.version_info.author}" Date="{datetime.date.today()}" Organization="{self.version_info.organization}" Version="{self.version_info.version}">\n')
        f.write('   <FBNetwork>\n')
        for fb in self.fb_network.function_blocks:
            f.write(f'   <FB Name="{fb.name}" Type="{fb.type}" Comment="{fb.comment}" x="{fb.x}" y="{fb.y}">\n')
            for var in fb.variables:
                if var.value is not None:
                    f.write(f'    <Parameter Name="{var.name}" Value="{var.value}"/>\n')
            f.write(f'   </FB>\n')
            f.write(f'   <EventConnections>\n')
            for connection in self.fb_network.event_connections:
                f.write(f'    <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
            f.write(f'   </EventConnections>\n')
            f.write(f'   <DataConnections>\n')
            for connection in self.fb_network.variable_connections:
                f.write(f'    <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
            f.write(f'   </DataConnections>\n')
        f.write('   </FBNetwork>\n')
        f.write('</ResourceType>')

        return True


class Device():
    def __init__(self, name, type, comment='', x=0.0, y=0.0):
        self.name = name
        self.type = type
        self.comment = comment
        self.version_info = VersionInfo()
        self.identification = Identification()
        self.x = x
        self.y = y
        self.resources = list()
        self.system = None
        
    def resource_add(self, resource):
        self.resources.append(resource)

    def _resource_add_(self, name):
        resource = Resource(name=name, type=None)
        self.resource_add(resource)
        
    def resource_get(self, name):
        for resource in self.resources:
            if resource.name == name:
                return resource
        return None
    
    def resource_name_exists(self, resource_name):
        return self.resource_get(resource_name) is not None
    
    def resource_rename(self, resource, new_name):
        if resource.name == new_name:
            return False
        if self.resource_name_exists(new_name):
            print("there's a resource with that name")
            return False
        resource.name = new_name
        return True
    
    def resource_remove(self, resource):
        if resource not in self.resources:
            return False
        self.system.resource_mapping_remove(resource)
        self.resources.remove(resource)
        return True
    
    def _resource_remove_(self, resource_name):
        resource = self.resource_name_exists(resource_name)
        if resource is not None:
            return self.resource_remove(resource)
        return False
    
    def resource_change_type(self, resource, new_type, new_resource):
        resource.type = new_type
        resource.fb_network = new_resource.fb_network
        
    def resource_change_comment(self, resource, new_comment):
        self.resource.comment = new_comment
        
    def save(self, path):
        file_path_name = path
        if file_path_name is None:
            if self._file_path_name is None:
                return False
            file_path_name = self._file_path_name
        else:
            file_path_name += '/'+self.name+".dev"
            self.set_file_path_name(file_path_name)
        
        f = open(file_path_name, 'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<DeviceType Name="{self.name}" Comment="{self.comment}">\n')
        f.write(f' <Identification Standard="{self.identification.standard}" Classification="{self.identification.classification}" ApplicationDomain="{self.identification.app_domain}" Function="{self.identification.function}" Type="{self.identification.type}" Description="{self.identification.description}">\n')
        f.write(f' </Identification>\n')
        f.write(f' <VersionInfo Organization="{self.version_info.organization}" Version="{self.version_info.version}" Author="{self.version_info.author}" Date="{datetime.date.today()}" Remarks="{self.version_info.remarks}">\n')
        f.write(f' </VersionInfo>\n')
        f.write(f'</DeviceType>')
        
            
        return True
        
class Application():
    def __init__(self, name, comment=''):
        self.name = name
        self.comment = comment
        self.version_info = VersionInfo()
        self.identification = Identification()
        self.subapp_network = Composite()
        
    # ---------------------------- FILE --------------------------- #

    def get_file_name(self):
        if self._file_path_name is not None:
            return os.path.basename(self._file_path_name)
        return None

    def get_file_path_name(self):
        return self._file_path_name

    def get_name(self):
        if self._file_path_name is not None:
            return self.get_file_name()
        elif self.name is not None:
            return self.name
        return 'Untitled'

    def set_file_path_name(self, file_path_name):
        self._file_path_name = file_path_name
        self._name = self.get_name()

    def clear_file_path_name(self):
        self._file_path_name = None

    def set_name(self, name):
        if self._file_path_name is None:
            self._name = name

    # ------------------------------------------------------------- #

    def save(self, path):
        file_path_name = path
        if file_path_name is None:
            if self._file_path_name is None:
                return False
            file_path_name = self._file_path_name
        else:
            file_path_name += '/'+self.name+".app"
            self.set_file_path_name(file_path_name)

        f = open(file_path_name, 'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f' <Application Name="{app.name}" Comment="{app.comment}">\n')
        f.write(f'  <SubAppNetwork>\n')
        for fb in self.subapp_network.function_blocks:
            f.write(f'   <FB Name="{fb.name}" Type="{fb.type}" Comment="{fb.comment}" x="{fb.x}" y="{fb.y}">\n')
            for var in fb.variables:
                if var.value is not None:
                    f.write(f'    <Parameter Name="{var.name}" Value="{var.value}"/>\n')
            f.write(f'   </FB>\n')
        f.write(f'   <EventConnections>\n')
        for connection in self.subapp_network.event_connections:
            f.write(f'    <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
        f.write(f'   </EventConnections>\n')
        f.write(f'   <DataConnections>\n')
        for connection in self.subapp_network.variable_connections:
            f.write(f'    <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
        f.write(f'   </DataConnections>\n')
        f.write(f'  </SubAppNetwork>\n')
        f.write(' </Application>\n')
        
class System():    
    def __init__(self, name='Untitled', comment=''):
        self.name = name
        self.comment = comment
        self.version_info = VersionInfo()
        self.identification = Identification()
        self.applications = list()
        self.devices = list()
        self.mapping = set()  # From FB to RES e.g mapping[CTD] = device.RES.CTD
        self.unnamed_applications = 0
        
    def applications_name_str(self):
        app_names = ''
        for app in self.applications:
            app_names += app.name + '\n'
        return app_names        
    
    def device_add(self, device):
        # print(f'device {device.name} added')
        self.devices.append(device)
    
    def device_get(self, name):
        for device in self.devices:
            if device.name == name:
                return device
        return None
    
    def device_remove(self, device):
        self.devices.remove(device)
        
    def _device_remove_(self, device):
        if device not in self.devices:
            return False
        self.device_mapping_remove(device)
        self.device_remove(device)
    
    def application_add(self, app):
        self.applications.append(app)
        
    def application_create(self):
        if(self.unnamed_applications == 0):
            app = Application(self.name+'App')
        else:
            app = Application(self.name+'App'+str(self.unnamed_applications))
        self.unnamed_applications += 1
        self.application_add(app)
        return app
        
    def application_get(self, name):
        for app in self.applications:
            if app.name == name:
                return app
        return None
    
    def application_name_exists(self, app_name):
        return self.application_get(app_name) is not None
    
    def application_rename(self, app, new_name):
        if app.name == new_name:
            return False
        if self.application_name_exists(new_name):
            print("there's an app with same name")
            return False
        app.name = new_name
        return True
    
    def application_remove(self, app):
        self.applications.remove(app)
    
    def mapping_add(self, mapping):
        self.mapping.add(mapping)
        
    def mapping_remove(self, connection):
        self.mapping.discard(connection)
    
    def device_mapping_remove(self, device):
        for connection in list(self.mapping):
            if device.name == connection[1][0].name:
                self.mapping_remove(connection)
        
    def resource_mapping_remove(self, resource):
        for connection in list(self.mapping):
            if resource.name == connection[1][1].name:
                self.mapping_remove(connection)
                
    # ---------------------------- FILE --------------------------- #
    
    def get_file_name(self):
        if self._file_path_name is not None:
            return os.path.basename(self._file_path_name)
        return None

    def get_file_path_name(self):
        return self._file_path_name

    def get_name(self):
        if self._file_path_name is not None:
            return self.get_file_name()
        elif self.name is not None:
            return self.name
        return 'Untitled'

    def set_file_path_name(self, file_path_name):
        self._file_path_name = file_path_name
        self._name = self.get_name()

    def clear_file_path_name(self):
        self._file_path_name = None

    def set_name(self, name):
        if self._file_path_name is None:
            self._name = name   
            
    # ------------------------------------------------------------- #  
    
    def save(self, file_path_name=None):
        if file_path_name is None:
            if self._file_path_name is None:
                return False
            file_path_name = self._file_path_name
        else:
            file_path_name += '/'+self.name+".sys"
            self.set_file_path_name(file_path_name)
        
        f = open(file_path_name, 'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<System Name="{self.name}" Comment="{self.comment}">\n')
        f.write(f' <Identification Standard="{self.identification.standard}" Classification="{self.identification.classification}" ApplicationDomain="{self.identification.app_domain}" Function="{self.identification.function}" Type="{self.identification.type}" Description="{self.identification.description}">\n')
        f.write(f' </Identification>\n')
        f.write(f' <VersionInfo Organization="{self.version_info.organization}" Version="{self.version_info.version}" Author="{self.version_info.author}" Date="{datetime.date.today()}" Remarks="{self.version_info.remarks}">\n')
        f.write(f' </VersionInfo>\n')
        for app in self.applications:
            f.write(f' <Application Name="{app.name}" Comment="{app.comment}">\n')
            f.write(f'  <SubAppNetwork>\n')
            for fb in app.subapp_network.function_blocks:
                f.write(f'   <FB Name="{fb.name}" Type="{fb.type}" Comment="{fb.comment}" x="{fb.x}" y="{fb.y}">\n')
                for var in fb.variables:
                    if var.value is not None:
                        f.write(f'    <Parameter Name="{var.name}" Value="{var.value}"/>\n')
                f.write(f'   </FB>\n')
            f.write(f'   <EventConnections>\n')
            for connection in app.subapp_network.event_connections:
                f.write(f'    <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
            f.write(f'   </EventConnections>\n')
            f.write(f'   <DataConnections>\n')
            for connection in app.subapp_network.variable_connections:
                f.write(f'    <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
            f.write(f'   </DataConnections>\n')
            f.write(f'  </SubAppNetwork>\n')
            f.write(' </Application>\n')
        for device in self.devices:
            f.write(f' <Device Name="{device.name}" Type="{device.type}" Comment="{device.comment}" x="{device.x}" y="{device.y}">\n')
            for resource in device.resources:
                f.write(f'  <Resource Name="{resource.name}" Type="{resource.type}" Comment="{resource.comment}" x="{resource.x}" y="{resource.y}">\n')
                f.write('   <FBNetwork>\n')
                for fb in resource.fb_network.function_blocks:
                    f.write(f'    <FB Name="{fb.name}" Type="{fb.type}" Comment="{fb.comment}" x="{fb.x}" y="{fb.y}">\n')
                    for var in fb.variables:
                        if var.value is not None:
                            f.write(f'     <Parameter Name="{var.name}" Value="{var.value}"/>\n')
                    f.write(f'    </FB>\n')
                f.write(f'    <EventConnections>\n')
                for connection in app.subapp_network.event_connections:
                    f.write(f'     <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
                f.write(f'    </EventConnections>\n')
                f.write(f'    <DataConnections>\n')
                for connection in app.subapp_network.variable_connections:
                    f.write(f'     <Connection Source="{connection[0][0].name}.{connection[0][1].name}" Destination="{connection[1][0].name}.{connection[1][1].name}"/>\n')
                f.write(f'    </DataConnections>\n')
                f.write('   </FBNetwork>\n')
                f.write('  </Resource>\n')
            f.write(' </Device>\n')
        for map in self.mapping:
            f.write(f' <Mapping From="{map[0][0].name}.{map[0][1].name}" To="{map[1][0].name}.{map[1][1].name}.{map[1][2].name}"/>\n')
        f.write('</System>')
            
        return True
                

