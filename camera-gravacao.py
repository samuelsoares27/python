import cv2
import datetime

def main():
    cap = cv2.VideoCapture(0)  # Abre a câmera padrão (0)
    
    if not cap.isOpened():
        print("Erro ao abrir a câmera")
        return
    
    # Define a resolução correta da câmera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Obtém data e hora atuais para o nome do arquivo
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"gravacao_{now}.avi"

    # Define o codec e cria o objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec para AVI
    out = cv2.VideoWriter(filename, fourcc, 30.0, (width, height))

    # Carregar o classificador em cascata para detecção de rosto
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()  # Captura frame a frame
        if not ret:
            print("Erro ao capturar o frame")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Converte para escala de cinza para melhorar a detecção
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Desenha um retângulo em torno dos rostos detectados
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Desenha retângulo verde

        # Exibe o frame na janela
        out.write(frame)  # Escreve o frame no arquivo
        cv2.imshow("Câmera com Reconhecimento Facial", frame)  # Exibe o frame com rostos detectados

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Pressione 'q' para sair
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
