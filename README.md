# Sistema de Visão Computacional para Detecção e Análise de Objetos em Tempo Real

Aplicação desenvolvida em Python para detecção, classificação e contagem de animais em imagens, vídeos e webcam em tempo real. O projeto utiliza obrigatoriamente a biblioteca OpenCV para manipulação visual e o modelo pré-treinado YOLOv8n (Ultralytics) para inferência local em CPU, contando ainda com interface gráfica em Tkinter e exportação automatizada de métricas e evidências.

Desenvolvido por: Guilherme Romero, Jhenyffer Christynna e Lucas Oliveira.

---

## Sumário

1. [Visão Geral e Funcionalidades](#visão-geral-e-funcionalidades)
2. [Tecnologias e Bibliotecas Utilizadas](#tecnologias-e-bibliotecas-utilizadas)
3. [Estrutura do Repositório](#estrutura-do-repositório)
4. [Passo a Passo de Instalação](#passo-a-passo-de-instalação)
5. [Como Executar e Usar a Interface](#como-executar-e-usar-a-interface)
6. [Interpretação dos Resultados Exportados](#interpretação-dos-resultados-exportados)
7. [Testes Automatizados](#testes-automatizados)
8. [Limitações e Premissas Técnicas](#limitações-e-premissas-técnicas)

---

## Visão Geral e Funcionalidades

- **Múltiplas fontes de entrada:** suporte a arquivos de imagem (`JPG`, `JPEG`, `PNG`, `BMP`, `WEBP`), arquivos de vídeo (`MP4`, `AVI`, `MOV`, `MKV`) e captura ao vivo via webcam.
- **Filtragem de 10 classes de animais (dataset COCO):** pássaro (`bird`), gato (`cat`), cachorro (`dog`), cavalo (`horse`), ovelha (`sheep`), vaca (`cow`), elefante (`elephant`), urso (`bear`), zebra (`zebra`) e girafa (`giraffe`).
- **Interface gráfica e modo CLI:** tela inicial desenvolvida em Tkinter para seleção de mídia e ajuste dinâmico do limiar de confiança, além de suporte completo à execução via linha de comando.
- **Painel de telemetria não obstrutivo:** exibição de contagem total, contagem por classe e tempo de processamento (em milissegundos) em uma faixa superior externa, evitando sobreposição sobre os objetos detectados.
- **Destaques automáticos em vídeo:** ao finalizar a leitura de um vídeo, o sistema salva e exibe os quadros de maior confiança e de maior quantidade simultânea de animais.
- **Auditoria e exportação:** geração automática de arquivos `deteccoes.csv`, `resumo.json` e capturas anotadas em pastas organizadas por data e hora.

---

## Tecnologias e Bibliotecas Utilizadas

- **Python (3.11, 3.12 ou 3.13 - 64 bits):** linguagem base da aplicação.
- **OpenCV (`opencv-python>=4.10,<5`):** responsável pela leitura de imagens, decodificação de vídeos, acesso à webcam, redimensionamento proporcional dos quadros, desenho das caixas delimitadoras (*bounding boxes*), renderização do painel superior e gerenciamento das janelas de exibição.
- **Ultralytics (`ultralytics>=8.3,<9`):** fornece a arquitetura YOLOv8n (*You Only Look Once* versão 8 nano) pré-treinada no conjunto de dados COCO, executando a inferência de detecção de objetos localmente em CPU.
- **NumPy (`numpy>=1.26,<3`):** utilizada na manipulação matricial dos quadros e na leitura segura de arquivos de imagem em caminhos que contenham caracteres especiais ou acentuação no Windows.
- **Tkinter (biblioteca padrão do Python):** utilizada no módulo `interface.py` para construir a tela inicial gráfica de configuração e seleção de arquivos.
- **Módulos nativos (`argparse`, `csv`, `json`, `collections`, `pathlib`, `unittest`):** empregados no tratamento de argumentos de terminal, geração de relatórios tabulares e estruturados, contagem por classe e execução de testes unitários.

---

## Estrutura do Repositório

```text
Sistema-de-Visao-Computacional-para-Deteccao-e-Analise-de-Objetos-em-Tempo-Real/
├── README.md
└── Atividade final A2/
    ├── app.py               # Núcleo da aplicação: leitura, inferência YOLO, desenho e exportação
    ├── interface.py         # Tela inicial gráfica em Tkinter
    ├── iniciar.bat          # Atalho de execução rápida no Windows após a instalação
    ├── requirements.txt     # Lista de dependências com versões compatíveis
    ├── test_revisao.py      # Suíte de testes unitários e de regressão
    ├── yolov8n.pt           # Pesos pré-treinados do modelo YOLOv8n
    ├── exemplos/
    │   ├── cachorro.jpg     # Imagem de exemplo para validação funcional
    │   └── ORIGEM.md        # Referência de origem da imagem de exemplo
    └── resultados/          # Diretório onde são salvas as pastas de cada execução
```
---

## Passo a Passo de Instalação
### 1. Clonar o repositório
 ``` Abra o terminal (PowerShell, Prompt de Comando ou Git Bash) e execute:

git clone [https://github.com/GuigoDev/Sistema-de-Visao-Computacional-para-Deteccao-e-Analise-de-Objetos-em-Tempo-Real.git](https://github.com/GuigoDev/Sistema-de-Visao-Computacional-para-Deteccao-e-Analise-de-Objetos-em-Tempo-Real.git)
Acesse a pasta principal do código:

cd "Sistema-de-Visao-Computacional-para-Deteccao-e-Analise-de-Objetos-em-Tempo-Real/Atividade final A2"
```

``` 2. Criar e ativar o ambiente virtual (Windows PowerShell)
Recomenda-se isolar as dependências em um ambiente virtual .venv:

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
Caso prefira não ativar o ambiente no terminal, basta invocar diretamente o executável .\.venv\Scripts\python.exe nos comandos seguintes.
```
``` 3. Instalar as dependências
Com o ambiente virtual ativo, atualize o pip e instale as bibliotecas listadas em requirements.txt:

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Observação: o pacote ultralytics instala o PyTorch como dependência, portanto o download inicial pode levar alguns minutos. Caso o arquivo yolov8n.pt não esteja presente localmente, ele será baixado automaticamente na primeira execução (requer conexão com a internet).

Como Executar e Usar a Interface
Opção A: Usando a Interface Gráfica (Recomendado)
No terminal (dentro da pasta Atividade final A2), execute:

python app.py
```

### Alternativamente, no Windows Explorer, dê um duplo clique no arquivo iniciar.bat.

Na janela Detector de animais - A2:

Confiança mínima (%): defina o percentual mínimo de certeza exigido para exibir uma detecção (padrão: 40%). Valores mais altos reduzem falsos positivos; valores mais baixos aumentam a sensibilidade.

Abrir imagem: abre o seletor de arquivos para escolher uma foto e exibir o resultado anotado.

Abrir vídeo: abre o seletor de arquivos para processar um vídeo quadro a quadro.

Iniciar webcam: inicia a captura em tempo real utilizando o índice de câmera informado ao lado (padrão: 0 para a webcam principal).

Atalhos de teclado durante a detecção:

S: salva manualmente o quadro atual na pasta da execução.

Q ou ESC: encerra a visualização atual e retorna à tela inicial.

1 e 2 (na tela de encerramento de vídeo): alterna entre o quadro de Maior Confiança (1) e o quadro de Maior Quantidade (2).

Para fechar completamente o programa, feche a janela inicial do Tkinter.

Opção B: Execução Direta via Terminal (CLI)
Você pode iniciar o processamento diretamente por linha de comando sem passar pela tela gráfica:

---

```PowerShell
# Processar uma imagem específica
python app.py --imagem "exemplos/cachorro.jpg"

# Processar uma imagem definindo limiar de confiança de 60%
python app.py --imagem "exemplos/cachorro.jpg" --confianca 0.60

# Processar um arquivo de vídeo
python app.py --video "caminho/para/video.mp4"

# Iniciar detecção pela webcam principal
python app.py --webcam 0

# Usar menu interativo em modo texto
python app.py --terminal

# Processar imagem ou vídeo em lote sem abrir janela gráfica
python app.py --imagem "exemplos/cachorro.jpg" --sem-janela
Interpretação dos Resultados Exportados
Cada execução cria automaticamente um subdiretório identificado por data e hora em resultados/AAAAMMDD_HHMMSS_ffffff/ contendo:
```
### deteccoes.csv: arquivo separado por ponto e vírgula (;) com as colunas quadro, classe, confianca, x1, y1, x2, y2 e processamento_ms. Quadros sem animais recebem a marcação nenhum. As coordenadas referem-se ao quadro redimensionado (limite de 960 x 720 pixels), desconsiderando a faixa superior de telemetria.

### resumo.json: arquivo estruturado contendo quadros_processados, quadros_com_animais, maximo_animais_em_um_quadro, maximo_por_classe, limiar_confianca, tempo_medio_processamento_ms, status da execução e os destaques capturados.

### resultado.jpg: imagem final anotada (gerada em execuções de imagem ou em vídeos sem detecções).

### maior_confianca.jpg e maior_quantidade.jpg: capturas salvas automaticamente ao término da leitura completa de um vídeo.

# Testes Automatizados
O projeto possui testes unitários em test_revisao.py que validam o redimensionamento proporcional, rejeição de parâmetros inválidos, exportação em caminhos com acentuação, fluxo de retorno ao menu e seleção de quadros de destaque em vídeo. Para executá-los:

```PowerShell
python -m unittest -v test_revisao.py
```
