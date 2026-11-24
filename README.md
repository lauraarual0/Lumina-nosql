# Lumina - Plataforma de Curadoria Digital Pedagógica

## Descrição do Sistema (A0 e A1)
O Lumina é uma plataforma SaaS institucional voltada para escolas de educação infantil. Seu objetivo é combater a sobrecarga de conteúdos digitais, oferecendo um acervo de planos de aula (Trilhas) compostos por materiais educacionais (vídeos, cartilhas em PDF, jogos interativos) que passam por curadoria pedagógica antes da aplicação em sala.

## Arquitetura NoSQL (Modelo de Agregação Puro)
O banco de dados foi modelado no **MongoDB** seguindo o princípio da desnormalização e do modelo de agregação puro.

1. **`usuarios`:** Armazena dados de autenticação e controle de acesso (`curador` vs. `colaborador`). Mantida isolada por questões de segurança e para futura integração de cache de login.
2. **`trilhas`:** Coleção principal (Agregado). Cada documento de trilha embute os dados do criador e o array completo de `materiais`. Isso garante leitura instantânea da tela do plano de aula e aproveita o polimorfismo do NoSQL para armazenar vídeos, PDFs e jogos com atributos técnicos distintos dentro da mesma estrutura.

## Funcionalidades Implementadas (A2)
* **Pipeline 1 (Ranking de Temas Pedagógicos):** Desmembra os arrays de materiais e tags (`$unwind`) para contabilizar (`$group`) os assuntos mais frequentes entre os conteúdos aprovados.
* **Pipeline 2 (Painel de Prontidão das Trilhas):** Analisa os materiais internamente sem desmembrar os documentos (`$filter`, `$size`), calcula o percentual de aprovação e classifica cada trilha automaticamente (`$switch`).

## Evidências de Execução
![Pipeline 1](resultado_p1.png)
![Pipeline 2](resultado_p2.png)
