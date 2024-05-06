from xml.dom.minidom import parse
import os
import sys
import xml.etree.ElementTree as ET
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)
# from pathlib import Path
# path = Path("/here/your/path/file.txt")

from .function_block import*

def convert_xml_basic_fb(xml):
    print("XML: " + cur_path)
    fb_import_list = set()
    tree = ET.parse(xml)
    root = tree.getroot()
    fb_diagram = None
    for read in root.iter("FBType"):
        fb_name = read.get("Name")
        fb_comment = read.get("Comment")
        FB = FunctionBlock(name=fb_name, comment=fb_comment, type=fb_name)
        ECC = FB.get_ecc()
        

    for read in root.iter("EventInputs"):
        for read_1 in read.iter("Event"):	
            name = read_1.get("Name")
            FB.event_add(name, is_input=True, fb=FB)
            for read_2 in read_1.iter("With"):
                event = FB.event_get(name)
                event.variable_add(read_2.get("Var")) # Add var name to event's var list
                
    for read in root.iter("EventOutputs"):
        for read_1 in read.iter("Event"):	
            name = read_1.get("Name")
            FB.event_add(name, is_input=False, fb=FB)
            for read_2 in read_1.iter("With"):
                event = FB.event_get(name)
                event.variable_add(read_2.get("Var")) # Add var to event's var list

    for read in root.iter("InputVars"):
        for read_1 in read.iter("VarDeclaration"):
            name = read_1.get("Name")	
            comment = read_1.get("Comment")
            type = read_1.get("Type")
            FB.variable_add(name, fb=FB, comment=comment, is_input=True,type=type)
            
    for read in root.iter("OutputVars"):
        for read_1 in read.iter("VarDeclaration"):
            name = read_1.get("Name")	
            comment = read_1.get("Comment")
            type = read_1.get("Type")	
            FB.variable_add(name, fb=FB, comment=comment, is_output=True,type=type)
            
   
    for read in root.iter("FBNetwork"):
        fb_diagram = Composite()    
        for read_1 in read.iter("FB"):
            fb,_ = convert_xml_basic_fb('Projects/fbe/src/models/fb_library/'+read_1.get("Type")+'.fbt')  # Blocks declared in FBNetwork must be inside src/models/diac_library
            # print("Network FB = "+fb.name)
            fb.change_pos(float(read_1.get("x"))/3, float(read_1.get("y"))/4)
            fb.name = read_1.get("Name")
            fb.type = read_1.get("Type")
            fb_diagram.add_function_block(fb)
            fb_import_list.add(fb)
            for read_2 in read_1.iter("Parameter"):
                var = fb.variable_get(read_2.get("Name"))
                var.value = read_2.get("Value")
        #for fb in fb_diagram.function_blocks:
            # print("FBD: " + fb.name)    
    
    
    
    #print("Current FB = " + FB.name)   
    
    for read in root.iter("DataConnections"):
        for con in read.iter("Connection"):
            fb_destination = fb_diagram.get_fb(con.get("Destination").split(".")[0])
            if fb_destination != None:
                # print("Data FB Destination = " + fb_destination.name)
                var_destination = fb_destination.variable_get(con.get("Destination").split(".")[1])
            else:
                var_destination = FB.variable_get(con.get("Destination"))
                
            # print("Data Destination = " + var_destination.name) 
                
            fb_source = fb_diagram.get_fb(con.get("Source").split(".")[0])
            if fb_source != None:
                # print("Data FB Source = " + fb_source.name)
                var_source = fb_source.variable_get(con.get("Source").split(".")[1])
            else:
                var_source = FB.variable_get(con.get("Source"))
                
            # print("Data Source = " + var_source.name)  
              
                           
            fb_diagram.connect_variables(var_source, var_destination, False)
            
    for read in root.iter("EventConnections"):
        for con in read.iter("Connection"):
            fb_destination = fb_diagram.get_fb(con.get("Destination").split(".")[0])
            if fb_destination != None:
                # print("Event FB Destination = " + fb_destination.name)
                event_destination = fb_destination.event_get(con.get("Destination").split(".")[1])
            else:
                event_destination = FB.event_get(con.get("Destination"))
                
            # print("Event Destination = " + event_destination.name)       
                
            fb_source = fb_diagram.get_fb(con.get("Source").split(".")[0])
            if fb_source != None:
                # print("Event FB Source = " + fb_source.name)
                event_source = fb_source.event_get(con.get("Source").split(".")[1])
            else:
                event_source = FB.event_get(con.get("Source"))
                
            # print("Event Source = " + event_source.name)  
            
                
            fb_diagram.connect_events(event_source, event_destination, False)                
            
    for read in root.iter("ECState"):
        name = read.get("Name")
        comment = read.get("Comment")
        x_cord = abs(float(read.get("x"))/2)
        y_cord = abs(float(read.get("y"))/2)
        if x_cord <= 50:
            x_cord += 50  # For some reason coordinates below 48 behave weird in the drawing area (putting 50 just to make sure)
        if y_cord <= 50:
            y_cord += 50 
        ECC.state_add(name, x=x_cord, y=y_cord, comment=comment, fb=FB)
        state = ECC.state_get(name)
        if name == "START":
            state.set_initial_state()
            ECC.current_state = state
        for read_2 in read.iter("ECAction"):
            alg_name = read_2.get("Algorithm")
            output_event = FB.event_get(read_2.get("Output"))
            action = state.action_add()
            action.state = state
            if output_event is not None:
                action.output_event = output_event
            # print(f'XML -> STATE = {state.name}')
            ECC.actions.add(action)
            # print(f'XML -> {action.state.name}')
            if alg_name is not None:
                if FB.algorithm_get(alg_name) is not None:
                    algorithm = FB.algorithm_get(alg_name)
                    action.algorithm = algorithm
                else:
                    algorithm = action.algorithm_add(name=alg_name)
                FB.algorithms.add(algorithm)

    transitions = list()
    for read in root.iter("ECTransition"):
        transition_list = list()
        transition = read.get("Condition")
        if transition[0] == "[":  # [N = 0]
            transition = transition.replace("[", "") 
            transition = transition.replace("]", "") 
            transition = transition.replace("(", " ")
            transition = transition.replace(")", " ")
            transition_list = transition.split()
            transition_list.insert(0, None) 
        elif "[" in transition:
            transition = transition.replace("[", " ")
            transition = transition.replace("]", " ")
            transition = transition.replace("(", " ")
            transition = transition.replace(")", " ")
            transition_list = transition.split() 

        elif transition[0] != "1":
            transition = transition.replace("[", " ")
            transition = transition.replace("]", " ")
            transition_list = transition.split()
        else:
            transition_list = ["1"]

        transition_list.append(read.get("Destination")) ## E.G: [1, to_state, from_state] -> 3; [None, N, =, 0 , to_state, from_state] -> 5; [CU, CV, &lt;, 65535] -> 4;
        transition_list.append(read.get("Source"))  # Condition 
        transition_list.append(read.get("Comment"))
        transition_list.append(read.get("x"))
        transition_list.append(read.get("y"))
        transitions.append(transition_list)
        

    for transition in transitions:
        if transition[0] == "1" and len(transition) == 6: # (1, from_state, to_state)
            from_state = ECC.state_get(transition[2])
            to_state = ECC.state_get(transition[1])
            comment = transition[3]
            x, y = transition[4], transition[5]
            trans = Transition(comment = comment, x=x, y=y, from_state=from_state, to_state=to_state,event=Event(),
                                                condition=(None, 1, None, None))
            from_state.transition_out_add(trans) # 1
            to_state.transition_in_add(trans)
            ECC.transition_add(trans)
            #print("3")  
        
        elif transition[0] == "1" and len(transition) > 6:
            from_state = ECC.state_get(transition[5])
            to_state = ECC.state_get(transition[4])
            var = FB.variable_get(transition[1])
            operator = transition[2]
            operand = transition[3]
            comment = transition[6]
            x, y = transition[7], transition[8]
            trans = Transition(comment = comment, x=x, y=y, from_state=from_state, to_state=to_state,event=Event(),
                                                     condition=(1, var, operator, operand))
            from_state.transition_out_add(trans) # 1[CV &lt; 65535]
            to_state.transition_in_add(trans)
            ECC.transition_add(trans)
            #print("6")

        elif len(transition) == 7:
            from_state = ECC.state_get(transition[3])  
            to_state = ECC.state_get(transition[2])
            event = FB.event_get(transition[0])
            var = FB.variable_get(transition[1])
            comment = transition[4]
            x, y = transition[5], transition[6]
            if event is None:
                event = Event()
            trans = Transition(comment = comment, x=x, y=y, from_state=from_state, to_state=to_state,event=event,
                                                     condition=(event, var, "=", 1))
            from_state.transition_out_add(trans) # CU[CV = 1]
            to_state.transition_in_add(trans)
            ECC.transition_add(trans)
            #print("4")

        elif len(transition) == 8:
            from_state = ECC.state_get(transition[4])
            to_state = ECC.state_get(transition[3])
            event = FB.event_get(transition[0])
            var = FB.variable_get(transition[2])
            comment = transition[5]
            x, y = transition[6], transition[7]
            if event is None:
                event = Event()
            trans = Transition(comment = comment, x=x, y=y, from_state=from_state, to_state=to_state,event=event,
                                                     condition=(event, var, "!=", 0))
            from_state.transition_out_add(trans) # CU[CV != 0]
            to_state.transition_in_add(trans)
            ECC.transition_add(trans)
            #print("5")
            
        elif len(transition) == 9:
            #print(transition)
            from_state = ECC.state_get(transition[5])
            to_state = ECC.state_get(transition[4])
            event = FB.event_get(transition[0])
            var = FB.variable_get(transition[1])
            operator = transition[2]
            operand = transition[3]
            comment = transition[6]
            x, y = transition[7], transition[8]
            if event is None:
                event = Event()
            trans = Transition(comment = comment, x=x, y=y, from_state=from_state, to_state=to_state,event=event,
                                                     condition=(event, var, operator, operand))
            from_state.transition_out_add(trans) # CU[CV &lt; 65535]
            to_state.transition_in_add(trans)
            ECC.transition_add(trans)
            #print("6")

        elif len(transition) == 11:
            from_state = ECC.state_get(transition[7])
            to_state = ECC.state_get(transition[6])
            event = FB.event_get(transition[0])
            var = FB.variable_get(transition[1])
            operator = transition[2]
            function = transition[3] # MIN(x, y)
            function_x = transition[4]
            function_y = transition[5]
            comment = transition[8]
            x, y = transition[9], transition[10]
            operand = function + '(' + function_x + ',' + function_y + ')'
            if event is None:
                event = Event()
            trans = Transition(comment = comment, x=x, y=y, from_state=from_state, to_state=to_state,event=event,
                                                     condition=(event, var, operator, operand))
            from_state.transition_out_add(trans) # CU[CV &lt; 65535]
            to_state.transition_in_add(trans)
            ECC.transition_add(trans)
            #print("8")

        else:
            from_state = ECC.state_get(transition[2])
            to_state = ECC.state_get(transition[1])
            event = FB.event_get(transition[0])
            comment = transition[3]
            x, y = transition[4], transition[5]
            if event is None:
                event = Event()
            trans = Transition(comment = comment, x=x, y=y, from_state=from_state, to_state=to_state,event=event,
                                                     condition=(event, None, None, None))
            from_state.transition_out_add(trans) # EI
            to_state.transition_in_add(trans)
            ECC.transition_add(trans)
            #print("6")

    for read in root.iter("Algorithm"): 
        name = read.get("Name")
        comment = read.get("Comment")
        for read_2 in read.iter("ST"):
            algorithm_str = read_2.get("Text")
            algorithm = FB.algorithm_get(name)
            algorithm.comment = comment
            algorithm.algorithm_str = algorithm_str
            FB.map_algorithm_states[algorithm] = set()
            for state in ECC.states:
                for action in state.actions:
                    if algorithm.name == action.algorithm.name:
                        FB.algorithm_state_add(state, algorithm)

                        
          
	
    for read in root.iter("Service"):
        FB.service = Service(comment=read.get("Comment"), interfaces=(read.get("LeftInterface"), read.get("RightInterface")))
        for sequence in read.iter("ServiceSequence"):
            service_sequence = ServiceSequence(comment=sequence.get("Comment"), name=sequence.get("Name"))
            
            for transaction in sequence.iter("ServiceTransaction"):
                service_transaction = ServiceTransaction()
                
                for input in transaction.iter("InputPrimitive"):
                    service_transaction.input_primitive = (input.get("Event"), input.get("Interface"), input.get("Parameters"))
                
                for output in transaction.iter("OutputPrimitive"):
                    service_transaction.output_primitive = (output.get("Event"), output.get("Interface"), output.get("Parameters"))
                    
                service_sequence.add_service_transaction(service_transaction)
                
            FB.service.add_service_sequence((sequence.get("Name"), service_sequence))

    FB.fb_network = fb_diagram
    #for fb in fb_import_list:
        # print(fb.name)  
    #FB._str_service()
    # print("done")
    return FB, fb_diagram

