import tkinter as tk
import speech_recognition as sr
import threading

# Função para realizar o reconhecimento de fala
def reconhecer_fala():
    recognizer = sr.Recognizer()

    # Usar microfone como fonte de entrada
    with sr.Microphone() as source:
        texto_saida.delete(1.0, tk.END)  # Limpa o campo de texto antes de começar
        status_label.config(text="Aguardando... Fale agora!")
        root.update()  # Atualiza a interface

        # Começa o efeito de "captura de áudio"
        for _ in range(10):
            barra_captura.config(width=barra_captura.winfo_width() + 5)  # Aumenta o tamanho da barra
            root.update()
            root.after(100)  # Espera um pouco antes de aumentar novamente

        try:
            recognizer.adjust_for_ambient_noise(source)  # Ajusta o ruído ambiente
            audio = recognizer.listen(source)  # Captura o áudio do microfone
            texto = recognizer.recognize_google(audio, language='pt-BR')  # Reconhece o áudio em português
            status_label.config(text="Reconhecimento concluído")
            texto_saida.insert(tk.END, texto)  # Exibe o texto reconhecido na interface
        except sr.UnknownValueError:
            status_label.config(text="Não consegui entender o que você disse.")
        except sr.RequestError:
            status_label.config(text="Erro ao conectar ao serviço de reconhecimento.")
        finally:
            barra_captura.config(width=0)  # Reseta a barra

# Criar a interface gráfica com Tkinter
root = tk.Tk()
root.title("Reconhecimento de Fala")

# Definir o tamanho da janela
root.geometry("400x300")

# Adicionar um título
titulo_label = tk.Label(root, text="Reconhecimento de Fala", font=("Arial", 16))
titulo_label.pack(pady=10)

# Botão para iniciar o reconhecimento de fala
botao_falar = tk.Button(root, text="Falar", font=("Arial", 14), command=lambda: threading.Thread(target=reconhecer_fala).start())
botao_falar.pack(pady=20)

# Label para mostrar o status
status_label = tk.Label(root, text="Clique no botão e fale", font=("Arial", 12))
status_label.pack(pady=10)

# Barra de progresso para mostrar o "efeito de captura de áudio"
barra_captura = tk.Label(root, text="    ", bg="lightblue", height=2, width=0)
barra_captura.pack(pady=10)

# Caixa de texto para mostrar o texto reconhecido
texto_saida = tk.Text(root, height=5, width=40, font=("Arial", 12))
texto_saida.pack(pady=20)

# Iniciar o loop da interface gráfica
root.mainloop()
