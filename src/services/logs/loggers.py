from datetime import datetime
def log(informations: str, cat="INFO"):
    data = f"{datetime.now()} > {cat} > {informations}"
    print(data)
    save_log(data)

def save_log(data,log_file = r"C:\Users\tallar\Documents\PROJETS\GenAI\src\services\logs\logs.txt"):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(data + "\n")