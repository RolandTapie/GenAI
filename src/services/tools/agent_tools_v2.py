import ast
import json
import os
import importlib.util
from typing import Dict, Any, List, Tuple

class AgentTools:

    def __init__(self):
        print("Initialization of the tool manager")
        self.tools: List[Tuple[str, str]] = []
        self.function_map: Dict[str, Any] = {}

    def get_tools(self) -> List[Tuple[str, str]]:
        return self.tools

    def map_py_type_to_json(self, py_type: str) -> str:
        """Mapping simple Python type (as string) -> JSON Schema type."""
        if py_type in ["int", "float"]:
            return "number"
        elif py_type in ["bool"]:
            return "boolean"
        elif py_type in ["list", "dict"]:
            return "object"
        else:
            return "string"

    def extract_tools(self, filepath: str, all_tools_openai: List[Dict], all_tools_google: List[Dict]):

        # Analysis AST
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if "f_" in node.name:
                    func_name = node.name
                    description = ast.get_docstring(node) or "No description available."

                    # --- Construction of JSON Schema ---
                    properties = {}
                    required = []
                    for arg in node.args.args:
                        arg_name = arg.arg
                        arg_type_str = ast.unparse(arg.annotation) if arg.annotation else "str"
                        param_type = self.map_py_type_to_json(arg_type_str)

                        properties[arg_name] = {
                            "type": param_type,
                            "description": f"Paramètre {arg_name}"
                        }

                        required.append(arg_name)

                    parameters = {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }

                    tool_openai = {
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "description": description.strip(),
                            "parameters": parameters
                        }
                    }

                    tool_google = {
                        "function_declarations":
                            [
                                {
                                    "name": func_name,
                                    "description": description.strip(),
                                    "parameters": parameters
                                } ]
                    }

                    all_tools_openai.append(tool_openai)
                    all_tools_google.append(tool_google)

                    self.tools.append([func_name, description])

        return all_tools_openai, all_tools_google

    def list_of_tools(self, racine: str) -> Tuple[List[Dict], List[Dict]]:
        all_tools_openai: List[Dict] = []
        all_tools_google: List[Dict] = []

        for folder, _, files in os.walk(racine):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    chemin_complet = os.path.join(folder, file)

                    try:
                        # 1. JSON schema extraction
                        self.extract_tools(chemin_complet, all_tools_openai, all_tools_google)

                        # 2. Dynamic importation
                        module_name = file[:-3] # remove .py
                        spec = importlib.util.spec_from_file_location(module_name, chemin_complet)
                        if spec and spec.loader:
                            tool_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(tool_module)

                            # 3. Recording functions in the map
                            for func_name, _ in self.tools:
                                if hasattr(tool_module, func_name) and func_name not in self.function_map:
                                    self.function_map[func_name] = getattr(tool_module, func_name)

                    except Exception as e:
                        print(f"Error during analysis or import of {chemin_complet}: {e}")

        return all_tools_openai, all_tools_google

    def functions_calls(self,result):
        resp = result  # ta réponse ChatCompletion

        # prendre le premier choix
        choice = resp.choices[0]
        msg = choice.message
        messages = [msg]

        if msg.tool_calls:
            for tool in msg.tool_calls:
                print(tool)
                call_id = tool.id
                name = tool.function.name
                arguments = tool.function.arguments  # c'est une string JSON

                print("call_id:", call_id)
                print("name:", name)
                print("arguments:", arguments)
                call = self.use_tool(name, json.loads(arguments))
                #print(f"le resultat après appel {call}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": json.dumps(call)
                })
        return messages

    def use_tool(self, func_name: str, args: Dict) -> Any:
        """Executes the tool using the internal function mapping."""

        if func_name in self.function_map:
            func = self.function_map[func_name]
            try:
                return func(**args)
            except Exception as e:
                return f"Error during the tool exceution{func_name}: {e}"
        else:
            return f"Error: The tool {func_name} was not found or loaded."
