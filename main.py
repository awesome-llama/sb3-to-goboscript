# test

import zipfile
import json
import os

import blocks
import utilities as utils
import assets
import tw_config
import postprocess


def replace_slashes(path:str):
    return path.replace('\\', '/')


def convert_project(project_path, output_directory=None):
    """Create a goboscript project. Copies assets and blocks into a valid file structure for goboscript. Output folder is in the same path as the source sb3 file."""

    project_archive = zipfile.ZipFile(project_path, 'r')
    project_data = json.loads(project_archive.read('project.json'))

    print(f'Loaded project {project_path}')

    
    # Create project folder
    base_dir, file_name = os.path.split(project_path)
    project_name = os.path.splitext(file_name)[0]

    if output_directory is None:
        output_dir = os.path.join(base_dir, project_name)
    else:
        output_dir = os.path.join(output_directory, project_name)
    
    os.makedirs(output_dir, exist_ok=True)

    
    #######
    
    np = utils.NamePool()

    # add global vars and lists to name pool

    shared_project_data = {'name_pool':np}

    # validate sprite names
    for target in project_data['targets']:
        target['original_name'] = target['name'] # note that the name may change affecting blocks
        if target['isStage']: 
            target['name'] = 'stage'
            continue
        target['name'] = utils.valid_file_name(target['name'])

    remapped_costume_names = assets.get_remapped_costume_names(project_data)
    
    # copy now that the paths are known
    for md5ext, path in remapped_costume_names.items():
        path = os.path.join(output_dir, path)
        os.makedirs(os.path.split(path)[0], exist_ok=True)
        
        if not os.path.exists(path):
            project_archive.extract(md5ext, os.path.split(path)[0])
            os.rename(os.path.join(os.path.split(path)[0], md5ext), path)


    
    
    # first convert the scripts
    for i, target in enumerate(project_data['targets']):
        goboscript_code = []
        goboscript_code.append('# Converted from sb3 file\n')

        # list declaration (happens in all sprites)
        for var in target['lists'].values():
            goboscript_code.append(f"list {np.get_valid_name(var[0], target['name'])} = {json.dumps(var[1])};")
        if len(target['lists']) > 0:
            goboscript_code.append('')
        
        # global var declaration
        if target['isStage']:
            
            project_globals = []
            for var in target['variables'].values():
                if isinstance(var[1], str): var[1] = f'"{var[1]}"'
                project_globals.append(f"    {np.get_valid_name(var[0], target['name'])} = {var[1]};")
            
            goboscript_code.append('on "reset globals" {\n' + '\n'.join(project_globals) + '\n}\n\n')


        # find the costumes to use 
        costumes = []
        for costume in target['costumes']:
            md5ext = remapped_costume_names[costume['md5ext']]
            costume_name = str(costume['name'])
            
            # note there is an edge case with costume names being valid file paths
            #if costume_name == os.path.splitext(md5ext)[0]: # extensionless names must match (with no subfolders)
            #    costumes.append(f'"{replace_slashes(os.path.split(md5ext)[1])}"')
            #else:
            costumes.append(f'"{replace_slashes(md5ext)}" as {json.dumps(costume_name)}')
            
        goboscript_code.append('costumes ' + ', '.join(costumes) + ';\n')

        # enumerate over blocks of a target, if applicable replace with their translation
        for block_id, block in target['blocks'].items():
            
            if isinstance(block, list): continue # variable or list reporter, not used by goboscript

            if not block['topLevel']: continue # this block is not first in any script, skip

            # get block and search recursively
            goboscript_code.append(f'# script {block_id} ({block.get('x',0)},{block.get('y',0)})')
            goboscript_code.append(blocks.recursive_block_search(target, block_id, shared_project_data))
            goboscript_code.append('') # spacing for next


        # save goboscript file
        goboscript_file_name = os.path.join(output_dir, target['name'] +".gs")
        with open(goboscript_file_name, 'w', encoding='utf-8') as f:
            f.write('\n'.join([str(l) for l in goboscript_code])) # save flattened data


    postprocess.create_postprocess_file(project_data, shared_project_data, output_dir)
    tw_config.create_config_file(project_data, output_dir)
    
    print(f'Saved project to {output_dir}')


if __name__ == '__main__':
    #convert_project('samples/fbd.sb3', 'output')
    #convert_project('samples/ARE Full Engine (INCOMPLETE).sb3', 'output')
    #convert_project('samples/tm3d.sb3', 'output')
    #convert_project('samples/proc_sandbox2.sb3', 'output')
    #convert_project('samples/UI block based 4.sb3', 'output')
    #convert_project('samples/The Mast [3D] 1.4.4.sb3', 'output')
    convert_project('samples/TextImage RGB8 Decoder Only.sb3', 'output')

