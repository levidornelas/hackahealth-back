from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(
    title="DATASUS API",
    description="API para análise de dados do DATASUS",
    version="1.0.0"
)

# Modelos Pydantic
class EstatisticasBasicas(BaseModel):
    contagem: int
    media: float
    desvio_padrao: float
    minimo: float
    q25: float
    mediana: float
    q75: float
    maximo: float

class DadosHospital(BaseModel):
    hospital: str
    custo_total: float
    quantidade_pacientes: int

class DadosCID(BaseModel):
    cid: str
    tempo_medio_internacao: float
    quantidade_pacientes: int

# Função para converter gráfico para base64
def plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode()
    buf.close()
    plt.close(fig)
    return img_str

# Função para criar gráfico de barras
def create_bar_chart(data, x, y, title, xlabel, ylabel, rotation=45):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(data[x], data[y], color='skyblue')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=rotation)
    plt.tight_layout()
    return fig

# Rotas da API
@app.get("/")
async def root():
    return {"message": "DATASUS API está funcionando"}

@app.get("/estatisticas", response_model=Dict[str, EstatisticasBasicas])
async def get_estatisticas():
    try:
        df = pd.read_csv("datasus.csv")
        stats = df.describe().to_dict()
        return {col: EstatisticasBasicas(**stat) for col, stat in stats.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hospitais", response_model=List[DadosHospital])
async def get_dados_hospitais():
    try:
        df = pd.read_csv("datasus.csv")
        hospitais = df.groupby('Hospital').agg({
            'Custo_Total_Atendimento': 'sum',
            'Paciente_ID': 'count'
        }).reset_index()
        
        return [
            DadosHospital(
                hospital=row['Hospital'],
                custo_total=float(row['Custo_Total_Atendimento']),
                quantidade_pacientes=int(row['Paciente_ID'])
            )
            for _, row in hospitais.iterrows()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cids", response_model=List[DadosCID])
async def get_dados_cid():
    try:
        df = pd.read_csv("datasus.csv")
        cids = df.groupby('CID_Principal').agg({
            'Tempo_Internação_Dias': 'mean',
            'Paciente_ID': 'count'
        }).reset_index()
        
        return [
            DadosCID(
                cid=row['CID_Principal'],
                tempo_medio_internacao=float(row['Tempo_Internação_Dias']),
                quantidade_pacientes=int(row['Paciente_ID'])
            )
            for _, row in cids.iterrows()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graficos/{tipo}")
async def get_grafico(tipo: str):
    try:
        df = pd.read_csv("datasus.csv")
        
        if tipo == "sexo":
            sexo_counts = df['Sexo'].value_counts().reset_index()
            sexo_counts.columns = ['Sexo', 'Contagem']  # Renomeando as colunas
            fig = create_bar_chart(
                sexo_counts,
                'Sexo', 'Contagem',
                'Distribuição de Pacientes por Sexo',
                'Sexo', 'Número de Pacientes'
            )
        
        elif tipo == "hospital":
            hospital_costs = df.groupby('Hospital')['Custo_Total_Atendimento'].sum().reset_index()
            fig = create_bar_chart(
                hospital_costs,
                'Hospital', 'Custo_Total_Atendimento',
                'Custo Total por Hospital',
                'Hospital', 'Custo Total (R$)'
            )
        
        elif tipo == "cid":
            cid_tempo = df.groupby('CID_Principal')['Tempo_Internação_Dias'].mean().reset_index()
            fig = create_bar_chart(
                cid_tempo,
                'CID_Principal', 'Tempo_Internação_Dias',
                'Tempo Médio de Internação por CID Principal',
                'CID Principal', 'Tempo de Internação (Dias)'
            )
        
        else:
            raise HTTPException(status_code=400, detail="Tipo de gráfico inválido")
        
        img_str = plot_to_base64(fig)
        return JSONResponse(content={"image": img_str})
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo 'datasus.csv' não encontrado")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Coluna não encontrada no CSV: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)