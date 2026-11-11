# LinkBase

LinkBase é um aplicativo local para guardar links em categorias. Cada conta tem
sua própria biblioteca e pode criar, renomear e excluir categorias, além de
adicionar, editar e remover links.

## Recursos

- Cadastro com nome de usuário, e-mail e senha em texto puro.
- Login com nome de usuário ou e-mail.
- Categorias pessoais para organizar os links.
- Links com título, endereço e descrição, que podem ser criados, editados e excluídos.
- Página de conta para atualizar dados, trocar a senha e excluir a conta.
- Interface adaptável a celular, tablet e computador.
- Banco SQLite local.

## Requisitos

- Python 3.10 ou superior.
- `pip`.

As dependências diretas do projeto estão listadas em `requirements.txt`.

## Como executar

Abra um terminal nesta pasta e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Depois, abra <http://127.0.0.1:5000> no navegador. Na primeira execução, o
aplicativo cria o banco e as tabelas automaticamente.

Para encerrar o servidor, volte ao terminal e pressione `Ctrl+C`.

## Desenvolvimento e otimização

Durante o desenvolvimento deste projeto, houve auxílio de inteligência artificial para apoiar melhorias focadas em:

- organização da estrutura do aplicativo em Flask;
- criação e ajuste das rotas de cadastro, login, categorias e links;
- melhoria da lógica de validação de formulários e mensagens de erro;
- organização do banco de dados SQLite e das relações entre usuários, categorias e links;
- otimização da experiência de uso e da navegação entre páginas;
- revisão da arquitetura do código para deixar a manutenção mais simples e eficiente;
- reforço de boas práticas de segurança básica e controle de sessão.

Esse suporte contribuiu para deixar o sistema mais estável, mais fácil de evoluir e com melhor desempenho na gestão de contas, categorias e links.

## Banco de dados

O SQLite é criado localmente no diretório `instance`, no arquivo
`linkbase.db`. Os dados não são enviados a um serviço externo. Apagar esse
arquivo remove as contas, categorias e links guardados nele.

## Pastas principais

```text
main.py                 Rotas, modelos e regras do aplicativo
requirements.txt        Bibliotecas Python necessárias
templates/              Páginas HTML renderizadas pelo Flask
static/style.css        Estilos e regras de responsividade
instance/linkbase.db    Banco SQLite criado ao iniciar o aplicativo
```

## Observações

- As senhas são armazenadas em texto puro, conforme solicitado e seguindo o
  material-base. Não use este aplicativo com senhas reais nem o publique na
  internet.
- O servidor de desenvolvimento do Flask é destinado a testes locais, não à
  publicação na internet.
- O programa usa uma chave de sessão simples para funcionar localmente. Não
  publique o aplicativo com essa chave.
- Links salvos aceitam endereços iniciados por `http://` ou `https://`.
