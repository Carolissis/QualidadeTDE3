import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

def conectar():
    return sqlite3.connect('nc_database.db')

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nc_database (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            responsavel TEXT NOT NULL,
            impacto TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aberta',
            aplicavel TEXT NOT NULL CHECK (aplicavel IN ('Sim', 'Não'))
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_nc():
    descricao = descricao_entry.get()
    responsavel = responsavel_entry.get()
    impacto = impacto_combo.get()
    aplicavel = aplicavel_combo.get()

    if not descricao or not responsavel or impacto not in ['Alto', 'Médio', 'Baixo'] or aplicavel not in ['Sim', 'Não']:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos corretamente.")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO nc_database (descricao, responsavel, impacto, aplicavel)
        VALUES (?, ?, ?, ?)
    ''', (descricao, responsavel, impacto, aplicavel))
    conn.commit()
    conn.close()
    listar_nc_database()

def listar_nc_database():
    for item in tree.get_children():
        tree.delete(item)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM nc_database
        ORDER BY 
            CASE impacto 
                WHEN 'Alto' THEN 1
                WHEN 'Médio' THEN 2
                WHEN 'Baixo' THEN 3
            END
    ''')
    registros = cursor.fetchall()
    conn.close()

    for reg in registros:
        impacto = reg[3]
        if impacto == 'Alto':
            tag = 'alto'
        elif impacto == 'Médio':
            tag = 'medio'
        else:
            tag = 'baixo'

        tree.insert("", "end", values=reg, tags=(tag,))
    
    atualizar_percentual()

def atualizar_percentual():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM nc_database WHERE aplicavel = "Sim"')
    total_aplicaveis = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM nc_database 
        WHERE aplicavel = "Sim" AND LOWER(status) = "resolvida"
    ''')
    resolvidas = cursor.fetchone()[0]
    conn.close()

    if total_aplicaveis == 0:
        percentual_label.config(text="Percentual de Aderência: N/A")
        return

    porcentagem = (resolvidas / total_aplicaveis) * 100
    percentual_label.config(text=f"Percentual de Aderência: {porcentagem:.2f}%")

def atualizar_status():
    selecionado = tree.focus()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma não-conformidade para atualizar.")
        return

    id = tree.item(selecionado)['values'][0]
    novo_status = status_combo.get()

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE nc_database SET status = ? WHERE id = ?', (novo_status, id))
    conn.commit()
    conn.close()
    listar_nc_database()

def excluir_nao_conformidade():
    selecionado = tree.focus()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma não-conformidade para excluir.")
        return

    id = tree.item(selecionado)['values'][0]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM nc_database WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    listar_nc_database()

# Interface Tkinter
root = tk.Tk()
root.title("Sistema de Acompanhamento de Não-Conformidades")

# Widgets de entrada
tk.Label(root, text="Descrição").grid(row=0, column=0)
descricao_entry = tk.Entry(root)
descricao_entry.grid(row=0, column=1)

tk.Label(root, text="Responsável").grid(row=1, column=0)
responsavel_entry = tk.Entry(root)
responsavel_entry.grid(row=1, column=1)

tk.Label(root, text="Impacto").grid(row=2, column=0)
impacto_combo = ttk.Combobox(root, values=["Alto", "Médio", "Baixo"])
impacto_combo.grid(row=2, column=1)

tk.Label(root, text="Aplicável").grid(row=3, column=0)
aplicavel_combo = ttk.Combobox(root, values=["Sim", "Não"])
aplicavel_combo.grid(row=3, column=1)

# Botões
tk.Button(root, text="Adicionar", command=adicionar_nc).grid(row=4, column=0, columnspan=2)

# Treeview para exibir as não-conformidades
tree = ttk.Treeview(root, columns=("ID", "Descrição", "Responsável", "Impacto", "Status", "Aplicável"), show="headings")
tree.grid(row=5, column=0, columnspan=2)
for col in tree["columns"]:
    tree.heading(col, text=col)

# Definindo as cores para cada tipo de impacto
tree.tag_configure('alto', background='#FFB6B6')   # Vermelho claro
tree.tag_configure('medio', background='#FFFFB6')  # Amarelo claro
tree.tag_configure('baixo', background='#B6FFB6')  # Verde claro

# Widgets para atualizar status
tk.Label(root, text="Novo Status").grid(row=6, column=0)
status_combo = ttk.Combobox(root, values=["Aberta", "Em Andamento", "Resolvida"])
status_combo.grid(row=6, column=1)

tk.Button(root, text="Atualizar Status", command=atualizar_status).grid(row=7, column=0, columnspan=2)
tk.Button(root, text="Excluir", command=excluir_nao_conformidade).grid(row=8, column=0, columnspan=2)

# Label para exibir o percentual de aderência
percentual_label = tk.Label(root, text="Percentual de Aderência: N/A")
percentual_label.grid(row=9, column=0, columnspan=2)

# Inicializar a tabela e o banco de dados
criar_tabela()
listar_nc_database()

# Iniciar o loop da interface
root.mainloop()
