import pandas as pd

# Texto dos exames
dados = """
pH: 7,25
pCO₂: 30 mmHg
HCO₃⁻: 15 mEq/L
Lactato: 4,5 mmol/L

Pré-operatório
pH: 7,40
pCO₂: 40 mmHg
HCO₃⁻: 24 mEq/L
Lactato: 1,2 mmol/L

"""
# Processar os dados
linhas = dados.strip().split("\n")
data = []
categoria = "Pós-operatório"  # Definição inicial da categoria

for linha in linhas:
    linha = linha.strip()  # Remove espaços extras
    if not linha:  
        continue  # Ignora linhas vazias
    if "Pré-operatório" in linha:
        categoria = "Pré-operatório"
        continue
    if ":" in linha:  # Verifica se a linha tem o formato correto
        exame, valor = linha.split(":", 1)  # Divide apenas na primeira ocorrência de ":"
        data.append([categoria, exame.strip(), valor.strip()])

# Criar DataFrame e salvar em CSV
df = pd.DataFrame(data, columns=["Categoria", "Exame", "Valor"])
df.to_csv("exames_convertidos.csv", index=False, encoding="utf-8")

print("CSV gerado com sucesso!")
