"""

Abstract templates.

They're used to register new component templates, based on existing frontend templates and a backend-provided component definition. 

"""

from typing import Dict

from writer.ss_types import AbstractTemplate

templates:Dict[str, AbstractTemplate]  = {}

def register_abstract_template(type: str, abstract_template: AbstractTemplate):
    templates[type] = abstract_template
