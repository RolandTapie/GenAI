from typing import List, Dict, Optional
from typing import List, Dict, Any
from openai import OpenAI
from llm import *
from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.getenv("openai_key")
gemini_api_key = os.getenv("gemini_key")

import json

class model():
    def __init__(self):
        self.openai_key= None
        self.gemini_key= None
        self.openai_model= None
        self.gemini_model= None
        self.base_url_openai=""
        self.base_url_gemini=""
        self.prompt=None

    def set_openai_key (self,key: str):
        self.openai_key=key

    def set_gemini_key (self,key: str):
        self.gemini_key=key

    def set_openai_model (self,model: str):
            self.openai_model=model

    def set_gemini_model (self,model: str):
        self.gemini_model=model

    def set_openai_base_url(self, url: str):
        self.openai_base_url = url

    def set_gemini_base_url(self, url: str):
        self.gemini_base_url = url

    def init_model(self, mode):
        if mode=="openai":
            self.model=OpenAI(api_key=openai_api_key,base_url=self.openai_base_url)
            self.llm_model=self.openai_model
        elif mode=="gemini":
            self.model=OpenAI(api_key=gemini_api_key,base_url=self.gemini_base_url)
            self.llm_model=self.gemini_model

    def ask(self, message):
        messages=[
            {"role": "system", "content": "Tu es un assistant"},
            {"role": "user", "content": f"{message}"}
        ]
        result = self.model.chat.completions.create(
            model=self.llm_model,
            messages=messages
            #tools=self.prompt["tools"],
            #temperature=0
        )
        return result.choices[0].message.content

    def build_system_message(self, content: str) -> Dict[str, str]:
        return {"role": "system", "content": content}


    def build_user_message(self, content: str) -> Dict[str, str]:
        return {"role": "user", "content": content}


    def build_prompt(self,
                     model: str,
                     system_prompt: str,
                     user_prompt: Optional[str] = None,
                     tools: Optional[List[Dict[str, str]]] = None
                     ) -> List[Dict[str, str]]:
        """
        Assemble tous les composants en une liste de messages structurée.
        """
        messages = []

        # Ajout du système
        if system_prompt:
            messages.append(self.build_system_message(system_prompt))

        # Introduction utilisateur
        if user_prompt:
            messages.append(self.build_user_message(user_prompt))


        prompt={}
        prompt["model"]=model
        prompt["messages"]=messages

        # Outils
        if tools:
            prompt["tools"]=tools

        # Message final
        #messages.append(self.build_user_message(new_user_message))

        self.prompt=prompt
        return prompt

    def find_function(self, tools: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
        print(tools)
        if tools["function"]["name"]=="nom_fonction":
            print("ok")
            print(tools["function"]["parameters"])

    def add_parameter(self,schema,function_name, name, types, description,required):

        if schema["function"]["name"]==function_name:
            schema["function"]["parameters"]["properties"][name] = {
                "type": types,
                "description": description
            }

            if required and name not in schema["function"]["parameters"]["required"]:
                schema["function"]["parameters"]["required"].append(name)

            return schema

    def create_tool_definition(self,
                               function_name: str,
                               description: str,
                               parameters: dict,
                               required_fields: list
                               ) -> dict:
        return {
            "type": "function",
            "function": {
                "name": function_name,
                "description": description,
                "parameters":parameters
            }
        }

    def generate_prompt(self,model,system_prompt,user_prompt,fonctions,properties):
        tools=[]
        for fonction in fonctions:
            function_name=fonction
            function_description="description de la fonction"
            parametres = {"type": "object","properties": {},"required": []}
            schema=self.create_tool_definition(function_name,function_description,parametres,"les paramètres requis")

            for propriete in properties:
                schema = self.add_parameter(schema,fonction,propriete,"string","description"+propriete,"true")

            tools.append(schema)
        prompt=self.build_prompt(model,system_prompt,user_prompt,tools)

        self.prompt = prompt

        return prompt