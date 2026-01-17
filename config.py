import os
import json


def find_comment_json(sprite):
    """Find the TurboWarp config comment in the sprite and try to load it as JSON."""
    
    for comment in sprite['comments'].values():
        if comment['text'].endswith('_twconfig_'):
            try:
                decoded_text = bytes(comment['text'], "utf-8").decode("unicode_escape")
                data_line = decoded_text.split('\n')[-1]
                end = -list(reversed(data_line)).index('}')
                return json.loads(data_line[:end])
            except:
                return None
    return None



def get_layers(project_data):
    sprites = []
    for target in project_data['targets']:
        if not target['isStage']:
            sprites.append((target['name'], target.get('layerOrder', 1000)))

    sprites.sort(key=lambda e: e[1])

    return [e[0] for e in sprites]




def create_config_file(project_data, output_directory):
    """Create a goboscript.toml file."""
    
    for target in project_data['targets']:
        if target['isStage']: 
            config = find_comment_json(target)
            
            if config is None: return # no config found

            file = ''

            if 'framerate' in config: file += f"frame_rate = {config['framerate']}\n"

            if 'runtimeOptions' in config:
                runtime_options = config['runtimeOptions']
                if 'maxClones' in runtime_options: 
                    _clones = runtime_options['maxClones']
                    if _clones == 'Infinity': _clones = 'inf'
                    file += f"max_clones = {_clones}\n"

                if 'miscLimits' in runtime_options: file += f"no_miscellaneous_limits = {str(not runtime_options['miscLimits']).lower()}\n"
                
                if 'fencing' in runtime_options: file += f"no_sprite_fencing = {str(not runtime_options['fencing']).lower()}\n"

            if 'interpolation' in config: file += f"frame_interpolation = {str(config['interpolation']).lower()}\n"
                
            if 'hq' in config: file += f"high_quality_pen = {str(config['hq']).lower()}\n"

            if 'width' in config: file += f"stage_width = {str(config['width']).lower()}\n"
            
            if 'height' in config: file += f"stage_height = {str(config['height']).lower()}\n"

            file += "bitmap_resolution = 2\n"

            file += f"layers = {json.dumps(get_layers(project_data))}"

            with open(os.path.join(output_directory, 'goboscript.toml'), 'w', encoding='utf-8') as f:
                f.write(file)

            break




if __name__ == '__main__':
    config = find_comment_json({
        "comments": {
            "f@": {"text": "Configuration for https://turbowarp.org/\\nYou can move, resize, and minimize this comment, but don't edit it by hand. This comment can be deleted to remove the stored settings.\\n{\\\"framerate\\\":60,\\\"runtimeOptions\\\":{\\\"fencing\\\":false},\\\"hq\\\":true} // _twconfig_"}
            }})
    print(config)