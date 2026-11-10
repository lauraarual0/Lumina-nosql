# Lumina - Plataforma de Curadoria Digital Pedagógica

## Descrição do Sistema (Atividade A0 e A1)
O Lumina é um sistema SaaS institucional para escolas de educação infantil. Seu objetivo é mitigar a sobrecarga de conteúdos digitais, servindo como um repositório onde materiais educacionais (vídeos, cartilhas, jogos) passam por uma curadoria pedagógica antes de serem liberados para os professores montarem seus planos de aula (Trilhas).

A arquitetura NoSQL foi escolhida porque permite flexibilidade polimórfica: um vídeo e um PDF possuem atributos técnicos completamente diferentes, mas habitam a mesma coleção `materiais` sem gerar colunas nulas, otimizando o armazenamento e a busca.

## Estrutura de Coleções
1. **usuarios:** Dados e perfis de acesso (colaborador vs. curador).
2. **materiais:** O acervo curado com metadados pedagógicos e técnicos.
3. **trilhas:** Planos de aula criados pelos professores, que referenciam os IDs dos materiais.