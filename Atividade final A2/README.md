# Detector de animais — Atividade A2

Aplicação Python com **OpenCV obrigatório e YOLOv8n pré-treinado**, correspondente à opção 2 do enunciado. Usa imagem, vídeo ou webcam; desenha caixas com classe e confiança; apresenta contagem por classe e tempo de processamento. A inferência acontece no computador, em CPU.

## O professor definiu o tipo de aplicativo?

Definiu visão computacional em Python, mas permite escolher o problema. **Detecção de animais em imagens é uma das sugestões expressas** no A2-5.pdf. Portanto, este tema está dentro da lista; a exigência de aprovação citada no documento se refere a outros temas.

O grupo pode ter até 3 alunos. O enunciado informa prazo de 2 semanas, sem uma data de calendário: confirme a data de entrega informada em aula.

## Instalação no Windows

Abra o terminal nesta pasta. Use Python 64 bits (3.11, 3.12 ou 3.13).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Não é necessário ativar o ambiente. A instalação inclui PyTorch e pode demorar. A primeira execução baixa `yolov8n.pt` e precisa de internet. Depois, com dependências e pesos presentes, a detecção funciona localmente. Não precisa de chave de API nem de treinamento próprio.

Na tela inicial, escolha imagem, webcam ou vídeo usando os botões. Você pode ajustar a confiança mínima e o índice da câmera. Após instalar, dê dois cliques em `iniciar.bat` para abrir essa tela. Para usar o menu textual, execute `app.py --terminal`. Também é possível executar diretamente:

```powershell
.\.venv\Scripts\python.exe app.py --imagem "C:\imagens\gato.jpg"
.\.venv\Scripts\python.exe app.py --webcam 0
.\.venv\Scripts\python.exe app.py --video "C:\videos\animais.mp4"
.\.venv\Scripts\python.exe app.py --imagem "C:\imagens\gato.jpg" --confianca 0.60
```

Na janela de detecção, **Q ou ESC** volta à tela inicial; **S** salva o quadro. Para encerrar o programa, feche a tela inicial (ou escolha 0 no menu textual). Imagens são salvas automaticamente. O CSV é salvo em todas as modalidades, dentro de `resultados/<execucao>/`. Para processar imagem/vídeo sem abrir janela e encerrar ao terminar, acrescente `--sem-janela`.

Ao concluir a leitura de um vídeo, o programa salva os quadros de maior confiança e maior quantidade em `maior_confianca.jpg` e `maior_quantidade.jpg`. Na tela final, use **1** e **2** para alternar entre eles. Se nenhum animal for detectado, salva o último quadro como `resultado.jpg`. Os destaques automáticos são gerados ao chegar ao fim da leitura; sair antes com Q/ESC não gera essa tela final.

## Animais e interpretação dos resultados

As classes disponíveis são: pássaro, gato, cachorro, cavalo, ovelha, vaca, elefante, urso, zebra e girafa. O modelo não reconhece todos os animais nem identifica raças. Nomes no desenho usam letras sem acentos por compatibilidade com a fonte do OpenCV.

Confiança é a pontuação do modelo para aquela detecção, **não a acurácia medida do aplicativo**. Pode haver falsos positivos e animais não detectados. A contagem é por quadro, não de indivíduos únicos ao longo do vídeo. Somar as linhas do CSV não fornece o número de animais distintos.

O CSV registra classe, confiança entre 0 e 1, caixa e tempo de processamento. Coordenadas referem-se ao quadro redimensionado, antes da faixa superior adicionada à visualização. Essa faixa aumenta conforme o número de classes exibidas. Quadros vazios recebem uma linha `nenhum`. Vídeos são processados na velocidade possível da CPU, sem sincronização com o áudio ou a taxa original; não há gravação de vídeo de saída.

Cada execução também gera `resumo.json`: quadros processados, quadros com animais, máximo simultâneo total e por classe, limiar e tempo médio de processamento. Os máximos por classe podem ocorrer em quadros diferentes. O tempo inclui inferência e desenho das caixas, mas não captura, exportação ou espera da janela. A primeira inferência pode ser mais lenta. O resumo registra encerramento manual, erro ou fim da leitura; OpenCV não distingue de forma confiável o fim normal de um vídeo de uma falha de decodificação após quadros válidos.

## Organização e explicação do código

- `argumentos` e `escolher_fonte`: configuram a entrada e o limiar de confiança.
- `interface.py`: tela inicial com Tkinter (incluído na instalação padrão do Python para Windows).
- `preparar_quadro`: limita a imagem a 960 × 720 preservando a proporção.
- `detectar`: executa YOLO, filtra animais, desenha caixas e calcula métricas.
- `executar`: lê imagens ou quadros com OpenCV, exibe resultados, escreve CSV e libera a câmera.
- `roteiro_video.md`: sequência para gravar a demonstração.
- `test_revisao.py`: testes automatizados das correções e exportação; execute `.\.venv\Scripts\python.exe -m unittest -v test_revisao.py`.

## Verificação antes de entregar

1. Execute uma foto de gato e uma de cachorro; confira caixas, nomes e confiança.
2. Execute uma foto com mais de um animal e compare a contagem manual.
3. Execute uma foto sem animais e registre eventuais falsos positivos.
4. Teste um vídeo com animais; a webcam é uma alternativa opcional para quem possui câmera. O enunciado aceita imagem, vídeo ou webcam.
5. Experimente limiares 0.25, 0.40 e 0.70 na mesma imagem.
6. Abra os JPGs e CSVs produzidos e use evidências reais no relatório.

Se a câmera não abrir, feche programas que a utilizam, confira a permissão do Windows e tente `--webcam 1`. Se o download falhar, confira a internet e execute novamente. Se não detectar, confira iluminação, tamanho do animal e limiar. Para reduzir lentidão, feche outros programas.

## Entrega exigida pelo PDF

- Código organizado e comentado, README e requirements.txt.
- Relatório de **2 a 4 páginas**, com introdução, objetivos, tecnologias, metodologia, resultados, dificuldades e conclusões.
- Vídeo de **3 a 5 minutos**, com funcionamento, resultados e explicação do código principal.

O relatório final é mantido separadamente da pasta do código e deve acompanhar a entrega, com 2 a 4 páginas e todas as seções exigidas. O vídeo precisa ser gravado pelo grupo.

Para enviar o código, mantenha `app.py`, `interface.py`, `README.md` e `requirements.txt`. Inclua também `iniciar.bat` para facilitar a abertura após a instalação. `test_revisao.py`, `exemplos/` (com a origem da imagem) e evidências selecionadas de `resultados/` são complementos opcionais. `roteiro_video.md` é material de apoio à gravação, não um entregável obrigatório.

Não inclua `.venv`, `.tools` ou `__pycache__` no envio; são pastas locais de dependências e arquivos gerados. Não é necessário enviar todo o histórico de `resultados/` nem o vídeo sintético `resultados/teste_video.avi`. O arquivo `yolov8n.pt` contém os pesos do modelo, não é documento extra: mantenha-o localmente. No pacote de entrega, ele é opcional se houver internet para o download automático; para distribuí-lo, observe as condições da Ultralytics.

**Observação sobre a nota:** o enunciado anuncia 1,50 ponto, mas os valores individuais da tabela somam 1,30. Confirme essa diferença com o professor.

## Referências

- https://docs.ultralytics.com/modes/predict/
- https://docs.ultralytics.com/datasets/detect/coco/
- https://docs.opencv.org/4.x/

Versões exatas usadas em uma execução podem ser registradas com `python -m pip freeze` no ambiente virtual.
