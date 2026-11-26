import os
import json
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import redis

load_dotenv()

app = FastAPI(title="Lumina API - MongoDB + Redis")

# 1. Conexão com MongoDB Atlas
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["lumina_db"]

# 2. Conexão com Redis Cloud
r = redis.Redis(
    host="wellcrafted-field-health-80288.db.redis.io",
    port=18925,
    username="default",
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# Garante que o Bloom Filter e o Count-Min Sketch existam no Redis
def inicializar_estruturas_redis():
    if not r.exists("bf:emails_cadastrados"):
        r.bf().reserve("bf:emails_cadastrados", 0.01, 1000)
        for u in db.usuarios.find({}, {"email": 1}):
            r.bf().add("bf:emails_cadastrados", u["email"])
    if not r.exists("cms:acessos_trilhas"):
        r.cms().initbyprob("cms:acessos_trilhas", 0.001, 0.01)

inicializar_estruturas_redis()

class LoginRequest(BaseModel):
    email: str

# =========================================================================
# ROTA 1: LOGIN (Bloom Filter + Cache TTL + HyperLogLog + MongoDB)
# =========================================================================
@app.post("/login")
def fazer_login(dados: LoginRequest):
    email = dados.email.strip().lower()

    # 1. Bloom Filter: barreira ultrarrápida contra e-mails inexistentes
    if not r.bf().exists("bf:emails_cadastrados", email):
        raise HTTPException(status_code=404, detail="E-mail não cadastrado (barrado pelo Bloom Filter).")

    chave_cache = f"sessao:{email}"
    origem = "Redis (Cache Hit)"

    # 2. Tenta buscar no Cache do Redis
    usuario_cache = r.get(chave_cache)
    if usuario_cache:
        usuario = json.loads(usuario_cache)
    else:
        # Cache Miss: busca no MongoDB e salva no Redis com TTL de 5 minutos
        usuario = db.usuarios.find_one({"email": email})
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado no MongoDB.")
        r.setex(chave_cache, 300, json.dumps(usuario))
        origem = "MongoDB (Cache Miss -> salvo no Redis)"

    # 3. HyperLogLog: registra usuário único do dia
    chave_hll = f"hll:usuarios_unicos:{date.today().isoformat()}"
    r.pfadd(chave_hll, usuario["_id"])

    return {
        "mensagem": "Login realizado com sucesso!",
        "origem_dados": origem,
        "ttl_restante_seg": r.ttl(chave_cache),
        "usuario": usuario
    }

# =========================================================================
# ROTA 2: LISTAR TRILHAS (MongoDB) E REGISTRAR ACESSO (Count-Min Sketch)
# =========================================================================
@app.get("/trilhas")
def listar_trilhas():
    trilhas = list(db.trilhas.find({}))
    return trilhas

@app.post("/trilhas/{trilha_id}/visualizar")
def registrar_visualizacao(trilha_id: str):
    r.cms().incrby("cms:acessos_trilhas", [trilha_id], [1])
    total = r.cms().query("cms:acessos_trilhas", trilha_id)[0]
    return {"trilha_id": trilha_id, "acessos_estimados": total}

# =========================================================================
# ROTA 3: PIPELINE 1 - RANKING DE TAGS APROVADAS (MongoDB)
# =========================================================================
@app.get("/relatorios/tags")
def ranking_tags():
    pipeline = [
        {"$unwind": "$materiais"},
        {"$match": {"materiais.status": "aprovado"}},
        {"$unwind": "$materiais.tags"},
        {"$group": {"_id": "$materiais.tags", "total_aparicoes": {"$sum": 1}}},
        {"$sort": {"total_aparicoes": -1}}
    ]
    return list(db.trilhas.aggregate(pipeline))

# =========================================================================
# ROTA 4: PIPELINE 2 - PAINEL DE PRONTIDÃO DAS TRILHAS (MongoDB)
# =========================================================================
@app.get("/relatorios/prontidao")
def painel_prontidao():
    pipeline = [
        {
            "$addFields": {
                "total_materiais": {"$size": "$materiais"},
                "materiais_aprovados": {
                    "$size": {
                        "$filter": {
                            "input": "$materiais",
                            "as": "mat",
                            "cond": {"$eq": ["$$mat.status", "aprovado"]}
                        }
                    }
                }
            }
        },
        {
            "$addFields": {
                "percentual_aprovacao": {
                    "$cond": [
                        {"$eq": ["$total_materiais", 0]},
                        0,
                        {"$round": [{"$multiply": [{"$divide": ["$materiais_aprovados", "$total_materiais"]}, 100]}, 1]}
                    ]
                }
            }
        },
        {
            "$addFields": {
                "status_prontidao": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$percentual_aprovacao", 100]}, "then": "Pronta para Aula"},
                            {"case": {"$gt": ["$percentual_aprovacao", 0]}, "then": "Parcialmente Aprovada"}
                        ],
                        "default": "Pendente de Curadoria"
                    }
                }
            }
        },
        {
            "$project": {
                "titulo": 1,
                "faixa_etaria": 1,
                "criador.nome": 1,
                "total_materiais": 1,
                "materiais_aprovados": 1,
                "percentual_aprovacao": 1,
                "status_prontidao": 1
            }
        }
    ]
    return list(db.trilhas.aggregate(pipeline))

# =========================================================================
# ROTA 5: ESTATÍSTICAS PROBABILÍSTICAS (Redis)
# =========================================================================
@app.get("/estatisticas/redis")
def estatisticas_redis():
    chave_hll = f"hll:usuarios_unicos:{date.today().isoformat()}"
    usuarios_unicos = r.pfcount(chave_hll)

    ids_trilhas = [t["_id"] for t in db.trilhas.find({}, {"_id": 1})]
    contagens = r.cms().query("cms:acessos_trilhas", *ids_trilhas) if ids_trilhas else []
    popularidade = dict(zip(ids_trilhas, contagens))

    return {
        "usuarios_unicos_hoje_hll": usuarios_unicos,
        "acessos_por_trilha_cms": popularidade
    }