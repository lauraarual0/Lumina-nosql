// Seleciona/Cria o banco de dados
use lumina_db;

// 1. Criação das coleções 
db.createCollection("usuarios");
db.createCollection("materiais");
db.createCollection("trilhas");

// 2. Inserção de Documentos de Exemplo (Usuarios)
db.usuarios.insertMany([
  { _id: "usr_001", nome: "Renan Silva", perfil_acesso: "curador", email: "renan@escola.com" },
  { _id: "usr_002", nome: "Laura", perfil_acesso: "colaborador", email: "laura@escola.com" }
]);

// 3. Inserção de Documentos de Exemplo (Materiais)
db.materiais.insertMany([
  {
    _id: "mat_101",
    titulo: "O Ciclo da Água - Animação",
    tipo: "video",
    faixa_etaria: "4 a 6 anos",
    tags: ["ciências", "meio ambiente", "lúdico"],
    detalhes_tecnicos: { duracao_min: 4.5, resolucao: "1080p" },
    status: "aprovado"
  },
  {
    _id: "mat_102",
    titulo: "Cartilha de Coordenação Motora",
    tipo: "pdf",
    faixa_etaria: "4 a 6 anos",
    tags: ["coordenação motora", "desenho"],
    detalhes_tecnicos: { paginas: 12, tamanho_mb: 2.1 },
    status: "aprovado"
  },
  {
    _id: "mat_103",
    titulo: "Jogo das Vogais",
    tipo: "interativo",
    faixa_etaria: "3 a 5 anos",
    tags: ["alfabetização", "lúdico"],
    detalhes_tecnicos: { requer_internet: true },
    status: "pendente"
  }
]);

// 4. Inserção de Documentos de Exemplo (Trilhas)
db.trilhas.insertMany([
  {
    _id: "trl_001",
    titulo: "Semana de Ciências Naturais",
    criado_por: "usr_002",
    // Aqui referenciamos os materiais em vez de duplicar os dados
    materiais_ids: ["mat_101", "mat_102"] 
  }
]);