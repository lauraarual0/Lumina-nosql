// =========================================================================
// FUNCIONALIDADE 1: Relatório de Tendências Pedagógicas (Tags mais usadas)
// Objetivo: Descobrir quais são os temas (tags) mais abundantes no sistema 
// para a faixa etária de "4 a 6 anos" em materiais já aprovados.
// Diferencial: Usa $unwind para desmembrar o array de tags e $group para contar.
// =========================================================================
db.materiais.aggregate([
  { $match: { status: "aprovado", faixa_etaria: "4 a 6 anos" } },
  { $unwind: "$tags" }, // Separa o array de tags em documentos individuais
  { $group: { 
      _id: "$tags", 
      quantidade_materiais: { $sum: 1 } 
    } 
  },
  { $sort: { quantidade_materiais: -1 } } // Ordena do mais usado para o menos usado
]);

// =========================================================================
// FUNCIONALIDADE 2: Visualização Completa de uma Trilha de Aprendizagem
// Objetivo: Quando o professor clica na Trilha "Semana de Ciências Naturais",
// o sistema busca os detalhes dos materiais vinculados a ela para exibir na tela.
// Diferencial: Usa $lookup para cruzar dados entre coleções diferentes (Trilhas -> Materiais).
// =========================================================================
db.trilhas.aggregate([
  { $match: { _id: "trl_001" } },
  { 
    $lookup: {
      from: "materiais",         // Coleção alvo
      localField: "materiais_ids", // Campo na coleção trilhas
      foreignField: "_id",       // Campo correspondente na coleção materiais
      as: "detalhes_dos_materiais" // Nome do novo array gerado com os resultados
    }
  },
  {
    $project: {
      titulo: 1,
      criado_por: 1,
      "detalhes_dos_materiais.titulo": 1,
      "detalhes_dos_materiais.tipo": 1,
      "detalhes_dos_materiais.tags": 1
    }
  }
]);