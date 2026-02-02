import argparse
import convert_project
from pathlib import Path

parser = argparse.ArgumentParser(
    prog='sb3_to_goboscript',
    description="Convert a Scratch project into goboscript. If no output path is given, the project is created in the same path as the input."
)

parser.add_argument("input", type=Path, help="sb3 file")
parser.add_argument("-o", "--output", type=Path, default=None, help="goboscript project output path")

args = parser.parse_args()
input_path = args.input
output_path = args.output

convert_project.convert_project(input_path, output_path)
