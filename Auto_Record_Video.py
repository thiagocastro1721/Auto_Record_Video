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
from tkinter import Tk, Label, Entry, Button, messagebox, Frame, BooleanVar, Checkbutton
import keyboard
import sys
import subprocess
import os
import ctypes
import json

# Variáveis globais
largura, altura = pyautogui.size()
gravacao_ativa = False
deve_abortar = False

# ── CONFIGURAÇÃO OBS ──────────────────────────────────────────────────────────
OBS_EXE = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
OBS_CWD = r"C:\Program Files\obs-studio\bin\64bit"  # obrigatório: OBS busca en-US.ini aqui
# ─────────────────────────────────────────────────────────────────────────────

# ── PERSISTÊNCIA ──────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(_BASE_DIR, "obs_automacao_config.json")

def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            defaults = {"clique_duplo_pausa": True, "reduzir_brilho": False, "mutar_audio": False}
            return {**defaults, **json.load(f)}
    except Exception:
        return {"clique_duplo_pausa": True, "reduzir_brilho": False, "mutar_audio": False}

def salvar_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Não foi possível salvar configurações: {e}")
# ─────────────────────────────────────────────────────────────────────────────

# ── BRILHO ────────────────────────────────────────────────────────────────────
def obter_brilho_atual():
    """Retorna o brilho atual (0-100) via PowerShell, ou None em caso de erro."""
    try:
        saida = subprocess.check_output(
            ["powershell", "-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
            stderr=subprocess.DEVNULL,
            startupinfo=_startupinfo_oculto()
        ).decode(errors='ignore').strip()
        return int(saida)
    except Exception:
        return None

def definir_brilho(nivel: int):
    """Define o brilho (0-100) via PowerShell."""
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
             f".WmiSetBrightness(1,{nivel})"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            startupinfo=_startupinfo_oculto()
        )
        print(f"💡 Brilho definido para {nivel}%")
    except Exception as e:
        print(f"⚠️ Não foi possível alterar brilho: {e}")
# ─────────────────────────────────────────────────────────────────────────────

# ── ÁUDIO (MUTE SISTEMA) — pycaw (Windows Core Audio API) ────────────────────
#
# pycaw é a biblioteca padrão Python para controle de áudio no Windows.
# Instalar: pip install pycaw
# Encapsula IMMDeviceEnumerator + IAudioEndpointVolume de forma confiável.

def _definir_mute_ps(mutar: bool):
    """
    Muta/desmuta o dispositivo de áudio padrão via pycaw (Core Audio API).
    Determinístico: define o estado explicitamente, sem toggle.
    """
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMute(1 if mutar else 0, None)

        acao = "Áudio mutado 🔇" if mutar else "Áudio desmutado 🔊"
        print(f"   ✓ {acao}")

    except ImportError:
        print("⚠️ pycaw não instalado. Execute: pip install pycaw")
        print("   Tentando fallback via tecla mute...")
        _mute_fallback_tecla(mutar)
    except Exception as e:
        print(f"⚠️ Erro ao alterar mute: {e}")
        _mute_fallback_tecla(mutar)


def _mute_fallback_tecla(mutar: bool):
    """
    Fallback: usa a tecla VK_VOLUME_MUTE.
    Como é toggle, verifica o estado atual antes de agir.
    """
    # Tenta ler estado atual via PowerShell simples (sem Add-Type)
    estado_atual = _obter_mute_ps()
    if estado_atual is None:
        # Não conseguiu ler — pressiona a tecla e torce
        _pressionar_mute()
        return
    if estado_atual != mutar:
        _pressionar_mute()


def _obter_mute_ps() -> bool | None:
    """Retorna None — leitura de mute via WMI não é suportada; usa toggle."""
    return None


def _pressionar_mute():
    VK_VOLUME_MUTE = 0xAD
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)

def _startupinfo_oculto():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    return si
# ─────────────────────────────────────────────────────────────────────────────

