import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Lumina - Curadoria Pedagógica", page_icon="✨", layout="wide")

# Inicializa o estado da sessão no Streamlit
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "info_login" not in st.session_state:
    st.session_state["info_login"] = None

# =========================================================================
# BARRA LATERAL: LOGIN (Redis Cache + Bloom Filter + HyperLogLog)
# =========================================================================
st.sidebar.title("✨ Lumina")
st.sidebar.caption("Plataforma de Curadoria Pedagógica")

if st.session_state["usuario"] is None:
    st.sidebar.subheader("Acesso ao Sistema")
    email_input = st.sidebar.text_input("E-mail institucional", placeholder="laura.silva@escola.edu.br")
    
    if st.sidebar.button("Entrar", use_container_width=True):
        resp = requests.post(f"{API_URL}/login", json={"email": email_input})
        if resp.status_code == 200:
            dados = resp.json()
            st.session_state["usuario"] = dados["usuario"]
            st.session_state["info_login"] = dados
            st.rerun()
        else:
            st.sidebar.error(resp.json().get("detail", "Erro ao fazer login"))
    
    st.sidebar.info("💡 **Dica de teste:**\n- `laura.silva@escola.edu.br`\n- `renan.silva@escola.edu.br`")
else:
    u = st.session_state["usuario"]
    info = st.session_state["info_login"]
    st.sidebar.success(f"Olá, **{u['nome']}**!\n\nPerfil: `{u['perfil_acesso']}`")
    st.sidebar.caption(f"⚡ Origem: {info['origem_dados']}")
    st.sidebar.caption(f"⏱️ TTL do Cache: {info['ttl_restante_seg']}s")
    
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state["usuario"] = None
        st.session_state["info_login"] = None
        st.rerun()

# =========================================================================
# CORPO PRINCIPAL
# =========================================================================
st.title("✨ Lumina — Curadoria Pedagógica Digital")

aba1, aba2, aba3 = st.tabs(["📚 Trilhas Pedagógicas", "📊 Relatórios (MongoDB)", "⚡ Estatísticas em Tempo Real (Redis)"])

# -------------------------------------------------------------------------
# ABA 1: TRILHAS (MongoDB + Count-Min Sketch)
# -------------------------------------------------------------------------
with aba1:
    st.subheader("Trilhas Disponíveis")
    trilhas = requests.get(f"{API_URL}/trilhas").json()
    
    for t in trilhas:
        with st.expander(f"📘 {t['titulo']}  |  Faixa etária: {t['faixa_etaria']}"):
            st.write(f"**Criador:** {t['criador'].get('nome', 'Não informado')}")
            
            # Botão que registra visualização no Count-Min Sketch (Redis)
            if st.button(f"👁️ Registrar Visualização ({t['_id']})", key=f"btn_{t['_id']}"):
                r_vis = requests.post(f"{API_URL}/trilhas/{t['_id']}/visualizar").json()
                st.toast(f"Visualização registrada! Total estimado no Redis: {r_vis['acessos_estimados']}")
            
            st.markdown("**Materiais embutidos:**")
            for m in t.get("materiais", []):
                cor = "🟢" if m["status"] == "aprovado" else "🟡"
                tags_str = ", ".join(m.get("tags", []))
                st.markdown(f"- {cor} **{m['titulo']}** ({m['tipo']}) — Status: `{m['status']}` | Tags: *{tags_str}*")

# -------------------------------------------------------------------------
# ABA 2: PIPELINES DE AGREGAÇÃO (MongoDB)
# -------------------------------------------------------------------------
with aba2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏷️ Ranking de Tags Aprovadas")
        st.caption("Pipeline 1: $unwind → $match → $unwind → $group → $sort")
        tags_data = requests.get(f"{API_URL}/relatorios/tags").json()
        if tags_data:
            df_tags = pd.DataFrame(tags_data).rename(columns={"_id": "Tag", "total_aparicoes": "Aparições"})
            st.bar_chart(df_tags.set_index("Tag"))
            st.dataframe(df_tags, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("✅ Prontidão das Trilhas")
        st.caption("Pipeline 2: $addFields + $filter + $switch")
        prontidao_data = requests.get(f"{API_URL}/relatorios/prontidao").json()
        if prontidao_data:
            df_pront = pd.DataFrame([
                {
                    "Trilha": p["titulo"],
                    "Aprovados": f"{p['materiais_aprovados']}/{p['total_materiais']}",
                    "Aprovação (%)": p["percentual_aprovacao"],
                    "Status": p["status_prontidao"]
                }
                for p in prontidao_data
            ])
            st.dataframe(df_pront, use_container_width=True, hide_index=True)

# -------------------------------------------------------------------------
# ABA 3: ESTRUTURAS PROBABILÍSTICAS (Redis)
# -------------------------------------------------------------------------
with aba3:
    st.subheader("Métricas de Uso via Estruturas Probabilísticas")
    if st.button("🔄 Atualizar Métricas"):
        st.rerun()
        
    stats = requests.get(f"{API_URL}/estatisticas/redis").json()
    
    st.metric(label="👥 Usuários Únicos Hoje (HyperLogLog)", value=stats["usuarios_unicos_hoje_hll"])
    
    st.markdown("#### 🔥 Popularidade das Trilhas (Count-Min Sketch)")
    cms_data = stats["acessos_por_trilha_cms"]
    if cms_data:
        df_cms = pd.DataFrame(list(cms_data.items()), columns=["Trilha ID", "Acessos Estimados"])
        st.bar_chart(df_cms.set_index("Trilha ID"))
        st.dataframe(df_cms, use_container_width=True, hide_index=True)