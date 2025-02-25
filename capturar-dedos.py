import cv2
import mediapipe as mp
import math

# Função para calcular a distância entre dois pontos
def calcular_distancia(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Função para verificar se um dedo está levantado
def dedo_levantado(landmarks, dedo_base, dedo_topo):
    # Acessa as posições dos pontos de referência
    x_base, y_base = landmarks.landmark[dedo_base].x, landmarks.landmark[dedo_base].y
    x_topo, y_topo = landmarks.landmark[dedo_topo].x, landmarks.landmark[dedo_topo].y
    
    # Distância entre o dedo base e o dedo topo (se a distância for grande, consideramos que o dedo está esticado)
    distancia = calcular_distancia(x_base, y_base, x_topo, y_topo)
    
    return distancia > 0.1  # Ajuste o valor conforme necessário para detecção de dedos levantados

# Função para desenhar os botões flutuantes
def desenhar_botoes(frame, botoes, toques):
    cores = [(0, 255, 0), (0, 0, 255), (255, 0, 0)]  # Verde, vermelho, azul
    raio = 50  # Raio do botão

    # Desenhar os botões e colorir conforme os toques
    for i, (x, y) in enumerate(botoes):
        cor = cores[i] if toques[i] else (200, 200, 200)  # Mudando a cor ao tocar
        cv2.circle(frame, (x, y), raio, cor, -1)  # Desenha um círculo preenchido como botão
        
        # Exibe o texto quando o botão é tocado
        if toques[i]:
            texto = f'Button {i + 1} pressionado'
            cv2.putText(frame, texto, (x - 80, y + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

def main():
    cap = cv2.VideoCapture(0)  # Abre a câmera padrão (0)
    
    if not cap.isOpened():
        print("Erro ao abrir a câmera")
        return
    
    # Define a resolução correta da câmera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Inicializa o MediaPipe para detecção de mãos
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_draw = mp.solutions.drawing_utils

    # Definindo os botões flutuantes na tela (posição no quadro de vídeo)
    botoes = [(400, 300), (700, 300), (1000, 300)]  # Posições dos botões
    toques = [False, False, False]  # Estado de cada botão (se foi tocado ou não)

    while True:
        ret, frame = cap.read()  # Captura frame a frame
        if not ret:
            print("Erro ao capturar o frame")
            break
        
        # Converte a imagem para RGB (MediaPipe usa RGB em vez de BGR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)  # Processa a imagem para detectar as mãos

        # Se mãos forem detectadas
        if result.multi_hand_landmarks:
            for landmarks in result.multi_hand_landmarks:
                # Desenha os pontos de referência das mãos detectadas
                mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

                # Verifica se o indicador está sobre os botões
                x_index, y_index = landmarks.landmark[8].x * frame.shape[1], landmarks.landmark[8].y * frame.shape[0]

                for i, (bx, by) in enumerate(botoes):
                    distancia = calcular_distancia(x_index, y_index, bx, by)
                    # Se o indicador estiver perto do botão (distância pequena)
                    if distancia < 50:
                        toques[i] = True  # Marca que o botão foi tocado
                    else:
                        toques[i] = False  # Caso contrário, o botão não foi tocado

        # Desenha os botões na tela e exibe o texto quando pressionado
        desenhar_botoes(frame, botoes, toques)

        # Exibe o frame com as mãos detectadas e os botões
        cv2.imshow("Detecção de Mãos e Botões", frame)

        # Pressione 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
