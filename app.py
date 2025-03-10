from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import json  # Importe a biblioteca json

app = Flask(__name__)
DATABASE_NAME = 'database.db'

# Função para conectar ao banco de dados
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return conn

# Função para criar as tabelas
def criar_tabelas():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pontos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora_inicio DATETIME NOT NULL,
                data_hora_fim DATETIME,
                descricao TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relatorios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_geracao DATETIME NOT NULL,
                dados TEXT NOT NULL,  -- Armazenar os dados do relatório como JSON
                total_horas INTEGER NOT NULL,
                total_minutos INTEGER NOT NULL,
                total_segundos INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

criar_tabelas()

class Ponto:
    def __init__(self, id, data_hora_inicio, data_hora_fim, descricao):
        self.id = id
        self.data_hora_inicio = data_hora_inicio
        self.data_hora_fim = data_hora_fim
        self.descricao = descricao

    @property
    def data_hora_inicio_formatada(self):
        if self.data_hora_inicio:
            dt = datetime.datetime.strptime(self.data_hora_inicio, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%dT%H:%M')
        return None

    @property
    def data_hora_fim_formatada(self):
        if self.data_hora_fim:
            dt = datetime.datetime.strptime(self.data_hora_fim, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%dT%H:%M')
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pontos ORDER BY id DESC LIMIT 1")
        ultimo_registro = cursor.fetchone()
        conn.close()

        ultimo_ponto = None
        if ultimo_registro:
           ultimo_ponto = Ponto(ultimo_registro['id'], ultimo_registro['data_hora_inicio'], ultimo_registro['data_hora_fim'], ultimo_registro['descricao'])

        return render_template('index.html', ultimo_ponto=ultimo_ponto)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/iniciar', methods=['POST'])
def iniciar_ponto():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO pontos (data_hora_inicio) VALUES (?)", (agora,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/descrever/<int:ponto_id>', methods=['POST'])
def descrever_ponto(ponto_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        descricao = request.form['descricao']
        try:
            cursor.execute("UPDATE pontos SET descricao = ? WHERE id = ?", (descricao, ponto_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao atualizar a descrição: {e}")
            conn.rollback()
            return "Erro ao atualizar a descrição no banco de dados", 500
        finally:
            conn.close()
        return redirect(url_for('listar_pontos'))
    return "Erro ao conectar ao banco de dados", 500

@app.route('/excluir/<int:ponto_id>', methods=['POST'])
def excluir_ponto(ponto_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pontos WHERE id = ?", (ponto_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao excluir o ponto: {e}")
            conn.rollback()
            return "Erro ao excluir o ponto no banco de dados", 500
        finally:
            conn.close()
        return redirect(url_for('listar_pontos'))
    return "Erro ao conectar ao banco de dados", 500

@app.route('/editar/<int:ponto_id>')
def editar_ponto(ponto_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pontos WHERE id = ?", (ponto_id,))
        registro = cursor.fetchone()
        conn.close()

        if registro:
            # Converta o registro do banco de dados em um objeto Ponto
            ponto = Ponto(registro['id'], registro['data_hora_inicio'], registro['data_hora_fim'], registro['descricao'])
            return render_template('editar_ponto.html', ponto=ponto)
        else:
            return "Ponto não encontrado", 404
    return "Erro ao conectar ao banco de dados", 500

@app.route('/salvar_edicao_ponto/<int:ponto_id>', methods=['POST'])
def salvar_edicao_ponto(ponto_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        data_hora_inicio = request.form['data_hora_inicio']
        data_hora_fim = request.form['data_hora_fim'] or None  # Permite que seja nulo
        descricao = request.form['descricao']

        try:
            # Converta as datas para o formato correto do banco de dados
            data_hora_inicio_formatada = datetime.datetime.strptime(data_hora_inicio, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
            if data_hora_fim:
                data_hora_fim_formatada = datetime.datetime.strptime(data_hora_fim, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
            else:
                data_hora_fim_formatada = None

            cursor.execute('''
                UPDATE pontos
                SET data_hora_inicio = ?,
                    data_hora_fim = ?,
                    descricao = ?
                WHERE id = ?
            ''', (data_hora_inicio_formatada, data_hora_fim_formatada, descricao, ponto_id))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao salvar a edição do ponto: {e}")
            conn.rollback()
            return "Erro ao salvar a edição do ponto no banco de dados", 500
        finally:
            conn.close()

        return redirect(url_for('listar_pontos'))
    return "Erro ao conectar ao banco de dados", 500

@app.route('/parar', methods=['POST'])
def parar_ponto():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            UPDATE pontos
            SET data_hora_fim = ?
            WHERE id = (SELECT id FROM pontos WHERE data_hora_fim IS NULL ORDER BY id DESC LIMIT 1)
        ''', (agora,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/listar')
def listar_pontos():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pontos")
        registros = cursor.fetchall()
        conn.close()

        # Calcular a duração para cada ponto
        pontos_com_duracao = []
        for registro in registros:
            inicio_str = registro['data_hora_inicio']
            fim_str = registro['data_hora_fim']

            inicio = datetime.datetime.strptime(inicio_str, '%Y-%m-%d %H:%M:%S')
            if fim_str:
                fim = datetime.datetime.strptime(fim_str, '%Y-%m-%d %H:%M:%S')
                duracao = fim - inicio
                duracao_str = str(duracao)  # Formata a duração como string
            else:
                duracao_str = "Aberto"  # Indica que o ponto ainda está aberto

            # Adiciona a duração ao dicionário do registro
            ponto_com_duracao = {
                'id': registro['id'],
                'data_hora_inicio': registro['data_hora_inicio'],
                'data_hora_fim': registro['data_hora_fim'],
                'descricao': registro['descricao'],
                'duracao': duracao_str  # Adiciona a duração formatada
            }

            pontos_com_duracao.append(ponto_com_duracao)

        return render_template('listar.html', registros=pontos_com_duracao)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/relatorio')
def relatorio_horas():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pontos WHERE data_hora_fim IS NOT NULL ORDER BY data_hora_inicio")
        registros = cursor.fetchall()
        conn.close()

        # Organizar dados por dia
        relatorio_por_dia = {}
        total_segundos = 0

        for registro in registros:
            inicio_str = registro['data_hora_inicio']
            fim_str = registro['data_hora_fim']
            descricao = registro['descricao']
            id = registro['id']

            inicio = datetime.datetime.strptime(inicio_str, '%Y-%m-%d %H:%M:%S')
            fim = datetime.datetime.strptime(fim_str, '%Y-%m-%d %H:%M:%S')
            diferenca = fim - inicio
            total_segundos += diferenca.total_seconds()

            dia = inicio.date()  # Extrai a data (ano-mês-dia)

            dia_str = dia.strftime('%Y-%m-%d')  # Converte para string!

            if dia_str not in relatorio_por_dia:
                relatorio_por_dia[dia_str] = []

            relatorio_por_dia[dia_str].append({
                'id': id,
                'inicio': inicio.strftime('%H:%M:%S'),
                'fim': fim.strftime('%H:%M:%S'),
                'descricao': descricao,
                'duracao': diferenca.total_seconds()
            })

        # Calcula o total de horas, minutos e segundos
        horas = int(total_segundos // 3600)
        minutos = int((total_segundos % 3600) // 60)
        segundos = int(total_segundos % 60)

        # Salvar o relatório no banco de dados
        data_geracao = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dados = json.dumps(relatorio_por_dia, default=str)  # Converte para JSON
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO relatorios (data_geracao, dados, total_horas, total_minutos, total_segundos)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data_geracao, dados, horas, minutos, segundos))
                conn.commit()
                print("Relatório salvo no banco de dados com sucesso!")
            except sqlite3.Error as e:
                print(f"Erro ao salvar o relatório no banco de dados: {e}")
                conn.rollback()
            finally:
                conn.close()

        return render_template('relatorio.html', relatorio=relatorio_por_dia, horas=horas, minutos=minutos, segundos=segundos)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/listar_relatorios')
def listar_relatorios():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, data_geracao, total_horas, total_minutos, total_segundos FROM relatorios ORDER BY data_geracao DESC")
        relatorios = cursor.fetchall()
        conn.close()
        return render_template('listar_relatorios.html', relatorios=relatorios)
    return "Erro ao conectar ao banco de dados", 500

@app.route('/visualizar_relatorio/<int:relatorio_id>')
def visualizar_relatorio(relatorio_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT dados, total_horas, total_minutos, total_segundos FROM relatorios WHERE id = ?", (relatorio_id,))
        relatorio = cursor.fetchone()
        conn.close()

        if relatorio:
            dados = json.loads(relatorio['dados'])  # Converte de JSON para dicionário
            horas = relatorio['total_horas']
            minutos = relatorio['total_minutos']
            segundos = relatorio['total_segundos']
            return render_template('visualizar_relatorio.html', relatorio=dados, horas=horas, minutos=minutos, segundos=segundos)
        else:
            return "Relatório não encontrado", 404
    return "Erro ao conectar ao banco de dados", 500

@app.route('/zerar_historico', methods=['POST'])
def zerar_historico():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pontos")
            conn.commit()
            print("Histórico de pontos zerado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao zerar o histórico de pontos: {e}")
            conn.rollback()
            return "Erro ao zerar o histórico de pontos no banco de dados", 500
        finally:
            conn.close()
        return redirect(url_for('index'))
    return "Erro ao conectar ao banco de dados", 500

# Agendamento da tarefa de zerar o histórico
def agendar_tarefa():
    scheduler = BackgroundScheduler()
    # Agendar para executar no primeiro dia de cada mês às 00:00
    scheduler.add_job(id='zerar_historico_mensal', func=zerar_historico_agendado, trigger='cron', day=1, hour=0, minute=0)
    scheduler.start()

    # Garante que o scheduler seja desligado quando o app for encerrado
    atexit.register(lambda: scheduler.shutdown())

def zerar_historico_agendado():
    with app.app_context(): # Cria um contexto de aplicação para o scheduler
        zerar_historico()
        print('Zerando o histórico...')

# Inicia o agendador
agendar_tarefa()

if __name__ == '__main__':
    app.run(debug=True)
