
import os
from collections import defaultdict
import utilities
import zipfile


def get_remapped_asset_names(project_data, key='costumes'):
    """Return a dict of asset names with keys as md5 file name (with extension), and values as desired relative project path (with extension)"""

    # accumulate names
    asset_uses = defaultdict(list)
    for target in project_data['targets']:
        for asset in target[key]:
            asset_uses[asset['md5ext']].append(asset['name'])
    
    remapped_asset_names = {}

    # copy
    for target in project_data['targets']:
        for asset in target[key]:
            
            if len(asset_uses[asset['md5ext']]) == 1:
                # asset is used only 1 time and can be stored in sprite folder
                file_name = f'{utilities.valid_file_name(asset['name'])}.{asset['dataFormat']}'
                new_path = os.path.join(key, target['name'], file_name)

                remapped_asset_names[asset['md5ext']] = new_path
            
            elif asset['md5ext'] not in remapped_asset_names: 
                if len(set(asset_uses[asset['md5ext']])) == 1: # only 1 name
                    file_name = f'{utilities.valid_file_name(asset['name'])}.{asset['dataFormat']}'
                else:
                    file_name = asset['md5ext']
                
                remapped_asset_names[asset['md5ext']] = os.path.join(key, file_name)

    return remapped_asset_names


def get_remapped_costume_names(project_data):
    return get_remapped_asset_names(project_data, 'costumes')

def get_remapped_sound_names(project_data):
    return get_remapped_asset_names(project_data, 'sounds')



def copy_assets_to_folder(project_archive: zipfile.ZipFile, output_dir, names: dict):
    for md5ext, path in names.items():
        path = os.path.join(output_dir, path)
        os.makedirs(os.path.split(path)[0], exist_ok=True)
        
        if not os.path.exists(path):
            project_archive.extract(md5ext, os.path.split(path)[0])
            os.rename(os.path.join(os.path.split(path)[0], md5ext), path)



if __name__ == '__main__':
    import json
    with open('test/tm3d.json') as f:
        project_data = json.load(f)
        print(json.dumps(get_remapped_costume_names(project_data), indent=2))
        print(json.dumps(get_remapped_sound_names(project_data), indent=2))



