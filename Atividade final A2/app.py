"""Detector de animais: OpenCV captura e desenha; YOLO identifica objetos."""

import argparse
from collections import Counter
import csv
import json
from datetime import datetime
from pathlib import Path
import time
import textwrap


# Nomes COCO em inglês são usados para selecionar as classes do modelo.
ANIMAIS = {
    "bird": "passaro", "cat": "gato", "dog": "cachorro",
    "horse": "cavalo", "sheep": "ovelha", "cow": "vaca",
    "elephant": "elefante", "bear": "urso", "zebra": "zebra",
    "giraffe": "girafa",
}
PASTA = Path(__file__).resolve().parent


def argumentos():
    parser = argparse.ArgumentParser(description=__doc__)
    fonte = parser.add_mutually_exclusive_group()
    fonte.add_argument("--imagem", type=Path, help="Caminho da imagem")
    fonte.add_argument("--video", type=Path, help="Caminho do vídeo")
    fonte.add_argument("--webcam", type=int, help="Índice da câmera, geralmente 0")
    parser.add_argument("--terminal", action="store_true", help="Usar menu textual em vez da tela inicial")
    parser.add_argument("--confianca", type=float, default=0.40)
    parser.add_argument("--sem-janela", action="store_true", help="Para testar arquivos sem interface")
    args = parser.parse_args()
    if not 0 < args.confianca <= 1:
        parser.error("A confiança deve ser maior que 0 e menor ou igual a 1.")
    if args.webcam is not None and args.webcam < 0:
        parser.error("O índice da câmera não pode ser negativo.")
    if args.sem_janela and args.webcam is not None:
        parser.error("Use --sem-janela somente com imagem ou vídeo.")
    if args.sem_janela and args.imagem is None and args.video is None:
        parser.error("Informe --imagem ou --video com --sem-janela.")
    return args


def escolher_fonte(args):
    """Menu inicial para quem prefere executar sem parâmetros."""
    if args.imagem is not None or args.video is not None or args.webcam is not None:
        return
    if not args.terminal:
        from interface import escolher
        escolher(args)
        return
    print("\nDETECTOR DE ANIMAIS\n1 - Imagem\n2 - Webcam\n3 - Vídeo\n0 - Sair")
    opcao = input("Escolha: ").strip()
    if opcao == "0":
        raise SystemExit(0)
    if opcao == "2":
        args.webcam = 0
    elif opcao in ("1", "3"):
        caminho = Path(input("Caminho completo do arquivo: ").strip().strip('"'))
        if opcao == "1":
            args.imagem = caminho
        else:
            args.video = caminho
    else:
        raise ValueError("Opção inválida. Execute novamente e escolha 1, 2 ou 3.")


def preparar_quadro(cv2, quadro):
    """Reduz imagens grandes sem distorcer a proporção."""
    altura, largura = quadro.shape[:2]
    escala = min(1.0, 960 / largura, 720 / altura)
    if escala < 1:
        quadro = cv2.resize(quadro, (max(1, round(largura * escala)), max(1, round(altura * escala))),
                            interpolation=cv2.INTER_AREA)
    return quadro


