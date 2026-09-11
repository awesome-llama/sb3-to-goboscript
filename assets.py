import os
from collections import defaultdict
import utilities
import zipfile


# this is poorly written


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



def get_rotation_centers(project_data):
    asset_rotation_center = {}

    for target in project_data['targets']:
        for asset in target['costumes']:
            # assumed that all uses of the costume have the same center
            asset_rotation_center[asset['md5ext']] = (asset.get('rotationCenterX'), asset.get('rotationCenterY'))

    return asset_rotation_center



def get_remapped_costume_names(project_data):
    return get_remapped_asset_names(project_data, 'costumes')

def get_remapped_sound_names(project_data):
    return get_remapped_asset_names(project_data, 'sounds')



def copy_assets_to_folder(project_archive: zipfile.ZipFile, output_dir, names: dict, rotation_centers: dict):
    for md5ext, local_path in names.items():
        path = os.path.join(output_dir, local_path)
        folder = os.path.split(path)[0]
        os.makedirs(folder, exist_ok=True)
        
        if not os.path.exists(path): # only write if the file hasn't been written already
            try:
                if md5ext.endswith('.svg') and (md5ext in rotation_centers):
                    rc = rotation_centers[md5ext]

                    if (rc[0] == 0 and rc[1] == 0):
                        project_archive.extract(md5ext, folder)
                        os.rename(os.path.join(folder, md5ext), path)
                        continue
                    
                    # svg gets costume center appended
                    file_content = str(project_archive.read(md5ext), encoding='utf-8')

                    if ('<!--rotationCenter:' not in file_content):
                        # be aware that editing the file will change the hash
                        file_content += f"<!--rotationCenter:{rc[0]}:{rc[1]}-->"

                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(file_content)

                else:
                    project_archive.extract(md5ext, folder)
                    os.rename(os.path.join(folder, md5ext), path)

            except Exception as e:
                print(f"Could not extract {md5ext} to {local_path}")


if __name__ == '__main__':
    import json
    with open('test/tm3d.json') as f:
        project_data = json.load(f)
        print(json.dumps(get_remapped_costume_names(project_data), indent=2))
        print(json.dumps(get_remapped_sound_names(project_data), indent=2))



