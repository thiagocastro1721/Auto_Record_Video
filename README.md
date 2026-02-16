# 🎥 Automação de Gravação OBS com Chrome

Este script automatiza a gravação em **tela cheia** de vídeos executados no **Google Chrome**, utilizando o **OBS Studio** em segundo plano, sem necessidade de interação manual durante o processo.

---

## 📋 Índice

1. [Requisitos do Sistema](#-requisitos-do-sistema)
2. [Gerar Executável (Opcional)](#-gerar-executável-opcional)
3. [Configuração do Google Chrome](#-configuração-obrigatória-do-google-chrome)
4. [Configuração do Windows](#-configuração-obrigatória-do-windows)
5. [Configuração do OBS Studio](#-configuração-obrigatória-do-obs-studio)
6. [Vídeo Tutorial de Configuração](#-vídeo-tutorial-de-configuração)
7. [Como Usar](#-como-usar-o-script)
8. [Atalhos de Teclado](#%EF%B8%8F-atalhos-de-teclado)
9. [Solução de Problemas](#-solução-de-problemas)

---

## 💻 Requisitos do Sistema

- **Sistema Operacional:** Windows 11 (desenvolvido e testado)
- **Teclado Numérico:** Obrigatório (dedicado ou externo)
- **Software Necessário:**
  - Google Chrome (atualizado)
  - OBS Studio (versão 28 ou superior recomendada)
  - Python 3.8+ com as bibliotecas: `pyautogui`, `pydirectinput`, `pygetwindow`, `keyboard`
- **Hardware:** Recomenda-se RAM suficiente (8GB+) e processador razoável para gravação fluida

---

## 🔧 Gerar Executável (Opcional)

Esta etapa é **opcional**. O script pode ser executado diretamente do:
- Visual Studio Code
- Thonny
- PyCharm ou outra IDE
- Terminal/CMD com Python

**💡 Por que gerar um executável?**
- Não precisa abrir IDE toda vez
- Duplo clique para executar (como qualquer programa)
- Mais prático para uso frequente
- Não precisa ter Python visível no sistema

### Passo a Passo para Criar o Executável

#### 1️⃣ Instalar o PyInstaller

Abra o **Prompt de Comando** (CMD) como Administrador e digite:

```bash
pip install pyinstaller
```

Aguarde a instalação terminar.

#### 2️⃣ Verificar se a Instalação foi Bem-sucedida

No mesmo CMD, digite:

```bash
pyinstaller --version
```

Deve aparecer algo como: `6.11.1` (ou outra versão)

Se aparecer a versão, a instalação foi bem-sucedida! ✅

#### 3️⃣ Organizar os Arquivos

Crie uma pasta específica para o projeto. Exemplo:

```
C:\Users\[SeuUsuário]\Documentos\Automacao_OBS\
```

Coloque o arquivo `Auto_Record_Video.py` dentro desta pasta.

#### 4️⃣ Navegar até a Pasta no CMD

No Prompt de Comando, navegue até a pasta criada usando o comando `cd`:

```bash
cd C:\Users\[SeuUsuário]\Documentos\Automacao_OBS
```

**💡 Dica:** Você pode copiar o caminho da pasta no Windows Explorer e colar no CMD.

**🖱️ Atalho rápido:**
- No Windows Explorer, segure `Shift` e clique com botão direito na pasta
- Escolha "Abrir janela do PowerShell aqui" ou "Abrir no Terminal"

#### 5️⃣ Gerar o Executável

Com o CMD já na pasta correta, execute o comando:

```bash
python -m PyInstaller --onefile --noconsole Auto_Record_Video.py
```

**Explicação dos parâmetros:**
- `--onefile` → Cria um único arquivo `.exe` (mais prático)
- `--noconsole` → Não abre janela preta do console ao executar
- `Auto_Record_Video.py` → Nome do seu script

#### 6️⃣ Aguardar a Compilação

O PyInstaller irá:
- Analisar o script
- Coletar todas as dependências
- Criar o executável

Isso pode levar de 30 segundos a 2 minutos dependendo do seu computador.

#### 7️⃣ Localizar o Executável

Após a conclusão, o executável estará em:

```
C:\Users\[SeuUsuário]\Documentos\Automacao_OBS\dist\Auto_Record_Video.exe
```

**📂 Estrutura de pastas criada:**
```
Automacao_OBS/
├── Auto_Record_Video.py          (script original)
├── Auto_Record_Video.spec        (arquivo de configuração)
├── build/                              (pasta temporária)
└── dist/
    └── Auto_Record_Video.exe     ⭐ SEU EXECUTÁVEL AQUI!
```

#### 8️⃣ Usar o Executável

Agora você pode:

✅ Copiar o arquivo `.exe` da pasta `dist` para onde quiser
✅ Criar um atalho na Área de Trabalho
✅ Executar com duplo clique
✅ O executável é **portátil** (pode copiar para outro PC Windows)

**⚠️ Importante:**
- O executável gerado funciona **apenas no Windows**
- Antivírus podem dar falso positivo (é normal com PyInstaller)
- Se o antivírus bloquear, adicione uma exceção

### 🎨 Adicionar Ícone Personalizado (Opcional)

Se quiser um ícone personalizado no executável:

1. Obtenha um arquivo `.ico` (ícone)
2. Coloque-o na mesma pasta do script
3. Use o comando:

```bash
python -m PyInstaller --onefile --noconsole --icon=icone.ico Auto_Record_Video.py
```

### 🔄 Recompilar Após Mudanças

Se você modificar o script:

1. Delete as pastas `build` e `dist`
2. Execute o comando do PyInstaller novamente
3. Um novo executável será gerado com as mudanças

### 🚨 Solução de Problemas - PyInstaller

**Problema: "pyinstaller não é reconhecido como comando"**

Solução:
```bash
python -m pip install --upgrade pyinstaller
```

**Problema: Executável não abre / fecha imediatamente**

Solução:
- Remova `--noconsole` para ver os erros:
```bash
python -m PyInstaller --onefile Auto_Record_Video.py
```
- Execute o `.exe` pelo CMD para ver mensagens de erro

**Problema: Antivírus bloqueia o executável**

Solução:
- É um falso positivo comum com PyInstaller
- Adicione exceção no antivírus
- Ou assine digitalmente o executável (avançado)

---

## 🌐 Configuração Obrigatória do Google Chrome

### ⚠️ Desabilitar Aceleração Gráfica

Esta etapa é **ESSENCIAL** para evitar travamentos e garantir gravação suave.

**Passo a passo:**

1. Abra o Google Chrome
2. Cole este endereço na barra de navegação e pressione Enter:
   ```
   chrome://settings/system
   ```
3. Localize a opção: **"Usar aceleração gráfica quando disponível"**
4. **Desative** esta opção (o botão deve ficar cinza/desligado)
5. Reinicie o Chrome para aplicar as mudanças

**📌 Por que fazer isso?**
A aceleração gráfica pode causar conflitos com a captura de tela do OBS, resultando em tela preta ou travamentos.

---

## 🪟 Configuração Obrigatória do Windows

### ⚙️ Configurar OBS para Alto Desempenho Gráfico

Esta configuração garante que o Windows priorize o desempenho do OBS.

**Passo a passo detalhado:**

1. Clique no **botão Iniciar** do Windows
2. Vá em **Configurações** (ícone de engrenagem ⚙️)
3. Navegue até: **Sistema** → **Tela**
4. Role até encontrar e clique em: **Configurações de elementos gráficos**
5. Clique no botão **"Procurar"**
6. Navegue até a pasta de instalação do OBS:
   - Normalmente está em: `C:\Program Files\obs-studio\bin\64bit\obs64.exe`
   - Ou procure por "OBS Studio" nos arquivos de programas
7. Selecione o arquivo **`obs64.exe`** e clique em **"Adicionar"**
8. Com o OBS já listado, clique no botão **"Opções"** ao lado dele
9. Selecione a opção: **"Alto desempenho"**
10. Clique em **"Salvar"**

**📌 Por que fazer isso?**
Garante que a GPU dedicada (se disponível) seja usada pelo OBS, melhorando drasticamente a qualidade e performance da gravação.

---

## 🎙️ Configuração Obrigatória do OBS Studio

### ⌨️ Configurar Atalhos Globais

O script precisa que o OBS responda a comandos mesmo quando está em segundo plano.

**Passo a passo:**

1. Abra o **OBS Studio**
2. Vá em: **Arquivo** → **Configurações** (ou pressione `Ctrl + ,`)
3. No menu lateral, clique em **"Atalhos de Teclado"**
4. Localize as seguintes opções e configure:

   | Função | Atalho | Observação |
   |--------|--------|------------|
   | **Iniciar Gravação** | Tecla **1** (alfanumérica) | ⚠️ NÃO use o teclado numérico |
   | **Parar Gravação** | Tecla **2** (alfanumérica) | ⚠️ NÃO use o teclado numérico |

5. Clique em **"Aplicar"** e depois em **"OK"**

**📌 Importante:**
- Use as teclas **1** e **2** da linha principal do teclado (acima das letras Q, W, E)
- **NÃO** use o teclado numérico (Numpad) para esses atalhos
- O teclado numérico será usado apenas para digitar a duração da gravação

**💡 Não tem teclado numérico?**
Se seu teclado não possui um teclado numérico dedicado:
- Você precisará editar o código do script para usar outros atalhos
- Modifique também os atalhos do OBS conforme sua necessidade

---

## 🎬 Vídeo Tutorial de Configuração

Se preferir assistir um vídeo explicativo completo sobre todas as configurações acima (Chrome, Windows e OBS), acesse:

**🔗 [Tutorial em Vídeo - Configuração Completa](https://www.youtube.com/watch?v=PGMaGwt10Aw)**

Este vídeo mostra visualmente:
- ✅ Como desabilitar aceleração gráfica no Chrome
- ✅ Como configurar alto desempenho gráfico no Windows
- ✅ Como configurar atalhos globais no OBS Studio

---

## 🚀 Como Usar o Script

### Preparação Antes de Executar

**Antes de iniciar o script, certifique-se de que:**

1. ✅ O **OBS Studio** está aberto e configurado
2. ✅ O **Google Chrome** está aberto com o vídeo já carregado na aba
3. ✅ O vídeo está **pausado** e pronto para começar
4. ✅ Você tem **tempo livre** - não mexa no computador durante a gravação
5. ✅ O **Num Lock** está ativado (luz acesa no teclado)

### Executando o Script

1. Execute o arquivo Python: `python Auto_Record_Video.py`

2. **Primeira janela:** Leia as instruções e clique em **"OK"**

3. **Segunda janela - Duração:**
   - Digite a duração desejada nos três campos:
     - **Horas** (0 a 999)
     - **Minutos** (0 a 59)
     - **Segundos** (0 a 59)
   - Use o **teclado numérico** para digitar
   - Pressione **Enter** ou clique em **"✓ Confirmar"**

4. **Automação em ação:**
   - Aguarde 3 segundos (contagem regressiva aparecerá no console)
   - O Chrome será ativado e entrará em tela cheia
   - A gravação do OBS iniciará automaticamente
   - O script aguardará o tempo configurado
   - A gravação será finalizada automaticamente

5. **Finalização:**
   - O Chrome sairá do modo tela cheia
   - Uma janela informará que a gravação foi concluída
   - O vídeo estará salvo na pasta de gravações do OBS

### 📁 Onde encontrar o vídeo gravado?

Por padrão, o OBS salva em:
```
C:\Users\[SeuUsuário]\Videos\
```

Você pode verificar/alterar em: **OBS** → **Configurações** → **Saída** → **Caminho de Gravação**

---

## ⌨️ Atalhos de Teclado

| Atalho | Função | Quando usar |
|--------|--------|-------------|
| **Ctrl + Shift + Q** | ⏹️ Abortar gravação | Durante a gravação, para parar antecipadamente |
| **Enter** | ✅ Confirmar duração | Na janela de configuração de tempo |
| **Esc** | ❌ Cancelar | Na janela de configuração de tempo |

### 🛑 Como Abortar a Gravação

Se precisar **interromper a gravação antes do tempo acabar**:

1. Pressione **Ctrl + Shift + Q** a qualquer momento
2. O script irá:
   - Parar a gravação do OBS
   - Sair do modo tela cheia
   - Salvar o vídeo parcial
   - Mostrar uma mensagem de confirmação

**💾 O vídeo parcial é salvo?** Sim! Tudo que foi gravado até o momento ficará salvo.

---

## 🔧 Solução de Problemas

### ❌ Problema: "Chrome não encontrado"

**Solução:**
- Certifique-se de que o Chrome está aberto
- Verifique se há "Chrome" no título da janela
- Tente renomear a janela do navegador

### ❌ Problema: Gravação não inicia no OBS

**Soluções:**
1. Verifique se os atalhos estão configurados corretamente (tecla **1** para iniciar)
2. Teste manualmente: pressione a tecla **1** com o OBS aberto
3. Certifique-se de que são atalhos **globais** (funcionam mesmo com OBS em segundo plano)

### ❌ Problema: Tela preta na gravação

**Soluções:**
1. Desabilite a aceleração gráfica do Chrome (veja [seção específica](#-configuração-obrigatória-do-google-chrome))
2. Configure o Chrome como fonte de captura no OBS
3. Use "Captura de Janela" em vez de "Captura de Tela" no OBS

### ❌ Problema: Gravação travando/cortando

**Soluções:**
1. Feche outros programas pesados
2. Configure o OBS para usar menos recursos:
   - Diminua a resolução de saída
   - Use codec x264 (mais leve que NVENC em alguns casos)
3. Verifique se o Windows está configurado para "Alto desempenho" para o OBS

### ❌ Problema: Não consigo digitar a duração

**Solução:**
- Verifique se o **Num Lock** está ativado (luz acesa)
- Use o teclado numérico (não as teclas numéricas da linha superior)
- Se não tiver teclado numérico, você precisará editar o código

### ❌ Problema: Ctrl + Shift + Q não funciona

**Soluções:**
1. Execute o script como **Administrador**
2. Verifique se outro programa não está usando esse atalho
3. Tente pressionar as três teclas **simultaneamente e segurar** por 1 segundo

---

## 📊 Dicas de Otimização

### Para Melhor Desempenho:

1. **Feche programas desnecessários** antes de gravar
2. **Desative atualizações automáticas** temporariamente
3. **Use modo "Alto desempenho"** nas configurações de energia do Windows
4. **Tenha espaço em disco suficiente** (pelo menos 10GB livres)
5. **Conecte o notebook na tomada** (não use bateria)

### Configurações Recomendadas do OBS:

- **Taxa de bits:** 2500-6000 kbps (dependendo da qualidade desejada)
- **Encoder:** x264 ou NVENC (se tiver GPU Nvidia)
- **Taxa de quadros:** 30 fps (ou 60 fps para jogos)
- **Resolução:** 1920x1080 (Full HD)

---

## 📝 Notas Finais

- ⚠️ **Não mexa no mouse/teclado** durante a execução do script
- ⚠️ O script assumirá controle do mouse e teclado automaticamente
- ⚠️ Planeje antecipadamente: calcule a duração correta do vídeo
- ✅ Teste primeiro com vídeos curtos (1-2 minutos) para garantir que tudo funciona

---

## 📞 Suporte

Se encontrar problemas não listados aqui:
1. Revise **todas as configurações** acima cuidadosamente
2. Teste os atalhos do OBS manualmente
3. Verifique os logs do console do Python para mensagens de erro

---

## 📜 Licença

Este script é fornecido "como está", para uso pessoal e educacional.

---

**Desenvolvido para Windows 11** | Última atualização: 2025
