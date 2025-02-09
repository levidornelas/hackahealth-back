from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

# Cria uma instância do FastAPI com metadados sobre a API
medData = FastAPI(
    title="API de Evolução do Paciente",
    description="API para análise e visualização de dados de evolução do paciente",
    version="1.0.0"
)

# Configura o middleware CORS para permitir requisições de origens específicas
medData.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.0.104:3000", "http://10.0.50.217:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dicionário com os intervalos de referência para cada exame
REFERENCE_RANGES = {
    'INR/TAP': (0.8, 1.2),
    'Lactato (mmol/L)': (0.5, 1.6),
    'AST (U/L)': (5, 40),
    'ALT (U/L)': (7, 56),
    'pH (Gasometria)': (7.35, 7.45),
    'pCO₂ (mmHg)': (35, 45),
    'pO₂ (mmHg)': (80, 100),
    'HCO₃⁻ (mmol/L)': (22, 26),
    'BE (Base Excess)': (-2, 2),
    'Creatinina (mg/dL)': (0.7, 1.2),
    'Plaquetas (x10³/µL)': (150, 400),
    'Bilirrubina Total (mg/dL)': (0.3, 1.2),
    'Bilirrubina Direta (mg/dL)': (0.1, 0.3),
    'Bilirrubina Indireta (mg/dL)': (0.2, 0.9),
    'Fibrinogênio (mg/dL)': (200, 400),
    'Glicemia (mg/dL)': (70, 100),
    'Leucócitos (x10³/µL)': (4.0, 11.0),
    'PCR (mg/L)': (0, 10),
    'Procalcitonina (ng/mL)': (0, 0.5)
}

# Converte um gráfico matplotlib para uma string base64
def plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode()
    buf.close()
    plt.close(fig)
    return img_str

# Cria um gráfico de linha aprimorado com intervalos de referência
def create_enhanced_line_chart(data, x, y, title, xlabel, ylabel, exame):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plota a linha principal
    ax.plot(data[x], data[y], marker="o", linestyle="-", color="b", label="Valores")
    
    # Adiciona intervalos de referência, se disponíveis
    if exame in REFERENCE_RANGES:
        ref_min, ref_max = REFERENCE_RANGES[exame]
        ax.axhline(y=ref_min, color='g', linestyle='--', alpha=0.5, label=f'Min: {ref_min}')
        ax.axhline(y=ref_max, color='r', linestyle='--', alpha=0.5, label=f'Max: {ref_max}')
        ax.fill_between(data[x], ref_min, ref_max, color='green', alpha=0.1)
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()
    return fig

# Analisa a tendência dos valores (melhorando, piorando ou oscilando)
def analyze_trend(values):
    if len(values) < 2:
        return "Insuficiente"
    recent_trend = values[-2:]
    if np.all(np.diff(recent_trend) > 0):
        return "PIORANDO ↑"
    elif np.all(np.diff(recent_trend) < 0):
        return "MELHORANDO ↓"
    return "OSCILANDO →"

# Analisa o status e a tendência de um parâmetro específico
def analyze_parameter(param, values, ref_range):
    if len(values) < 2:
        return {"status": "Insuficiente", "tendencia": "Insuficiente"}
    
    ref_min, ref_max = ref_range
    last_value = values[-1]
    prev_value = values[-2]
    
    # Determina o status atual
    if last_value < ref_min:
        status = "Abaixo"
    elif last_value > ref_max:
        status = "Acima"
    else:
        status = "Normal"
    
    # Determina a tendência
    if param in ['pH (Gasometria)', 'BE (Base Excess)', 'HCO₃⁻ (mmol/L)', 'pCO₂ (mmHg)', 'pO₂ (mmHg)']:
        dist_to_range_last = min(abs(last_value - ref_min), abs(last_value - ref_max))
        dist_to_range_prev = min(abs(prev_value - ref_min), abs(prev_value - ref_max))
        tendencia = "MELHORANDO ↓" if dist_to_range_last < dist_to_range_prev else "PIORANDO ↑"
    else:
        if last_value > ref_max:
            tendencia = "MELHORANDO ↓" if last_value < prev_value else "PIORANDO ↑"
        elif last_value < ref_min:
            tendencia = "MELHORANDO ↑" if last_value > prev_value else "PIORANDO ↓"
        else:
            tendencia = "NORMALIZADO ✓"
    
    return {"status": status, "tendencia": tendencia}

# Endpoint para obter o dashboard do paciente Y
@medData.get("/dashboard-y")
async def get_dashboard_paciente_y():
    try:
        # Carrega o arquivo CSV
        df = pd.read_csv("dataset.csv")
        
        # Transforma os dados para análise
        data = []
        analysis_results = {}
        
        for _, row in df.iterrows():
            parametro = row["Parâmetro"]
            valores = [
                row["Pré-Operatório"],
                row["Pós-Operatório (24h)"],
                row["Pós-Operatório (48h)"],
                row["Pós-Operatório (72h)"]
            ]
            
            # Adiciona os dados transformados para plotagem
            for idx, categoria in enumerate(["Pré-Operatório", "Pós-Operatório (24h)", "Pós-Operatório (48h)", "Pós-Operatório (72h)"]):
                data.append([categoria, parametro, valores[idx]])
            
            # Analisa o parâmetro se o intervalo de referência existir
            if parametro in REFERENCE_RANGES:
                analysis = analyze_parameter(parametro, valores, REFERENCE_RANGES[parametro])
                analysis_results[parametro] = {
                    "valores": valores,
                    "referencia": REFERENCE_RANGES[parametro],
                    "status_atual": analysis["status"],
                    "tendencia": analysis["tendencia"],
                    "valor_atual": valores[-1]
                }

        # Cria um DataFrame para plotagem
        df_transformed = pd.DataFrame(data, columns=["Categoria", "Exame", "Valor"])
        df_transformed["Categoria"] = pd.Categorical(
            df_transformed["Categoria"],
            categories=["Pré-Operatório", "Pós-Operatório (24h)", "Pós-Operatório (48h)", "Pós-Operatório (72h)"],
            ordered=True
        )
        df_transformed = df_transformed.sort_values(by=["Exame", "Categoria"])

        # Gera gráficos aprimorados
        graficos = {}
        exames = df_transformed["Exame"].unique()
        for exame in exames:
            df_exame = df_transformed[df_transformed["Exame"] == exame]
            fig = create_enhanced_line_chart(
                df_exame,
                "Categoria", "Valor",
                f"Evolução do {exame}",
                "Categoria", "Valor",
                exame
            )
            img_str = plot_to_base64(fig)
            graficos[exame] = img_str

        return JSONResponse(content={
            "graficos": graficos,
            "analise": analysis_results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Inicia o servidor FastAPI
import uvicorn
uvicorn.run(medData, host="192.168.0.104", port=8000)