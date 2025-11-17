

class Agent():

    def __init__(self,model, tools,memory):
        print("Construction de l'agent")
        self.model = model
        self.model.initialize(tools,memory)
        self.tools = self.model.get_tools()

    def run(self, user, context, question):
        return self.model.process(user, context,question)

    def get_tools(self):
        """
        Extrait une liste lisible des fonctions (outils) à partir de la structure de données donnée.

        Chaque outil est stocké sous forme de dictionnaire {nom_outil: détails}.
        Les outils dupliqués (basés sur le nom) sont automatiquement gérés.

        Args:
            data_list (list): La liste des dictionnaires décrivant les outils.

        Returns:
            dict: Un dictionnaire où la clé est le nom de l'outil et la valeur est un dictionnaire
                  contenant 'description', 'parameters' (liste de noms) et 'required' (liste de noms).
        """
        tools = {}
        data_list = self.tools

        formatted_output = ""
        processed_names = set()  # Pour éviter les doublons

        for item in data_list:
            if item.get('type') == 'function':
                function_data = item.get('function', {})
                name = function_data.get('name')

                # Traiter seulement les noms d'outils uniques
                if name and name not in processed_names:
                    description = function_data.get('description', 'No description available.')

                    # Nettoyage et simplification de la description
                    # Remplacement des sauts de ligne par des espaces
                    cleaned_description = description.replace('\n', ' ').strip()

                    parameters_data = function_data.get('parameters', {})

                    # Récupérer les noms des paramètres
                    properties = parameters_data.get('properties', {})
                    parameter_names = list(properties.keys())
                    param_total = ', '.join(parameter_names) if parameter_names else 'Aucun'

                    # Récupérer les paramètres requis
                    required_params = parameters_data.get('required', [])
                    param_required = ', '.join(required_params) if required_params else 'Aucun'

                    # Construction de la chaîne formatée pour cet outil
                    tool_string = f"""--- Outil : **{name}** ---\nDescription : {cleaned_description}\nParamètres (Total) : {param_total}\nParamètres Requis : {param_required}\n--------------------\n"""

                    formatted_output += tool_string
                    processed_names.add(name)

        return formatted_output.strip() # Supprimer l'éventuel dernier saut de ligne