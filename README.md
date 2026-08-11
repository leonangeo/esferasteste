# Guia do Projeto: Versionamento e Deploy

## 0. Requisitos
Instalar Python, Git, Vscode.
Criar conta no Github, e baixar aplicativo github (windows, mac, linux).
Login no Github local.
Ver tutoriais se necessário, é fácil.
* **Teste** Crie uma pasta chamada 'PROJETO' na área de trabalho -> Botão direito do mouse -> Abrir no terminal -> Digite 'python --version' e tecle enter (deve mostrar a versão instalada do python) -> Digite 'python' (deve mudar o terminal, com duas setas >> quer dizer que está rodando python) -> Digite 'print("ooi")' e tecle enter (deve responder ooi, se sim tudo certo).
* **Se o teste falhou** pesquise como instalar e rodar python.

## 1. Conceitos Básicos (Visão Geral)
* **Git:** Ferramenta que salva o histórico do código. Funciona como um "desfazer/ctrl+Z" que você pode voltar em qualquer ponto anterior.
* **GitHub:** Plataforma em nuvem que guarda o histórico do Git para acesso remoto.
* **Streamlit:** Servidor que lê o código Python e o transforma em uma página web interativa, como um site simples.
* **Fluxo de Deploy:** O desenvolvedor escreve o código, salva no Git e envia para o GitHub. O Streamlit monitora o GitHub e atualiza a aplicação em produção automaticamente a cada envio.

## 2. Configuração do Ambiente Virtual (`venv`)
O `venv` isola as bibliotecas do projeto. O `requirements.txt` avisa ao Streamlit quais bibliotecas instalar no servidor. Abra o terminal na pasta do projeto e execute:

```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
pip install streamlit
pip freeze > requirements.txt
```

## 3. Versionamento Prático (Git)
Inicie o rastreamento do projeto:
```bash
git init
```

### Passo 1: Commit Inicial (Olá Mundo)
Crie o arquivo `main.py`:
```python
import streamlit as st

st.write("Ola mundo")
```
Salve a versão:
```bash
git add .
git commit -m "feat: commit inicial com ola mundo"
```

### Passo 2: Nova Funcionalidade (Contagem até 10)
Edite o `main.py`:
```python
import streamlit as st

st.write("Ola mundo")

for i in range(1, 11):
    st.write(i)
```
Salve a versão:
```bash
git add .
git commit -m "feat: adiciona laco de contagem ate 10"
```

### Passo 3: Nova Funcionalidade (Importação e Matemática)
Edite o `main.py`:
```python
import streamlit as st
import math

st.write("Ola mundo")

for i in range(1, 11):
    st.write(i)

pi_arredondado = round(math.pi, 2)
st.write(f"Valor de Pi arredondado: {pi_arredondado}")
```
Salve a versão:
```bash
git add .
git commit -m "feat: adiciona importacao e arredondamento de pi"
```

## 4. Execução Local
Para testar o aplicativo localmente antes de enviar para produção:
```bash
streamlit run main.py
```

## 5. Navegação no Histórico (Reversão de Código)
Para ver o histórico de salvamentos e os hashes (IDs dos commits):
```bash
git log --oneline
```
Saída esperada:
```text
c3d4e5f feat: adiciona importacao e arredondamento de pi
b2c3d4e feat: adiciona laco de contagem ate 10
a1b2c3d feat: commit inicial com ola mundo
```

Para **voltar** no tempo e testar o código da primeira versão ("Olá mundo"):
```bash
git checkout a1b2c3d
```

Para **retornar** à versão mais recente e atual com todas as features:
```bash
git checkout main
```

## 6. Deploy (Atualização em Produção)
Vincule a pasta local ao GitHub e envie o código:
```bash
git remote add origin <URL_DO_SEU_REPOSITORIO_NO_GITHUB>
git push -u origin main
```
Após o `git push`, o Streamlit detecta a alteração no GitHub, lê o `requirements.txt` e atualiza a aplicação no ar de forma 100% automática.

## 7. Como Continuar o Projeto (Para Novos Desenvolvedores)

Se você vai dar continuidade ao projeto, o primeiro passo é baixar o código que já está no GitHub para o seu computador, fazer as alterações e enviá-las de volta.

### Passo 1: Baixar o Projeto (Clone)
Abra o terminal, navegue até a pasta onde deseja guardar o projeto e execute o comando abaixo para copiar o repositório:
```bash
git clone <URL_DO_SEU_REPOSITORIO_NO_GITHUB>
```
Em seguida, entre na pasta do projeto que acabou de ser criada (substitua pelo nome real da pasta):
```bash
cd <NOME_DA_PASTA_DO_PROJETO>
```

### Passo 2: Preparar o Ambiente
Crie e ative o ambiente virtual para instalar as bibliotecas que o projeto já utiliza:
```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### Passo 3: Fazer as Alterações
Abra o arquivo `main.py` no seu editor, faça as mudanças necessárias e salve. Exemplo de nova adição:
```python
# Código existente acima...
st.write("Nova funcionalidade adicionada pelo novo desenvolvedor!")
```

### Passo 4: Salvar e Subir o Código (Commit e Push)
Com as alterações feitas, registre as mudanças no Git e envie para o GitHub:

1. Prepare os arquivos modificados:
```bash
git add .
```

2. Crie o ponto de salvamento com uma mensagem descritiva:
```bash
git commit -m "feat: adiciona nova mensagem na tela principal"
```

3. Envie as alterações para o repositório online:
```bash
git push
```

**Pronto!** Após o `git push`, o Streamlit detectará a mudança no GitHub e atualizará a aplicação em produção automaticamente, seguindo o mesmo fluxo já configurado.
