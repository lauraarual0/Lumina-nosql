import redis
import json
import time
import os 
from dotenv import load_dotenv
load_dotenv() 

# 1. CONEXÃO COM O REDIS CLOUD
r = redis.Redis(
    host="wellcrafted-field-health-80288.db.redis.io",
    port=18925,
    username="default",
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# Testa a conexão
print("Conexão com Redis:", "OK!" if r.ping() else "Falhou")
print("-" * 50)

# =========================================================================
# 2. CACHE DE LOGIN DE USUÁRIO (String + TTL)
# =========================================================================
print("=== 1. CACHE DE LOGIN ===")

# Simulando dados vindos do MongoDB após o login
usuario_logado = {
    "id": "usr_002",
    "nome": "Laura Silva",
    "perfil": "colaborador"
}

chave_sessao = "sessao:usr_002"

# Salva no Redis com expiração (TTL) de 60 segundos para teste
r.setex(chave_sessao, 60, json.dumps(usuario_logado))

# Busca do cache (Cache Hit)
dados_cache = r.get(chave_sessao)
tempo_restante = r.ttl(chave_sessao)

print(f"Sessão recuperada do cache: {dados_cache}")
print(f"Tempo restante da sessão (TTL): {tempo_restante} segundos\n")

# =========================================================================
# 3. BLOOM FILTER (BF) - Checar se e-mail já existe no sistema
# =========================================================================
print("=== 2. BLOOM FILTER (E-mails Cadastrados) ===")

chave_bf = "bf:emails_cadastrados"
r.delete(chave_bf)  # Limpa para permitir rodar o script várias vezes

# Cria o Bloom Filter (taxa de erro 1%, capacidade inicial 1000 itens)
r.bf().reserve(chave_bf, 0.01, 1000)

# Adiciona os e-mails cadastrados no Lumina
r.bf().add(chave_bf, "renan.silva@escola.edu.br")
r.bf().add(chave_bf, "laura.silva@escola.edu.br")

# Testa consultas rápidas
email_existente = "laura.silva@escola.edu.br"
email_novo = "visitante@escola.edu.br"

print(f"'{email_existente}' existe? {bool(r.bf().exists(chave_bf, email_existente))}")
print(f"'{email_novo}' existe? {bool(r.bf().exists(chave_bf, email_novo))}\n")

# =========================================================================
# 4. HYPERLOGLOG (HLL) - Contar usuários únicos no dia
# =========================================================================
print("=== 3. HYPERLOGLOG (Usuários Únicos Hoje) ===")

chave_hll = "hll:usuarios_unicos:2026-11-25"
r.delete(chave_hll)

# Simula vários acessos (Laura entra 3 vezes, Renan entra 2 vezes)
r.pfadd(chave_hll, "usr_002", "usr_002", "usr_001", "usr_002", "usr_001")

total_unicos = r.pfcount(chave_hll)
print(f"Total de acessos simulados: 5 | Usuários ÚNICOS contados: {total_unicos}\n")

# =========================================================================
# 5. COUNT-MIN SKETCH (CMS) - Frequência de acesso por trilha
# =========================================================================
print("=== 4. COUNT-MIN SKETCH (Popularidade das Trilhas) ===")

chave_cms = "cms:acessos_trilhas"
r.delete(chave_cms)

# Inicializa o CMS (erro 0.1%, probabilidade 1%)
r.cms().initbyprob(chave_cms, 0.001, 0.01)

# Registra visualizações das trilhas
r.cms().incrby(
    chave_cms,
    ["trl_001", "trl_002", "trl_003"],
    [15, 4, 9]
)

# Consulta a estimativa de acessos
contagens = r.cms().query(chave_cms, "trl_001", "trl_002", "trl_003")
print(f"Acessos estimados -> trl_001: {contagens[0]} | trl_002: {contagens[1]} | trl_003: {contagens[2]}")