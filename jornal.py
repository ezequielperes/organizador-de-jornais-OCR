from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
class Jornal:

    #Atributos
    def __init__(self, nome_pdf, n_pag, caminho_poppler, nome_png=None):
        self.nome_pdf = nome_pdf
        self.nome_png = nome_png
        self.n_pag = n_pag
        self.caminho_poppler = caminho_poppler

    #Métodos
    def pdf_to_image(self, dpi=300):

        #Tranforma a página do pdf em uma imagem para o PaddleOCR entender
        paginas = convert_from_path(
            self.nome_pdf, dpi=dpi, first_page=self.n_pag, last_page=self.n_pag, poppler_path=self.caminho_poppler
        )
        if self.nome_png is not None:
            paginas[0].save(self.nome_png)
        return paginas[0]


class OCRProcessor:
    def __init__(self):
        from paddleocr import PaddleOCR
        # Inicializa o OCR
        # lang='pt' para entender nossa acentuação
        # use_gpu=False evita que ele tente procurar placa de vídeo à toa ( se tiver troque para True )
        #Atributos
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='pt', use_gpu=False)

    #Métodos
    def execute(self, image):
        image = np.array(image)

        leitor = self.ocr_engine.ocr(image, cls=True)# Executa o OCR na imagem e retorna textos, coordenadas e confiança

        result = leitor[0]

        boxes = [line[0] for line in result] # Coordenada dos boxes encontrados
        txts = [line[1][0] for line in result] # Textos encontrados
        scores = [line[1][1] for line in result] # Pontuação dos textos
        return {'boxes': boxes, 'txts': txts, 'scores': scores}


    def dados_imagem(self, image, boxes, txts, scores, n_pag=None, image_show=False, test=False):
        if test:
            # Se não funcionar, você pode passar apenas "arial.ttf" ou o caminho completo
            # Desenha o OCR
            image = image.convert('RGB')
            font_path = "C:/Windows/Fonts/arial.ttf"
            from paddleocr.tools.infer.utility import draw_ocr
            im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
            im_show = Image.fromarray(im_show)
            im_show.save(f'result{n_pag}.png')

            # Converte de RGB (PIL) para BGR (OpenCV) para exibir corretamente
            if image_show:
                img_show = cv2.cvtColor(np.array(im_show), cv2.COLOR_RGB2BGR)

                # Exibe a imagem (precisa de um nome para a janela)
                cv2.imshow('Resultado do OCR', img_show)

                # Espera uma tecla ser pressionada para não fechar o programa na hora
                cv2.waitKey(0)
                cv2.destroyAllWindows()

