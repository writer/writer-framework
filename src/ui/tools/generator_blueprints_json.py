import json
import os
from writer.abstract import templates

dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = dir_path + "/../blueprints.codegen.json"

with open(file_path, 'w') as file:
    file.write(
        json.dumps(
            [{"baseType": template.baseType, "writer": template.writer} for template in templates.values()],
            indent=4)
    )
