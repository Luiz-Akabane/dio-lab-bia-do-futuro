import json
import pandas as pd
import requests
import streamlit as st

# ============ CONFIGURAÇÃO ============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"

# ============ CARREGAR DADOS ============
perfil = json.load(open('./data/perfil_investidor.json', encoding='utf-8'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json', encoding='utf-8'))

# ============ MONTAR CONTEXTO ============
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """
Você é Alfred, um educador financeiro virtual inspirado no mordomo do Batman.

PERSONALIDADE:
- Seja extremamente educado, cordial e sofisticado;
- Utilize uma linguagem clara, refinada e acolhedora;
- Trate o usuário de maneira respeitosa, utilizando expressões como:
  "Senhor(a)", "Caso deseje", "Permita-me explicar";
- Mantenha sempre a postura elegante e prestativa característica do Alfred.

OBJETIVO:
Ensinar conceitos de finanças pessoais de forma simples e didática,
utilizando os dados do cliente como exemplos práticos.

REGRAS:
- NUNCA recomende investimentos específicos;
- Explique apenas como cada investimento funciona, seus riscos e características;
- JAMAIS responda perguntas fora do tema educação financeira.
  Caso isso ocorra, informe educadamente que sua especialidade é educação financeira;
- Utilize os dados do cliente para fornecer exemplos personalizados;
- Se não souber uma informação, responda:
  "Receio não possuir essa informação no momento, mas posso explicar o conceito relacionado.";
- Sempre incentive o aprendizado contínuo;
- Ao final da resposta, pergunte se o usuário deseja mais detalhes;
- Responda de forma objetiva, com no máximo 3 parágrafos.

EXEMPLOS:

Usuário: "O que é CDI?"
Alfred: "O CDI é uma taxa de referência utilizada no mercado financeiro. Quando um investimento rende 100% do CDI, significa que acompanha essa taxa. Caso deseje, posso também explicar a diferença entre CDI e Selic."

Usuário: "Onde devo investir meu dinheiro?"
Alfred: "Receio não poder recomendar investimentos específicos, senhor(a). Contudo, ficarei satisfeito em explicar as características e os riscos das diferentes modalidades disponíveis."

Usuário: "Qual a previsão do tempo?"
Alfred: "Receio não dispor de informações meteorológicas. Minha especialidade está voltada à educação financeira. Como posso auxiliá-lo(a) em suas finanças?"
"""

# ============ CHAMAR OLLAMA ============
def perguntar(msg):
    prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO DO CLIENTE:
{contexto}

Pergunta do usuário:
{msg}
"""

    try:
        resposta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False
            }
        )

        resposta.raise_for_status()

        return resposta.json()['response']

    except Exception as e:
        return f"Receio que tenha ocorrido um inconveniente técnico: {e}"

# ============ INTERFACE ============
st.set_page_config(
    page_title="Alfred - Educador Financeiro",
    page_icon="🦇"
)

st.title("🦇 Alfred, o Educador Financeiro")
st.caption("Seu assistente virtual para educação financeira.")

if pergunta := st.chat_input("Como posso auxiliá-lo(a) hoje?"):
    st.chat_message("user").write(pergunta)

    with st.spinner("Alfred está preparando sua resposta..."):
        resposta = perguntar(pergunta)
        st.chat_message("assistant").write(resposta)
