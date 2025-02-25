import pyttsx3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

# Inicializa o motor de TTS
engine = pyttsx3.init()

# Função para listar as vozes disponíveis
def listar_vozes():
    voices = engine.getProperty('voices')
    return voices

# Função para atualizar a lista de vozes no menu suspenso
def atualizar_vozes():
    vozes = listar_vozes()
    voz_combobox['values'] = [voz.name for voz in vozes]
    voz_combobox.current(0)  # Seleciona a primeira voz por padrão

# Função para selecionar a voz
def selecionar_voz():
    voz_selecionada = voz_combobox.get()
    vozes = listar_vozes()
    for voz in vozes:
        if voz.name == voz_selecionada:
            engine.setProperty('voice', voz.id)
            break

# Função para salvar o áudio com nome e data
def salvar_audio():
    texto = texto_entry.get("1.0", tk.END).strip()  # Obtemos o texto da caixa de texto
    if not texto:
        messagebox.showwarning("Aviso", "Por favor, digite um texto para converter.")
        return

    nome_arquivo = nome_arquivo_entry.get().strip()
    if not nome_arquivo:
        messagebox.showwarning("Aviso", "Por favor, forneça um nome para o arquivo de áudio.")
        return

    nome_arquivo_completo = f"{nome_arquivo}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
    engine.save_to_file(texto, nome_arquivo_completo)
    engine.runAndWait()

    messagebox.showinfo("Sucesso", f"Áudio salvo como: {nome_arquivo_completo}")

# Função para converter e reproduzir o áudio
def reproduzir_audio():
    texto = texto_entry.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showwarning("Aviso", "Por favor, digite um texto para converter.")
        return

    selecionar_voz()

    # Reproduzir o áudio
    engine.say(texto)
    engine.runAndWait()

# Configura a janela principal
root = tk.Tk()
root.title("Conversor de Texto para Fala")

# Tamanho da janela
root.geometry("400x400")

# Texto de instrução
titulo_label = tk.Label(root, text="Digite o texto abaixo e selecione a voz:", font=("Arial", 12))
titulo_label.pack(pady=10)

# Caixa de texto para o usuário digitar o texto
texto_entry = tk.Text(root, height=5, width=40)
texto_entry.pack(pady=10)

# Campo de entrada para o nome do arquivo
nome_arquivo_label = tk.Label(root, text="Nome do arquivo de áudio:", font=("Arial", 10))
nome_arquivo_label.pack(pady=5)
nome_arquivo_entry = tk.Entry(root, width=40)
nome_arquivo_entry.pack(pady=5)

# Seleção de voz
voz_label = tk.Label(root, text="Selecione a voz:", font=("Arial", 10))
voz_label.pack(pady=5)
voz_combobox = ttk.Combobox(root, width=40, state="readonly")
voz_combobox.pack(pady=5)

# Atualiza as vozes disponíveis no menu suspenso
atualizar_vozes()

# Botão para converter e reproduzir o áudio
reproduzir_button = tk.Button(root, text="Reproduzir Texto", command=reproduzir_audio, width=30)
reproduzir_button.pack(pady=20)

# Botão para salvar o áudio sem reproduzir
salvar_button = tk.Button(root, text="Salvar Áudio", command=salvar_audio, width=30)
salvar_button.pack(pady=5)

# Executa a interface gráfica
root.mainloop()
