A tool to convert Scratch projects into [goboscript](https://github.com/aspizu/goboscript) projects.

Projects are formatted targeting my own style as seen in [Procedural Sandbox](https://github.com/awesome-llama/procedural-sandbox/tree/main/src). Projects may compile with errors. It is intended that the user edits the code afterward to fix this and other possible formatting issues.


### Notable behaviour

- Costumes and sounds are placed in their own directories. Those unique to a particular sprite are placed in directories of that sprite's name.
- goboscript.toml is generated from the TurboWarp config comment in the stage.
- Code without hats will be commented out.
- Code is indented with 4 spaces.
- Numbers stored as strings in project.json are converted to numbers if known it will not change behaviour.
- List and variable names are not differentiated currently. This may introduce code bugs.
- Custom block names are currently not nicely formatted to prevent name collisions. For now it is suggested to use a code editor's find-and-replace function.
- List data is not placed in separate files currently. Long lists may clutter the code.


## Usage

Run the `convert_project` function in `main.py` with arguments for input and output paths.


## Contributing

Note that this tool is for my own use and its behaviour caters to this. Contributions affecting this are unlikely to be accepted.