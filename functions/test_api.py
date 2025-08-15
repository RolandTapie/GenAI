import requests

url = "http://localhost:8000/load_document"
data = {"document": r"C:\Users\tallar\Downloads\Famille bamendjou de liege-20250801T201343Z-1-001\Famille bamendjou de liege\ARESBAL_ ROI et statut.pdf"}

response = requests.post(url, json=data)
print(response.json()["results"])