def detectar(cv2, modelo, quadro, classes, confianca):
    inicio = time.perf_counter()
    # O próprio YOLO também redimensiona/normaliza a entrada para inferência.
    resultado = modelo.predict(quadro, classes=classes, conf=confianca,
                               imgsz=640, device="cpu", verbose=False)[0]
    registros = []
    anotado = quadro.copy()
    for caixa in resultado.boxes:
        classe = int(caixa.cls.item())
        nome = ANIMAIS[modelo.names[classe]]
        score = float(caixa.conf.item())
        x1, y1, x2, y2 = map(int, caixa.xyxy[0].tolist())
        registros.append((nome, score, x1, y1, x2, y2))
        cv2.rectangle(anotado, (x1, y1), (x2, y2), (70, 220, 90), 2)
        cv2.putText(anotado, f"{nome} {score:.1%}", (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (70, 220, 90), 2)
    contagem = Counter(r[0] for r in registros)
    # Inclui inferência e desenho; não é a taxa de captura da câmera.
    duracao = time.perf_counter() - inicio
    resumo = " | ".join(f"{nome}: {n}" for nome, n in sorted(contagem.items())) or "Nenhum animal detectado"
    linhas = [f"Animais no quadro: {len(registros)} | processamento: {duracao * 1000:.0f} ms",
              *textwrap.wrap(resumo, width=78), "Q/ESC: voltar ao inicio | S: salvar imagem"]
    # Faixa separada evita cobrir as caixas da imagem original.
    painel = cv2.copyMakeBorder(anotado, 10 + 30 * len(linhas), 0, 0, max(0, 800 - anotado.shape[1]),
                                cv2.BORDER_CONSTANT, value=(25, 25, 25))
    for indice, linha in enumerate(linhas):
        cv2.putText(painel, linha, (10, 25 + 30 * indice),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (240, 240, 240), 1)
    return painel, registros, duracao


def salvar_imagem(cv2, caminho, quadro):
    """imencode/tofile aceita caminhos com acentos no Windows."""
    sucesso, dados = cv2.imencode(".jpg", quadro)
    if not sucesso:
        raise OSError("Não foi possível codificar a imagem de saída.")
    dados.tofile(str(caminho))
    print(f"Imagem salva: {caminho}")


def resultado_video(cv2, pasta, destaques, ultimo, estatisticas, sem_janela):
    """Salva os destaques e espera o usuário fechar o resultado final."""
    telas = []
    for chave, titulo in (("confianca", "MAIOR CONFIANCA"), ("quantidade", "MAIOR QUANTIDADE")):
        destaque = destaques.get(chave)
        if destaque is None:
            continue
        quadro = destaque["painel"]
        texto = (f'{destaque["valor"]:.1%}' if chave == "confianca"
                 else str(destaque["valor"]))
        telas.append((f"maior_{chave}.jpg", quadro, f'{titulo}: {texto} | quadro {destaque["quadro"]}'))
    if not telas:
        telas.append(("resultado.jpg", ultimo, "Nenhum animal detectado no video"))

    finais = []
    for arquivo, quadro, titulo in telas:
        painel = cv2.copyMakeBorder(quadro, 95, 0, 0, 0, cv2.BORDER_CONSTANT, value=(25, 25, 25))
        linhas = ["LEITURA DO VIDEO ENCERRADA - RESULTADO", titulo,
                  "1: confianca | 2: quantidade | S: salvar | Q/ESC: voltar ao inicio"]
        for i, linha in enumerate(linhas):
            cv2.putText(painel, linha, (10, 23 + 28 * i), cv2.FONT_HERSHEY_SIMPLEX,
                        .48, (240, 240, 240), 1)
        salvar_imagem(cv2, pasta / arquivo, painel)
        finais.append(painel)
    estatisticas["capturas_video"] = [tela[0] for tela in telas]
    (pasta / "resumo.json").write_text(json.dumps(estatisticas, ensure_ascii=False, indent=2), encoding="utf-8")
    if sem_janela:
        return
    selecionado = 0
    # Não há inferência nesta espera: o resultado permanece até Q/ESC ou fechar.
    while True:
        cv2.imshow("Detector de animais", finais[selecionado])
        tecla = cv2.waitKey(30) & 0xFF
        if tecla in (ord("q"), 27) or cv2.getWindowProperty("Detector de animais", cv2.WND_PROP_VISIBLE) < 1:
            return
        if tecla in (ord("1"), ord("2")):
            selecionado = min(tecla - ord("1"), len(finais) - 1)
        if tecla == ord("s"):
            salvar_imagem(cv2, pasta / telas[selecionado][0], finais[selecionado])


def executar(args):
    import cv2
    import numpy as np
    from ultralytics import YOLO

    arquivo = args.imagem if args.imagem is not None else args.video
    if arquivo is not None and not arquivo.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
    print("Carregando YOLOv8n local..." if (PASTA / "yolov8n.pt").is_file()
          else "Baixando YOLOv8n pela primeira vez; é necessária conexão com a internet.")
    modelo = YOLO(str(PASTA / "yolov8n.pt"))
    classes = [indice for indice, nome in modelo.names.items() if nome in ANIMAIS]
    if not classes:
        raise ValueError("O modelo carregado não possui as classes de animais esperadas.")
    pasta_saida = PASTA / "resultados" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    pasta_saida.mkdir(parents=True)
    captura = None
    estatisticas = {"quadros_processados": 0, "quadros_com_animais": 0,
                    "maximo_animais_em_um_quadro": 0, "maximo_por_classe": {},
                    "limiar_confianca": args.confianca, "tempo_medio_processamento_ms": 0,
                    "observacao": "Contagens por quadro; não representam indivíduos únicos no vídeo."}
    tempo_total = 0
    destaques = {}
    status = "erro"
    try:
        if args.imagem is not None:
            quadro = cv2.imdecode(np.fromfile(str(args.imagem), dtype=np.uint8), cv2.IMREAD_COLOR)
            if quadro is None:
                raise ValueError("Não foi possível ler a imagem. Use JPG ou PNG válido.")
        else:
            fonte = str(args.video) if args.video is not None else args.webcam
            captura = cv2.VideoCapture(fonte)
            if not captura.isOpened():
                raise RuntimeError("Não foi possível abrir a fonte. Confira o vídeo ou a permissão da câmera.")

        with (pasta_saida / "deteccoes.csv").open("w", newline="", encoding="utf-8-sig") as f:
            escritor = csv.writer(f, delimiter=";")
            escritor.writerow(["quadro", "classe", "confianca", "x1", "y1", "x2", "y2", "processamento_ms"])
            numero = 0
            while True:
                if captura is not None:
                    ok, quadro = captura.read()
                    if not ok:
                        if numero == 0:
                            raise RuntimeError("A fonte abriu, mas nenhum quadro pôde ser lido.")
                        if args.webcam is not None:
                            raise RuntimeError("A webcam parou de enviar quadros. Confira a conexão e as permissões.")
                        print("Fim do vídeo ou interrupção da leitura do arquivo.")
                        break
                numero += 1
                quadro = preparar_quadro(cv2, quadro)
                painel, registros, duracao = detectar(cv2, modelo, quadro, classes, args.confianca)
                if args.video is not None and registros:
                    melhor = max(registros, key=lambda registro: registro[1])
                    for chave, valor in (("confianca", melhor[1]), ("quantidade", len(registros))):
                        # Empates preservam o primeiro quadro; guarda apenas dois painéis.
                        if chave not in destaques or valor > destaques[chave]["valor"]:
                            destaques[chave] = {"valor": valor, "quadro": numero, "painel": painel.copy()}
                            estatisticas[f"maior_{chave}"] = {"valor": valor, "quadro": numero}
                            if chave == "confianca":
                                estatisticas["maior_confianca"]["classe"] = melhor[0]
                estatisticas["quadros_processados"] += 1
                estatisticas["quadros_com_animais"] += bool(registros)
                estatisticas["maximo_animais_em_um_quadro"] = max(estatisticas["maximo_animais_em_um_quadro"], len(registros))
                for nome, quantidade in Counter(r[0] for r in registros).items():
                    maximos = estatisticas["maximo_por_classe"]
                    maximos[nome] = max(maximos.get(nome, 0), quantidade)
                tempo_total += duracao
                for nome, score, *caixa in registros:
                    escritor.writerow([numero, nome, round(score, 4), *caixa, round(duracao * 1000, 2)])
                if not registros:
                    escritor.writerow([numero, "nenhum", "", "", "", "", "", round(duracao * 1000, 2)])
                if args.imagem is not None:
                    salvar_imagem(cv2, pasta_saida / "resultado.jpg", painel)
                    print("Contagem:", dict(Counter(r[0] for r in registros)) or "nenhum animal")
                if not args.sem_janela:
                    cv2.imshow("Detector de animais", painel)
                    # Imagem fica aberta até Q, ESC ou fechar a janela.
                    while True:
                        tecla = cv2.waitKey(30) & 0xFF
                        if tecla == ord("s"):
                            salvar_imagem(cv2, pasta_saida / f"quadro_{numero}.jpg", painel)
                        if tecla in (ord("q"), 27) or cv2.getWindowProperty("Detector de animais", cv2.WND_PROP_VISIBLE) < 1:
                            status = "encerrado_pelo_usuario"
                            return
                        if captura is not None:
                            break
                if args.imagem is not None:
                    break
            status = "imagem_concluida" if args.imagem is not None else "fim_video_ou_interrupcao_leitura"
        if args.video is not None:
            captura.release()
            captura = None
            estatisticas["status"] = status
            estatisticas["tempo_medio_processamento_ms"] = round(1000 * tempo_total / numero, 2)
            resultado_video(cv2, pasta_saida, destaques, painel, estatisticas, args.sem_janela)
    except KeyboardInterrupt:
        status = "interrompido"
        raise
    finally:
        if captura is not None:
            captura.release()
        if not args.sem_janela:
            cv2.destroyAllWindows()
        estatisticas["status"] = status
        if estatisticas["quadros_processados"]:
            estatisticas["tempo_medio_processamento_ms"] = round(1000 * tempo_total / estatisticas["quadros_processados"], 2)
        (pasta_saida / "resumo.json").write_text(json.dumps(estatisticas, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Resultados desta execução: {pasta_saida}")


def main():
    args = argumentos()
    try:
        while True:
            escolher_fonte(args)
            executar(args)
            if args.sem_janela:
                break
            # Limpa a entrada anterior para reabrir o seletor, mantendo a confiança.
            args.imagem = None
            args.video = None
            args.webcam = None
    except ImportError as erro:
        print(f"Dependência ausente: {erro}. Execute: python -m pip install -r requirements.txt")
        return 1
    except KeyboardInterrupt:
        print("\nExecução encerrada.")
        return 0
    except Exception as erro:
        print(f"Erro: {erro}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
