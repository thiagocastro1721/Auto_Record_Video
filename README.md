# Automação de Gravação OBS com WebSocket + Chrome

Este script automatiza a gravação em **tela cheia** de vídeos no **Google Chrome** usando o **OBS Studio**, controlado inteiramente via **WebSocket** — sem simular teclas de atalho, sem risco de conflito com digitação.

---

## Índice

1. [Requisitos do Sistema](#requisitos-do-sistema)
2. [Configuração do Google Chrome](#configuração-do-google-chrome)
3. [Configuração do Windows](#configuração-do-windows)
4. [Configuração do OBS Studio](#configuração-do-obs-studio)
5. [Ajuste de Sincronização (OVERHEAD_FINALIZACAO)](#ajuste-de-sincronização-overhead_finalizacao)
6. [Gerar Executável (Opcional)](#gerar-executável-opcional)
7. [Como Usar](#como-usar-o-script)
8. [Atalhos de Teclado](#atalhos-de-teclado)
9. [Solução de Problemas](#solução-de-problemas)

---

## Requisitos do Sistema

- **Sistema Operacional:** Windows 11 (desenvolvido e testado)
- **Software Necessário:**
  - Google Chrome (atualizado)
  - OBS Studio 28 ou superior (o servidor WebSocket está embutido a partir dessa versão)
  - Python 3.8+ com as bibliotecas abaixo

### Instalação das Dependências Python

```bash
pip install pyautogui pygetwindow keyboard obsws-python pycaw
```

| Biblioteca | Função |
|---|---|
| `pyautogui` | Controle de mouse e teclado |
| `pygetwindow` | Localizar janelas abertas |
| `keyboard` | Hotkey global CTRL+SHIFT+Q |
| `obsws-python` | Comunicação com OBS via WebSocket |
| `pycaw` | Mutar áudio do sistema (opcional) |

---

## Configuração do Google Chrome

### ⚠️ Desabilitar Aceleração Gráfica

Esta etapa é **essencial** para evitar tela preta ou travamentos na captura do OBS.

1. Abra o Chrome e cole na barra de endereços:
   ```
   chrome://settings/system
   ```
2. Localize **"Usar aceleração gráfica quando disponível"** e **desative**.
3. Reinicie o Chrome.

---

## Configuração do Windows

### ⚙️ Configurar OBS para Alto Desempenho Gráfico

1. Abra **Configurações do Windows** → **Sistema** → **Tela**
2. Clique em **Configurações de elementos gráficos**
3. Clique em **Procurar** e navegue até:
   ```
   C:\Program Files\obs-studio\bin\64bit\obs64.exe
   ```
4. Com o OBS listado, clique em **Opções** → selecione **Alto desempenho** → **Salvar**

---

## Configuração do OBS Studio

> ⚠️ Esta é a etapa mais importante desta versão. O script controla o OBS **exclusivamente via WebSocket** — não são mais necessários atalhos de teclado no OBS.

### 1. Ativar o Servidor WebSocket

1. Abra o OBS Studio
2. Vá em **Ferramentas** → **Configurações do WebSocket Server**
3. Marque **✓ Ativar servidor WebSocket**
4. Confirme que a porta está em **4455**
5. Defina uma senha (opcional, mas recomendado):
   - Se definir senha, anote — você precisará informá-la na tela de configuração do script
   - Se preferir sem senha, deixe o campo em branco
6. Clique em **OK**
7. **Feche o OBS** — o script o abrirá automaticamente no momento certo

> **💡 Dica:** Use o botão **"Testar"** na janela de duração do script para verificar se a conexão WebSocket está funcionando antes de iniciar a gravação.

### 2. Verificar Caminho do OBS

Por padrão, o script espera o OBS em:
```
C:\Program Files\obs-studio\bin\64bit\obs64.exe
```

Se o seu OBS estiver instalado em outro local, edite as constantes no início do script:

```python
OBS_EXE = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
OBS_CWD = r"C:\Program Files\obs-studio\bin\64bit"
```

### 3. Sobre Atalhos de Teclado no OBS

**Não é mais necessário configurar atalhos** de gravação no OBS. O script usa WebSocket para iniciar e parar a gravação diretamente, sem simular teclas. Isso elimina qualquer risco de acionar a gravação acidentalmente ao digitar a duração.

---

## Ajuste de Sincronização (OVERHEAD_FINALIZACAO)

Ao terminar a gravação, o script executa algumas ações (parar WebSocket, pausar vídeo, sair do fullscreen) que consomem alguns segundos. Para compensar esse tempo e fazer com que a duração gravada corresponda exatamente à duração configurada, existe a constante:

```python
OVERHEAD_FINALIZACAO = 0
```

### Como calibrar

1. Configure uma gravação de teste de **1 minuto** (60 segundos)
2. Após finalizar, verifique a duração real do arquivo gravado no OBS
3. Calcule a diferença:
   - Se o arquivo ficou **com mais tempo** do que o esperado → **aumente** `OVERHEAD_FINALIZACAO`
   - Se ficou **com menos tempo** → **diminua** (ou deixe em 0)

**Exemplo:** você configurou 60s e o arquivo ficou com 63s → defina `OVERHEAD_FINALIZACAO = 3`.

O valor é subtraído da duração do loop de espera, fazendo o script parar a gravação um pouco antes do tempo nominal para compensar o tempo das ações de finalização.

---

## Gerar Executável (Opcional)

### Instalação

```bash
pip install pyinstaller
```

### Gerar

```bash
python -m PyInstaller --onefile --noconsole Auto_Record_Video.py
```

O executável ficará em:
```
dist\Auto_Record_Video.exe
```

### Arquivos gerados junto ao executável

O script salva automaticamente suas preferências em:
```
obs_automacao_config.json
```

Mantenha esse arquivo na mesma pasta do `.exe` para preservar suas configurações entre execuções.

### Com ícone personalizado

```bash
python -m PyInstaller --onefile --noconsole --icon=icone.ico Auto_Record_Video.py
```

### Solução de Problemas com PyInstaller

Se o executável fechar imediatamente, remova `--noconsole` para ver os erros:
```bash
python -m PyInstaller --onefile Auto_Record_Video.py
```

Antivírus bloqueando? É falso positivo comum com PyInstaller — adicione exceção.

---

## Como Usar o Script

### Fluxo de execução

```
Iniciar script
    ↓
Ler instruções → OK
    ↓
Digitar duração + configurar senha WebSocket + opções → Confirmar
    ↓
OBS abre automaticamente (se não estiver aberto)
    ↓
Conexão WebSocket validada
    ↓
Chrome ativa → Tela cheia → Gravação inicia via WebSocket
    ↓
[aguarda duração configurada]
    ↓
Gravação para via WebSocket → Vídeo pausa → Sai do fullscreen → OBS fecha
    ↓
Mensagem de conclusão
```

### Preparação antes de executar

1. ✅ **OBS fechado** — será aberto automaticamente
2. ✅ **Chrome aberto** com o vídeo carregado e pausado no início
3. ✅ **WebSocket configurado** no OBS com a senha definida (se houver)
4. ✅ Você tem **tempo livre** — não mexa no mouse/teclado durante a gravação

### Passo a passo

1. Execute `python Auto_Record_Video.py` (ou o `.exe`)

2. Leia as instruções na primeira janela e clique **OK**

3. Na janela de duração:
   - Digite horas, minutos e segundos
   - No campo **Senha WebSocket**, informe a senha configurada no OBS (deixe em branco se não definiu senha)
   - Clique em **Testar** para confirmar que a conexão com o OBS está funcionando
   - Marque ou desmarque as opções conforme necessário:

   | Opção | Descrição |
   |---|---|
   | **Clique duplo para pausar** | Recomendado para YouTube — 1º clique fecha painel de recomendações, 2º pausa o vídeo |
   | **Reduzir brilho para 20%** | Funciona apenas em monitores internos (notebook). Não afeta a gravação. |
   | **Mutar áudio do sistema** | Silencia o som local durante a gravação. Não afeta o áudio gravado pelo OBS. |

   - Pressione **Enter** ou clique em **✓ Confirmar**

4. A automação começa — **não toque no mouse ou teclado**

5. Ao finalizar, uma janela confirma a conclusão

### Onde encontrar o vídeo gravado

Por padrão, o OBS salva em:
```
C:\Users\[SeuUsuário]\Videos\
```

Verifique ou altere em: **OBS** → **Configurações** → **Saída** → **Caminho de Gravação**

---

## Atalhos de Teclado

| Atalho | Função |
|---|---|
| **Ctrl + Shift + Q** | Aborta a gravação a qualquer momento |
| **Enter** | Confirma a duração na janela de configuração |
| **Esc** | Cancela a janela de configuração |

### Como abortar

Pressione **Ctrl + Shift + Q** durante a gravação. O script irá:
- Parar a gravação via WebSocket
- Sair do modo tela cheia
- Restaurar brilho e áudio (se alterados)
- Fechar o OBS
- Exibir mensagem confirmando que o vídeo parcial foi salvo

---

## Solução de Problemas

**"WebSocket indisponível" ao iniciar**
Verifique no OBS: **Ferramentas** → **Configurações do WebSocket Server** → confirme que está ativado na porta 4455 com a senha correta.

**Botão "Testar" retorna falha mas o OBS está aberto**
O servidor WebSocket pode demorar alguns segundos para inicializar após o OBS abrir. Aguarde 5–10 segundos e tente novamente.

**"Chrome não encontrado"**
Certifique-se de que o Chrome está aberto com pelo menos uma aba ativa antes de iniciar o script.

**Tela preta na gravação**
Desabilite a aceleração gráfica do Chrome (veja seção correspondente acima).

**Gravação com duração diferente da configurada**
Ajuste a constante `OVERHEAD_FINALIZACAO` no script (veja seção de sincronização acima).

**Ctrl + Shift + Q não responde**
Execute o script como **Administrador**.

---

## Dicas de Otimização

- Feche programas desnecessários antes de gravar
- Use modo **Alto desempenho** nas configurações de energia do Windows
- Tenha pelo menos **10 GB livres** em disco
- Conecte o notebook na tomada durante gravações longas

### Configurações Recomendadas do OBS

- **Taxa de bits:** 2500–6000 kbps
- **Encoder:** x264 ou NVENC (GPU Nvidia)
- **Taxa de quadros:** 30 fps
- **Resolução:** 1920×1080

---

## Notas Finais

- ⚠️ **Não mexa no mouse/teclado** após confirmar a duração
- ⚠️ Calcule bem a duração antes de iniciar
- ✅ Faça um teste curto (20–30 segundos) para calibrar o `OVERHEAD_FINALIZACAO` antes de gravações longas

---

**Desenvolvido para Windows 11** | Última atualização: 2026