def _rodar_comando_oculto(args):
    """
    Executa um comando de texto sem abrir janela visível.
    Compatível com VS Code e executáveis PyInstaller --noconsole.
    """
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0  # SW_HIDE — seguro para comandos de texto sem GUI
    try:
        return subprocess.check_output(
            args,
            startupinfo=si,
            stderr=subprocess.DEVNULL,
        ).decode(errors='ignore')
    except Exception:
        return None

def obs_processo_rodando():
    """Verifica se obs64.exe está rodando usando tasklist."""
    saida = _rodar_comando_oculto(['tasklist', '/FI', 'IMAGENAME eq obs64.exe', '/NH'])
    return saida is not None and 'obs64.exe' in saida.lower()

def garantir_obs_aberto():
    """
    Verifica se OBS está rodando. Se não estiver, abre com cwd correto
    (resolve 'Failed to find en-US.ini') e aguarda inicialização completa.
    A janela do OBS aparece normalmente para o usuário ver.
    """
    if obs_processo_rodando():
        print("✓ OBS já está aberto.")
        return True

    print("⚠️  OBS não encontrado. Abrindo...", flush=True)

    if not os.path.exists(OBS_EXE):
        print(f"❌ Executável não encontrado: {OBS_EXE}")
        return False

    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 1  # SW_SHOWNORMAL
        proc = subprocess.Popen(
            [OBS_EXE],
            cwd=OBS_CWD,
            startupinfo=si,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"   PID {proc.pid} — aguardando carregar", end="", flush=True)
    except Exception as e:
        print(f"\n❌ Falha ao iniciar OBS: {e}")
        return False

    for _ in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        if obs_processo_rodando():
            print(" ✓")
            time.sleep(3)
            return True

    print(" ✗ Timeout — OBS não iniciou em 30s")
    return False

def fechar_obs():
    """Encerra o processo obs64.exe via taskkill após a gravação ser salva."""
    print("🔴 Encerrando OBS...")
    _rodar_comando_oculto(['taskkill', '/F', '/IM', 'obs64.exe'])
    time.sleep(1)
    if not obs_processo_rodando():
        print("   ✓ OBS encerrado.")
    else:
        print("   ⚠️ OBS ainda em execução — encerre manualmente se necessário.")

