# -*- coding: utf-8 -*-
"""
Automação OBS com WebSocket + Global Hotkeys - Windows 11
Inicia e para gravação exclusivamente via WebSocket (sem input de teclado no OBS)
Pressione CTRL+SHIFT+Q para abortar a qualquer momento

Dependências:
    pip install pyautogui pygetwindow keyboard obsws-python pycaw

Configuração OBS:
    Ferramentas → Configurações do WebSocket Server
    ✓ Ativar WebSocket
    Porta: 4455
    Definir senha (ou deixar em branco)
"""

import pyautogui
import time
import pygetwindow as gw
from tkinter import Tk, Label, Entry, Button, messagebox, Frame, BooleanVar, Checkbutton
import keyboard
import sys
import subprocess
import os
import ctypes
import json

import obsws_python as obs

# Variáveis globais
largura, altura = pyautogui.size()
deve_abortar = False

# ── CONFIGURAÇÃO OBS ──────────────────────────────────────────────────────────
OBS_EXE = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
OBS_CWD = r"C:\Program Files\obs-studio\bin\64bit"

OBS_WS_HOST     = "localhost"
OBS_WS_PORT     = 4455
OBS_WS_PASSWORD = ""          # deixe em branco se não configurou senha no OBS
# ─────────────────────────────────────────────────────────────────────────────

# ── PERSISTÊNCIA ──────────────────────────────────────────────────────────────
_BASE_DIR   = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(_BASE_DIR, "obs_automacao_config.json")

def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            defaults = {
                "clique_duplo_pausa": True,
                "reduzir_brilho":     False,
                "mutar_audio":        False,
                "ws_password":        "",
            }
            return {**defaults, **json.load(f)}
    except Exception:
        return {
            "clique_duplo_pausa": True,
            "reduzir_brilho":     False,
            "mutar_audio":        False,
            "ws_password":        "",
        }

def salvar_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Não foi possível salvar configurações: {e}")
# ─────────────────────────────────────────────────────────────────────────────

# ── WEBSOCKET OBS ─────────────────────────────────────────────────────────────
def _criar_cliente_ws(password: str):
    pw = password or OBS_WS_PASSWORD
    try:
        cl = obs.ReqClient(
            host=OBS_WS_HOST,
            port=OBS_WS_PORT,
            password=pw,
            timeout=10,
        )
        return cl
    except Exception as e:
        raise ConnectionError(f"WebSocket: {e}")

def ws_iniciar_gravacao(password: str = ""):
    cl = _criar_cliente_ws(password)
    cl.start_record()
    cl.disconnect()
    print("   ✓ Gravação iniciada via WebSocket")

def ws_parar_gravacao(password: str = ""):
    cl = _criar_cliente_ws(password)
    cl.stop_record()
    cl.disconnect()
    print("   ✓ Gravação parada via WebSocket")

def testar_conexao_ws(password: str = "") -> bool:
    try:
        cl = _criar_cliente_ws(password)
        cl.get_version()
        cl.disconnect()
        return True
    except Exception:
        return False
# ─────────────────────────────────────────────────────────────────────────────

# ── BRILHO ────────────────────────────────────────────────────────────────────
def _startupinfo_oculto():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    return si

def obter_brilho_atual():
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

# ── ÁUDIO ─────────────────────────────────────────────────────────────────────
def _definir_mute_ps(mutar: bool):
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        devices   = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume    = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMute(1 if mutar else 0, None)
        print(f"   ✓ {'Áudio mutado 🔇' if mutar else 'Áudio desmutado 🔊'}")
    except ImportError:
        print("⚠️ pycaw não instalado. Execute: pip install pycaw")
        _pressionar_mute()
    except Exception as e:
        print(f"⚠️ Erro ao alterar mute: {e}")
        _pressionar_mute()

def _pressionar_mute():
    VK_VOLUME_MUTE = 0xAD
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
# ─────────────────────────────────────────────────────────────────────────────

