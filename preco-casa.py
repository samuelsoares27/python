import tkinter as tk
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np

X = np.array([
    [1, 50, 10],  # 1 quarto, 50m², 10 anos
    [2, 60, 5],   # 2 quartos, 60m², 5 anos
    [3, 90, 2],   # 3 quartos, 90m², 2 anos
    [4, 120, 20], # 4 quartos, 120m², 20 anos
    [5, 150, 15], # 5 quartos, 150m², 15 anos
    [2, 80, 8],   # 2 quartos, 80m², 8 anos
    [3, 100, 10], # 3 quartos, 100m², 10 anos
    [4, 130, 25], # 4 quartos, 130m², 25 anos
])

# Preço das casas (em milhares de unidades monetárias)
y = np.array([100000, 150000, 200000, 250000, 300000, 175000, 210000, 270000])

# 25% para teste e 75% para treinar o modelo
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Criar modelo regressão linear
model = LinearRegression()

# Treinar o modelo
model.fit(X_train, y_train)

def prever_valor_casa():
        
    #coletar os dados digitado
    numero_quartos = int(entry_quartos.get())
    area = float(entry_area.get())
    idade = int(entry_idade.get())

    dados_casa = np.array([[numero_quartos, area, idade]])

    preco_previsto = model.predict(dados_casa)

     # Atualizar o rótulo com o preço previsto
    label_resultado.config(text=f'O valor previsto para a casa é: R${preco_previsto[0]:,.2f}')

# Criando a interface gráfica com Tkinter
root = tk.Tk()
root.title("Previsão de Preço de Casa")

# Rótulos de entrada
label_quartos = tk.Label(root, text="Número de Quartos:")
label_quartos.pack()

entry_quartos = tk.Entry(root)
entry_quartos.pack()

label_area = tk.Label(root, text="Área da Casa (m²):")
label_area.pack()

entry_area = tk.Entry(root)
entry_area.pack()

label_idade = tk.Label(root, text="Idade da Casa (anos):")
label_idade.pack()

entry_idade = tk.Entry(root)
entry_idade.pack()

# Botão para fazer a previsão
button_prever = tk.Button(root, text="Prever Valor", command=prever_valor_casa)
button_prever.pack()

# Rótulo para exibir o resultado
label_resultado = tk.Label(root, text="Valor da casa será mostrado aqui.", font=("Arial", 14))
label_resultado.pack()

# Iniciar a interface gráfica
root.mainloop()