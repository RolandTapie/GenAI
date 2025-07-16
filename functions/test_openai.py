import openai
from functions.prompt import OpenAIPrompt
import json

api_key="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"
if api_key is None:
    raise ValueError("Vous devez fournir une clé API OpenAI via le paramètre 'api_key'.")
else:
    nom = input(f"Bonjour comment t'appeles tu ? ")
    while True:

        question = input(f"comment puis-je vous aider {nom} : ")
        if question.lower() in ['exit', 'quit']:
            break

        openai.api_key = api_key
        fonctions=["timer","weather", "agenda"]
        proprietes=["propriete_1","propriete_2"]

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
                    result = '23 dégrés'
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

        print(response.choices[0].message.content)