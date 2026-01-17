
import json
import sys
from blockinput import BlockInput
import utilities

MATH_OPS = {'abs':'abs', 'floor':'floor', 'ceiling':'ceil', 'sqrt':'sqrt', 'sin':'sin', 'cos':'cos', 'tan':'tan', 'asin':'asin', 'acos':'acos', 'atan':'atan', 'ln':'ln', 'log':'log','e ^':'antiln', '10 ^':'antilog'}

# only hats can be used at the start of a script in goboscript
HATS = {'event_whenflagclicked','event_whenkeypressed','event_whenthisspriteclicked','event_whenstageclicked','event_whenbackdropswitchesto','event_whengreaterthan','event_whenbroadcastreceived','control_start_as_clone','procedures_definition'}

sys.setrecursionlimit(2000) # I think there's something wrong if you need a single script with more than 2000 blocks


def recursive_block_search(target, current_block_id, shared_project_data) -> str:
    """Search a tree of blocks and return a string of indented goboscript code"""

    attached_comments = {}
    for comment in target['comments'].values():
        if comment.get('blockId', None) is not None:
            try:
                attached_comments[comment['blockId']] = bytes(comment['text'], "utf-8").decode("unicode_escape")
            except:
                pass

    is_commented_out = False
    if target['blocks'][current_block_id] is not None and target['blocks'][current_block_id]['opcode'] not in HATS:
        is_commented_out = True

    np = shared_project_data['name_pool']

    def valid_name(name, usage):
        return utilities.validate_name(name)
        #return np.get_valid_name(name, target['name'], usage)

    def block_search(current_block_id: str, indent_level=0) -> str:
        if current_block_id is None or current_block_id == "": 
            return ""

        indent = '    ' * max(0, indent_level) # make the string of characters
        if is_commented_out: indent = '# ' + indent # if commented out, prepend #

        block = target['blocks'][current_block_id]
        
        opcode = block['opcode']
        inputs = block['inputs']
        fields = block['fields']
        next = block['next']
        
        
        def parse_input(input_value) -> tuple:
            """Helper to handle block inputs. Returns a string with the general type of input it was."""
            
            def _get_slot_value(slot_contents: list) -> tuple:
                """Get a readable value from a slot."""
                
                if 3 < slot_contents[0] <= 8:
                    return (json.dumps(slot_contents[1]), 'number')
                if slot_contents[0] == 9:
                    return (json.dumps(slot_contents[1]), 'color')
                if slot_contents[0] == 10:
                    return (json.dumps(slot_contents[1]), 'text')
                if slot_contents[0] == 11: # broadcasts are [11, name, id]
                    return (json.dumps(slot_contents[1]), 'broadcast_name') # slot_contents[2]
                if slot_contents[0] == 12: 
                    return (valid_name(slot_contents[1], 'var'), 'var_name')
                if slot_contents[0] == 13:
                    return (valid_name(slot_contents[1], 'list'), 'list_name')
                raise Exception(f'unknown enum {slot_contents[0]}')

            bi = BlockInput.from_list(input_value)

            if isinstance(bi.block_slot, str):
                return (block_search(bi.block_slot, indent_level=0), 'block') # is block
            
            if bi.block_slot is not None:
                return _get_slot_value(bi.block_slot)

            if isinstance(bi.shadow_slot, str):
                return (block_search(bi.shadow_slot, indent_level=0), 'block') # is shadow block
            
            if bi.shadow_slot is not None:
                return _get_slot_value(bi.shadow_slot)

            return ("", None) # completely empty
        
        
        def get_block_in_input(input_name) -> dict | None:
            if input_name not in inputs: return None

            bi = BlockInput.from_list(inputs[input_name])
            if isinstance(bi.block_slot, str):
                return target['blocks'].get(bi.block_slot, None)
            return None

        def next_block(include_semicolon=True):
            """Helper that assumes the current block ends with semicolon and new line, and next block is at `next` and at the same indent"""
            next_block_data = block_search(next, indent_level)
            
            string_output = ''
            if include_semicolon: string_output += ';'
            
            if next_block_data == '': 
                return string_output
            
            if next in attached_comments:
                comment_lines = [f"{indent}# {s}" for s in attached_comments[next].split('\n')]
                string_output += '\n' + '\n'.join(comment_lines)

            string_output += '\n' + next_block_data
            return string_output


        def input(input_name) -> str:
            """Helper that assumes the input is a key in the input dict"""
            if input_name not in inputs: return ""

            return parse_input(inputs[input_name])[0]


        def input_num(input_name) -> str:
            """Helper that assumes the input is a key in the input dict with a possible numeric value"""
            if input_name not in inputs: return ""

            text, input_type = parse_input(inputs[input_name])
            if input_type == 'number':
                # try to convert string into number by removing the quotes
                stripped = text.strip("\"")
                try:
                    _ = float(stripped)
                    return stripped # is a valid number
                except:
                    return text # don't strip quotes, not a valid number

            return text


        def input_with_reporter(input_name) -> str:
            """Helper that assumes the input is solely a reporter block (such as the boolean condition of an if block)"""
            if input_name not in inputs: return "false"

            bi = BlockInput.from_list(inputs[input_name])
            if isinstance(bi.block_slot, str):
                return block_search(bi.block_slot, indent_level+1)
            
            return ""
        
        def input_with_stack(input_name) -> str:
            """Helper that assumes the input is solely a stack block (such as nested in a C shaped block)"""
            if input_name not in inputs: return ""

            bi = BlockInput.from_list(inputs[input_name])
            if isinstance(bi.block_slot, str):
                return block_search(bi.block_slot, indent_level+1)
            
            return ""
            


        def field(field_name, fallback=""):
            """Helper to get the value of a field, fallback if nonexistent"""
            if field_name not in fields: return fallback
            f = fields[field_name]
            if isinstance(f, list): f = f[0] # broadcasts stored as a list
            return json.dumps(f)

        def not_implemented():
            print(f'{opcode} is not implemented in goboscript')


        match opcode:
            
            # LOOKS

            case 'looks_say':
                return f"{indent}say {input('MESSAGE')}" + next_block()
            
            case 'looks_sayforsecs':
                return f"{indent}say {input('MESSAGE')}, {input_num('SECS')}" + next_block()

            case 'looks_think':
                return f"{indent}think {input('MESSAGE')}" + next_block()
            
            case 'looks_thinkforsecs':
                return f"{indent}think {input('MESSAGE')}, {input_num('SECS')}" + next_block()

            case 'looks_show':
                return f"{indent}show" + next_block()

            case 'looks_hide':
                return f"{indent}hide" + next_block()
            
            case 'looks_switchcostumeto':
                return f"{indent}switch_costume {input('COSTUME')}" + next_block()
            
            case 'looks_costume':
                return field('COSTUME')
            
            case 'looks_switchbackdropto':
                return f"{indent}switch_backdrop {input('BACKDROP')}" + next_block()
            
            case 'looks_backdrops':
                return field('BACKDROP')

            case 'looks_nextcostume':
                return f"{indent}next_costume" + next_block()

            case 'looks_nextbackdrop':
                return f"{indent}next_backdrop" + next_block()

            case 'looks_cleargraphiceffects':
                return f"{indent}clear_graphic_effects" + next_block()

            case 'looks_seteffectto':
                return f"{indent}set_{fields['EFFECT'][0].lower()}_effect {input('VALUE')}" + next_block()

            case 'looks_seteffectto':
                return f"{indent}change_{fields['EFFECT'][0].lower()}_effect {input_num('CHANGE')}" + next_block()
            
            case 'looks_setsizeto':
                return f"{indent}set_size {input('SIZE')}" + next_block()

            case 'looks_changesizeby':
                return f"{indent}change_size {input_num('CHANGE')}" + next_block()

            case 'looks_gotofrontback':
                return f"{indent}goto_{fields['FRONT_BACK'][0].lower()}" + next_block()
            
            case 'looks_goforwardbackwardlayers':
                return f"{indent}go_{fields['FORWARD_BACKWARD'][0].lower()} {input_num('NUM')}" + next_block()

            case 'looks_costumenumbername':
                return f"costume_{fields['NUMBER_NAME'][0].lower()}()"

            case 'looks_backdropnumbername':
                return f"backdrop{fields['NUMBER_NAME'][0].lower()}()"

            case 'looks_size':
                return "size()"


            # SOUNDS

            case 'sound_playuntildone':
                return f"{indent}play_sound_until_done {input('SOUND_MENU')}" + next_block()

            case 'sound_play':
                return f"{indent}start_sound {input('SOUND_MENU')}" + next_block()

            case 'sound_sounds_menu':
                return field('SOUND_MENU')
            
            case 'sound_stopallsounds':
                return f"{indent}stop_all_sounds" + next_block()
            
            case 'sound_changeeffectby':
                return f"{indent}change_{fields['EFFECT'][0].lower()}_effect {input_num('VALUE')}" + next_block()

            case 'sound_seteffectto':
                return f"{indent}set_{fields['EFFECT'][0].lower()}_effect {input_num('VALUE')}" + next_block()

            case 'sound_cleareffects':
                return f"{indent}clear_sound_effects" + next_block()

            case 'sound_changevolumeby':
                return f"{indent}change_volume {input_num('VOLUME')}" + next_block()

            case 'sound_setvolumeto':
                return f"{indent}set_volume {input_num('VOLUME')}" + next_block()

            case 'sound_volume':
                return "volume()"


            # EVENTS
            
            case 'event_whenflagclicked':
                return f"onflag {{\n{block_search(next, indent_level+1)}\n}}"
            
            case 'event_whenkeypressed':
                return f"onkey {field('KEY_OPTION', "")} {{\n{block_search(next, indent_level+1)}\n}}"

            case 'event_whenthisspriteclicked' | 'event_whenstageclicked':
                return f"onclick {{\n{block_search(next, indent_level+1)}\n}}"
            
            case 'event_whenbackdropswitchesto':
                return f"onbackdrop {field('BACKDROP', "")} {{\n{block_search(next, indent_level+1)}\n}}"
            
            case 'event_whengreaterthan':
                if fields['WHENGREATERTHANMENU'][0] == 'LOUDNESS': 
                    return f"onloudness {input_num('VALUE')} {{\n{block_search(next, indent_level+1)}\n}}"
                elif fields['WHENGREATERTHANMENU'][0] == 'TIMER':
                    return f"ontimer {input_num('VALUE')} {{\n{block_search(next, indent_level+1)}\n}}"
                else:
                    return "# FAILED {opcode}"
            
            case 'event_whenbroadcastreceived':
                return f"on {field('BROADCAST_OPTION')} {{\n{block_search(next, indent_level+1)}\n}}"
            
            case 'event_broadcast':
                return f"{indent}broadcast {input('BROADCAST_INPUT')}" + next_block()
            
            case 'event_broadcastandwait':
                return f"{indent}broadcast_and_wait {input('BROADCAST_INPUT')}" + next_block()


            
            # MOTION

            case 'motion_movesteps':
                return f"{indent}move {input_num('STEPS')}" + next_block()

            case 'motion_gotoxy':
                return f"{indent}goto {input_num('X')}, {input_num('Y')}" + next_block()
            
            case 'motion_goto':
                _target = input('TO')
                if _target == '"_mouse_"': return f"{indent}goto_mouse_pointer" + next_block()
                if _target == '"_random_"': return f"{indent}goto_random_position" + next_block()
                return f"{indent}goto {_target}" + next_block()
            
            case 'motion_goto_menu':
                return field('TO')

            case 'motion_turnright':
                return f"{indent}turn_right {input_num('DEGREES')}" + next_block()

            case 'motion_turnleft':
                return f"{indent}turn_left {input_num('DEGREES')}" + next_block()

            case 'motion_pointindirection':
                return f"{indent}point_in_direction {input_num('DIRECTION')}" + next_block()

            case 'motion_pointtowards':
                _target = input('TOWARDS')
                if _target == '"_mouse_"': return f"{indent}point_towards_mouse_pointer" + next_block()
                if _target == '"_random_"': return f"{indent}point_towards_random_direction" + next_block()
                return f"{indent}point_towards {_target}" + next_block()

            case 'motion_pointtowards_menu':
                return field('TOWARDS')
            
            case 'motion_glidesecstoxy':
                return f"{indent}glide {input_num('X')}, {input_num('Y')}, {input_num('SECS')}" + next_block()

            case 'motion_glideto':
                _target = input('TO')
                if _target == '"_mouse_"': return f"{indent}glide_to_mouse_pointer({input_num('SECS')})" + next_block()
                if _target == '"_random_"': return f"{indent}glide_to_random_position({input_num('SECS')})" + next_block()
                return f"{indent}glide {_target}, {input_num('SECS')}" + next_block()
                
            case 'motion_glideto_menu':
                return field('TO')
            
            case 'motion_ifonedgebounce':
                return f"{indent}if_on_edge_bounce" + next_block()

            case 'motion_setrotationstyle':
                _style = {'left-right':'left_right', 'don\'t rotate':'do_not_rotate', 'all around':'all_around'}[fields['STYLE'][0]]
                return f"set_rotation_style_{_style}"

            case 'motion_changexby':
                return f"{indent}change_x {input_num('DX')}" + next_block()

            case 'motion_setx':
                return f"{indent}set_x {input_num('X')}" + next_block()
            
            case 'motion_changeyby':
                return f"{indent}change_y {input_num('DY')}" + next_block()

            case 'motion_sety':
                return f"{indent}set_y {input_num('Y')}" + next_block()

            case 'motion_xposition':
                return "x_position()"

            case 'motion_yposition':
                return "y_position()"

            case 'motion_direction':
                return "direction()"


            # CONTROL

            case 'control_repeat':
                return f"{indent}repeat {input_num('TIMES')} {{\n{input_with_stack('SUBSTACK')}\n{indent}}}" + next_block(False)

            case 'control_repeat_until':
                return f"{indent}until {input_with_reporter('CONDITION')} {{\n{input_with_stack('SUBSTACK')}\n{indent}}}" + next_block(False)

            case 'control_while':
                return f"{indent}until not {input_with_reporter('CONDITION')} {{\n{input_with_stack('SUBSTACK')}\n{indent}}}" + next_block(False)

            case 'control_for_each':
                _var_name = valid_name(fields['VARIABLE'][0], 'var')
                return f"{indent}{_var_name} = 1;\n{indent}repeat {input_num('VALUE')} {{\n{input_with_stack('SUBSTACK')}\n{indent}    {_var_name}++;\n{indent}}}" + next_block(False)

            case 'control_forever':
                return f"{indent}forever {{\n{input_with_stack('SUBSTACK')}\n{indent}}}"

            case 'control_wait':
                return f"{indent}wait {input_num('DURATION')}" + next_block()

            case 'control_wait_until':
                return f"{indent}wait_until {input_with_reporter('CONDITION')}" + next_block()

            case 'control_if':
                # TODO convert to %if when input is blank
                return f"{indent}if {input_with_reporter('CONDITION')} {{\n{input_with_stack('SUBSTACK')}\n{indent}}}" + next_block(False)
            
            case 'control_if_else':
                # TODO elif
                return f"{indent}if {input_with_reporter('CONDITION')} {{\n{input_with_stack('SUBSTACK')}\n{indent}}} else {{\n{input_with_stack('SUBSTACK2')}\n{indent}}}" + next_block(False)
            
            case 'control_stop':
                _stop_option = fields['STOP_OPTION'][0]
                if _stop_option == 'this script':
                    return f"{indent}stop_this_script;"
                
                elif _stop_option == 'other scripts in sprite':
                    return f"{indent}stop_other_scripts" + next_block()
                
                return f"{indent}stop_all;"

            case 'control_create_clone_of':
                return f"{indent}clone {input('CLONE_OPTION')}" + next_block()
                
            case 'control_create_clone_of_menu':
                return f"{field('CLONE_OPTION')}"
            
            case 'control_delete_this_clone':
                return f"{indent}delete_this_clone;"

            case 'control_start_as_clone':
                return f"onclone {{\n{block_search(next, indent_level+1)}\n}}"
            
            case 'control_get_counter':
                return "control_counter"

            case 'control_incr_counter':
                return "control_counter++" + next_block()
               
            case 'control_clear_counter':
                return "control_counter = 0" + next_block()
            
            case 'control_all_at_once':
                return f"{indent}# control_all_at_once:\n{input_with_stack('SUBSTACK')}" + next_block(False)
            

            # SENSING

            case 'sensing_touchingobject':
                _target = input('TOUCHINGOBJECTMENU')
                if _target == '"_mouse_"': return "touching_mouse_pointer()"
                elif _target == '"_edge_"': return "touching_edge()"
                return f"touching({input('TOUCHINGOBJECTMENU')})"

            case 'sensing_touchingobjectmenu':
                return field('TOUCHINGOBJECTMENU')
            
            case 'sensing_touchingcolor':
                return f"touching_color({input('COLOR')})"
            
            case 'sensing_coloristouchingcolor':
                return f"color_is_touching_color({input('COLOR')}, {input('COLOR2')})"
            
            case 'sensing_distanceto':
                _target = input('DISTANCETOMENU')
                if _target == '"_mouse_"': return "distance_to_mouse_pointer()"
                return f"distance_to({target})"

            case 'sensing_distancetomenu':
                return field('DISTANCETOMENU')
            
            case 'sensing_askandwait':
                return f"{indent}ask {input('QUESTION')}" + next_block()
            
            case 'sensing_answer':
                return "answer()"

            case 'sensing_keypressed':
                return f"key_pressed({input('KEY_OPTION')})"
            
            case 'sensing_keyoptions':
                return field('KEY_OPTION')
            
            case 'sensing_mousedown':
                return "mouse_down()"
            
            case 'sensing_mousex':
                return "mouse_x()"
            
            case 'sensing_mousey':
                return "mouse_y()"
            
            case 'sensing_setdragmode':
                if fields['DRAG_MODE'][0] == 'draggable':
                    return f"{indent}set_drag_mode_draggable" + next_block()
                return f"{indent}set_drag_mode_not_draggable" + next_block()

            case 'sensing_loudness':
                return "loudness()"
            
            case 'sensing_timer':
                return "timer()"
            
            case 'sensing_resettimer':
                return f"{indent}reset_timer" + next_block()

            case 'sensing_of':
                return f"({input('OBJECT')}.{field('PROPERTY')})"

            case 'sensing_of_object_menu':
                return field('OBJECT')
            
            case 'sensing_current':
                _current_menu = fields['CURRENTMENU'][0]
                _current_str = {'YEAR':'year', 'MONTH':'month', 'DATE':'date', 'DAYOFWEEK':'day_of_week', 'HOUR':'hour', 'MINUTE':'minute', 'SECOND':'second'}[_current_menu]
                return f"current_{_current_str}()"

            case 'sensing_dayssince2000':
                return "days_since_2000()"
            
            case 'sensing_username':
                return "username()"


            # OPERATORS

            case 'operator_add':
                return f"({input_num('NUM1')}+{input_num('NUM2')})"

            case 'operator_subtract':
                return f"({input_num('NUM1')}-{input_num('NUM2')})"

            case 'operator_multiply':
                return f"({input_num('NUM1')}*{input_num('NUM2')})"

            case 'operator_divide':
                return f"({input_num('NUM1')}/{input_num('NUM2')})"
            

            case 'operator_mod':
                return f"({input_num('NUM1')}%{input_num('NUM2')})"

            case 'operator_round':
                return f"round({input_num('NUM')})"


            case 'operator_lt':
                return f"({input('OPERAND1')} < {input('OPERAND2')})"

            case 'operator_gt':
                return f"({input('OPERAND1')} > {input('OPERAND2')})"

            case 'operator_equals':
                return f"({input('OPERAND1')} == {input('OPERAND2')})"
            
            case 'operator_and':
                return f"({input_with_reporter('OPERAND1')} and {input_with_reporter('OPERAND2')})"
            
            case 'operator_or':
                return f"({input_with_reporter('OPERAND1')} or {input_with_reporter('OPERAND2')})"

            case 'operator_not':
                return f"(not {input_with_reporter('OPERAND')})"


            case 'operator_join':
                return f"({input('STRING1')} & {input('STRING2')})"
            
            case 'operator_letter_of':
                return f"{input('STRING')}[{input_num('LETTER')}]"
            
            case 'operator_length':
                return f"length({input('STRING')})"
            
            case 'operator_contains':
                return f"contains({input('STRING1')}, {input('STRING2')})"
                #return f"({input('STRING2')} in {input('STRING1')})" # reversed inputs
            
            case 'operator_mathop':
                _op = fields['OPERATOR'][0]
                return f"{MATH_OPS[_op]}({input_num('NUM')})"

            case 'operator_random':
                # pick random might need strings for floating point number picking
                # future improvement would be to check if that's needed
                return f"random({input('FROM')}, {input('TO')})"


            # DATA

            case 'data_setvariableto':
                return f"{indent}{valid_name(fields['VARIABLE'][0], 'var')} = {input('VALUE')}" + next_block()

            case 'data_changevariableby':
                return f"{indent}{valid_name(fields['VARIABLE'][0], 'var')} += {input_num('VALUE')}" + next_block()

            case 'data_showvariable':
                return f"{indent}show {valid_name(fields['VARIABLE'][0], 'var')}" + next_block()

            case 'data_hidevariable':
                return f"{indent}hide {valid_name(fields['VARIABLE'][0], 'var')}" + next_block()

            case 'data_addtolist':
                return f"{indent}add {input('ITEM')} to {valid_name(fields['LIST'][0], 'list')}" + next_block()

            case 'data_deleteoflist':
                return f"{indent}delete {valid_name(fields['LIST'][0], 'list')}[{input('INDEX')}]" + next_block()

            case 'data_deletealloflist':
                return f"{indent}delete {valid_name(fields['LIST'][0], 'list')}" + next_block()

            case 'data_insertatlist':
                return f"{indent}insert {input('ITEM')} {valid_name(fields['LIST'][0], 'list')}[{input_num('INDEX')}]" + next_block()

            case 'data_replaceitemoflist':
                return f"{indent}{valid_name(fields['LIST'][0], 'list')}[{input_num('INDEX')}] = {input('ITEM')}" + next_block()

            case 'data_itemoflist':
                return f"{valid_name(fields['LIST'][0], 'list')}[{input_num('INDEX')}]"

            case 'data_itemnumoflist': # (item # of [item] in list)
                return f"({input('ITEM')} in {valid_name(fields['LIST'][0], 'list')})" 
            
            case 'data_lengthoflist':
                return f"(length {valid_name(fields['LIST'][0], 'list')})"

            case 'data_listcontainsitem': # <list contains [item]?>
                return f"contains({valid_name(fields['LIST'][0], 'list')}, {input('ITEM')})"
                #return f"({input('ITEM')} in {valid_name(fields['LIST'][0])} > 0)" 

            case 'data_showlist':
                return f"{indent}show {valid_name(fields['LIST'][0], 'list')}" + next_block()

            case 'data_hidelist':
                return f"{indent}hide {valid_name(fields['LIST'][0], 'list')}" + next_block()


            # CUSTOM BLOCKS

            case 'procedures_definition':
                temp = f"proc {input('custom_block')} {{\n{block_search(next, indent_level+1)}\n}}"
                if temp.startswith("proc ____s comment {"): return "# proc ____s comment {}"
                return temp

            case 'procedures_prototype':
                # note that the proccode is sufficient for identifying a custom block, the argument names do not matter 
                
                _arg_names = json.loads(block['mutation']['argumentnames'])
                _validated_arg_names = [valid_name(a, 'arg') for a in _arg_names]
                
                return f"{valid_name(block['mutation']['proccode'], 'custom')} {', '.join(_validated_arg_names)}"

            case 'procedures_call':
                args = ''
                if len(block['inputs']) > 0:
                    args = f" {', '.join([input(k) for k in block['inputs'].keys()])}"
                
                proccode = block['mutation']['proccode']

                # comments
                if proccode == "// %s":
                    # remove quotes
                    args = args.strip()
                    if args[0] == '"' and args[-1] == '"': args = args[1:-1]
                    return f"{indent}# {args}" + next_block(False)
                
                # debug blocks
                if proccode == "\u200B\u200Blog\u200B\u200B %s":
                    return f"{indent}log{args}" + next_block()
                if proccode == "\u200B\u200Bwarn\u200B\u200B %s":
                    return f"{indent}warn{args}" + next_block()
                if proccode == "\u200B\u200Berror\u200B\u200B %s":
                    return f"{indent}error{args}" + next_block()
                if proccode == "\u200B\u200Bbreakpoint\u200B\u200B":
                    return f"{indent}breakpoint{args}" + next_block()
                
                return f"{indent}{valid_name(proccode, 'custom')}{args}" + next_block()

            case 'argument_reporter_string_number':
                return f"${valid_name(fields['VALUE'][0], 'arg')}"
        
            case 'argument_reporter_boolean':
                # mod blocks
                if fields['VALUE'][0] == "is compiled?":
                    return "tw_is_compiled()"
                if fields['VALUE'][0] == "is TurboWarp?":
                    return "tw_is_turbowarp()"
                if fields['VALUE'][0] == "is forkphorus?":
                    return "tw_is_forkphorus()"
                
                return f"${valid_name(fields['VALUE'][0], 'arg')}"


            # PEN

            case 'pen_clear':
                return f"{indent}erase_all" + next_block()

            case 'pen_stamp':
                return f"{indent}stamp" + next_block()
            
            case 'pen_penDown':
                return f"{indent}pen_down" + next_block()
            
            case 'pen_penUp':
                return f"{indent}pen_up" + next_block()
            
            case 'pen_setPenColorToColor':
                return f"{indent}set_pen_color {input('COLOR')}" + next_block()
            
            case 'pen_changePenColorParamBy':
                _cp = input('COLOR_PARAM').strip('"')
                if _cp not in ['hue', 'saturation', 'brightness', 'transparency']:
                    print('pen_changePenColorParamBy does not support block insertion in goboscript')
                    return "# pen_changePenColorParamBy"
                
                return f"{indent}change_pen_{_cp} {input_num('VALUE')}" + next_block()
            
            case 'pen_setPenColorParamTo':
                _cp = input('COLOR_PARAM').strip('"')
                if _cp not in ['hue', 'saturation', 'brightness', 'transparency']:
                    print('pen_setPenColorParamTo does not support block insertion in goboscript')
                    return "# pen_setPenColorParamTo"
                
                return f"{indent}set_pen_{_cp} {input_num('VALUE')}" + next_block()

            case "pen_menu_colorParam":
                _cp = field('colorParam')
                if _cp == '"color"':
                    return '"hue"'
                return _cp

            case 'pen_changePenSizeBy':
                return f"{indent}change_pen_size {input_num('SIZE')}" + next_block()

            case 'pen_setPenSizeTo':
                return f"{indent}set_pen_size {input_num('SIZE')}" + next_block()

            case 'pen_setPenShadeToNumber':
                not_implemented()
                return f"{indent}set_pen_shade {input_num('SHADE')}" + next_block()
            
            case 'pen_changePenShadeBy':
                not_implemented()
                return f"{indent}change_pen_shade {input_num('SHADE')}" + next_block()


            # MISC

            case _:
                if next in target['blocks']:
                    return f"{indent}# unhandled {opcode}\n{block_search(next, indent_level)}"
                return f"# unhandled {opcode}"

    #print(current_block_id)
    result = block_search(current_block_id, indent_level=0)
    if is_commented_out and result[0] != '#':
        result = '# ' + result
    
    return result



if __name__ == '__main__':
    pass
    
    #print(valid_name('1test hello'))