import json
import os
from jinja2 import Template

dir_path = os.path.dirname(os.path.realpath(__file__))
codegen_file_path = dir_path + "/../../src/ui/blueprints.codegen.json"
page_template_path = dir_path + "/../blueprints/blueprint_page.mdx.tpl"


with open(codegen_file_path, "r") as codegen_file, open(page_template_path, "r") as template_file:
    blueprints = json.load(codegen_file)
    page_template = Template(template_file.read())


for blueprint in blueprints:
    writer = blueprint["writer"]
    with open(dir_path + f"/../blueprints/{writer['name']}.mdx", "w") as output_file:
        output_file.write(page_template.render(**writer))
