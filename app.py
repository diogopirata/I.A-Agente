import streamlit as st
import google.generativeai as genai
import json
import os
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- Configurações de Caminho do Histórico ---
HISTORY_FILE = "historico_respostas_streamlit.json"

# --- CSS Customizado para Melhorar a Aparência ---
def load_custom_css():
    st.markdown("""
    <style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Aplicar fonte personalizada */
    .main, .sidebar .sidebar-content {
        font-family: 'Inter', sans-serif;
    }
    
    /* Estilizar título principal */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Estilizar subtítulos */
    .custom-subheader {
        color: #2c3e50;
        font-weight: 600;
        font-size: 1.4rem;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
    
    /* Card personalizado */
    .custom-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        color: #2d3748;
    }
    
    /* Card de análise com fundo escuro para melhor contraste */
    .analysis-card {
        background: #2d3748;
        color: #e2e8f0;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #4a5568;
        margin: 1rem 0;
        line-height: 1.6;
    }
    
    .analysis-card h1, .analysis-card h2, .analysis-card h3 {
        color: #e2e8f0;
    }
    
    .analysis-card strong {
        color: #90cdf4;
    }
    
    /* Botão personalizado */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Botão secundário */
    .secondary-button > button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        width: 100%;
    }
    
    .secondary-button > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(72, 187, 120, 0.4);
    }
    
    /* Estilizar sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Estilizar métricas */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Estilizar alertas de sucesso */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        border-radius: 8px;
    }
    
    /* Estilizar alertas de erro */
    .stError {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        border-radius: 8px;
    }
    
    /* Estilizar expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Animação de loading personalizada */
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Estilizar text areas */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        font-family: 'Fira Code', monospace;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Funções para Gerenciamento de Histórico ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                st.warning("⚠️ Arquivo de histórico corrompido. Iniciando um novo histórico.")
                return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# --- Função para criar visualizações dos dados ---
def create_data_visualizations(data):
    try:
        df = pd.DataFrame(data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="custom-subheader">📊 Vendas por Produto</div>', unsafe_allow_html=True)
            vendas_produto = df.groupby('produto')['vendas'].sum().reset_index()
            fig_produto = px.bar(
                vendas_produto, 
                x='produto', 
                y='vendas',
                color='vendas',
                color_continuous_scale='viridis',
                title="Total de Vendas por Produto"
            )
            fig_produto.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter"
            )
            st.plotly_chart(fig_produto, use_container_width=True)
        
        with col2:
            st.markdown('<div class="custom-subheader">🌍 Vendas por Região</div>', unsafe_allow_html=True)
            vendas_regiao = df.groupby('regiao')['vendas'].sum().reset_index()
            fig_regiao = px.pie(
                vendas_regiao, 
                values='vendas', 
                names='regiao',
                color_discrete_sequence=px.colors.qualitative.Set3,
                title="Distribuição de Vendas por Região"
            )
            fig_regiao.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter"
            )
            st.plotly_chart(fig_regiao, use_container_width=True)
        
        # Métricas resumidas
        st.markdown('<div class="custom-subheader">📈 Métricas Principais</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_vendas = df['vendas'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3>💰 Total Vendas</h3>
                <h2>{total_vendas:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            produtos_unicos = df['produto'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>🛍️ Produtos</h3>
                <h2>{produtos_unicos}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            regioes_unicas = df['regiao'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌎 Regiões</h3>
                <h2>{regioes_unicas}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            media_vendas = df['vendas'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Média</h3>
                <h2>{media_vendas:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Erro ao criar visualizações: {e}")

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="🚀 Agente de Análise de Dados IA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar CSS customizado
load_custom_css()

# --- Header Principal ---
st.markdown('<h1 class="main-title">🚀 Agente de Análise de Dados com IA</h1>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">
    Transforme seus dados em insights poderosos com a inteligência artificial do Google Gemini
</div>
""", unsafe_allow_html=True)

