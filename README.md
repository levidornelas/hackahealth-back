# API de Evolução do Paciente

Esta API foi desenvolvida para analisar e visualizar dados de evolução de pacientes, especialmente em contextos pós-operatórios. Ela fornece gráficos interativos e análises sobre parâmetros médicos, comparando-os com intervalos de referência pré-definidos. Ela foi desenvolvida para o Hackahealth 2025, promovido pelo Porto Digital e Sebrae. 

## Funcionalidades

- **Gráficos de Evolução**: Gera gráficos de linha mostrando a evolução dos parâmetros médicos ao longo do tempo.
- **Análise de Tendência**: Analisa se os valores dos parâmetros estão melhorando, piorando ou oscilando.
- **Intervalos de Referência**: Compara os valores dos parâmetros com intervalos de referência pré-definidos.
- **Dashboard Interativo**: Retorna gráficos e análises em formato JSON para integração com frontends.

## Como Usar

1. **Instalação**:
   - Certifique-se de ter Python 3.7+ instalado.
   - Instale as dependências com `pip install -r requirements.txt`.

2. **Execução**:
   - Execute a API com o comando:
     ```bash
     uvicorn main:medData --host 0.0.0.0 --port 8000
     ```
   - A API estará disponível em `http://localhost:8000`.

3. **Endpoint**:
   - Acesse o endpoint `/dashboard-y` para obter os gráficos e análises:
     ```bash
     GET /dashboard-y
     ```

## Estrutura do Projeto

- `main.py`: Contém o código da API.
- `dataset.csv`: Arquivo CSV com os dados dos pacientes.
- `README.md`: Este arquivo, com informações sobre o projeto.

## Exemplo de Resposta

A resposta do endpoint `/dashboard-y` inclui:

- **Gráficos**: Imagens codificadas em base64 dos gráficos de evolução.
- **Análise**: Status e tendência de cada parâmetro analisado.

```json
{
  "graficos": {
    "INR/TAP": "base64_encoded_image",
    "Lactato (mmol/L)": "base64_encoded_image"
  },
  "analise": {
    "INR/TAP": {
      "valores": [1.1, 1.3, 1.2, 1.1],
      "referencia": [0.8, 1.2],
      "status_atual": "Acima",
      "tendencia": "MELHORANDO ↓",
      "valor_atual": 1.1
    }
  }
}
