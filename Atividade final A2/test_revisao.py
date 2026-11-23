"""Testes de regressão. Execute: python -m unittest -v test_revisao.py."""

import argparse
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

import cv2
import numpy as np
import app


class ModeloSimulado:
    """Isola o fluxo da aplicação, sem download ou inferência nos testes unitários."""
    names = {i: nome for i, nome in enumerate(app.ANIMAIS)}

    def predict(self, quadro, **kwargs):
        caixas = [SimpleNamespace(cls=np.array(i), conf=np.array(.8),
                                  xyxy=np.array([[2, 25, 50, 80]])) for i in self.names]
        return [SimpleNamespace(boxes=caixas)]


class Revisao(unittest.TestCase):
    def test_volta_ao_menu_limpa_fonte_e_permite_nova_execucao(self):
        args = argparse.Namespace(imagem=None, video=None, webcam=None, confianca=.4,
                                  sem_janela=False, terminal=False)
        entradas = []
        def escolher(config):
            self.assertIsNone(config.imagem)
            self.assertIsNone(config.video)
            self.assertIsNone(config.webcam)
            self.assertEqual(config.confianca, .4 if not entradas else .7)
            if len(entradas) == 2:
                raise SystemExit(0)  # Fechar a tela inicial encerra o aplicativo.
            if not entradas:
                config.imagem = Path('gato.jpg')
            else:
                config.webcam = 0
        def executar(config):
            entradas.append((config.imagem, config.webcam))
            config.confianca = .7
        with patch.object(app, 'argumentos', return_value=args), \
             patch.object(app, 'escolher_fonte', side_effect=escolher) as menu, \
             patch.object(app, 'executar', side_effect=executar):
            with self.assertRaises(SystemExit) as encerramento:
                app.main()
        self.assertEqual(encerramento.exception.code, 0)
        self.assertEqual(menu.call_count, 3)
        self.assertEqual(entradas, [(Path('gato.jpg'), None), (None, 0)])

    def test_execucao_sem_janela_nao_reabre_menu(self):
        args = argparse.Namespace(imagem=Path('gato.jpg'), video=None, webcam=None,
                                  confianca=.4, sem_janela=True, terminal=False)
        with patch.object(app, 'argumentos', return_value=args), \
             patch.object(app, 'escolher_fonte') as menu, \
             patch.object(app, 'executar') as executar:
            self.assertEqual(app.main(), 0)
            executar.assert_called_once_with(args)
            menu.assert_called_once_with(args)

    def test_video_salva_picos_distintos_e_espera_apos_ultimo_quadro(self):
        self.verificar_video(sem_janela=False, vazio=False)

    def test_video_sem_janela_salva_picos_sem_esperar(self):
        self.verificar_video(sem_janela=True, vazio=False)

    def test_video_sem_animais_mantem_resultado_aberto(self):
        self.verificar_video(sem_janela=False, vazio=True)

    def verificar_video(self, sem_janela, vazio):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            arquivo = raiz / "video.avi"
            arquivo.touch()
            quadros = [np.full((100, 800, 3), cor, dtype=np.uint8) for cor in (30, 90, 150)]
            captura = Mock()
            captura.isOpened.return_value = True
            captura.read.side_effect = [(True, q) for q in quadros] + [(False, None)]
            # A maior confiança ocorre antes da maior quantidade; o último quadro é vazio.
            registros = [ [('gato', .95, 1, 1, 30, 30)],
                          [('gato', .7, 1, 1, 30, 30), ('cachorro', .8, 40, 1, 70, 30)], []]
            if vazio:
                registros = [[], [], []]
            args = argparse.Namespace(imagem=None, video=arquivo, webcam=None, confianca=.4, sem_janela=sem_janela)
            with patch.object(app, "PASTA", raiz), \
                 patch("ultralytics.YOLO", return_value=ModeloSimulado()), \
                 patch.object(cv2, "VideoCapture", return_value=captura), \
                 patch.object(app, "detectar", side_effect=[(q, r, .01) for q, r in zip(quadros, registros)]), \
                 patch.object(cv2, "imshow") as mostrar, \
                 patch.object(cv2, "waitKey", side_effect=[-1, -1, -1, -1, ord('2'), ord('s'), ord('q')]) as esperar, \
                 patch.object(cv2, "getWindowProperty", return_value=1), \
                 patch.object(cv2, "destroyAllWindows"):
                app.executar(args)
                if sem_janela:
                    esperar.assert_not_called()
                    mostrar.assert_not_called()
                else:
                    self.assertEqual(esperar.call_count, 7)
                    # A tela continua recebendo eventos após acabar a captura.
                    self.assertEqual(mostrar.call_count, 7)
                    np.testing.assert_array_equal(mostrar.call_args_list[-1].args[1][95:], quadros[-1 if vazio else 1])
            saida = next(raiz.glob("resultados/*"))
            resumo = json.loads((saida / 'resumo.json').read_text(encoding='utf-8'))
            self.assertEqual(resumo['quadros_processados'], 3)
            self.assertEqual(resumo['status'], 'fim_video_ou_interrupcao_leitura')
            if vazio:
                self.assertEqual(resumo['capturas_video'], ['resultado.jpg'])
                self.assertNotIn('maior_confianca', resumo)
            else:
                self.assertEqual(resumo['maior_confianca'], {'valor': .95, 'quadro': 1, 'classe': 'gato'})
                self.assertEqual(resumo['maior_quantidade'], {'valor': 2, 'quadro': 2})
                self.assertEqual(resumo['capturas_video'], ['maior_confianca.jpg', 'maior_quantidade.jpg'])
            for nome in resumo['capturas_video']:
                self.assertTrue((saida / nome).is_file())
            captura.release.assert_called_once()

    def test_imagem_muito_estreita_nao_produz_dimensao_zero(self):
        quadro = app.preparar_quadro(cv2, np.zeros((10000, 1, 3), dtype=np.uint8))
        self.assertEqual(quadro.shape[:2], (720, 1))

    def test_preserva_proporcao(self):
        quadro = app.preparar_quadro(cv2, np.zeros((1000, 2000, 3), dtype=np.uint8))
        self.assertEqual(quadro.shape[:2], (480, 960))

    def test_painel_com_todas_as_classes(self):
        painel, registros, _ = app.detectar(cv2, ModeloSimulado(), np.zeros((100, 100, 3), dtype=np.uint8), list(range(10)), .4)
        self.assertEqual(len(registros), 10)
        self.assertGreater(painel.shape[0], 200)  # Estatísticas ocupam mais de uma linha.
        self.assertGreaterEqual(painel.shape[1], 800)

    def test_rejeita_camera_negativa(self):
        with patch("sys.argv", ["app.py", "--webcam", "-1"]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as resultado:
                app.argumentos()
        self.assertEqual(resultado.exception.code, 2)

    def test_rejeita_confianca_invalida(self):
        for valor in ["0", "2", "nan"]:
            with self.subTest(valor=valor), patch("sys.argv", ["app.py", "--confianca", valor]), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    app.argumentos()

    def test_exporta_resumo_e_imagem_em_caminho_com_acento(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            caminho = raiz / "cão.png"
            ok, dados = cv2.imencode(".png", np.zeros((100, 100, 3), dtype=np.uint8))
            self.assertTrue(ok)
            dados.tofile(str(caminho))
            args = argparse.Namespace(imagem=caminho, video=None, webcam=None, confianca=.4, sem_janela=True)
            with patch.object(app, "PASTA", raiz), patch("ultralytics.YOLO", return_value=ModeloSimulado()), patch.object(cv2, "destroyAllWindows") as fechar:
                app.executar(args)
                fechar.assert_not_called()
            resumo = json.loads(next(raiz.glob("resultados/*/resumo.json")).read_text(encoding="utf-8"))
            self.assertEqual(resumo["quadros_processados"], 1)
            self.assertEqual(resumo["maximo_animais_em_um_quadro"], 10)
            self.assertEqual(resumo["status"], "imagem_concluida")
            self.assertTrue(next(raiz.glob("resultados/*/resultado.jpg")).is_file())


if __name__ == "__main__":
    unittest.main()