# --- Sidebar Melhorada ---
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    
    # Entrada da API Key com design melhorado
    st.markdown("### 🔑 Autenticação")
    api_key = st.text_input(
        "Chave de API do Google Gemini:", 
        type="password", 
        help="🔒 Sua chave é segura e não será armazenada",
        placeholder="Cole sua API key aqui..."
    )
    
    if api_key:
        st.success("✅ API Key configurada!")
    
    st.markdown("---")
    
    # Estatísticas do histórico
    historico_respostas = load_history()
    st.markdown("### 📚 Histórico")
    st.metric("Análises Realizadas", len(historico_respostas))
    
    if st.button("🗑️ Limpar Histórico", type="secondary"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            st.success("Histórico limpo!")
            st.experimental_rerun()

# --- Verificação da API ---
model_name = 'models/gemini-1.5-flash'
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        disponivel_modelo_escolhido = False
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                if m.name == model_name:
                    disponivel_modelo_escolhido = True
        
        if not disponivel_modelo_escolhido:
            st.error(f"❌ O modelo '{model_name}' não foi encontrado.")
            with st.expander("Ver modelos disponíveis"):
                for name in available_models:
                    st.write(f"• {name}")
            st.stop()

    except Exception as e:
        st.error(f"❌ Erro ao configurar API: {e}")
        st.stop()

# --- Seção de Entrada de Dados ---
st.markdown('<div class="custom-subheader">📋 Dados de Vendas</div>', unsafe_allow_html=True)

default_data = """[
  {"produto": "Camiseta", "vendas": 150, "regiao": "Sudeste", "mes": "Jan"},
  {"produto": "Calça", "vendas": 80, "regiao": "Nordeste", "mes": "Jan"},
  {"produto": "Tênis", "vendas": 200, "regiao": "Sudeste", "mes": "Fev"},
  {"produto": "Camiseta", "vendas": 100, "regiao": "Sul", "mes": "Fev"},
  {"produto": "Bermuda", "vendas": 70, "regiao": "Norte", "mes": "Jan"},
  {"produto": "Boné", "vendas": 120, "regiao": "Sudeste", "mes": "Fev"}
]"""

dados_vendas = st.text_area(
    "Cole seus dados JSON aqui:", 
    default_data, 
    height=300,
    help="📝 Formato JSON válido com campos: produto, vendas, regiao, mes"
)

# Validação do JSON
dados_validos = False
if dados_vendas:
    try:
        data_parsed = json.loads(dados_vendas)
        dados_validos = True
        
        # Mostrar visualizações dos dados
        create_data_visualizations(data_parsed)
        
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON inválido: {e}")
        dados_validos = False

# --- Função para gerar análise ---
def gerar_analise(user_question=""):
    if not api_key:
        st.warning("⚠️ Por favor, configure sua API Key na barra lateral.")
        return
    elif not dados_validos:
        st.warning("⚠️ Por favor, forneça dados JSON válidos.")
        return
    
    # Loading animation personalizada
    with st.spinner("🤖 Analisando seus dados com IA..."):
        try:
            model = genai.GenerativeModel(model_name)

            # Prompt melhorado
            prompt_analise = f"""
Você é um analista de dados sênior especializado em vendas e business intelligence. 
Analise os seguintes dados de vendas e forneça insights estratégicos e acionáveis.

**Dados de Vendas:**
{dados_vendas}

**Análise Solicitada:**
1. **📊 Resumo Executivo:** Principais números e tendências em 2-3 frases
2. **🏆 Top Performers:** Produtos e regiões com melhor desempenho
3. **⚠️ Pontos de Atenção:** Produtos ou regiões que precisam de foco
4. **📈 Tendências Temporais:** Análise mês a mês (se aplicável)
5. **💡 Recomendações Estratégicas:** 3-4 ações concretas para melhorar vendas
6. **🎯 Oportunidades:** Onde focar esforços para maximizar resultados
"""
            
            if user_question.strip():
                prompt_analise += f"""

**🔍 Pergunta Específica do Usuário:**
{user_question}

Por favor, responda à pergunta específica APÓS a análise padrão.
"""
            
            prompt_analise += """

**Formato da Resposta:**
- Use emojis para tornar a resposta mais visual
- Estruture com títulos claros
- Inclua números específicos quando relevante
- Seja conciso mas detalhado
- Use linguagem profissional mas acessível
"""

            generation_config = {
                "temperature": 0.1, 
                "max_output_tokens": 8192
            }

            response = model.generate_content(
                prompt_analise, 
                generation_config=generation_config
            )
            analysis_text = response.text
            
            # Exibir análise com design melhorado
            st.markdown('<div class="custom-subheader">🎉 Análise Gerada pela IA</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="analysis-card">
                {analysis_text}
            </div>
            """, unsafe_allow_html=True)
            
            # Salvar no histórico
            historico_respostas = load_history()
            nova_entrada = {
                "timestamp": datetime.datetime.now().isoformat(),
                "prompt_original": prompt_analise,
                "pergunta_usuario": user_question,
                "dados_analisados": dados_vendas,
                "resposta_gemini": analysis_text
            }
            historico_respostas.append(nova_entrada)
            save_history(historico_respostas)
            
            st.success("✅ Análise salva no histórico!")

        except Exception as e:
            st.error(f"❌ Erro ao gerar análise: {e}")

# --- Botões de Análise ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Gerar Análise Inteligente Agente", type="primary"):
        gerar_analise()

with col2:
    # Aplicar CSS personalizado para o botão secundário
    st.markdown('<div class="secondary-button">', unsafe_allow_html=True)
    if st.button("💬 Ou Faça sua Pergunta", type="secondary"):
        # Mostrar campo de input para pergunta
        st.session_state.show_question_input = True
    st.markdown('</div>', unsafe_allow_html=True)

# --- Campo de pergunta condicional ---
if st.session_state.get('show_question_input', False):
    st.markdown("---")
    user_question = st.text_input(
        "Digite sua pergunta específica sobre os dados:",
        placeholder="Ex: Qual produto teve melhor performance? Quais regiões precisam de atenção?",
        key="user_question_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔍 Analisar com Pergunta Agente", type="primary"):
            if user_question:
                gerar_analise(user_question)
                st.session_state.show_question_input = False
                st.experimental_rerun()
            else:
                st.warning("Por favor, digite uma pergunta.")

# --- Seção de Histórico ---
st.markdown("---")
st.markdown('<div class="custom-subheader">📚 Histórico de Análises</div>', unsafe_allow_html=True)

historico_respostas = load_history()
if historico_respostas:
    historico_respostas.reverse()
    
    for i, entry in enumerate(historico_respostas[:5]):  # Mostrar apenas as 5 mais recentes
        timestamp = entry.get('timestamp', 'Data Indisponível')
        try:
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp_formatted = dt.strftime("%d/%m/%Y às %H:%M")
        except:
            timestamp_formatted = timestamp
            
        with st.expander(f"📋 Análise #{len(historico_respostas) - i} - {timestamp_formatted}"):
            if entry.get('pergunta_usuario'):
                st.markdown(f"**🔍 Pergunta:** {entry.get('pergunta_usuario')}")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**📊 Análise:**")
                st.markdown(f"""
                <div class="analysis-card">
                    {entry.get('resposta_gemini', 'Conteúdo não encontrado.')}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📋 Dados (amostra):**")
                dados_sample = entry.get('dados_analisados', 'N/A')[:200]
                st.code(dados_sample + "..." if len(dados_sample) == 200 else dados_sample, language="json")
    
    if len(historico_respostas) > 5:
        st.info(f"📝 Mostrando as 5 análises mais recentes de {len(historico_respostas)} total.")
else:
    st.info("📭 Nenhuma análise anterior encontrada. Faça sua primeira análise!")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem;">
    <p>🚀 <strong>Agente de Análise de Dados com IA</strong></p>
    <p>Desenvolvido com ❤️ usando Streamlit e Google Gemini API</p>
    <p><small>Versão 2.2 - Botões Aprimorados</small></p>
</div>
""", unsafe_allow_html=True)