def _rodar_comando_oculto(args):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    try:
        return subprocess.check_output(
            args, startupinfo=si, stderr=subprocess.DEVNULL,
        ).decode(errors='ignore')
    except Exception:
        return None

def obs_processo_rodando():
    saida = _rodar_comando_oculto(['tasklist', '/FI', 'IMAGENAME eq obs64.exe', '/NH'])
    return saida is not None and 'obs64.exe' in saida.lower()

def garantir_obs_aberto():
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
        si.wShowWindow = 1
        proc = subprocess.Popen(
            [OBS_EXE], cwd=OBS_CWD, startupinfo=si,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
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
            time.sleep(5)  # aguarda WebSocket server inicializar também
            return True

    print(" ✗ Timeout — OBS não iniciou em 30s")
    return False

def fechar_obs():
    print("🔴 Encerrando OBS...")
    _rodar_comando_oculto(['taskkill', '/F', '/IM', 'obs64.exe'])
    time.sleep(1)
    if not obs_processo_rodando():
        print("   ✓ OBS encerrado.")
    else:
        print("   ⚠️ OBS ainda em execução — encerre manualmente se necessário.")

def _restaurar_brilho_mute(brilho_original, mutar_audio):
    if brilho_original is not None:
        print(f"💡 Restaurando brilho para {brilho_original}%...")
        definir_brilho(brilho_original)
    if mutar_audio:
        print("🔊 Restaurando áudio (desmutando)...")
        _definir_mute_ps(False)

def parar_gravacao_e_sair_fullscreen(ws_password: str = "", clique_duplo_pausa: bool = True):
    print("⏹️ Parando gravação OBS...")
    ws_parar_gravacao(ws_password)
    time.sleep(1.5)

    print("🖱️ Pausando vídeo...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    if clique_duplo_pausa:
        pyautogui.click()
        time.sleep(1)
        pyautogui.click()
        print("   (clique duplo ativado)")
    else:
        pyautogui.click()
        print("   (clique simples)")

    print("🖥️ Saindo do fullscreen (F11)...")
    pyautogui.press('f11')
    time.sleep(1.0)

def abortar():
    global deve_abortar
    deve_abortar = True
    print("\n🛑 CTRL+SHIFT+Q DETECTADO - ABORTANDO...")

def executar_abort(ws_password: str = "", brilho_original=None, mutar_audio=False):
    print("\n" + "="*70)
    print("  🛑🛑🛑 CANCELANDO GRAVAÇÃO 🛑🛑🛑")
    print("="*70 + "\n")

    print("⏹️ Parando gravação OBS...")
    try:
        ws_parar_gravacao(ws_password)
    except Exception as e:
        print(f"   ⚠️ Não foi possível parar via WebSocket: {e}")
    time.sleep(1)

    print("🖱️ Clicando no centro da tela...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(0.5)

    print("🖥️ Saindo do fullscreen (F11)")
    pyautogui.press('f11')
    time.sleep(0.5)

    _restaurar_brilho_mute(brilho_original, mutar_audio)
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
    config   = carregar_config()
    resultado = {
        'duracao':            None,
        'clique_duplo_pausa': config['clique_duplo_pausa'],
        'reduzir_brilho':     config['reduzir_brilho'],
        'mutar_audio':        config['mutar_audio'],
        'ws_password':        config.get('ws_password', ''),
    }

    def confirmar():
        try:
            horas    = int(entry_horas.get()    or 0)
            minutos  = int(entry_minutos.get()  or 0)
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

            resultado['duracao']            = total_segundos
            resultado['clique_duplo_pausa'] = var_clique_duplo.get()
            resultado['reduzir_brilho']     = var_reduzir_brilho.get()
            resultado['mutar_audio']        = var_mutar_audio.get()
            resultado['ws_password']        = entry_ws_password.get().strip()

            salvar_config({
                'clique_duplo_pausa': resultado['clique_duplo_pausa'],
                'reduzir_brilho':     resultado['reduzir_brilho'],
                'mutar_audio':        resultado['mutar_audio'],
                'ws_password':        resultado['ws_password'],
            })

            janela.quit()
            janela.destroy()

        except ValueError:
            messagebox.showerror("Erro", "Digite apenas números!", parent=janela)

    def cancelar():
        janela.quit()
        janela.destroy()

    def testar_ws():
        pw = entry_ws_password.get().strip()

        if not obs_processo_rodando():
            messagebox.showinfo(
                "Abrindo OBS",
                "OBS não está rodando.\nAbrindo automaticamente para teste...",
                parent=janela
            )
            obs_abriu = garantir_obs_aberto()
            if not obs_abriu:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível abrir o OBS.\nVerifique se está instalado.",
                    parent=janela
                )
                return

        ok = testar_conexao_ws(pw)
        if ok:
            messagebox.showinfo(
                "✓ WebSocket OK",
                "Conexão com OBS estabelecida com sucesso!",
                parent=janela
            )
        else:
            messagebox.showerror(
                "✗ Falha WebSocket",
                "Não foi possível conectar ao OBS via WebSocket.\n\n"
                "Verifique:\n"
                "• Ferramentas → Configurações do WebSocket Server\n"
                "• ✓ Ativar servidor WebSocket\n"
                "• Porta: 4455\n"
                "• Senha correta (ou em branco se sem senha)",
                parent=janela
            )

    janela = Tk()
    janela.title("⏱️ Duração da Gravação")
    janela.geometry("440x490")
    janela.resizable(False, False)
    janela.attributes('-topmost', True)
    janela.lift()
    janela.focus_force()

    janela.update_idletasks()
    x = (janela.winfo_screenwidth()  // 2) - (440 // 2)
    y = (janela.winfo_screenheight() // 2) - (490 // 2)
    janela.geometry(f"440x490+{x}+{y}")
    janela.update()
    janela.deiconify()

    Label(janela, text="Digite a duração da gravação:",
          font=("Arial", 12, "bold")).pack(pady=12)

    frame_campos = Frame(janela)
    frame_campos.pack(pady=8)

    for col, (label, default) in enumerate([("Horas","0"), ("Minutos","0"), ("Segundos","0")]):
        fr = Frame(frame_campos)
        fr.grid(row=0, column=col, padx=10)
        Label(fr, text=label, font=("Arial", 10)).pack()
        e = Entry(fr, width=6, font=("Arial", 16), justify="center")
        e.pack()
        e.insert(0, default)
        if col == 0:   entry_horas    = e
        elif col == 1: entry_minutos  = e
        else:          entry_segundos = e

    Label(janela, text="💡 Use o teclado numérico",
          font=("Arial", 9), fg="gray").pack(pady=3)

    # ── WebSocket ─────────────────────────────────────────────────────────────
    frame_ws = Frame(janela, relief="groove", bd=1)
    frame_ws.pack(pady=6, padx=20, fill="x")

    Label(frame_ws, text="🔌 OBS WebSocket",
          font=("Arial", 10, "bold")).pack(anchor="w", padx=8, pady=(6, 2))

    frame_ws_linha = Frame(frame_ws)
    frame_ws_linha.pack(fill="x", padx=8, pady=(0, 8))

    Label(frame_ws_linha, text="Senha:", font=("Arial", 9)).pack(side="left")
    entry_ws_password = Entry(frame_ws_linha, width=18, font=("Arial", 10), show="*")
    entry_ws_password.pack(side="left", padx=6)
    entry_ws_password.insert(0, config.get('ws_password', ''))

    Button(frame_ws_linha, text="Testar", command=testar_ws,
           font=("Arial", 9), bg="#2196F3", fg="white").pack(side="left")
    # ─────────────────────────────────────────────────────────────────────────

    # ── Checkboxes ────────────────────────────────────────────────────────────
    frame_opcoes = Frame(janela)
    frame_opcoes.pack(pady=4, padx=20, fill="x")

    var_clique_duplo = BooleanVar(value=config['clique_duplo_pausa'])
    Checkbutton(frame_opcoes,
                text="Clique duplo para pausar (Painel de recomendações)",
                variable=var_clique_duplo, font=("Arial", 9), anchor="w").pack(fill="x")

    var_reduzir_brilho = BooleanVar(value=config['reduzir_brilho'])
    Checkbutton(frame_opcoes,
                text="Reduzir brilho para 20% durante a gravação",
                variable=var_reduzir_brilho, font=("Arial", 9), anchor="w").pack(fill="x")

    Label(frame_opcoes,
          text="   ℹ️ Funciona apenas em monitores internos (notebook).\n"
               "   Monitores externos via HDMI/DP não são suportados.",
          font=("Arial", 8), fg="#555555", justify="left", anchor="w").pack(fill="x", pady=(0, 4))

    var_mutar_audio = BooleanVar(value=config['mutar_audio'])
    Checkbutton(frame_opcoes,
                text="Mutar áudio do sistema durante a gravação",
                variable=var_mutar_audio, font=("Arial", 9), anchor="w").pack(fill="x")

    Label(frame_opcoes,
          text="⚠️ Brilho/mute afetam apenas o monitor/som local,\n"
               "    NÃO alteram a gravação do OBS.",
          font=("Arial", 8), fg="#B05000", justify="left", anchor="w").pack(fill="x", pady=(2, 0))
    # ─────────────────────────────────────────────────────────────────────────

    frame_botoes = Frame(janela)
    frame_botoes.pack(pady=12)

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
    global deve_abortar

    keyboard.add_hotkey('ctrl+shift+q', abortar, suppress=True)
    print("✓ Hotkey CTRL+SHIFT+Q registrado")

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0.15

    root_msg = Tk()
    root_msg.withdraw()

    messagebox.showinfo(
        "Automação OBS - WebSocket",
        "Certifique-se de que:\n\n"
        "✓ obsws-python instalado (controle via WebSocket)\n"
        "✓ Player de vídeo aberto no Chrome\n\n"
        "ℹ️  O OBS será aberto automaticamente.\n"
        "    Use o botão Testar na próxima tela para\n"
        "    verificar a conexão WebSocket.\n\n"
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

    duracao_segundos   = resultado['duracao']
    clique_duplo_pausa = resultado['clique_duplo_pausa']
    reduzir_brilho     = resultado['reduzir_brilho']
    mutar_audio        = resultado['mutar_audio']
    ws_password        = resultado['ws_password']

    horas    = duracao_segundos // 3600
    minutos  = (duracao_segundos % 3600) // 60
    segundos = duracao_segundos % 60
    tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    print(f"\n{'='*70}")
    print(f"  Duração configurada : {tempo_formatado} ({duracao_segundos}s)")
    print(f"  Clique duplo pausa  : {'Sim' if clique_duplo_pausa else 'Não'}")
    print(f"  Reduzir brilho      : {'Sim (→ 20%)' if reduzir_brilho else 'Não'}")
    print(f"  Mutar áudio         : {'Sim' if mutar_audio else 'Não'}")
    print(f"  🔥 CTRL+SHIFT+Q para abortar")
    print(f"{'='*70}\n")

    # ── Abrir OBS ─────────────────────────────────────────────────────────────
    print("🎬 Abrindo OBS...")
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

    # ── Validar WebSocket ──────────────────────────────────────────────────────
    ws_ok = testar_conexao_ws(ws_password)
    if not ws_ok:
        root_err = Tk()
        root_err.withdraw()
        root_err.attributes('-topmost', True)
        messagebox.showerror(
            "WebSocket indisponível",
            "Não foi possível conectar ao OBS via WebSocket.\n\n"
            "Verifique:\n"
            "• Ferramentas → Configurações do WebSocket Server\n"
            "• ✓ Ativar servidor WebSocket\n"
            "• Porta: 4455\n"
            "• Senha correta (ou em branco se sem senha)",
            parent=root_err
        )
        root_err.destroy()
        fechar_obs()
        keyboard.unhook_all()
        return

    print("Aguardando 3 segundos...")
    for i in range(3, 0, -1):
        if deve_abortar:
            executar_abort(ws_password)
        print(f"  {i}...")
        time.sleep(1)

    # ── Procurar Chrome ────────────────────────────────────────────────────────
    print("\n🌐 Procurando Chrome...")
    chrome_windows = gw.getWindowsWithTitle("Chrome")
    if not chrome_windows:
        messagebox.showerror("Erro", "Chrome não encontrado.")
        fechar_obs()
        keyboard.unhook_all()
        return

    print("   ✓ Ativando Chrome...")
    chrome_windows[0].activate()
    time.sleep(1)

    # ── Brilho / Mute ──────────────────────────────────────────────────────────
    brilho_original = None
    if reduzir_brilho:
        brilho_original = obter_brilho_atual()
        print(f"💡 Brilho original: {brilho_original}% → reduzindo para 20%")
        definir_brilho(20)

    if mutar_audio:
        print("🔇 Mutando áudio do sistema...")
        _definir_mute_ps(True)
        time.sleep(1)

    # ── Fullscreen e foco ──────────────────────────────────────────────────────
    print("🖥️ Fullscreen (F)...")
    pyautogui.press('f')
    time.sleep(1)

    print("🖱️ Dando foco e movendo cursor para o centro...")
    pyautogui.moveTo(largura // 2, altura // 2, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)

    # ── Aguarda overlay sumir ──────────────────────────────────────────────────
    print("⏳ Aguardando overlay sumir (~3s)...")
    for i in range(3, 0, -1):
        if deve_abortar:
            _restaurar_brilho_mute(brilho_original, mutar_audio)
            executar_abort(ws_password, brilho_original, mutar_audio)
        time.sleep(1)

    if deve_abortar:
        _restaurar_brilho_mute(brilho_original, mutar_audio)
        executar_abort(ws_password, brilho_original, mutar_audio)

    # ── Iniciar gravação via WebSocket ────────────────────────────────────────
    print("🔴 Iniciando gravação via WebSocket...")
    try:
        ws_iniciar_gravacao(ws_password)
    except Exception as e:
        print(f"❌ Falha ao iniciar gravação: {e}")
        _restaurar_brilho_mute(brilho_original, mutar_audio)
        fechar_obs()
        keyboard.unhook_all()
        return

    time.sleep(1)

    # ── Loop de espera ─────────────────────────────────────────────────────────
    OVERHEAD_FINALIZACAO = 0

    print(f"\n⏱️ Gravação ativa! Duração: {tempo_formatado}")
    tempo_fim = time.time() + duracao_segundos - OVERHEAD_FINALIZACAO
    print(f"   Fim previsto: {time.strftime('%H:%M:%S', time.localtime(tempo_fim))}")
    print(f"   🔥 CTRL+SHIFT+Q para abortar\n")

    intervalo_update = 60
    ultimo_update    = time.time()

    while True:
        if deve_abortar:
            _restaurar_brilho_mute(brilho_original, mutar_audio)
            executar_abort(ws_password, brilho_original, mutar_audio)

        tempo_restante = tempo_fim - time.time()

        if tempo_restante <= 0:
            break

        if tempo_restante <= 3:
            print(f"   ⏱️ {int(tempo_restante) + 1}s...")
            time.sleep(min(0.5, tempo_restante))
        else:
            if time.time() - ultimo_update >= intervalo_update:
                horas_rest    = int(tempo_restante) // 3600
                minutos_rest  = (int(tempo_restante) % 3600) // 60
                segundos_rest = int(tempo_restante) % 60
                print(f"   ⏳ Restam {horas_rest:02d}:{minutos_rest:02d}:{segundos_rest:02d}")
                ultimo_update = time.time()
            time.sleep(min(1, tempo_restante))

    print(f"\n   ✓ Concluído! {tempo_formatado}")

    parar_gravacao_e_sair_fullscreen(ws_password, clique_duplo_pausa)
    fechar_obs()
    time.sleep(3)

    _restaurar_brilho_mute(brilho_original, mutar_audio)

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
