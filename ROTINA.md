# Rotina semanal de conteúdo — @martinsbastosviagens

Instruções para a sessão do Claude que roda toda semana (tarefa agendada). Siga na ordem.

## Conta e ferramentas
- Instagram: **@martinsbastosviagens** (Martins Bastos Viagens & Turismo), conectado no Zernio.
- Zernio accountId: `6af24526b4772ff9a2eb8254`. A chave de API vem no prompt da tarefa: salve em `~/.zernio/key` (chmod 600). **Nunca** grave a chave neste repositório.
- Este repositório é público: o Zernio busca as imagens em `raw.githubusercontent.com/.../main/posts/...`.
- `tools/render.py post.json pasta_saida` gera os slides (1080x1350 feed, 1080x1920 story) no estilo da marca. Tipos de slide: `cover`, `tip`, `cta`, `story` (veja `posts/2026-11-11-dicas-fim-de-ano/post1.json` como exemplo).
- `tools/zernio.py posts/<pasta> AAAA-MM-DDT19:00:00` agenda o feed às 19h e o story às 12h do mesmo dia (horário de Brasília). Sem data, salva como rascunho.
- Dependências: `pip install playwright --break-system-packages` se faltar; Chrome em `/usr/bin/google-chrome`.

## Plano de conteúdo
- **1 post no feed por dia às 19h** + **1 story por dia às 12h** (o story divulga o post do dia).
- Formatos variados: carrossel de dicas (5–7 slides), post de imagem única (frase/destino), e story.
- Temas, em rodízio na semana:
  - **Destinos** (priorizar saída do Rio de Janeiro; Serra Gaúcha, Nordeste, Foz, Bonito, cruzeiros, Beto Carrero, internacional).
  - **Dicas de viagem** (documentos, bagagem, seguro, economia, viajar com crianças, épocas do ano).
  - **Institucional / bastidores** (por que viajar com agência, atendimento, Alessandra).
  - **Engajamento** (enquetes de "que tipo de viajante é você", "qual destino escolher").
  - **Depoimentos**: só com texto/print REAL enviado pelo cliente/dono. **Nunca inventar depoimento.**
  - **Pacotes em promoção**: só os que o dono enviar (preço, datas, hotel). Nunca inventar preço, datas ou condições.
- Público: maioria da Região dos Lagos/RJ (Cabo Frio, Arraial do Cabo, São Pedro da Aldeia), 25–44 anos, mais mulheres. Pense em casal e família.
- Datas sazonais: aproveitar feriados, férias escolares, Natal/Réveillon, Carnaval.

## Tom e legenda (siga o padrão dos posts atuais)
- Português do Brasil, acolhedor, próximo, sem exagero. Emojis com moderação (✈️ 🤎 🌴 📲 👉).
- Estrutura: gancho na 1ª linha → 2–4 linhas de valor → chamada para salvar/compartilhar → CTA:
  `📲 WhatsApp (22) 99883-9397 ou chama no direct.` → assinatura `Martins Bastos Viagens e Turismo` → 6–10 hashtags (sempre `#martinsbastosviagens`).
- Fatos (regras de documento, vistos, seguro, eventos) precisam estar corretos; na dúvida, pesquise ou deixe de fora.

## Fluxo semanal
1. Clone/atualize este repositório. Leia as legendas recentes em `posts/` para não repetir temas.
2. Planeje os **7 dias seguintes** (próximo sábado a sexta) — tema, formato, gancho.
3. Para cada dia, crie `posts/AAAA-MM-DD-slug/` com `post.json`, `legenda.txt` e os .jpg gerados por `render.py` (o story termina em `_story.jpg`). Abra as imagens e confira visualmente (texto cortado, erro de português).
4. Faça commit e push.
5. **Peça aprovação**: envie ao usuário uma prévia (um quadro com as miniaturas de cada dia + as legendas) e pergunte o que aprovar/ajustar. NÃO agende nada antes do "aprovado".
6. Após aprovação, rode `tools/zernio.py` para cada dia com a data às 19:00. Confirme o status `scheduled` e informe o resumo.
7. Se o usuário não responder, deixe os posts no repositório e não agende.
