# -*- coding: utf-8 -*-
"""
Automação OBS com Global Hotkeys - Windows 11
Inicia e para gravação SEM focar OBS
Pressione CTRL+SHIFT+Q para abortar a qualquer momento
"""

import pyautogui
import pydirectinput
import time
import pygetwindow as gw
from tkinter import Tk, simpledialog, messagebox
import keyboard
import sys

# Variáveis globais
largura, altura = pyautogui.size()
gravacao_ativa = False

def abortar():
    """Abortar gravação ao pressionar CTRL+SHIFT+Q"""
    global gravacao_ativa
    
    if not gravacao_ativa:
        return
    
    print("\n" + "="*70)
    print("  🛑🛑🛑 CTRL+SHIFT+Q PRESSIONADO - CANCELANDO GRAVAÇÃO 🛑🛑🛑")
    print("="*70 + "\n")
    
    # ⏹️ PARAR GRAVAÇÃO (GLOBAL)
    print("⏹️ Parando gravação OBS (NumPad 2)")
    time.sleep(1)
    pydirectinput.press('2')
    time.sleep(1)
    
    # Clicar no centro para garantir foco
    print("🖱️ Clicando no centro da tela...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(1)
    
    # Sair do fullscreen
    print("🖥️ Saindo do fullscreen (F11)")
    pyautogui.press('f11')
    time.sleep(0.5)
    
    gravacao_ativa = False
    
    #print("\n" + "="*70)
    #print("  ✓ Gravação interrompida - Mostrando popup...")
    #print("="*70 + "\n")
    
    #print("📢 Mostrando popup de cancelamento...\n")
    
    
    # Tkinter oculto 
    root = Tk() 
    root.withdraw()
    
    messagebox.showinfo(
        "⚠️ Gravação Cancelada",
        "A gravação foi INTERROMPIDA pelo usuário (CTRL+SHIFT+Q pressionado).\n\n"
        "✓ A gravação OBS foi parada\n"
        "✓ O vídeo parcial foi salvo\n\n"
        "📁 Verifique o arquivo na pasta de gravações do OBS."
    )
    
    # Aguardar 3 segundos DEPOIS do usuário clicar OK no popup
    #print("⏱️ Aguardando 1 segundos antes de encerrar...\n")
    time.sleep(1)
    
    print("🛑 Script interrompido pelo usuário")
    sys.exit(0)

# Registrar hotkey Ctrl+Shift+Q
keyboard.add_hotkey('ctrl+shift+q', abortar)

# Segurança
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


def main():
    global gravacao_ativa
    
    # Tkinter oculto
    root = Tk()
    root.withdraw()

    messagebox.showinfo(
        "Automação OBS - Global Hotkeys",
        "Certifique-se de que:\n\n"
        "✓ Você tenha um teclado numérico com Num Lock ativado para digitar a duração\n"
        "✓ OBS está aberto\n"
        "✓ Atalhos do OBS são GLOBAIS:\n"
        "  • Tecla 1 do teclado não numérico = Iniciar gravação.\n"
        "  • Tecla 2 do teclado não numérico = Parar gravação.\n"
        "✓ O player de vídeo está aberto no Chrome\n\n"
        "⚠️ NÃO mexa no mouse/teclado após clicar OK\n"
        "⚠️ Pressione CTRL+SHIFT+Q para ABORTAR a qualquer momento\n\n"
        "Clique OK para continuar..."
    )

    # Duração
    duracao_minutos = simpledialog.askfloat(
        "Duração do vídeo",
        "Digite a duração (em minutos) no teclado numérico:",
        minvalue=0.1,
        maxvalue=999
    )

    if duracao_minutos is None:
        return

    duracao_segundos = int(duracao_minutos * 60)

    print(f"\n{'='*70}")
    print(f"  Duração configurada: {duracao_minutos} minutos ({duracao_segundos} segundos)")
    print(f"  Pressione CTRL+SHIFT+Q a qualquer momento para abortar")
    print(f"{'='*70}\n")

    # Aguardar 3 segundos
    print("Aguardando 3 segundos para preparar...")
    for i in range(3, 0, -1):
        print(f"  Iniciando em {i}...")
        time.sleep(1)

    # Ativar Chrome
    print("\n🌐 Procurando janela do Chrome...")
    chrome_windows = gw.getWindowsWithTitle("Chrome")
    if not chrome_windows:
        messagebox.showerror("Erro", "Chrome não encontrado.")
        return

    print("   ✓ Chrome encontrado - Ativando...")
    chrome_windows[0].activate()
    time.sleep(1)

    # Tela cheia
    print("🖥️ Ativando tela cheia (F11)...")
    pyautogui.press('f11')
    time.sleep(1)

    # Clique ÚNICO para foco do player
    print("🖱️ Clicando no centro para garantir foco...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(3)
    
    # Iniciar gravação
    print("🔴 Iniciando gravação OBS (NumPad 1)...")
    pydirectinput.press('1')
    time.sleep(0.5)
    
    gravacao_ativa = True

    # Play do vídeo (opcional)
    # print("▶️ Iniciando reprodução...")
    # pyautogui.press("space")
    # time.sleep(0.5)

    # Esperar duração com feedback
    print(f"\n⏱️ Gravação iniciada! Aguardando {duracao_minutos} minutos...")
    print(f"   Término previsto: {time.strftime('%H:%M:%S', time.localtime(time.time() + duracao_segundos))}")
    print(f"   Pressione CTRL+SHIFT+Q para abortar\n")
    
    tempo_decorrido = 0
    intervalo_update = 60
    
    while tempo_decorrido < duracao_segundos:
        if not gravacao_ativa:  # Verificar se foi abortado
            return
            
        time.sleep(1)
        tempo_decorrido += 1
        tempo_restante = duracao_segundos - tempo_decorrido
        
        # Contagem regressiva nos últimos 10 segundos
        if tempo_restante <= 10 and tempo_restante > 0:
            print(f"   ⏱️ Finalizando em {tempo_restante} segundos...")
        # Mostrar progresso a cada minuto
        elif tempo_decorrido % intervalo_update == 0 and tempo_restante > 10:
            minutos_restantes = tempo_restante / 60
            print(f"   ⏳ Tempo restante: {minutos_restantes:.1f} minutos")

    print(f"\n   ✓ Tempo finalizado! Total: {duracao_minutos} minutos")

    # ⏹️ PARAR GRAVAÇÃO (GLOBAL)
    print("\n⏹️ Parando gravação OBS (NumPad 2)...")
    pydirectinput.press('2')
    time.sleep(1)
    
    # Clicar para garantir foco
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(1)
    
    # Sair do fullscreen
    print("🖥️ Saindo do fullscreen (F11)...")
    pyautogui.press('f11')
    time.sleep(0.5)
    
    gravacao_ativa = False

    messagebox.showinfo(
        "✅ Gravação Concluída",
        f"Script finalizado com sucesso!\n\n"
        f"Duração: {duracao_minutos} minutos\n"
        f"A gravação foi salva pelo OBS.\n\n"
        f"Verifique o arquivo de vídeo na pasta de gravações."
    )

    print("\n" + "="*70)
    print("  ✅ Script finalizado com sucesso!")
    print("  📁 Verifique sua gravação no OBS.")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except pyautogui.FailSafeException:
        messagebox.showwarning(
            "Interrompido",
            "Script interrompido pelo FAILSAFE.\n"
            "Mouse foi para o canto superior esquerdo."
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Script interrompido pelo usuário (Ctrl+C).")
    except Exception as e:
        print(f"\n\n❌ Erro durante execução: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro:\n\n{e}")
