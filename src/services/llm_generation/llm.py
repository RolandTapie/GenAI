import json
from pprint import pprint

from typing import Optional
from typing import List, Dict, Any
from openai import OpenAI
import anthropic

import requests
import numpy as np
import faiss
from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.getenv("openai_key")
gemini_api_key = os.getenv("gemini_key")
claude_api_key = os.getenv("claude_key")
tools_path = os.getenv("tools")


class Agent():
    def __init__(self, agent_llm, agent_tools, agent_memory):
        self.model_name = agent_llm
        self.agent_tools=agent_tools
        self.agent_memory = agent_memory
        tools_openai, tools_google = self.agent_tools.list_of_tools(tools_path)

        if self.model_name=="openai":
            self.tools = tools_openai
        elif self.model_name=="gemini":
            self.tools=tools_google


        self.openai_key= None
        self.gemini_key= None
        self.openai_model= None
        self.gemini_model= None
        self.prompt=None
        self.embeddings= None
        self.documents=None
        self.role="Tu es un assistant"
        self.task=""
        self.context=""
        self.source=""
        self.reasoning=""
        self.output_format=""
        self.stop_condition=""
        self.api_key=None

        self.set_openai_key(openai_api_key)
        self.set_openai_model("gpt-4o")
        self.set_openai_base_url("https://api.openai.com/v1")

        self.set_gemini_key(gemini_api_key)
        self.set_gemini_model("gemini-2.5-flash")
        self.set_gemini_base_url("https://generativelanguage.googleapis.com/v1beta")

        self.set_claude_key(claude_api_key)
        self.set_claude_model("claude-opus-4-20250514")
        self.set_claude_base_url("https://api.anthropic.com/v1/")

        self.init_model()

    def set_document(self, document):
        self.documents=document
    def set_openai_key (self,key: str):
        self.openai_key=key

    def set_openai_model (self,model: str):
        self.openai_model=model

    def set_openai_base_url(self, url: str):
        self.openai_base_url = url


    def set_gemini_key (self,key: str):
        self.gemini_key=key

    def set_gemini_model (self,model: str):
        self.gemini_model=model

    def set_gemini_base_url(self, url: str):
        self.gemini_base_url = url

    def set_claude_key (self,key: str):
        self.claude_key=key

    def set_claude_model (self,model: str):
        self.claude_model=model

    def set_claude_base_url(self, url: str):
        self.claude_base_url = url

    def set_context(self, context: str):
        self.context = context

    def set_task(self, task: str):
        self.task=task

    def set_source(self,source):
        self.source=source

    def init_model(self):
        self.role="Tu es un assistant ia"

        if self.model_name=="openai":
            self.model=OpenAI(api_key=openai_api_key,base_url=self.openai_base_url)
            self.llm_model=self.openai_model
            self.api_key = self.openai_key

        elif self.model_name=="gemini":
            self.model=OpenAI(api_key=self.gemini_key,base_url=self.gemini_base_url)
            self.llm_model=self.gemini_model
            self.api_key = self.gemini_key

        elif self.model_name=="claude":
            self.model=anthropic.Anthropic(api_key=claude_api_key)
            self.llm_model=self.claude_model
            self.api_key = self.claude_key

    def decouper_en_chunks(self,texte, taille_max=500, overlap=50):
        """
        Découpe le texte en morceaux (chunks) avec chevauchement optionnel.
        - taille_max : taille maximale d'un chunk (en caractères)
        - overlap : nombre de caractères qui se chevauchent entre deux chunks
        """
        chunks = []
        start = 0
        while start < len(texte):
            end = start + taille_max
            chunk = texte[start:end]
            chunks.append(chunk)
            start += taille_max - overlap  # avance avec chevauchement
        return chunks

    def embedding(self, chunks):

        embeddings=[]
        for chunck in chunks:
            resp = self.model.embeddings.create(
                model="text-embedding-3-small",
                input=chunck
            )
            embeddings.append(resp.data[0].embedding)
        return np.array(embeddings).astype("float32")

    def Faiss_index(self):
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 = distance euclidienne
        self.index.add(self.embeddings)
        print(f"{self.index.ntotal} documents indexés.")

    def find_similarity(self, text):
        text_emb = self.embedding(text)
        distances, indices = self.index.search(text_emb, k=5)
        print("\nRésultats de la recherche :")
        results=[]
        for idx, dist in zip(indices[0], distances[0]):
            results.append(self.documents[idx])
        return results

    def ask(self, source,message, model="openai"):
        tools=self.tools
        k=0
        prompt=Prompt(self.role,self.context,source,message,)
        print(f"Préparation de la réponse avec {model}")
        if model == "openai":
            result = self.model.chat.completions.create(
                model=self.llm_model,
                messages=prompt.openai(),
                tools = tools
            )
            #print(result)
            if result.choices[0].message.content:
                return result.choices[0].message.content
            elif result.choices[0].message.tool_calls:
                while result.choices[0].message.tool_calls and k<=5:
                    print(f"appel de fonction {k}")
                    k=k+1
                    calls = self.agent_tools.functions_calls(result)
                    result = self.model.chat.completions.create(
                        model=self.llm_model,
                        messages=calls,
                        tools=tools,
                        temperature=0.2
                    )
                    print("----le prompt après appels des fonctions----")
                    print (calls)
                return result.choices[0].message.content
        if model == "gemini":
            result = self.model.chat.completions.create(
                model=self.llm_model,
                messages=prompt.gemini(),
                tools = tools
            )
            #print(result)
            if result.choices[0].message.content:
                return result.choices[0].message.content
            elif result.choices[0].message.tool_calls:
                while result.choices[0].message.tool_calls and k<=5:
                    print(f"appel de fonction {k}")
                    k=k+1
                    calls = self.agent_tools.functions_calls(result)
                    print(f"model : {self.model_name}")
                    print(f"messages :")
                    pprint(calls)
                    print(f"tools : {tools}")
                    print(f"temperature : 0.0")

                    result = self.model.chat.completions.create(
                        model=self.llm_model,
                        messages=calls,
                        tools=tools,
                        temperature=0.2
                    )
                return result.choices[0].message.content
        if model == "claude":
            result = self.model.messages.create(
                model=self.llm_model,   # ex: "claude-3-opus-20240229"
                system="Tu es un assistant",
                max_tokens=500,
                messages=prompt.claude()
            )
            return result.content[0].text

        else:
            prompt = prompt.mistral()
            response = requests.post(
                "http://localhost:11434/api/generate", json=prompt,
            )
            #response.raise_for_status()
            return response.json().get("response", "").strip()

    def rag(self, question):
        context = self.find_similarity(question)
        self.set_context(context)
        self.set_task(f"répond à la question suivante en utilisant uniquement le contexte: {question}")
        print(self.ask(self.task))

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

    def test_llm_server(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            print(response.status_code)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False

    def send_mistral(self,user , prompt , model_name="mistral", contexte = None, api_key=None):
        print(self.test_llm_server())
        try:
            if model_name.lower() == "mistral":
                print(prompt)
                response = requests.post(
                    "http://localhost:11434/api/generate", json=prompt,
                    #timeout=30  # Sécurité : éviter que ça tourne en boucle
                )
                response.raise_for_status()
                #debug = response.json()
                print(response.json().get("response", "").strip())
                return response.json().get("response", "").strip()

            else:
                raise ValueError(f"Modèle non pris en charge : {model_name}")

        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau avec le modèle local : {e}")
        except Exception as e:
            print(f"Erreur inattendue : {e}")

        return ""

class Prompt():
    def __init__(self,role,context,source,question,tools=None,temperature=0.7, max_tokens=500, stream=True):
        self.role=role
        self.context=context
        self.source=source
        self.question=question
        self.tools=tools
        self.temperature=temperature
        self.max_tokens=max_tokens
        self.top_p=None
        self.stream=stream

    def set_question (self, question):
        self.question=question

    def openai(self):
        prompt=[
            {"role": "system", "content": "Tu es un assistant"},
            {"role": "user", "content": f" tu es un {self.role} ; context: {self.context} ; task: {self.question} reasoning:"" "}
        ]
        return prompt

    def claude(self):
        prompt=[
            {"role": "user", "content": f" tu es un {self.role} ; context: {self.context} ; task: {self.question} reasoning:"" "}
        ]
        return prompt

    def gemini(self):
        prompt=[
            {"role": "system", "content": "Tu es un assistant"},
            {"role": "user", "content": f" tu es un {self.role} ; context: {self.context} ; task: {self.question} reasoning:"" "}
        ]
        return prompt

    def mistral(self):

        prompt = {
            "model": "mistral",
            "prompt": f"""
                        [Role]
                        {self.role}

                        [Contexte strict]
                        {self.context}
                        [Objectif]
                        Répondre à la question : {self.question}
                        
                        [source]
                        la source : {self.source}

                        [Contraintes]
                        -Répondre en une ligne
                        -utiliser uniquement les informations du contexte et citer la source de la réponse

                        """,
            "stream":False}

        return prompt