def convert_xml_system(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    fb_import_list = set()
    for read in root.iter("System"):
        system_name = read.get("Name")
        system_comment = read.get("Comment")
        SYSTEM = System(system_name, system_comment)
    
    for read in root.iter("Application"):
        application_name = read.get("Name")
        application_comment = read.get("Comment")
        app = Application(application_name, application_comment)
        
        for read_1 in read.iter("SubAppNetwork"):
            fb_diagram = Composite()
            for read_2 in read_1.iter("FB"):
                fb_name = read.get("Name")
                fb_type = read.get("Type")
                fb_comment = read.get("Comment")
                fb_x = read.get("x")
                fb_y = read.get("y")
                fb = FunctionBlock(fb_name, fb_comment, fb_type, fb_x, fb_y)
                for read_3 in read_2.iter("Parameter"):
                        var = fb.variable_get(read_3.get("Name"))
                        var.value = read_3.get("Value")
                fb_diagram.add_function_block(fb)
                
            for read_2 in read_1.iter("EventConnections"):
                for con in read_2.iter("Connection"):
                    fb_destination = fb_diagram.get_fb(con.get("Destination").split(".")[0])
                    if fb_destination != None:
                        event_destination = fb_destination.event_get(con.get("Destination").split(".")[1])     
                        
                    fb_source = fb_diagram.get_fb(con.get("Source").split(".")[0])
                    if fb_source != None:
                        event_source = fb_source.event_get(con.get("Source").split(".")[1])                        
                        
                    fb_diagram.connect_events(event_source, event_destination, False)
            
            for read_2 in read_1.iter("DataConnections"):
                for con in read_2.iter("Connection"):
                    fb_destination = fb_diagram.get_fb(con.get("Destination").split(".")[0])
                    if fb_destination != None:
                        var_destination = fb_destination.variable_get(con.get("Destination").split(".")[1])
                                                
                    fb_source = fb_diagram.get_fb(con.get("Source").split(".")[0])
                    if fb_source != None:
                        var_source = fb_source.variable_get(con.get("Source").split(".")[1])                                            
                                
                    fb_diagram.connect_variables(var_source, var_destination, False)
            
            app.subapp_network = fb_diagram 
            
        SYSTEM.application_add(app)
                
                
    for read in root.iter("Device"):
        device_name = read.get("Name")
        device_type = read.get("Type")
        device_comment = read.get("Comment")
        device_x = read.get("x")
        device_y = read.get("y")
        DEVICE = Device(device_name, device_type, device_comment, device_x, device_y)
        
        for read_1 in read.iter("Resource"):
            resource_name = read_1.get("Name")
            resource_type = read_1.get("Type")
            resource_comment = read_1.get("Comment")
            resource_x = read_1.get("x")
            resource_y = read_1.get("y")
            
            for read_2 in read_1.iter("FBNetwork"):
                fb_diagram = Composite()
                for read_3 in read_2.iter("FB"):
                    fb,_ = convert_xml_basic_fb('Projects/fbe/src/models/fb_library/'+read_1.get("Type")+'.fbt')  # Blocks declared in FBNetwork must be inside src/models/diac_library
                    # print("Network FB = "+fb.name)
                    fb.change_pos(float(read_3.get("x"))/3, float(read_3.get("y"))/4)
                    fb.name = read_3.get("Name")
                    fb.type = read_3.get("Type")
                    fb_diagram.add_function_block(fb)
                    fb_import_list.add(fb)
                    for read_3 in read_2.iter("Parameter"):
                        var = fb.variable_get(read_3.get("Name"))
                        var.value = read_3.get("Value")
            
            RESOURCE = Resource(resource_name, resource_type, resource_comment, resource_x, resource_y, fb_diagram)
            RESOURCE.device = DEVICE
            DEVICE.resource_add(RESOURCE)
        
        DEVICE.system = SYSTEM
        SYSTEM.device_add(DEVICE)
    
    for read in root.iter("Mapping"):
        source_app = SYSTEM.application_get(read.get("From").split(".")[0])
        source_fb = source_app.subapp_network.get_fb(read.get("From").split(".")[1])
        source = (source_app, source_fb)  # (app, F_ADD)
        destination_resource = SYSTEM.device_get(read.get("To").split(".")[0]).resource_get(read.get("To").split(".")[1])
        destination_fb = destination_resource.fb_network.get_fb(read.get("To").split(".")[2])
        destination = (destination_resource, destination_fb)  # (EMB_RES, F_ADD)
        SYSTEM.mapping_add((source, destination))  # Adds the tuple ((app, F_ADD), (EMB_RES, F_ADD))

    return SYSTEM