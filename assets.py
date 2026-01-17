
import os
from collections import defaultdict
import utilities as utils

def get_remapped_costume_names(project_data):
    """Return a dict of costume names with keys as md5 file name (with extension), and values as desired relative project path (with extension)"""

    # accumulate names
    costume_uses = defaultdict(list)
    for target in project_data['targets']:
        for costume in target['costumes']:
            costume_uses[costume['md5ext']].append(costume['name'])
    
    remapped_costume_names = {}

    # copy
    for target in project_data['targets']:
        for costume in target['costumes']:
            
            if len(costume_uses[costume['md5ext']]) == 1:
                # unique and can be stored in sprite folder
                file_name = f'{utils.valid_file_name(costume['name'])}.{costume['dataFormat']}'
                new_path = os.path.join('costumes', target['name'], file_name)

                remapped_costume_names[costume['md5ext']] = new_path
            
            elif costume['md5ext'] not in remapped_costume_names: 
                if len(set(costume_uses[costume['md5ext']])) == 1: # only 1 name
                    file_name = f'{utils.valid_file_name(costume['name'])}.{costume['dataFormat']}'
                else:
                    file_name = costume['md5ext']
                
                remapped_costume_names[costume['md5ext']] = os.path.join('costumes', file_name)
    
    #print(remapped_costume_names)
    return remapped_costume_names


