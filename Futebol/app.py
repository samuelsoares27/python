import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

class FutebolRanking:
    def __init__(self, db_name="futebol.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()
        self.iniciar_interface()

    def criar_tabelas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS jogadores (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nome TEXT UNIQUE NOT NULL,
                                posicao TEXT NOT NULL
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS partidas (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                jogador_id INTEGER,
                                data TEXT NOT NULL,
                                nota REAL DEFAULT 0,
                                FOREIGN KEY (jogador_id) REFERENCES jogadores(id),
                                UNIQUE(jogador_id, data)  -- Chave composta para garantir unicidade
                            )''')
        self.conn.commit()
    
    def cadastrar_jogador(self):
        nome = self.nome_entry.get()
        posicao = self.posicao_entry.get()
        try:
            self.cursor.execute("INSERT INTO jogadores (nome, posicao) VALUES (?, ?)", (nome, posicao))
            self.conn.commit()
            self.nome_entry.delete(0, tk.END)
            self.posicao_entry.delete(0, tk.END)
            self.atualizar_lista_jogadores()
            messagebox.showinfo("Sucesso", f"Jogador {nome} cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Jogador já cadastrado.")
    
    def registrar_partida(self):
        jogador_id = self.jogador_id_entry.get()
        data = self.data_entry.get()
        try:
            nota = float(self.nota_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Nota inválida. Use um número decimal.")
            return
        
        # Verificar se a data está no formato DD/MM/AAAA
        try:
            dia, mes, ano = map(int, data.split("/"))
            data_formatada = f"{dia:02d}/{mes:02d}/{ano:04d}"  # Mantendo o formato DD/MM/AAAA
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
            return

        self.cursor.execute("SELECT id FROM jogadores WHERE id = ?", (jogador_id,))
        jogador = self.cursor.fetchone()
        if jogador:
            self.cursor.execute("SELECT id FROM partidas WHERE jogador_id = ? AND data = ?", (jogador_id, data_formatada))
            partida_existente = self.cursor.fetchone()
            
            if partida_existente:
                # Atualizar a partida existente
                self.cursor.execute("UPDATE partidas SET nota = ? WHERE jogador_id = ? AND data = ?", 
                                    (nota, jogador_id, data_formatada))
                messagebox.showinfo("Sucesso", "Partida atualizada.")
            else:
                # Inserir uma nova partida
                self.cursor.execute("INSERT INTO partidas (jogador_id, data, nota) VALUES (?, ?, ?)",
                                    (jogador_id, data_formatada, nota))
                messagebox.showinfo("Sucesso", "Partida registrada.")
            
            self.conn.commit()
            self.data_entry.delete(0, tk.END)
            self.nota_entry.delete(0, tk.END)
            self.atualizar_historico()
            self.atualizar_medias()
        else:
            messagebox.showerror("Erro", "Jogador não encontrado.")
    
    def atualizar_lista_jogadores(self):
        for item in self.lista_jogadores.get_children():
            self.lista_jogadores.delete(item)
        self.cursor.execute("SELECT id, nome, posicao FROM jogadores")
        jogadores = self.cursor.fetchall()
        for jogador in jogadores:
            self.lista_jogadores.insert("", "end", values=jogador)
    
    def atualizar_historico(self):
        for item in self.historico_jogos.get_children():
            self.historico_jogos.delete(item)
        self.cursor.execute("SELECT j.id, j.nome, p.data, p.nota FROM partidas p JOIN jogadores j ON p.jogador_id = j.id")
        partidas = self.cursor.fetchall()
        for partida in partidas:
            self.historico_jogos.insert("", "end", values=partida)
    
    def atualizar_medias(self):
        for item in self.medias_jogadores.get_children():
            self.medias_jogadores.delete(item)
        self.cursor.execute("SELECT j.id, j.nome, j.posicao, COALESCE(AVG(p.nota), 0) FROM jogadores j LEFT JOIN partidas p ON j.id = p.jogador_id GROUP BY j.id")
        medias = self.cursor.fetchall()
        for media in medias:
            self.medias_jogadores.insert("", "end", values=media)
    
    def excluir_jogador(self):
        selected_item = self.lista_jogadores.selection()  # Pega o item selecionado na tabela
        if selected_item:
            jogador_id = self.lista_jogadores.item(selected_item, "values")[0]  # Pega o ID do jogador
            try:
                # Excluir partidas associadas ao jogador
                self.cursor.execute("DELETE FROM partidas WHERE jogador_id = ?", (jogador_id,))
                # Excluir o jogador
                self.cursor.execute("DELETE FROM jogadores WHERE id = ?", (jogador_id,))
                self.conn.commit()
                self.atualizar_lista_jogadores()
                self.atualizar_historico()
                self.atualizar_medias()
                messagebox.showinfo("Sucesso", "Jogador excluído com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir jogador: {e}")
        else:
            messagebox.showerror("Erro", "Por favor, selecione um jogador para excluir.")

    def excluir_partida(self):
        selected_item = self.historico_jogos.selection()  # Pega o item selecionado na tabela
        if selected_item:
            jogador_id = self.historico_jogos.item(selected_item, "values")[0]  # Pega o ID do jogador
            data = self.historico_jogos.item(selected_item, "values")[2]  # Pega a data da partida
            try:
                # Excluir a partida
                self.cursor.execute("DELETE FROM partidas WHERE jogador_id = ? AND data = ?", (jogador_id, data))
                self.conn.commit()
                self.atualizar_historico()
                self.atualizar_medias()
                messagebox.showinfo("Sucesso", "Partida excluída com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir partida: {e}")
        else:
            messagebox.showerror("Erro", "Por favor, selecione uma partida para excluir.")

    def iniciar_interface(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Futebol")
        self.root.geometry("900x500")
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both")
        
        aba_jogadores = tk.Frame(notebook)
        aba_historico = tk.Frame(notebook)
        aba_medias = tk.Frame(notebook)
        notebook.add(aba_jogadores, text="Jogadores")
        notebook.add(aba_historico, text="Histórico de Jogos")
        notebook.add(aba_medias, text="Médias")
        
        tk.Label(aba_jogadores, text="Cadastro de Jogador", font=("Arial", 12, "bold")).pack()
        frame_cadastro = tk.Frame(aba_jogadores, pady=10)
        frame_cadastro.pack()
        
        tk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.nome_entry = tk.Entry(frame_cadastro)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_cadastro, text="Posição:").grid(row=1, column=0, padx=5, pady=5)
        self.posicao_entry = tk.Entry(frame_cadastro)
        self.posicao_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Organizando os botões lado a lado com espaçamento
        botao_cadastrar = tk.Button(frame_cadastro, text="Cadastrar", command=self.cadastrar_jogador)
        botao_cadastrar.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        
        botao_excluir = tk.Button(frame_cadastro, text="Excluir Jogador", command=self.excluir_jogador)
        botao_excluir.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        
        # Lista de jogadores com scroll
        self.lista_jogadores = ttk.Treeview(aba_jogadores, columns=("ID", "Nome", "Posição"), show="headings")
        self.lista_jogadores.heading("ID", text="ID")
        self.lista_jogadores.heading("Nome", text="Nome")
        self.lista_jogadores.heading("Posição", text="Posição")
        
        # Scrollbar para a lista
        scrollbar = tk.Scrollbar(aba_jogadores, orient="vertical", command=self.lista_jogadores.yview)
        self.lista_jogadores.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.lista_jogadores.pack(expand=True, fill="both")
        
        self.atualizar_lista_jogadores()
        
        # Aba Histórico de Jogos
        tk.Label(aba_historico, text="Cadastro de Partidas", font=("Arial", 12, "bold")).pack()
        frame_partida = tk.Frame(aba_historico, pady=5)
        frame_partida.pack()
        
        tk.Label(frame_partida, text="ID Jogador:").grid(row=0, column=0, padx=5, pady=5)
        self.jogador_id_entry = tk.Entry(frame_partida)
        self.jogador_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_partida, text="Data (DD/MM/AAAA):").grid(row=1, column=0, padx=5, pady=5)
        self.data_entry = tk.Entry(frame_partida)
        self.data_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_partida, text="Nota:").grid(row=2, column=0, padx=5, pady=5)
        self.nota_entry = tk.Entry(frame_partida)
        self.nota_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Organizando os botões de partida lado a lado
        botao_registrar = tk.Button(frame_partida, text="Registrar Partida", command=self.registrar_partida)
        botao_registrar.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        
        botao_excluir_partida = tk.Button(frame_partida, text="Excluir Partida", command=self.excluir_partida)
        botao_excluir_partida.grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        
        self.historico_jogos = ttk.Treeview(aba_historico, columns=("ID", "Nome", "Data", "Nota"), show="headings")
        self.historico_jogos.heading("ID", text="ID")
        self.historico_jogos.heading("Nome", text="Nome")
        self.historico_jogos.heading("Data", text="Data")
        self.historico_jogos.heading("Nota", text="Nota")
        
        # Scrollbar para o histórico
        scrollbar_historico = tk.Scrollbar(aba_historico, orient="vertical", command=self.historico_jogos.yview)
        self.historico_jogos.config(yscrollcommand=scrollbar_historico.set)
        scrollbar_historico.pack(side="right", fill="y")
        self.historico_jogos.pack(expand=True, fill="both")
        
        self.atualizar_historico()
        
        # Aba Médias
        self.medias_jogadores = ttk.Treeview(aba_medias, columns=("ID", "Nome", "Posição", "Média"), show="headings")
        self.medias_jogadores.heading("ID", text="ID")
        self.medias_jogadores.heading("Nome", text="Nome")
        self.medias_jogadores.heading("Posição", text="Posição")
        self.medias_jogadores.heading("Média", text="Média")
        
        # Scrollbar para médias
        scrollbar_medias = tk.Scrollbar(aba_medias, orient="vertical", command=self.medias_jogadores.yview)
        self.medias_jogadores.config(yscrollcommand=scrollbar_medias.set)
        scrollbar_medias.pack(side="right", fill="y")
        self.medias_jogadores.pack(expand=True, fill="both")
        
        self.atualizar_medias()
        
        self.root.mainloop()


if __name__ == "__main__":
    FutebolRanking()
