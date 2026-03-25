from rapidfuzz import fuzz, process
import re
from datetime import datetime
def extrair_datas(txts, boxes, ultimo_ano_valido=None, ultimo_dia_valido=None):
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho',
             'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    d_semana = ['feira', 'sabado', 'domingo']

    #Encontra o tamanho do eixo y do PDF
    altura = max(p[1] for box in boxes for p in box)

    melhor_pts = melhor_txt = melhor_mes = 0
    filtro_txt_llama = []
    for txt, box in zip(txts, boxes):
        pts = 0
        txt = txt.lower()
        txt = re.sub(r'[^a-z0-9\s/]', '', txt) # filtra os Dados para q apenas tenham a-z; 0-9; espaços; /

        if ('/' in txt or 'de' in txt) and any(c.isdigit() for c in txt) and len(txt) < 80: # início da filtragem

            # A filtragem utiliza um sistema de pontuação (metodo de decisão multicritério)
            if 'de' in txt:
                pts += 1
            if 'r$' in txt or '%' in txt:
                pts -= 1
            if box[1][1] < altura * 0.25 or box[1][1] > altura * 0.75:
                pts += 2


            mes = process.extractOne(txt, meses, scorer=fuzz.partial_ratio)
            score_mes = mes[1]
            if score_mes >= 90:
                pts += 3
            elif 80 <= score_mes < 90:
                pts += 2
            elif 70 <= score_mes < 80:
                pts += 1
            score_semana = process.extractOne(txt, d_semana, scorer=fuzz.partial_ratio)[1]
            if score_semana >= 90:
                pts += 2
            elif score_semana >= 80:
                pts += 1
            if len([n for n in txt if n.isdigit()]) >= 4:
                pts += 2
            if pts > melhor_pts:
                melhor_pts = pts
                melhor_txt = txt
                melhor_mes = mes[0]
            if pts >= 2:
                txt_llama = {'txt': txt, 'pts': pts}
                filtro_txt_llama.append(txt_llama)
    txts_ordenados = sorted(filtro_txt_llama, key=lambda x: x['pts'], reverse=True)

    if melhor_pts < 5:
        return 'Not Found', txts_ordenados
    else:
        numeros = re.findall(r'\d+', melhor_txt)

        #filtragem do dia
        dia = None
        for n in numeros:
            if 1 <= int(n) <= 31:
                dia = n.zfill(2)
                break
        if len(numeros) < 2 or dia is None:
            if ultimo_dia_valido is None:
                return 'Not Found', txts_ordenados
            dia = ultimo_dia_valido

        mes = str(meses.index(melhor_mes) + 1).zfill(2)

        #filtragem do ano
        ano = None

        for n in numeros:
            if len(n) == 4 and 1920 <= int(n) <= datetime.now().year:
                ano = n
                break
        if not ano:
            n = numeros[-1]

            if len(n) == 2:
                if 70 <= int(n) <= 99:
                    ano = '19' + n

            elif len(n) == 3:
                if ultimo_ano_valido:
                    ano = ultimo_ano_valido

        if not ano:
            return 'Not Found', txts_ordenados

        return f'{dia}-{mes}-{ano}', txts_ordenados


from gpt4all import GPT4All
model_path = r"C:\Users\quiel\Documents\Jornal\Modelo\Llama-3.2-3B-Instruct-Q4_K_M.gguf"
gptj = GPT4All(model_path, n_threads=10) #liga a IA

def prompt_data(txts):
    # Recebe os textos previamente filtrados com maior relevância
    # Prompt estruturado para maximizar a precisão na extração de datas via LLM
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    Você extrai datas de jornais antigos.

    Regras:
    - A data geralmente aparece no topo ou rodapé.
    - Pode aparecer em formatos como:
      "14 de dezembro de 1999", "14/12/99", etc.
    - Pode haver erros de OCR.

    Responda APENAS com a data correta no formato DD/MM/AAAA.
    Se não tiver certeza, responda: Data não encontrada.
    <|eot_id|>

    <|start_header_id|>user<|end_header_id|>
    Textos OCR:

    {txts}

    Qual é a data mais consistente?
    <|eot_id|>

    <|start_header_id|>assistant<|end_header_id|>"""

    print("--- Llama analisando ---")

    resposta = gptj.generate(
        prompt,
        max_tokens=30,
        temp=0.1
    )

    resposta = resposta.strip()
    print(f"IA disse: {resposta}")

    match = re.search(r'\d{2}/\d{2}/\d{4}', resposta) # organiza o texto da IA para já deixar em formato de data (00/00/0000)

    if match:
        d, m, a = match.group().split('/')
        return f"{d}-{m}-{a}"

    return 'Not Found'