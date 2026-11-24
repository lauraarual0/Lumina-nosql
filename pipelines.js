use lumina_db;

// =========================================================================
// FUNCIONALIDADE 1: Ranking de Temas Pedagógicos (Tags mais usadas)
// Objetivo: Mostrar à coordenação quais temas (tags) mais aparecem em 
// materiais já aprovados em todas as trilhas do sistema.
// Operadores-chave: $unwind (duplo), $match, $group, $sort
// =========================================================================
db.trilhas.aggregate([
  { $unwind: "$materiais" },
  { $match: { "materiais.status": "aprovado" } },
  { $unwind: "$materiais.tags" },
  {
    $group: {
      _id: "$materiais.tags",
      total_aparicoes: { $sum: 1 }
    }
  },
  { $sort: { total_aparicoes: -1 } }
]);

// =========================================================================
// FUNCIONALIDADE 2: Painel de Prontidão das Trilhas
// Objetivo: Calcular, sem desmembrar os documentos, quantos materiais cada 
// trilha possui, quantos estão aprovados, o percentual de aprovação e gerar 
// um selo automático de prontidão para o professor.
// Operadores-chave: $addFields, $filter, $size, $cond, $round, $switch, $project
// =========================================================================
db.trilhas.aggregate([
  {
    $addFields: {
      total_materiais: { $size: "$materiais" },
      materiais_aprovados: {
        $size: {
          $filter: {
            input: "$materiais",
            as: "mat",
            cond: { $eq: ["$$mat.status", "aprovado"] }
          }
        }
      }
    }
  },
  {
    $addFields: {
      percentual_aprovacao: {
        $cond: [
          { $eq: ["$total_materiais", 0] },
          0,
          {
            $round: [
              { $multiply: [{ $divide: ["$materiais_aprovados", "$total_materiais"] }, 100] },
              1
            ]
          }
        ]
      }
    }
  },
  {
    $addFields: {
      status_prontidao: {
        $switch: {
          branches: [
            { case: { $eq: ["$percentual_aprovacao", 100] }, then: "Pronta para Aula" },
            { case: { $gt: ["$percentual_aprovacao", 0] }, then: "Parcialmente Aprovada" }
          ],
          default: "Pendente de Curadoria"
        }
      }
    }
  },
  {
    $project: {
      titulo: 1,
      faixa_etaria: 1,
      "criador.nome": 1,
      total_materiais: 1,
      materiais_aprovados: 1,
      percentual_aprovacao: 1,
      status_prontidao: 1
    }
  }
]);
