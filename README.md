# OCR de Jornais com Extração Automática de Datas

Projeto desenvolvido para organizar automaticamente páginas de jornais digitalizados com base na data identificada em cada página.

## Problema

O projeto surgiu a partir de uma necessidade real: o centro de pesquisa histórica da minha faculdade enfrentava dificuldades na organização de jornais digitalizados, onde as páginas não estavam separadas corretamente por data.

## Solução

Foi desenvolvido um sistema que:

- Lê páginas de PDF
- Extrai textos via OCR
- Identifica a data mais provável
- Organiza automaticamente os arquivos em pastas estruturadas

## Tecnologias

- Python
- PaddleOCR
- pdf2image
- GPT4All (Llama 3.2 3B)
- RapidFuzz

## Como funciona

O sistema utiliza uma abordagem híbrida:

1. OCR para extração dos textos
2. Sistema de pontuação (heurística) inspirado em decisão multicritério
3. Validação por contexto (continuidade entre páginas)
4. Uso de IA como fallback em casos ambíguos

Além disso:
- Cria automaticamente as pastas por ano/mês
- Gera PDFs organizados
- Pode gerar imagens com bounding boxes para debug

## Resultados

- 86 páginas processadas
- 87,2% de acurácia
- Erros principalmente devido a falhas no OCR ou baixa qualidade do material

## Como executar

1. Instale as dependências:
pip install -r requirements.txt
2. Baixe o arquivo Llama-3.2-3B-Instruct-Q4_K_M.gguf:
https://ollama.com/library/llama3.2:3b-instruct-q4_K_M
3. Instale o pacote do poppler-25.12.0:
https://github.com/oschwartz10612/poppler-windows/releases/
