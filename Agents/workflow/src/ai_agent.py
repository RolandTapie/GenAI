import openai
from functions.prompt import OpenAIPrompt
from tools.weather import get_weather
import json
from colorama import Fore, Style, init
from dotenv import load_dotenv
import os

# Charger les variables depuis le fichier .env
load_dotenv()

# Lire les variables d'environnement
openai_api_key = os.getenv("openai_key")

init()

api_key=openai_api_key

if api_key is None:
    raise ValueError("Vous devez fournir une clé API OpenAI via le paramètre 'api_key'.")
else:
    nom = input(f"{Fore.BLUE}🤖 : Bonjour, comment t'appelles tu ? \n👤 : {Style.RESET_ALL}")
    while True:

        question = input(f"{Fore.BLUE}🤖 : comment puis-je t'aider {nom} : \n👤 {nom} : {Style.RESET_ALL}")
        if question.lower() in ['exit', 'quit',"bye"]:
            print(f"🤖 : je suis ravi de t'avoir aidé {nom}, à la prochaine...")
            break

        openai.api_key = api_key
        fonctions=["timer","weather", "agenda"]
        proprietes=["latitude","longitude"]

        #question="quel est le president du honduras"
        prompt=OpenAIPrompt().generate_prompt("gpt-4o","tu es un assistant expert",question,fonctions,proprietes)
        #print(prompt["messages"])
        response = openai.chat.completions.create(
            model=prompt["model"],
            messages=prompt["messages"],
            tools=prompt["tools"],
            temperature=0
        )
        message=prompt["messages"]

        if  not response.choices[0].message.tool_calls == None:
            for tool_call in response.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                message.append(response.choices[0].message)
                if name=="agenda":
                    result="le rendez vous a été enregistré dans l'agenda personnelle"
                elif name=="weather":
                    result = get_weather(**args)
                message.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            response = openai.chat.completions.create(
                model=prompt["model"],
                messages=message,
                tools=prompt["tools"],
                temperature=0.7
            )

        print(f"{Fore.BLUE}🤖 " + response.choices[0].message.content)