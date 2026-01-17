import re
import math

ALLOWED_NAME_PATTERN = re.compile('[_a-zA-Z0-9]')
DISALLOWED_NAMES = {'costumes','sounds','global','list','nowarp','onflag','onkey','onbackdrop','onloudness','ontimer','on','onclone','if','else','elif','until','forever','repeat','delete','at','add','to','insert','true','false','as','struct','enum','return','error','warn','breakpoint','local','not','and','or','in','length','round','abs','floor','ceil','sqrt','sin','cos','tan','asin','acos','atan','ln','log','antiln','antilog','move','turn_left','turn_right','goto_random_position','goto_mouse_pointer','goto','glide','glide_to_random_position','glide_to_mouse_pointer','point_in_direction','point_towards_mouse_pointer','point_towards_random_direction','point_towards','change_x','set_x','change_y','set_y','if_on_edge_bounce','set_rotation_style_left_right','set_rotation_style_do_not_rotate','set_rotation_style_all_around','say','think','switch_costume','next_costume','switch_backdrop','next_backdrop','set_size','change_size','change_color_effect','change_fisheye_effect','change_whirl_effect','change_pixelate_effect','change_mosaic_effect','change_brightness_effect','change_ghost_effect','set_color_effect','set_fisheye_effect','set_whirl_effect','set_pixelate_effect','set_mosaic_effect','set_brightness_effect','set_ghost_effect','clear_graphic_effects','show','hide','goto_front','goto_back','go_forward','go_backward','play_sound_until_done','start_sound','stop_all_sounds','change_pitch_effect','change_pan_effect','set_pitch_effect','set_pan_effect','change_volume','set_volume','clear_sound_effects','broadcast','broadcast_and_wait','wait','wait_until','stop_all','stop_this_script','stop_other_scripts','delete_this_clone','clone','ask','set_drag_mode_draggable','set_drag_mode_not_draggable','reset_timer','erase_all','stamp','pen_down','pen_up','set_pen_color','change_pen_size','set_pen_size','set_pen_hue','set_pen_saturation','set_pen_brightness','set_pen_transparency','change_pen_hue','change_pen_saturation','change_pen_brightness','change_pen_transparency','rest','set_tempo','change_tempo','distance_to_moues_pointer','distance_to','x_position','y_position','direction','size','costume_number','costume_name','backdrop_number','backdrop_name','volume','touching_mouse_pointer','touching_edge','touching','key_pressed','mouse_down','mouse_x','mouse_y','loudness','timer','current_year','current_month','current_date','current_day_of_week','current_hour','current_minute','current_second','days_since_2000','username','touching_color','color_is_touching_color','answer','random','func'}


def validate_name(name: str):
    """Make a variable, list, or custom block name valid for goboscript. Removes special characters."""

    new_name = ''
    for char in name:
        if char.isascii():
            if re.match(ALLOWED_NAME_PATTERN, char):
                new_name += char
            else: new_name += '_'
        else: 
            char.encode()
            new_name += f"0x{ord(char):06X}" # padded hexadecimal representing special character
    
    if (not new_name) or new_name[0].isnumeric() or new_name in DISALLOWED_NAMES:
        new_name = '_' + new_name

    return new_name


def hash_stringified(value):
    CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    value = hash(value)
    result = ''
    for _ in range(5):
        result = CHARS[value % 62] + result
        value = math.floor(value / 62)

    return result


class NamePool():
    """A database of names to prevent duplicates as goboscript has a more restrictive character set."""
    
    def __init__(self):
        self.pool = {} # key is name as found in scratch + target, value is (new name, usage)
        self.used_names = set() # keeps track of used valid names. tuples include sprite because scratch and goboscript allows names to be unique across sprites
        self.goboscript_names = [] # register of every goboscript_name, only to be read from.

    # each entry needs source name (key), usage, target (key), mapped name (key)

    def get_valid_name(self, scratch_name: str, usage='var', target='stage'):
        if target is None: target = 'stage'

        if target != 'stage': # search sprite first for local name
            _found = self.pool.get((scratch_name, usage, target), None)
            if _found is not None: return _found
        
        _found = self.pool.get((scratch_name, usage, 'stage'), None)
        if _found is not None: return _found
        
        # no exact matching name was found, register a new one and return it
        # to register, first find a validated name that is not in use in the current sprite.
        # first check if the validated name unmodified has been used.

        proposed_name = validate_name(scratch_name)
        if target != 'stage':
            if (proposed_name, target) not in self.used_names and (proposed_name, 'stage') not in self.used_names:
                self.used_names.add((proposed_name, target))
                self.pool[(scratch_name, usage, target)] = proposed_name
                return proposed_name
        
        if (proposed_name, 'stage') not in self.used_names:
            self.used_names.add((proposed_name, 'stage'))
            self.pool[(scratch_name, usage, 'stage')] = proposed_name
            return proposed_name
        
        # the proposed name is in use, finally generate a random new one

        proposed_name = validate_name(scratch_name) + '_' + hash_stringified((scratch_name, usage, target))
        self.used_names.add((proposed_name, target))
        self.pool[(scratch_name, usage, target)] = proposed_name
        return proposed_name




def valid_file_name(name: str):
    """Convert a name into a valid file name"""

    # Define invalid characters for filenames across all platforms
    replacement = '_'
    sanitised = re.sub(r'[<>:"/\\|?*]', replacement, name) # replace invalid characters

    sanitised = sanitised.rstrip(". ") # remove trailing dots and spaces (invalid in Windows)

    # check if the filename matches a reserved name and append character to make it not so
    if sanitised.upper() in {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}:
        sanitised += replacement

    if not sanitised: sanitised = replacement # ensure the filename is not empty

    return sanitised


if __name__ == '__main__':
    #print(valid_file_name('.this is a test.! .'))

    np = NamePool()

    print(np.get_valid_name('this!', 'var', 'stage'))
    print(np.get_valid_name('this!', 'var', 'a'))
    print(np.get_valid_name('this!', 'custom', 'stage')) # remap to this_1, already exists in stage
    print(np.get_valid_name('this!', 'custom', 'a')) # remap to this_1, already exists in a

    #print(np.pool, np.used_names)
    print(np.get_valid_name('this_', 'var', 'a')) # remap to this_2, already exists in a
    print(np.get_valid_name('this_', 'var', 'a')) # this_2, registered already
    
    print(np.get_valid_name('this_', 'var', 'stage')) # remap to this_2, already exists in a

