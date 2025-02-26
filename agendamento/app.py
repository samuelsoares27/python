import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configura a pasta onde os logs serão salvos
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)  # Cria a pasta se não existir
log_file = os.path.join(log_folder, "erro_log.txt")

# Função para aguardar até o horário de execução
def esperar_ate_horario_execucao(horario_execucao_str):
    horario_execucao = datetime.strptime(horario_execucao_str, "%H:%M")
    horario_atual = datetime.now().replace(second=0, microsecond=0)

    while horario_atual < horario_execucao:
        time.sleep(10)
        horario_atual = datetime.now().replace(second=0, microsecond=0)
        print(f"Aguardando... Hora atual: {horario_atual.strftime('%H:%M')}, aguardando até: {horario_execucao.strftime('%H:%M')}")

# Carregar os dados do config.json
with open('config.json', 'r') as f:
    config = json.load(f)

print("Configuração carregada:", config)    

if config.get("executar_script", False):
    esperar_ate_horario_execucao(config["horario_execucao"])

    driver = webdriver.Chrome()

    driver.get("https://www.rankingtenis.com.br/login")

    print("Esperando....")  
    time.sleep(2)    

    telefone_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "telefoneLogin"))
    )
    senha_field = driver.find_element(By.NAME, "senhaLogin")

    telefone_field.send_keys(config["telefone"])
    senha_field.send_keys(config["senha"])

    login_button = driver.find_element(By.NAME, "btnLogar")
    login_button.click()

    driver.get("https://www.rankingtenis.com.br/agendar")
    time.sleep(5)

    try:        

        # Aguarda até o campo estar presente e visível
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "data"))
        )

        data_field = driver.find_element(By.ID, "data")
        data_field.click()
        data_field.send_keys(config["data"])
        data_field.submit()

        # Espera até que o campo 'hora' esteja presente
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "hora"))
        )

        time.sleep(5)
        # Aumenta o tempo de espera caso o DOM ainda esteja sendo atualizado
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "hora"))
        )

        hora_field = driver.find_element(By.ID, "hora")
        select = Select(hora_field)
        select.select_by_value(str(config["hora"]))

        quadra_id = f"idQuadra{config['idQuadra']}"
        quadra = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, quadra_id))
        )
        quadra.click()

        oponente_field = driver.find_element(By.NAME, "oponente")
        oponente_field.send_keys(config["oponente"])

        tipo_jogo_field = driver.find_element(By.NAME, "opcaoJogo")
        Select(tipo_jogo_field).select_by_value(config["opcaoJogo"])

        modalidade_field = driver.find_element(By.NAME, "tipoJogo")
        Select(modalidade_field).select_by_value(config["tipoJogo"])

    except Exception as e:
            error_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Erro ao preencher a data: {str(e)}\n"
    
    # Exibe no console
    print(error_message)

    # Salva no arquivo de log
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(error_message)
    
    print("Fim do preenchimento")  

    # Aguarda o botão de agendamento e clica nele
    #    btn_agendar = WebDriverWait(driver, 10).until(
    #      EC.element_to_be_clickable((By.NAME, "btnAgendar"))
    #  )
    #btn_agendar.click()

    time.sleep(5)
    print("Agendamento realizado com sucesso!")  

    #driver.quit()
else:
    print("Script não será executado, configuração 'executar_script' é False.")
