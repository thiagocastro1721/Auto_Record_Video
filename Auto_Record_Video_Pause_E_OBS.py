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
from tkinter import Tk, Label, Entry, Button, messagebox, Frame
import keyboard
import sys
import subprocess
import os
import ctypes
import psutil

# Variáveis globais
largura, altura = pyautogui.size()
gravacao_ativa = False
deve_abortar = False

def abortar():
    """Abortar gravação ao pressionar CTRL+SHIFT+Q"""
    global deve_abortar
    deve_abortar = True
    print("\n🛑 CTRL+SHIFT+Q DETECTADO - ABORTANDO...")

def executar_abort():
    """Executa as ações de abort na thread principal"""
    global gravacao_ativa
    
    print("\n" + "="*70)
    print("  🛑🛑🛑 CANCELANDO GRAVAÇÃO 🛑🛑🛑")
    print("="*70 + "\n")
    
    # ⏹️ PARAR GRAVAÇÃO (GLOBAL)
    print("⏹️ Parando gravação OBS (Tecla 2)")
    time.sleep(0.5)
    pydirectinput.press('2')
    time.sleep(1)
    
    # Clicar no centro para garantir foco
    print("🖱️ Clicando no centro da tela...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(0.5)
    
    # Sair do fullscreen
    print("🖥️ Saindo do fullscreen (F11)")
    pyautogui.press('f11')
    time.sleep(0.5)
    
    gravacao_ativa = False
    
    # Mostrar popup — só cria o Tk DEPOIS de toda automação terminar
    root = Tk() 
    root.withdraw()
    root.attributes('-topmost', True)
    
    messagebox.showinfo(
        "⚠️ Gravação Cancelada",
        "A gravação foi INTERROMPIDA pelo usuário (CTRL+SHIFT+Q).\n\n"
        "✓ A gravação OBS foi parada\n"
        "✓ O vídeo parcial foi salvo\n\n"
        "📁 Verifique o arquivo na pasta de gravações do OBS.",
        parent=root
    )
    
    root.destroy()
    
    print("🛑 Script interrompido pelo usuário")
    keyboard.unhook_all()
    sys.exit(0)

def obter_duracao():
    """Cria janela customizada com 3 campos: horas, minutos, segundos"""
    
    resultado = {'duracao': None}
    
    def confirmar():
        try:
            horas = int(entry_horas.get() or 0)
            minutos = int(entry_minutos.get() or 0)
            segundos = int(entry_segundos.get() or 0)
            
            # Validações
            if horas < 0 or minutos < 0 or segundos < 0:
                messagebox.showerror("Erro", "Valores não podem ser negativos!", parent=janela)
                return
            
            if minutos > 59:
                messagebox.showerror("Erro", "Minutos: 0 a 59!", parent=janela)
                return
                
            if segundos > 59:
                messagebox.showerror("Erro", "Segundos: 0 a 59!", parent=janela)
                return
            
            total_segundos = (horas * 3600) + (minutos * 60) + segundos
            
            if total_segundos == 0:
                messagebox.showerror("Erro", "Duração deve ser maior que zero!", parent=janela)
                return
            
            if total_segundos > 86400:
                resp = messagebox.askyesno(
                    "Aviso", 
                    f"Duração muito longa!\n({horas}h {minutos}m {segundos}s)\n\nContinuar mesmo assim?",
                    parent=janela
                )
                if not resp:
                    return
            
            resultado['duracao'] = total_segundos
            janela.quit()
            janela.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Digite apenas números!", parent=janela)
    
    def cancelar():
        janela.quit()
        janela.destroy()
    
    # Criar janela
    janela = Tk()
    janela.title("⏱️ Duração da Gravação")
    janela.geometry("420x270")
    janela.resizable(False, False)
    
    # FORÇAR aparecer em primeiro plano
    janela.attributes('-topmost', True)
    janela.lift()
    janela.focus_force()
    
    # Centralizar na tela
    janela.update_idletasks()
    x = (janela.winfo_screenwidth() // 2) - (420 // 2)
    y = (janela.winfo_screenheight() // 2) - (270 // 2)
    janela.geometry(f"420x270+{x}+{y}")
    
    # Atualizar para garantir que aparece
    janela.update()
    janela.deiconify()
    
    # Título
    Label(janela, text="Digite a duração da gravação:", 
          font=("Arial", 12, "bold")).pack(pady=15)
    
    # Frame para os campos
    frame_campos = Frame(janela)
    frame_campos.pack(pady=20)
    
    # Campo HORAS
    frame_horas = Frame(frame_campos)
    frame_horas.grid(row=0, column=0, padx=10)
    Label(frame_horas, text="Horas", font=("Arial", 10)).pack()
    entry_horas = Entry(frame_horas, width=6, font=("Arial", 16), justify="center")
    entry_horas.pack()
    entry_horas.insert(0, "0")
    
    # Campo MINUTOS
    frame_minutos = Frame(frame_campos)
    frame_minutos.grid(row=0, column=1, padx=10)
    Label(frame_minutos, text="Minutos", font=("Arial", 10)).pack()
    entry_minutos = Entry(frame_minutos, width=6, font=("Arial", 16), justify="center")
    entry_minutos.pack()
    entry_minutos.insert(0, "0")
    
    # Campo SEGUNDOS
    frame_segundos = Frame(frame_campos)
    frame_segundos.grid(row=0, column=2, padx=10)
    Label(frame_segundos, text="Segundos", font=("Arial", 10)).pack()
    entry_segundos = Entry(frame_segundos, width=6, font=("Arial", 16), justify="center")
    entry_segundos.pack()
    entry_segundos.insert(0, "0")
    
    # Dica
    Label(janela, text="💡 Use o teclado numérico", 
          font=("Arial", 9), fg="gray").pack(pady=10)
    
    # Botões
    frame_botoes = Frame(janela)
    frame_botoes.pack(pady=15)
    
    Button(frame_botoes, text="✓ Confirmar", command=confirmar, 
           width=12, height=2, bg="#4CAF50", fg="white", 
           font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10)
    
    Button(frame_botoes, text="✗ Cancelar", command=cancelar, 
           width=12, height=2, bg="#f44336", fg="white",
           font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10)
    
    # Focar no campo de horas
    entry_horas.focus_set()
    entry_horas.select_range(0, 'end')
    
    # Bind Enter para confirmar
    janela.bind('<Return>', lambda e: confirmar())
    janela.bind('<Escape>', lambda e: cancelar())
    
    # Impedir fechamento pela janela
    janela.protocol("WM_DELETE_WINDOW", cancelar)
    
    # CRITICAL: Iniciar loop de eventos
    janela.mainloop()
    
    return resultado['duracao']

OBS_EXE = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
OBS_CWD = r"C:\Program Files\obs-studio\bin\64bit"   # obrigatório: OBS busca en-US.ini aqui

def obs_processo_rodando():
    """
    Verifica se o processo obs64.exe está rodando via psutil.
    Muito mais confiável que checar títulos de janela.
    """
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'obs' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def minimizar_janelas_obs():
    """
    Minimiza todas as janelas cujo processo-dono é obs64.exe,
    usando EnumWindows + ctypes. Não chama SetForegroundWindow,
    portanto não rouba o foco de nenhuma outra janela.
    """
    SW_MINIMIZE = 6
    user32 = ctypes.windll.user32

    # Monta set de PIDs do OBS
    obs_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'obs' in proc.info['name'].lower():
                obs_pids.add(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not obs_pids:
        return

    # Callback para EnumWindows
    resultados = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))

    def callback(hwnd, _):
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in obs_pids and user32.IsWindowVisible(hwnd):
            resultados.append(hwnd)
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)

    for hwnd in resultados:
        user32.ShowWindow(hwnd, SW_MINIMIZE)

def garantir_obs_aberto():
    """
    Verifica se OBS está rodando (por processo). Se não estiver,
    abre com cwd correto para resolver 'Failed to find /en-US.ini'.
    Minimiza a janela sem roubar foco e aguarda inicialização completa.
    """
    if obs_processo_rodando():
        print("✓ OBS já está aberto.")
        return True

    print("⚠️  OBS não encontrado. Abrindo...", flush=True)

    if not os.path.exists(OBS_EXE):
        print(f"❌ Executável não encontrado: {OBS_EXE}")
        return False

    try:
        proc = subprocess.Popen(
            [OBS_EXE],
            cwd=OBS_CWD,          # <-- corrige o erro en-US.ini
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"   PID {proc.pid} — aguardando carregar", end="", flush=True)
    except Exception as e:
        print(f"\n❌ Falha ao iniciar OBS: {e}")
        return False

    # Aguarda até 30s o processo estar rodando, minimizando logo que aparecer
    obs_minimizado = False
    for _ in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        if obs_processo_rodando():
            if not obs_minimizado:
                time.sleep(1)  # pequena pausa para a janela criar o handle
                minimizar_janelas_obs()
                obs_minimizado = True
                print(" (minimizado)", end="", flush=True)
            print(" ✓")
            time.sleep(10)  # OBS demora ~7s para inicializar completamente (locale, plugins, etc)
            return True

    print(" ✗ Timeout — OBS não iniciou em 30s")
    return False


def parar_gravacao_e_sair_fullscreen():
    """
    Sequência de parar gravação, pausar vídeo e sair do fullscreen.
    Totalmente isolada de qualquer janela Tk para evitar roubo de foco.
    """
    # 1. Parar gravação OBS via hotkey global
    print("⏹️ Parando gravação OBS (Tecla 2)...")
    pydirectinput.press('2')
    time.sleep(1.5)  # Aguarda OBS confirmar parada

    # 2. Garantir que o Chrome/player ainda tem foco antes de interagir
    print("🌐 Re-ativando janela do Chrome...")
    chrome_windows = gw.getWindowsWithTitle("Chrome")
    if chrome_windows:
        chrome_windows[0].activate()
        time.sleep(0.8)

    # 3. Mover mouse para o centro e clicar para dar foco ao player
    # NOTA: o clique já pausa o vídeo no player HTML5 — não pressionar Space depois
    print("🖱️ Clicando no centro da tela (pausa o vídeo + foco)...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.3)
    pyautogui.click()
    time.sleep(0.8)

    # 4. Sair do fullscreen
    print("🖥️ Saindo do fullscreen (F11)...")
    pyautogui.press('f11')
    time.sleep(1.0)

def main():
    global gravacao_ativa, deve_abortar
    
    # Registrar hotkey ANTES de tudo
    keyboard.add_hotkey('ctrl+shift+q', abortar, suppress=True)
    print("✓ Hotkey CTRL+SHIFT+Q registrado")

    # Segurança
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.15
    
    # Primeira mensagem
    root_msg = Tk()
    root_msg.withdraw()
    
    messagebox.showinfo(
        "Automação OBS - Global Hotkeys",
        "Certifique-se de que:\n\n"
        "✓ Teclado numérico com Num Lock ativado\n"
        "✓ Atalhos do OBS são GLOBAIS:\n"
        "   • Tecla 1 = Iniciar gravação\n"
        "   • Tecla 2 = Parar gravação\n"
        "✓ Player de vídeo aberto no Chrome\n\n"
        "ℹ️  O OBS será aberto automaticamente se necessário\n\n"
        "⚠️ NÃO mexa no mouse/teclado depois\n"
        "⚠️ CTRL+SHIFT+Q para ABORTAR\n\n"
        "Clique OK para continuar...",
        parent=root_msg
    )
    
    root_msg.destroy()

    # Obter duração com 3 campos
    duracao_segundos = obter_duracao()
    
    if duracao_segundos is None:
        keyboard.unhook_all()
        return

    # Converter para exibição
    horas = duracao_segundos // 3600
    minutos = (duracao_segundos % 3600) // 60
    segundos = duracao_segundos % 60
    
    tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    print(f"\n{'='*70}")
    print(f"  Duração configurada: {tempo_formatado} ({duracao_segundos} segundos)")
    print(f"  🔥 CTRL+SHIFT+Q para abortar a qualquer momento")
    print(f"{'='*70}\n")

    # ── VERIFICAR / ABRIR OBS ─────────────────────────────────────────────────
    # Feito ANTES de mexer no Chrome para não perder o foco do navegador depois.
    # O OBS é aberto minimizado/em background, sem jamais se tornar janela ativa.
    # ─────────────────────────────────────────────────────────────────────────
    print("\n🎬 Verificando OBS...")
    obs_ok = garantir_obs_aberto()
    if not obs_ok:
        root_err = Tk()
        root_err.withdraw()
        root_err.attributes('-topmost', True)
        messagebox.showerror(
            "OBS não encontrado",
            "Não foi possível localizar ou abrir o OBS.\n\n"
            "Verifique se o OBS está instalado e tente novamente.\n"
            "Se instalado em caminho diferente, edite a lista OBS_CAMINHOS no script.",
            parent=root_err
        )
        root_err.destroy()
        keyboard.unhook_all()
        return

    # Aguardar 3 segundos
    print("Aguardando 3 segundos...")
    for i in range(3, 0, -1):
        if deve_abortar:
            executar_abort()
        print(f"  {i}...")
        time.sleep(1)

    # Ativar Chrome
    print("\n🌐 Procurando Chrome...")
    chrome_windows = gw.getWindowsWithTitle("Chrome")
    if not chrome_windows:
        messagebox.showerror("Erro", "Chrome não encontrado.")
        keyboard.unhook_all()
        return

    print("   ✓ Ativando Chrome...")
    chrome_windows[0].activate()
    time.sleep(1)

    # Tela cheia
    print("🖥️ Fullscreen (F11)...")
    pyautogui.press('f11')
    time.sleep(1)

    # Foco
    print("🖱️ Dando foco...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    #Espera para sumir o play da tela....
    time.sleep(3) 
    
    if deve_abortar:
        executar_abort()
    
    # Iniciar gravação
    print("🔴 Iniciando gravação (Tecla 1)...")
    pydirectinput.press('1')
    time.sleep(1)
    
    gravacao_ativa = True

    # Esperar duração
    print(f"\n⏱️ Gravação ativa! Duração: {tempo_formatado}")
    print(f"   Fim previsto: {time.strftime('%H:%M:%S', time.localtime(time.time() + duracao_segundos))}")
    print(f"   🔥 CTRL+SHIFT+Q para abortar\n")
    
    tempo_decorrido = 0
    intervalo_update = 60
    
    while tempo_decorrido < duracao_segundos:
        if deve_abortar:
            executar_abort()
            
        time.sleep(1)
        tempo_decorrido += 1
        tempo_restante = duracao_segundos - tempo_decorrido
        
        if tempo_restante <= 10 and tempo_restante > 0:
            print(f"   ⏱️ {tempo_restante}s...")
        elif tempo_decorrido % intervalo_update == 0 and tempo_restante > 10:
            horas_rest = tempo_restante // 3600
            minutos_rest = (tempo_restante % 3600) // 60
            segundos_rest = tempo_restante % 60
            print(f"   ⏳ Restam {horas_rest:02d}:{minutos_rest:02d}:{segundos_rest:02d}")

    print(f"\n   ✓ Concluído! {tempo_formatado}")

    # ── PONTO CRÍTICO ──────────────────────────────────────────────────────────
    # Toda a automação (parar OBS, pausar vídeo, sair do fullscreen) deve ser
    # concluída ANTES de qualquer janela Tk ser criada, pois o Tk pode roubar
    # o foco do Chrome/player e impedir que os comandos de teclado/mouse funcionem.
    # ──────────────────────────────────────────────────────────────────────────
    parar_gravacao_e_sair_fullscreen()
    
    gravacao_ativa = False

    # Só AGORA cria a janela de conclusão
    root_fim = Tk()
    root_fim.withdraw()
    root_fim.attributes('-topmost', True)

    messagebox.showinfo(
        "✅ Gravação Concluída",
        f"Script finalizado!\n\n"
        f"Duração: {tempo_formatado}\n"
        f"Gravação salva pelo OBS.\n\n"
        f"📁 Verifique a pasta de gravações.",
        parent=root_fim
    )

    root_fim.destroy()

    print("\n" + "="*70)
    print("  ✅ Finalizado com sucesso!")
    print("  📁 Verifique sua gravação no OBS.")
    print("="*70)
    
    keyboard.unhook_all()


if __name__ == "__main__":
    try:
        main()
    except pyautogui.FailSafeException:
        root_err = Tk()
        root_err.withdraw()
        messagebox.showwarning(
            "Interrompido",
            "FAILSAFE ativado.\nMouse no canto superior esquerdo.",
            parent=root_err
        )
        root_err.destroy()
    except KeyboardInterrupt:
        print("\n🛑 Ctrl+C detectado")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        root_err = Tk()
        root_err.withdraw()
        messagebox.showerror("Erro", f"Erro:\n\n{e}", parent=root_err)
        root_err.destroy()
    finally:
        keyboard.unhook_all()
