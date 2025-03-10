# Sistema de Registro de Ponto e Geração de Relatórios

Este projeto implementa um sistema simples de registro de ponto (entrada/saída) com funcionalidades de descrição de atividades, geração de relatórios de horas trabalhadas e histórico de relatórios. A aplicação é construída com Flask, um microframework web em Python, e utiliza SQLite como banco de dados.

## Funcionalidades

*   **Registro de Ponto:**
    *   Início de jornada de trabalho (registro de data e hora de início).
    *   Fim de jornada de trabalho (registro de data e hora de fim).
    *   Descrição opcional da atividade realizada (permite edição posterior).

*   **Listagem de Pontos:**
    *   Exibe todos os registros de ponto (entrada/saída) com data, hora e descrição.
    *   Calcula e exibe a duração de cada período de trabalho.
    *   Indica visualmente se um ponto está "aberto" (sem registro de saída).
    *   Opções para editar e excluir registros.

*   **Edição de Pontos:**
    *   Permite modificar a data/hora de início, data/hora de fim e a descrição de um registro de ponto.
    *   Validação de dados para garantir formatos corretos.
* **Exclusão de Pontos**
    * Permite excluir um ponto.

*   **Geração de Relatório de Horas:**
    *   Agrupa os registros de ponto por dia.
    *   Calcula o total de horas, minutos e segundos trabalhados.
    *   Exibe os detalhes de cada período de trabalho (início, fim, descrição, duração).
    *   Salva o relatório gerado em um histórico, com data e hora de geração, e os dados do relatório em formato JSON.

* **Listagem e visualização de relatórios**
    * Exibe todos os relatorios gerados com data, hora, total de horas, minutos e segundos
    * Permite visualizar o relatorio, exibindo data, hora de inicio e fim e descrição

*   **Zerar Histórico:**
    *   Permite limpar todos os registros de ponto do banco de dados (ação irreversível).
    *   Agendamento automático para zerar o histórico no primeiro dia de cada mês.

## Tecnologias Utilizadas

*   **Python 3:** Linguagem de programação principal.
*   **Flask:** Microframework web para construção da aplicação.
*   **SQLite:** Banco de dados leve e fácil de usar.
*   **HTML, CSS, JavaScript:** Para a interface web.
*   **APScheduler:** Biblioteca para agendamento de tarefas (zerar histórico mensalmente).

## Estrutura do Projeto


ponto_flask/
├── app.py # Código principal da aplicação Flask
├── database.db # Arquivo do banco de dados SQLite (criado automaticamente)
└── templates/ # Templates HTML
├── editar_ponto.html
├── index.html
├── listar.html
├── listar_relatorios.html
├── relatorio.html
└── visualizar_relatorio.html

## Configuração e Execução

1.  **Pré-requisitos:**
    *   Python 3.6+ instalado.
    *   Bibliotecas Python instaladas.

2.  **Instalação das dependências:**

    ```bash
    pip install Flask apscheduler
    ```

3.  **Execução:**

    ```bash
    python app.py
    ```

    Isso iniciará o servidor Flask (por padrão, na porta 5000).

4.  **Acesso:** Abra um navegador e acesse `http://127.0.0.1:5000/`.

## Detalhes da Implementação

*   **`app.py`:**
    *   Funções para interagir com o banco de dados (`get_db_connection`, `criar_tabelas`).
    *   Classe `Ponto` para representar um registro de ponto, com métodos para formatar data e hora.
    *   Rotas Flask para as diferentes funcionalidades (iniciar/parar ponto, listar, editar, excluir, gerar relatório, etc.).
    *   Uso de templates HTML (`templates/`) para renderizar as páginas.
    *   Tratamento de erros básicos (conexão com o banco de dados, atualização de dados).
    *   Agendamento da tarefa de zerar o histórico usando `APScheduler`.
    *   Armazenamento dos dados dos relatórios no banco, em formato JSON, para persistência.
    *   Contexto de aplicação (`with app.app_context():`) para a tarefa agendada.

*   **Banco de dados (`database.db`):**
    *   Criado automaticamente se não existir.
    *   Tabelas:
        *   `pontos`: Armazena os registros de ponto (ID, data/hora de início, data/hora de fim, descrição).
        *   `relatorios`: Armazena os relatórios gerados (ID, data de geração, dados do relatório em JSON, total de horas, minutos e segundos).

* **Templates HTML**
   * `index.html`: Página principal com a visualização do último ponto.
   * `listar.html`: Lista todos os registros.
   * `editar_ponto.html`: Edição de um ponto.
   * `relatorio.html`: Visualiza a geração do relatório por dia.
    *   `listar_relatorios.html`: Lista os relatórios gerados
    * `visualizar_relatorio.html`: Apresenta os dados de um relatório individual.

## Melhorias Futuras

*   **Interface:**
    *   Melhorar o design e a responsividade da interface (usar um framework CSS como Bootstrap).
    *   Adicionar validações no front-end (JavaScript).
    *   Implementar paginação na listagem de pontos.
    *   Adicionar gráficos para visualização dos dados do relatório.

*   **Funcionalidades:**
    *   Autenticação de usuários (login/senha).
    *   Permitir filtrar os pontos e relatórios por período (data inicial/final).
    *   Exportar relatórios para outros formatos (Excel, PDF).
    *   Notificações (por e-mail, por exemplo) sobre o início/fim da jornada.
    *   Cálculo de horas extras, faltas, etc.
    *   Suporte a múltiplas jornadas de trabalho por dia.
    *   Adicionar testes unitários e de integração.
* **Segurança:**
    * Adicionar tratamento de erros e prevenção contra ataques.

*   **Código:**
    *   Refatorar o código para melhor organização e modularidade.
    *   Usar um ORM (como SQLAlchemy) para interagir com o banco de dados de forma mais abstrata.
    *   Adicionar mais comentários e documentação (docstrings).
    * Utilizar um linter e formatador de código
*  **Outros**
    * Adicionar Docker para facilitar deploy.
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END

