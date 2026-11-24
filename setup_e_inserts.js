// Seleciona ou cria o banco de dados
use lumina_db;

// Limpa as coleções caso você precise rodar o script mais de uma vez para testar
db.usuarios.drop();
db.trilhas.drop();

// 1. Criação explícita das coleções
db.createCollection("usuarios");
db.createCollection("trilhas");

// 2. Inserção na coleção USUARIOS
db.usuarios.insertMany([
  {
    _id: "usr_001",
    nome: "Renan Silva",
    email: "renan.silva@escola.edu.br",
    perfil_acesso: "curador"
  },
  {
    _id: "usr_002",
    nome: "Laura Silva",
    email: "laura.silva@escola.edu.br",
    perfil_acesso: "colaborador"
  }
]);

// 3. Inserção na coleção TRILHAS (com criador e materiais embutidos)
db.trilhas.insertMany([
  {
    _id: "trl_001",
    titulo: "Semana de Ciências Naturais",
    faixa_etaria: "4 a 6 anos",
    data_criacao: new Date("2026-11-01T10:00:00Z"),
    criador: { id: "usr_002", nome: "Laura Silva" },
    materiais: [
      {
        titulo: "O Ciclo da Água - Animação",
        tipo: "video",
        tags: ["ciências", "meio ambiente", "lúdico"],
        detalhes_tecnicos: { duracao_min: 4.5, resolucao: "1080p" },
        status: "aprovado"
      },
      {
        titulo: "Cartilha de Coordenação Motora - Natureza",
        tipo: "pdf",
        tags: ["coordenação motora", "meio ambiente"],
        detalhes_tecnicos: { paginas: 12, tamanho_mb: 2.1 },
        status: "aprovado"
      }
    ]
  },
  {
    _id: "trl_002",
    titulo: "Introdução às Vogais e Sons",
    faixa_etaria: "3 a 5 anos",
    data_criacao: new Date("2026-11-05T14:30:00Z"),
    criador: { id: "usr_002", nome: "Laura Silva" },
    materiais: [
      {
        titulo: "Jogo das Vogais",
        tipo: "interativo",
        tags: ["alfabetização", "lúdico"],
        detalhes_tecnicos: { requer_internet: true, plataforma: "web" },
        status: "pendente"
      },
      {
        titulo: "Música do ABC",
        tipo: "video",
        tags: ["alfabetização", "música", "lúdico"],
        detalhes_tecnicos: { duracao_min: 3.0, resolucao: "720p" },
        status: "aprovado"
      }
    ]
  },
  {
    _id: "trl_003",
    titulo: "Projeto Água e Vida",
    faixa_etaria: "4 a 6 anos",
    data_criacao: new Date("2026-11-10T09:15:00Z"),
    criador: { id: "usr_001", nome: "Renan Silva" },
    materiais: [
      {
        titulo: "O Ciclo da Água - Animação",
        tipo: "video",
        tags: ["ciências", "meio ambiente", "lúdico"],
        detalhes_tecnicos: { duracao_min: 4.5, resolucao: "1080p" },
        status: "aprovado"
      },
      {
        titulo: "Experimento da Nuvem no Pote",
        tipo: "pdf",
        tags: ["ciências", "experimento"],
        detalhes_tecnicos: { paginas: 4, tamanho_mb: 0.8 },
        status: "pendente"
      }
    ]
  }
]);
