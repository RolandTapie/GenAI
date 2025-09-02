import json
from pprint import pprint

from typing import Optional
from typing import List, Dict, Any

from openai import OpenAI
import google.generativeai as genai

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
            genai.configure(api_key=gemini_api_key)
            self.model=genai.GenerativeModel(
                model_name=self.gemini_model, # Replace with your actual key
                tools=self.tools
            )
            self.llm_model=self.gemini_model
            self.api_key = self.gemini_key

        elif self.model_name=="claude":
            self.model=anthropic.Anthropic(api_key=claude_api_key)
            self.llm_model=self.claude_model
            self.api_key = self.claude_key


    def ask(self, source,message, model="openai"):
        tools=self.tools
        k=0
        prompt=Prompt(self.role,self.context,source,message,)
        print(f"Préparation de la réponse avec {model}")

        if model == "openai":
            prmt = prompt.openai()
            return prompt.openai_process(self.model,self.llm_model,self.agent_tools,prmt,self.tools)

        if model == "gemini":

            return prompt.gemini_process(self.model,self.agent_tools,message)


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

    def openai_process(self,model,llm_model,agent_tools,prompt,tools):
        result = model.chat.completions.create(
            model=llm_model,
            messages=prompt,
            tools = tools
        )
        k=1
        #print(result)
        if result.choices[0].message.content:
            return result.choices[0].message.content
        elif result.choices[0].message.tool_calls:
            while result.choices[0].message.tool_calls and k<=5:
                print(f"appel de fonction {k}")
                k=k+1
                calls = agent_tools.functions_calls(result)
                result = model.chat.completions.create(
                    model=llm_model,
                    messages=calls,
                    tools=tools,
                    temperature=0.2
                )
                print("----le prompt après appels des fonctions----")
                print (calls)
            return result.choices[0].message.content

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

    def gemini_process(self,model, agent, message):
        response = model.generate_content(message)
        tool_responses=[]
        # Print the result
        for part in response.candidates[0].content.parts:
            # Vérifier si la partie est un appel de fonction
            if hasattr(part, 'function_call'):
                tool_call = part.function_call

                # Obtenir le nom de la fonction et ses arguments
                tool_name = tool_call.name
                tool_args = tool_call.args

                print(f"Le modèle a demandé d'exécuter la fonction : {tool_name}")
                print(f"Avec les arguments : {tool_args}")
                result = agent.use_tool(tool_name,tool_args)

                tool_responses.append(result)

        if tool_responses:
            print("\n-------------------------------------------------------------")
            print("Résultat des outils obtenu. On le renvoie au modèle...")
            print("-------------------------------------------------------------")

            # 1. Créez un objet de contenu pour le message initial de l'utilisateur
            user_content = genai.protos.Content(
                parts=[genai.protos.Part(text=message)],
                role='user'
            )

            # 2. L'historique de la conversation commence par le message de l'utilisateur...
            chat_history = [user_content]

            # 3. ...suivi par la réponse du modèle qui contient l'appel de fonction...
            func_call= genai.protos.Content(parts=[genai.protos.Part(function_call=genai.protos.FunctionCall(name="f_get_bank_transaction",
                    args={}
                ))],
                role="model"
            )
            #chat_history.append(response.candidates[0].content)
            chat_history.append(func_call)
            # 4. ...suivi par la réponse de l'outil qui contient les résultats.
            tool_content = genai.protos.Content(
                parts=[genai.protos.Part(text=tool_responses[0])],
                role='user'
            )


            chat_history.append(tool_content)
            print(f"chat_history : {chat_history}")

            # Relancez generate_content avec l'historique complet pour obtenir la réponse finale
            final_response = model.generate_content(chat_history)
            print("\n-------------------------------------------------------------")
            print("Réponse finale du modèle :")
            print("-------------------------------------------------------------")
            return final_response.text
        else:
            print("\n-------------------------------------------------------------")
            print("Le modèle a fourni une réponse textuelle directe :")
            print("-------------------------------------------------------------")
            return response.text

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


