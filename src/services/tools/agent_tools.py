import ast
import json
import os

from src.services.tools.Bank.bank import *
from src.services.tools.meetings.meeting import *
from src.services.tools.weather.weather import *
from src.services.tools.DB.retrieve_db import *
from src.services.tools.Rag_tool.rag_backend import *
from src.services.tools.News.news import *


class AgentTools:
    def __init__(self):
        self.tools=[]

    def get_tools(self):
        return self.tools

    def extract_tools(self, filepath: str,tools_openai,tools_google):
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if "f_" in node.name:
                    func_name = node.name
                    description = ast.get_docstring(node) or "No description available."
                    self.tools.append([func_name,description])
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
                    #print(tool)
                    tools_openai.append(tool_openai)
                    tools_google.append(tool_google)

        return tools_openai,tools_google

    def list_of_tools(self,racine):
        all_tools_openai=[]
        all_tools_google=[]
        #print("----- la liste des outils -----")
        for dossier, _, fichiers in os.walk(racine):
            for fichier in fichiers:
                if fichier.endswith(".py"):
                    chemin_complet = os.path.join(dossier, fichier)
                    #print(f"\n=== {chemin_complet} ===\n")
                    try:
                        all_tools = self.extract_tools(chemin_complet,all_tools_openai, all_tools_google)

                    except Exception as e:
                        print(f"Erreur de lecture : {e}")
        return all_tools_openai,all_tools_google

    def use_tool(self,func_name, args):
        #try:
        #print("les arguments dans use_tool")
        #print(args)
        if func_name in globals():
            func = globals()[func_name]
            return(func(**args))
        else:
            #raise Exception (f"la fonction {func_name} n'existe pas dans le contexte globals()")
            return(f" une erreur :  l'appel au tool ne produit pas de résultat")
        #except Exception as e:
            #return(f"l'appel de la fonction n'a pas fourni de résultat")

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



# # Exemple d’utilisation
# if __name__ == "__main__":
#     filepath = r"/src/tools"
#     tools = list_of_tools(filepath)
#     print(json.dumps(tools, indent=2, ensure_ascii=False))

