"""Tela inicial Tkinter; a captura e a detecção continuam no app.py."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path


def escolher(args):
    janela = tk.Tk()
    janela.title("Detector de animais • A2")
    janela.geometry("600x480")
    janela.minsize(560, 460)
    quadro = ttk.Frame(janela, padding=28)
    quadro.pack(fill="both", expand=True)
    ttk.Label(quadro, text="Detector de animais", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(quadro, text="Escolha uma imagem, um vídeo ou a webcam.",
              font=("Segoe UI", 11)).pack(anchor="w", pady=(6, 20))
    ttk.Label(quadro, text="Confiança mínima (%) — valores maiores filtram mais detecções").pack(anchor="w")
    confianca = tk.StringVar(value=str(round(args.confianca * 100)))
    ttk.Spinbox(quadro, from_=1, to=100, textvariable=confianca, width=8).pack(anchor="w", pady=8)
    camera = tk.StringVar(value="0")
    selecionou = False

    def selecionar(tipo):
        nonlocal selecionou
        try:
            limite = float(confianca.get().replace(",", ".")) / 100
            if not 0 < limite <= 1:
                raise ValueError
            indice = int(camera.get()) if tipo == "webcam" else 0
            if indice < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Confira os valores", "Use confiança maior que 0 e até 100 e índice de câmera inteiro não negativo.", parent=janela)
            return
        if tipo == "webcam":
            args.webcam = indice
        else:
            tipos = [("Imagens", "*.jpg *.jpeg *.png *.bmp *.webp")] if tipo == "imagem" else [("Vídeos", "*.mp4 *.avi *.mov *.mkv")]
            arquivo = filedialog.askopenfilename(parent=janela, title="Escolha o arquivo", filetypes=tipos + [("Todos os arquivos", "*.*")])
            if not arquivo:
                return
            setattr(args, tipo, Path(arquivo))
        args.confianca = limite
        selecionou = True
        janela.destroy()

    ttk.Button(quadro, text="Abrir imagem", command=lambda: selecionar("imagem")).pack(fill="x", pady=5)
    ttk.Button(quadro, text="Abrir vídeo", command=lambda: selecionar("video")).pack(fill="x", pady=5)
    linha = ttk.Frame(quadro)
    linha.pack(fill="x", pady=5)
    ttk.Button(linha, text="Iniciar webcam", command=lambda: selecionar("webcam")).pack(side="left", fill="x", expand=True)
    ttk.Label(linha, text="  Câmera:").pack(side="left")
    ttk.Spinbox(linha, from_=0, to=10, textvariable=camera, width=4).pack(side="left")
    ttk.Label(quadro, text="Na detecção: S salva; Q ou ESC volta a esta tela.\nPara sair do programa, feche esta tela inicial.\nOs resultados ficam na pasta resultados.\nReconhece dez categorias, incluindo gatos e cachorros.",
              wraplength=520).pack(anchor="w", pady=20)
    janela.mainloop()
    if not selecionou:
        raise SystemExit(0)
