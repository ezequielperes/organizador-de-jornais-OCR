from pdf2image import pdfinfo_from_path

from jornal import Jornal, OCRProcessor

from filtragens import extrair_datas, prompt_data

import time
import os
import fitz

def fim(init=None):
    print("tempo:", time.time()-init)

inicio = time.time() # Início da contagem de tempo
ocr = OCRProcessor() # Liga o PaddleOCR

#nome do pdf a ser processado
nome_pdf = 'teste.pdf'
doc = fitz.open(nome_pdf)

#qnt páginas e poppler
caminho_poppler = r'poppler-25.12.0\Library\bin'
info = pdfinfo_from_path(nome_pdf, poppler_path=caminho_poppler)
total_paginas = info['Pages']

j = Jornal(nome_pdf, None, caminho_poppler)
ultimo_ano_valido = ultimo_dia_valido = ultimo_mes_valido = None
pdfs = {}

for paginas in range(1, 64+1):


    j.n_pag = paginas
    image = j.pdf_to_image(dpi=300)

    #Executa OCR
    dados = ocr.execute(image)

    #Mostra os dados do PaddleOCR juntamente com os dados
    ocr.dados_imagem(image, dados['boxes'], dados['txts'], dados['scores'], n_pag=paginas, image_show=True, test=True)

    #Extrai dados
    data, txts_ordenados = extrair_datas(txts=dados['txts'], boxes=dados['boxes'], ultimo_ano_valido=ultimo_ano_valido, ultimo_dia_valido=ultimo_dia_valido)

    usar_ia = False

    if data == 'Not Found':
        usar_ia = True

    elif ultimo_dia_valido:
        dia, mes, ano = data.split('-')
        # Se a diferença entre dias for muito grande, pode indicar erro, logo, ativa a IA
        if abs(int(dia) - int(ultimo_dia_valido)) > 5:
            usar_ia = True

    if usar_ia:
        top_txts = [d['txt'] for d in txts_ordenados if d['pts'] >= 4][:10]
        if not top_txts:
           top_txts = [d['txt'] for d in txts_ordenados if d['pts']][:10]
        data_ia = prompt_data(top_txts)

        if data_ia != 'Not Found':

            if data == 'Not Found':
                data = data_ia

            else:
                dia, mes, ano = data.split('-')
                dia_ia, mes_ia, ano_ia = data_ia.split('-')

                if ((mes_ia == mes or mes_ia == ultimo_mes_valido) and
                        abs(int(dia_ia) - int(ultimo_dia_valido or dia_ia)) <= 5):
                    data = data_ia

    #Gera o pdf e caminha o arquivo para pasta
    if data == 'Not Found':
        caminho_final = os.path.join('jornais_programa/not_found', f'pag_{paginas}.pdf')
    else:
        dia, mes, ano = data.split('-')
        ultimo_ano_valido = ano
        ultimo_dia_valido = dia
        ultimo_mes_valido = mes
        caminho_pasta = f'jornais_programa/{ano}/{mes}'
        caminho_final = os.path.join(caminho_pasta, f'{data}.pdf')

    #Abre o caminho do arquivo caso não esteja aberto ainda
    if caminho_final not in pdfs:
        pdfs[caminho_final] = fitz.open()
    pdfs[caminho_final].insert_pdf(doc, from_page=paginas - 1, to_page=paginas - 1)


    #Debug
    print(f"\033[1;32m[OK] Página {paginas} → {data}\033[m")
    fim(inicio) # Tempo de cada PDF

#salvar arquivos e fechar arquivos
for caminho, pdf in pdfs.items():
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    pdf.save(caminho)
    pdf.close()
doc.close()