def parar_gravacao_e_sair_fullscreen(clique_duplo_pausa=True):
    """
    Sequência de fim de gravação.
    clique_duplo_pausa=True: dois cliques (recomendado para YouTube/players com
                             painel de recomendações que aparece ao pausar).
    clique_duplo_pausa=False: um único clique para pausar.
    """

    # 1. Parar gravação OBS
    print("⏹️ Parando gravação OBS (Tecla 2)...")
    pydirectinput.press('2')
    time.sleep(1.5)

    print("🖱️ Pausando vídeo...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)

    if clique_duplo_pausa:
        # 1º clique: fecha painel de recomendações
        pyautogui.click()
        time.sleep(1)
        # 2º clique: pausa o vídeo
        pyautogui.click()
        print("   (clique duplo ativado)")
    else:
        pyautogui.click()
        print("   (clique simples)")

    # 2. Sair do fullscreen
    print("🖥️ Saindo do fullscreen (F11)...")
    pyautogui.press('f11')
    time.sleep(1.0)

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

    print("⏹️ Parando gravação OBS (Tecla 2)")
    time.sleep(0.5)
    pydirectinput.press('2')
    time.sleep(1)

    print("🖱️ Clicando no centro da tela...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(0.5)

    print("🖥️ Saindo do fullscreen (F11)")
    pyautogui.press('f11')
    time.sleep(0.5)

    gravacao_ativa = False
    fechar_obs()

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
    """Cria janela customizada com 3 campos: horas, minutos, segundos + opções."""

    config = carregar_config()
    resultado = {
        'duracao': None,
        'clique_duplo_pausa': config['clique_duplo_pausa'],
        'reduzir_brilho': config['reduzir_brilho'],
        'mutar_audio': config['mutar_audio'],
    }

    def confirmar():
        try:
            horas = int(entry_horas.get() or 0)
            minutos = int(entry_minutos.get() or 0)
            segundos = int(entry_segundos.get() or 0)

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
            resultado['clique_duplo_pausa'] = var_clique_duplo.get()
            resultado['reduzir_brilho'] = var_reduzir_brilho.get()
            resultado['mutar_audio'] = var_mutar_audio.get()
            salvar_config({
                'clique_duplo_pausa': resultado['clique_duplo_pausa'],
                'reduzir_brilho': resultado['reduzir_brilho'],
                'mutar_audio': resultado['mutar_audio'],
            })

            janela.quit()
            janela.destroy()

        except ValueError:
            messagebox.showerror("Erro", "Digite apenas números!", parent=janela)

    def cancelar():
        janela.quit()
        janela.destroy()

    janela = Tk()
    janela.title("⏱️ Duração da Gravação")
    janela.geometry("420x430")
    janela.resizable(False, False)
    janela.attributes('-topmost', True)
    janela.lift()
    janela.focus_force()

    janela.update_idletasks()
    x = (janela.winfo_screenwidth() // 2) - (420 // 2)
    y = (janela.winfo_screenheight() // 2) - (430 // 2)
    janela.geometry(f"420x430+{x}+{y}")
    janela.update()
    janela.deiconify()

    Label(janela, text="Digite a duração da gravação:",
          font=("Arial", 12, "bold")).pack(pady=15)

    frame_campos = Frame(janela)
    frame_campos.pack(pady=10)

    frame_horas = Frame(frame_campos)
    frame_horas.grid(row=0, column=0, padx=10)
    Label(frame_horas, text="Horas", font=("Arial", 10)).pack()
    entry_horas = Entry(frame_horas, width=6, font=("Arial", 16), justify="center")
    entry_horas.pack()
    entry_horas.insert(0, "0")

    frame_minutos = Frame(frame_campos)
    frame_minutos.grid(row=0, column=1, padx=10)
    Label(frame_minutos, text="Minutos", font=("Arial", 10)).pack()
    entry_minutos = Entry(frame_minutos, width=6, font=("Arial", 16), justify="center")
    entry_minutos.pack()
    entry_minutos.insert(0, "0")

    frame_segundos = Frame(frame_campos)
    frame_segundos.grid(row=0, column=2, padx=10)
    Label(frame_segundos, text="Segundos", font=("Arial", 10)).pack()
    entry_segundos = Entry(frame_segundos, width=6, font=("Arial", 16), justify="center")
    entry_segundos.pack()
    entry_segundos.insert(0, "0")

    Label(janela, text="💡 Use o teclado numérico",
          font=("Arial", 9), fg="gray").pack(pady=5)

    # ── CHECKBOXES ────────────────────────────────────────────────────────────
    frame_opcoes = Frame(janela)
    frame_opcoes.pack(pady=5, padx=20, fill="x")

    var_clique_duplo = BooleanVar(value=config['clique_duplo_pausa'])
    Checkbutton(
        frame_opcoes,
        text="Clique duplo para pausar (Painel de recomendações)",
        variable=var_clique_duplo,
        font=("Arial", 9),
        anchor="w",
    ).pack(fill="x")

    var_reduzir_brilho = BooleanVar(value=config['reduzir_brilho'])
    Checkbutton(
        frame_opcoes,
        text="Reduzir brilho para 20% durante a gravação",
        variable=var_reduzir_brilho,
        font=("Arial", 9),
        anchor="w",
    ).pack(fill="x")

    Label(
        frame_opcoes,
        text="   ℹ️ Funciona apenas em monitores internos (notebook).\n"
             "   Monitores externos via HDMI/DP não são suportados.",
        font=("Arial", 8),
        fg="#555555",
        justify="left",
        anchor="w",
    ).pack(fill="x", pady=(0, 4))

    var_mutar_audio = BooleanVar(value=config['mutar_audio'])
    Checkbutton(
        frame_opcoes,
        text="Mutar áudio do sistema durante a gravação",
        variable=var_mutar_audio,
        font=("Arial", 9),
        anchor="w",
    ).pack(fill="x")

    Label(
        frame_opcoes,
        text="⚠️ Brilho/mute afetam apenas o monitor/som local,\n"
             "    NÃO alteram a gravação do OBS.",
        font=("Arial", 8),
        fg="#B05000",
        justify="left",
        anchor="w",
    ).pack(fill="x", pady=(2, 0))
    # ─────────────────────────────────────────────────────────────────────────

    frame_botoes = Frame(janela)
    frame_botoes.pack(pady=15)

    Button(frame_botoes, text="✓ Confirmar", command=confirmar,
           width=12, height=2, bg="#4CAF50", fg="white",
           font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10)

    Button(frame_botoes, text="✗ Cancelar", command=cancelar,
           width=12, height=2, bg="#f44336", fg="white",
           font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10)

    entry_horas.focus_set()
    entry_horas.select_range(0, 'end')
    janela.bind('<Return>', lambda e: confirmar())
    janela.bind('<Escape>', lambda e: cancelar())
    janela.protocol("WM_DELETE_WINDOW", cancelar)
    janela.mainloop()

    return resultado

def main():
    global gravacao_ativa, deve_abortar

    keyboard.add_hotkey('ctrl+shift+q', abortar, suppress=True)
    print("✓ Hotkey CTRL+SHIFT+Q registrado")

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.15

    root_msg = Tk()
    root_msg.withdraw()

    messagebox.showinfo(
        "Automação OBS - Global Hotkeys",
        "Certifique-se de que:\n\n"
        "✓ Atalhos do OBS são GLOBAIS:\n"
        "   • Tecla 1 = Iniciar gravação\n"
        "   • Tecla 2 = Parar gravação\n"
        "✓ Player de vídeo aberto no Chrome\n\n"
        "ℹ️  O OBS será aberto automaticamente após\n"
        "   você digitar a duração — não é necessário\n"
        "   abri-lo antes.\n\n"
        "⚠️  Se o OBS já estiver aberto, feche-o antes\n"
        "   de digitar a duração para evitar conflito\n"
        "   com o teclado numérico.\n\n"
        "⚠️  NÃO mexa no mouse/teclado após confirmar\n"
        "⚠️  CTRL+SHIFT+Q para ABORTAR\n\n"
        "Clique OK para continuar...",
        parent=root_msg
    )

    root_msg.destroy()

    resultado = obter_duracao()

    if resultado['duracao'] is None:
        keyboard.unhook_all()
        return

    duracao_segundos = resultado['duracao']
    clique_duplo_pausa = resultado['clique_duplo_pausa']
    reduzir_brilho = resultado['reduzir_brilho']
    mutar_audio = resultado['mutar_audio']

    horas = duracao_segundos // 3600
    minutos = (duracao_segundos % 3600) // 60
    segundos = duracao_segundos % 60
    tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    print(f"\n{'='*70}")
    print(f"  Duração configurada: {tempo_formatado} ({duracao_segundos} segundos)")
    print(f"  Clique duplo para pausar: {'Sim' if clique_duplo_pausa else 'Não'}")
    print(f"  Reduzir brilho: {'Sim (→ 20%)' if reduzir_brilho else 'Não'}")
    print(f"  Mutar áudio: {'Sim' if mutar_audio else 'Não'}")
    print(f"  🔥 CTRL+SHIFT+Q para abortar a qualquer momento")
    print(f"{'='*70}\n")

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
            "Se instalado em caminho diferente, edite OBS_EXE no script.",
            parent=root_err
        )
        root_err.destroy()
        keyboard.unhook_all()
        return

    print("Aguardando 3 segundos...")
    for i in range(3, 0, -1):
        if deve_abortar:
            executar_abort()
        print(f"  {i}...")
        time.sleep(1)

    print("\n🌐 Procurando Chrome...")
    chrome_windows = gw.getWindowsWithTitle("Chrome")
    if not chrome_windows:
        messagebox.showerror("Erro", "Chrome não encontrado.")
        keyboard.unhook_all()
        return

    print("   ✓ Ativando Chrome...")
    chrome_windows[0].activate()
    time.sleep(1)

    # ── APLICAR BRILHO / MUTE AGORA — antes do fullscreen, foco e gravação ───
    # Qualquer som/transição do sistema ao mutar ocorre ANTES de o OBS gravar.
    brilho_original = None
    if reduzir_brilho:
        brilho_original = obter_brilho_atual()
        print(f"💡 Brilho original: {brilho_original}% → reduzindo para 20%")
        definir_brilho(20)

    if mutar_audio:
        print("🔇 Mutando áudio do sistema...")
        _definir_mute_ps(True)
        time.sleep(1)  # aguarda sistema estabilizar
    # ─────────────────────────────────────────────────────────────────────────

    print("🖥️ Fullscreen (F11)...")
    pyautogui.press('f11')
    time.sleep(1)

    print("🖱️ Dando foco...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(3)

    if deve_abortar:
        executar_abort()

    print("🔴 Iniciando gravação (Tecla 1)...")
    pydirectinput.press('1')
    time.sleep(1)

    gravacao_ativa = True

    OVERHEAD_FINALIZACAO = 1  # segundos — ajuste se ainda sobrar/faltar

    print(f"\n⏱️ Gravação ativa! Duração: {tempo_formatado}")
    tempo_fim = time.time() + duracao_segundos - OVERHEAD_FINALIZACAO
    print(f"   Fim previsto: {time.strftime('%H:%M:%S', time.localtime(tempo_fim))}")
    print(f"   🔥 CTRL+SHIFT+Q para abortar\n")

    intervalo_update = 60
    ultimo_update = time.time()

    while True:
        if deve_abortar:
            # Restaurar antes de abortar
            _restaurar_brilho_mute(brilho_original, mutar_audio)
            executar_abort()

        tempo_restante = tempo_fim - time.time()

        if tempo_restante <= 0:
            break

        if tempo_restante <= 3:
            print(f"   ⏱️ {int(tempo_restante) + 1}s...")
            time.sleep(min(0.5, tempo_restante))
        else:
            if time.time() - ultimo_update >= intervalo_update:
                horas_rest = int(tempo_restante) // 3600
                minutos_rest = (int(tempo_restante) % 3600) // 60
                segundos_rest = int(tempo_restante) % 60
                print(f"   ⏳ Restam {horas_rest:02d}:{minutos_rest:02d}:{segundos_rest:02d}")
                ultimo_update = time.time()
            time.sleep(min(1, tempo_restante))

    print(f"\n   ✓ Concluído! {tempo_formatado}")

    parar_gravacao_e_sair_fullscreen(clique_duplo_pausa)
    fechar_obs()
    time.sleep(3)

    # ── RESTAURAR BRILHO / MUTE ───────────────────────────────────────────────
    _restaurar_brilho_mute(brilho_original, mutar_audio)
    # ─────────────────────────────────────────────────────────────────────────

    gravacao_ativa = False

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


def _restaurar_brilho_mute(brilho_original, mutar_audio):
    """Restaura brilho e mute ao estado original."""
    if brilho_original is not None:
        print(f"💡 Restaurando brilho para {brilho_original}%...")
        definir_brilho(brilho_original)
    if mutar_audio:
        print("🔊 Restaurando áudio (desmutando)...")
        _definir_mute_ps(False)


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