class Model:

    def __init__(self, model_name, llm_model):
        self.model_name=model_name
        self.llm_model=llm_model
        self.agent_tools=None
        self.tools_openai=None
        self.tools_google = None
        self.memory=None
        self.context=None

    def initialize(self,agent_tools,memory):
        if agent_tools:
            self.agent_tools=agent_tools
            self.tools_openai, self.tools_google = self.agent_tools.list_of_tools(tools_path)
        if memory:
            self.memory=memory

        if self.model_name=="openai":
            tools = self.tools_openai
            self.model=OpenAI(api_key=os.getenv("openai_key"))

        elif self.model_name=="gemini":
            tools = self.tools_google
            genai.configure(api_key=os.getenv("gemini_key"))
            self.model=genai.GenerativeModel(
                model_name=self.llm_model, # Replace with your actual key
                tools=tools
            )

        elif self.model_name=="claude":
            self.model=anthropic.Anthropic(api_key=os.getenv("claude_key"))


    def get_prompt(self,role,context,question):
        if self.model_name=="openai":
            prompt=[
                {"role": "system", "content": "Tu es un assistant"},
                {"role": "user", "content": f" tu es un {role} ; context: {context} ; task: {question} reasoning:"" "}
            ]

        elif self.model_name=="gemini":
            prompt=[
                {"role": "system", "content": "Tu es un assistant"},
                {"role": "user", "content": f" tu es un {role} ; context: {context} ; task: {question} reasoning:"" "}
            ]

        elif self.model_name=="claude":
            prompt=[
                {"role": "user", "content": f" tu es un {role} ; context: {context} ; task: {question} reasoning:"" "}
            ]

        else: #mistral
            prompt = {
                "model": "mistral",
                "prompt": f"""
                        [Role]
                        {role}

                        [Contexte strict]
                        {context}
                        [Objectif]
                        Répondre à la question : {question}
                        
                        [source]
                        la source : {self.source}

                        [Contraintes]
                        -Répondre en une ligne
                        -utiliser uniquement les informations du contexte et citer la source de la réponse

                        """,
                "stream":False}
        return prompt

    def get_model(self):
        return self.model

    def get_llm_model(self):
        return self.llm_model


    def process(self,user,context,question):
        prompt=self.get_prompt(user,context,question)

        if self.model_name=="openai":
            results = self.openai_process(self.model,self.llm_model,self.agent_tools,prompt,self.tools_openai)

        elif self.model_name=="gemini":
            results = self.gemini_process(self.model,self.agent_tools,question)

        elif self.model_name=="claude":
            pass

        else:
            results = self.mistral_process(question)


        return results

    def openai_process(self,model,llm_model,agent_tools,prompt,tools):
        result = model.chat.completions.create(
            model=llm_model,
            messages=prompt,
            tools = tools
        )
        k=1
        #print(result)
        if result.choices[0].message.content:
            return result.choices[0].message.content
        elif result.choices[0].message.tool_calls:
            while result.choices[0].message.tool_calls and k<=5:
                print(f"appel de fonction {k}")
                k=k+1
                calls = agent_tools.functions_calls(result)
                result = model.chat.completions.create(
                    model=llm_model,
                    messages=calls,
                    tools=tools,
                    temperature=0.2
                )
                print("----le prompt après appels des fonctions----")
                print (calls)
            return result.choices[0].message.content

    def gemini_process(self,model, agent, message):

        #le message doit contenir les tools
        response = model.generate_content(message)
        tool_responses=[]
        # Print the result
        for part in response.candidates[0].content.parts:
            # Vérifier si la partie est un appel de fonction
            if hasattr(part, 'function_call'):
                tool_call = part.function_call

                # Obtenir le nom de la fonction et ses arguments
                tool_name = tool_call.name
                tool_args = tool_call.args

                print(f"Le modèle a demandé d'exécuter la fonction : {tool_name}")
                print(f"Avec les arguments : {tool_args}")
                result = agent.use_tool(tool_name,tool_args)

                tool_responses.append(result)

        if tool_responses:
            print("\n-------------------------------------------------------------")
            print("Résultat des outils obtenu. On le renvoie au modèle...")
            print("-------------------------------------------------------------")

            # 1. Créez un objet de contenu pour le message initial de l'utilisateur
            user_content = genai.protos.Content(
                parts=[genai.protos.Part(text=message)],
                role='user'
            )

            # 2. L'historique de la conversation commence par le message de l'utilisateur...
            chat_history = [user_content]

            # 3. ...suivi par la réponse du modèle qui contient l'appel de fonction...
            func_call= genai.protos.Content(parts=[genai.protos.Part(function_call=genai.protos.FunctionCall(name="f_get_bank_transaction",
                                                                                                             args={}
                                                                                                             ))],
                                            role="model"
                                            )
            #chat_history.append(response.candidates[0].content)
            chat_history.append(func_call)
            # 4. ...suivi par la réponse de l'outil qui contient les résultats.
            tool_content = genai.protos.Content(
                parts=[genai.protos.Part(text=tool_responses[0])],
                role='user'
            )


            chat_history.append(tool_content)
            print(f"chat_history : {chat_history}")

            # Relancez generate_content avec l'historique complet pour obtenir la réponse finale
            final_response = model.generate_content(chat_history)
            print("\n-------------------------------------------------------------")
            print("Réponse finale du modèle :")
            print("-------------------------------------------------------------")
            return final_response.text
        else:
            print("\n-------------------------------------------------------------")
            print("Le modèle a fourni une réponse textuelle directe :")
            print("-------------------------------------------------------------")
            return response.text

    def mistral_process(self,question):
        prompt = self.get_prompt("user","",question)
        response = requests.post(
            "http://localhost:11434/api/generate", json=prompt,
        )
        #response.raise_for_status()
        return response.json().get("response", "").strip()