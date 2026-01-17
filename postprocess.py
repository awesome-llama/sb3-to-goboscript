
import os
import json
import utilities

def create_postprocess_file(project_data, shared_project_data, output_dir):
    np: utilities.NamePool = shared_project_data['name_pool']

    # save postprocess data
    postprocess_output = {}

    targets = {}

    # set up all target properties
    for tgt in project_data['targets']:
        targets[tgt['name']] = {}
        
        if tgt['name'] != 'stage':
            for key in ['x', 'y', 'size', 'direction', 'visible', 'currentCostume', 'volume', 'layerOrder']:
                if key in tgt:
                    targets[tgt['name']][key] = tgt[key]
            
            targets[tgt['name']]['name'] = tgt['original_name']
        
    # add code_remap to target
    for k, v in np.pool.items():
        if v == k[0]: continue # don't nclude names that are unchanged
        
        if 'code_remap' not in targets[k[1]]:
            targets[k[1]]['code_remap'] = {}
        
        targets[k[1]]['code_remap'][v] = k[0]
    

    postprocess_output['targets'] = targets

    with open(os.path.join(output_dir, 'postprocess.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(postprocess_output, indent=2, ensure_ascii=False))