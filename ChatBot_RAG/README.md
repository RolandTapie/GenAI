pour llm mistral fusion: nous utilisons un llm local ollama/mistral ; il doit être lancé via ollama run mistral avec l'execution du RAG
model en local beaucoup plus lent si la machine n'a pas une bonne configuration
il faut avoir un bon prompt sinon bonjour les hallucinations (problème de langage et réponses non pertinentes)

avec le couplage mistral et opeanai, le RAG les réponses sont un peu mieux formuulées mais elles dépendent des données fournies par mistal