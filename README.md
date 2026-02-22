# 🎥 Automação de Gravação OBS com Chrome

Este script automatiza a gravação em **tela cheia** de vídeos executados no **Google Chrome**, utilizando o **OBS Studio** em segundo plano, sem necessidade de interação manual durante o processo.

---

## 📋 Índice

1. [Requisitos do Sistema](#-requisitos-do-sistema)
2. [Vídeo Tutorial de Configuração](#-vídeo-tutorial-de-configuração)
3. [Configuração do Google Chrome](#-configuração-obrigatória-do-google-chrome)
4. [Configuração do Windows](#-configuração-obrigatória-do-windows)
5. [Configuração do OBS Studio](#configuração-obrigatória-do-obs-studio)
6. [Gerar Executável (Opcional)](#-gerar-executável-opcional)
7. [Como Usar](#-como-usar-o-script)
8. [Atalhos de Teclado](#%EF%B8%8F-atalhos-de-teclado)
9. [Solução de Problemas](#-solução-de-problemas)

---

## 💻 Requisitos do Sistema

- **Sistema Operacional:** Windows 11 (desenvolvido e testado)
- **Software Necessário:**
  - Google Chrome (atualizado)
  - OBS Studio (versão 28 ou superior recomendada)
  - Python 3.8+ com as bibliotecas: `pyautogui`, `pydirectinput`, `pygetwindow`, `keyboard`
- **Hardware:** Recomenda-se RAM suficiente (8GB+) e processador razoável para gravação fluida

> **💡 Teclado numérico não é mais obrigatório.** O OBS abre automaticamente *depois* que você digita a duração, portanto não há conflito entre o teclado numérico e os atalhos do OBS. Você pode usar qualquer teclado.

---

## 🎬 Vídeo Tutorial de Configuração

Se preferir assistir um vídeo explicativo sobre as configurações abaixo (Chrome, Windows), acesse:

**🔗 [Tutorial em Vídeo - Configuração Completa](https://www.youtube.com/watch?v=PGMaGwt10Aw)**

Este vídeo mostra visualmente:
- ✅ Como desabilitar aceleração gráfica no Chrome
- ✅ Como configurar alto desempenho gráfico no Windows

---

## 🌐 Configuração Obrigatória do Google Chrome (Disponível no vídeo de configuração)

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

## 🪟 Configuração Obrigatória do Windows (Disponível no vídeo de configuração)

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
7. Selecione o arquivo **`obs64.exe`** e clique em **"Adicionar"**
8. Com o OBS já listado, clique no botão **"Opções"** ao lado dele
9. Selecione a opção: **"Alto desempenho"**
10. Clique em **"Salvar"**

**📌 Por que fazer isso?**
Garante que a GPU dedicada (se disponível) seja usada pelo OBS, melhorando drasticamente a qualidade e performance da gravação.

---

## Configuração Obrigatória do OBS Studio (Não disponível no vídeo de configuração)

### ⌨️ Configurar Atalhos Globais

O script precisa que o OBS responda a comandos mesmo quando está em segundo plano.

**Passo a passo:**

1. Abra o **OBS Studio**
2. Vá em: **Arquivo** → **Configurações** (ou pressione `Ctrl + ,`)
3. No menu lateral, clique em **"Atalhos de Teclado"**
4. Localize as seguintes opções e configure:

   | Função | Atalho |
   |--------|--------|
   | **Iniciar Gravação** | Tecla **1** (alfanumérica) |
   | **Parar Gravação** | Tecla **2** (alfanumérica) |

5. Clique em **"Aplicar"** e depois em **"OK"**
6. **Feche o OBS** após configurar — o script o abrirá automaticamente na hora certa.

**📌 Importante:**
- Use as teclas **1** e **2** da linha principal do teclado (acima das letras Q, W, E)
- **NÃO** use o teclado numérico (Numpad) para esses atalhos

---

## 🔧 Gerar Executável (Opcional)

Esta etapa é **opcional**. O script pode ser executado diretamente do Visual Studio Code, Thonny, PyCharm ou qualquer terminal com Python.

**💡 Por que gerar um executável?**
- Não precisa abrir IDE toda vez
- Duplo clique para executar
- Mais prático para uso frequente

### Passo a Passo para Criar o Executável

#### 1️⃣ Instalar o PyInstaller

```bash
pip install pyinstaller
```

#### 2️⃣ Gerar o Executável

Navegue até a pasta do script no CMD e execute:

```bash
python -m PyInstaller --onefile --noconsole Auto_Record_Video.py
```

#### 3️⃣ Localizar o Executável

```
dist\Auto_Record_Video.exe  ⭐ SEU EXECUTÁVEL AQUI
```

#### 4️⃣ Arquivos gerados junto ao executável

O script cria automaticamente um arquivo `Auto_Record_Video_config.json` na mesma pasta do `.exe` para salvar suas preferências (ex: clique duplo para pausar). Mantenha esse arquivo junto ao executável.

### 🎨 Adicionar Ícone Personalizado (Opcional)

```bash
python -m PyInstaller --onefile --noconsole --icon=icone.ico Auto_Record_Video.py
```

### 🚨 Solução de Problemas - PyInstaller

**Executável não abre / fecha imediatamente** — remova `--noconsole` para ver os erros:
```bash
python -m PyInstaller --onefile Auto_Record_Video.py
```

**Antivírus bloqueia** — é falso positivo comum com PyInstaller. Adicione exceção no antivírus.

---

## 🚀 Como Usar o Script

### Fluxo de execução

```
Iniciar script
    ↓
Ler instruções → OK
    ↓
Digitar duração + opções → Confirmar
    ↓
OBS abre automaticamente (se não estiver aberto)
    ↓
Chrome ativa → Tela cheia → Gravação inicia
    ↓
[aguarda duração configurada]
    ↓
Gravação para → Vídeo pausa → Sai do fullscreen → OBS fecha
    ↓
Mensagem de conclusão
```

### ⚠️ Sobre o OBS antes de iniciar

| Situação | O que acontece |
|----------|---------------|
| **OBS fechado** ✅ | O script abre automaticamente após você digitar a duração. Sem conflitos. |
| **OBS já aberto** ⚠️ | O script detecta e usa o OBS existente, mas **os atalhos do OBS (teclas 1 e 2) ficam ativos enquanto você digita a duração**, podendo iniciar/parar gravação acidentalmente. |

**Recomendação:** deixe o OBS fechado antes de iniciar o script. Ele será aberto automaticamente no momento correto.

### Preparação Antes de Executar

1. ✅ **OBS fechado** (será aberto automaticamente)
2. ✅ **Google Chrome** aberto com o vídeo carregado e pausado
3. ✅ Você tem **tempo livre** — não mexa no computador durante a gravação

### Executando o Script

1. Execute: `python Auto_Record_Video.py` (ou o `.exe`)

2. **Primeira janela:** Leia as instruções e clique em **"OK"**

3. **Segunda janela — Duração:**
   - Digite horas, minutos e segundos
   - Marque ou desmarque **"Clique duplo para pausar"** conforme seu player:
     - ✅ **Marcado** (padrão): recomendado para YouTube — o 1º clique fecha o painel de recomendações e o 2º pausa
     - ☐ **Desmarcado**: para players que pausam com um único clique
   - Esta preferência é **salva automaticamente** para a próxima execução
   - Pressione **Enter** ou clique em **"✓ Confirmar"**

4. **Automação em ação** (não toque no mouse/teclado):
   - OBS abre e inicializa (~10 segundos)
   - Chrome entra em tela cheia
   - Gravação inicia automaticamente
   - Script aguarda o tempo configurado
   - Gravação finaliza, vídeo pausa, OBS fecha

5. **Finalização:**
   - Uma janela confirma que a gravação foi concluída
   - O vídeo está salvo na pasta de gravações do OBS

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

Pressione **Ctrl + Shift + Q** a qualquer momento. O script irá parar a gravação do OBS, sair do modo tela cheia, salvar o vídeo parcial e mostrar uma mensagem de confirmação.

---

## 🔧 Solução de Problemas

### ❌ Problema: Gravação iniciou sozinha ao digitar a duração

**Causa:** O OBS estava aberto antes de iniciar o script, e os atalhos (teclas 1 e 2) ficaram ativos durante a digitação.

**Solução:** Feche o OBS antes de iniciar o script. Ele abrirá automaticamente no momento certo.

### ❌ Problema: "Chrome não encontrado"

**Solução:** Certifique-se de que o Chrome está aberto com uma aba ativa.

### ❌ Problema: Gravação não inicia no OBS

**Soluções:**
1. Verifique se os atalhos estão configurados (tecla **1** para iniciar, **2** para parar)
2. Confirme que são atalhos **globais**
3. Teste manualmente: pressione a tecla **1** com o OBS aberto

### ❌ Problema: Tela preta na gravação

**Soluções:**
1. Desabilite a aceleração gráfica do Chrome
2. Use "Captura de Janela" em vez de "Captura de Tela" no OBS

### ❌ Problema: Gravação com segundos a mais ou a menos

**Solução:** Ajuste a constante `OVERHEAD_FINALIZACAO` no script. Aumente se gravar a mais, diminua se gravar a menos.

### ❌ Problema: Ctrl + Shift + Q não funciona

**Soluções:**
1. Execute o script como **Administrador**
2. Verifique se outro programa não está usando esse atalho

---

## 📊 Dicas de Otimização

1. **Feche programas desnecessários** antes de gravar
2. **Use modo "Alto desempenho"** nas configurações de energia do Windows
3. **Tenha espaço em disco suficiente** (pelo menos 10GB livres)
4. **Conecte o notebook na tomada** (não use bateria)

### Configurações Recomendadas do OBS:

- **Taxa de bits:** 2500–6000 kbps
- **Encoder:** x264 ou NVENC (GPU Nvidia)
- **Taxa de quadros:** 30 fps
- **Resolução:** 1920×1080

---

## 📝 Notas Finais

- ⚠️ **Não mexa no mouse/teclado** após confirmar a duração
- ⚠️ Planeje antecipadamente: calcule a duração correta do vídeo
- ✅ Teste primeiro com vídeos curtos (20–30 segundos) para calibrar o tempo

---

## 📞 Suporte

Se encontrar problemas não listados aqui:
1. Revise todas as configurações acima
2. Teste os atalhos do OBS manualmente
3. Verifique o console do Python para mensagens de erro

---

## 📜 Licença

Este script é fornecido "como está", para uso pessoal e educacional.

---

**Desenvolvido para Windows 11** | Última atualização: 2026
