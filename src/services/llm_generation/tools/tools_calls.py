import ast
import json
import os

from src.services.llm_generation.tools.Bank.bank import *
from src.services.llm_generation.tools.meetings.meeting import *
from src.services.llm_generation.tools.weather.weather import *
#from src.services.llm_generation.tools.Rag_tool.rag_tool import *


def extract_tools(filepath: str,tools):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            description = ast.get_docstring(node) or "No description available."

            # Construire le JSON Schema des paramètres
            properties = {}
            required = []
            for arg in node.args.args:
                arg_name = arg.arg
                if arg.annotation:
                    arg_type = ast.unparse(arg.annotation)
                else:
                    arg_type = "string"  # fallback

                # mapping simple python -> JSON Schema
                if arg_type in ["int", "float"]:
                    param_type = "number"
                elif arg_type in ["bool"]:
                    param_type = "boolean"
                else:
                    param_type = "string"

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

            tool = {
                "type": "function",
                "function": {
                    "name": func_name,
                    "description": description.strip(),
                    "parameters": parameters
                }
            }
            tools.append(tool)

    return tools

def list_of_tools(racine):
    all_tools=[]
    for dossier, _, fichiers in os.walk(racine):
        for fichier in fichiers:
            if fichier.endswith(".py"):
                chemin_complet = os.path.join(dossier, fichier)
                #print(f"\n=== {chemin_complet} ===\n")
                try:
                    all_tools = extract_tools(chemin_complet,all_tools)

                except Exception as e:
                    print(f"Erreur de lecture : {e}")
    return all_tools

def use_tool(func_name, args):
    #try:
    print("les arguments dans use_tool")
    print(args)
    if func_name in globals():
        func = globals()[func_name]
        return(func(**args))
    else:
        raise Exception (f"la fonction {func_name} n'existe pas dans le contexte globals()")
    #except Exception as e:
        #return(f"l'appel de la fonction n'a pas fourni de résultat")

def functions_calls(result):
    resp = result  # ta réponse ChatCompletion

    # prendre le premier choix
    choice = resp.choices[0]
    msg = choice.message
    messages = [msg]

    if msg.tool_calls:
        for tool in msg.tool_calls:
            call_id = tool.id
            name = tool.function.name
            arguments = tool.function.arguments  # c'est une string JSON

            print("call_id:", call_id)
            print("name:", name)
            print("arguments:", arguments)
            call = use_tool(name, json.loads(arguments))
            print(f"le resultat après appel {call}")
            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": json.dumps(call)
            })
    return messages



# # Exemple d’utilisation
# if __name__ == "__main__":
#     filepath = r"/src/tools"
#     tools = list_of_tools(filepath)
#     print(json.dumps(tools, indent=2, ensure_ascii=False))

