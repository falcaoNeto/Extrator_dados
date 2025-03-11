# Projeto Extrator de Dados

## Descrição

Este projeto é um extrator de dados desenvolvido para coletar, processar e disponibilizar informações de diversas fontes por meio de uma API REST. A aplicação foi concebida para facilitar a integração com outros sistemas, permitindo extrair dados de forma automatizada e escalável.

## Funcionalidades

- **Extração Automatizada:** Coleta dados de fontes definidas e as armazena para processamento num banco SQLite.
- **API REST:** Disponibiliza endpoints para consulta dos dados via AgentSQL, envio de uma ou mais fotos e documentos PDF para extração.
- **BOT TELEGRAM:** Por onde a extração é feita, o bot facilita a comodidade do dia a dia para os usuários de dispositivos móveis.
- **Contêinerização com Docker:** Facilita a instalação, o deploy e a escalabilidade da aplicação.

## Rotas da API

A seguir estão descritas as rotas implementadas:

### POST `/uploadPhoto`
- **Descrição:** Rota para receber uma imagem e extrai os textos.
- - **Parâmetros:** Arquivo de imagem enviado no corpo da requisição.
- **Retorno:** Dados extraídos da imagem ou erro ao salvar.

### POST `/uploadPhotos`
- **Descrição:** Recebe múltiplas imagens e extrai os textos.
- **Parâmetros:** Arquivo de imagem enviado no corpo da requisição.
- **Retorno:** Dados extraídos das imagens ou erro ao salvar.

### POST `/uploadPhotos`
- **Descrição:** Recebe um arquivo PDF e extrai as informações contidas.
- **Parâmetros:** Arquivo de imagem enviado no corpo da requisição.
- **Retorno:** Dados extraídos das imagens ou erro ao salvar.

### POST `/response`
- **Descrição:** Envia uma mensagem para processamento pelo agente de IA.
- **Parâmetros:** JSON contendo a mensagem a ser analisada.
- **Retorno:** Resposta do agente.

> **Observação:** As rotas acima são exemplos iniciais e podem ser expandidas conforme as necessidades do projeto.

## Tecnologias Utilizadas

- **Linguagem de Programação:** (Python)
- **Framework:** (FastAPI)
- **Banco de Dados:** (SQLite)
- **Docker:** Utilizado para contêinerização.

## Como Executar o Projeto com Docker

Siga os passos abaixo para executar o projeto utilizando Docker:

1. **Clone o Repositório:**
   ```bash
   git clone https://github.com/falcaoNeto/Extrator_dados.git
   cd Extrator_dados
   ```

2. **Crie o Arquivo de Configuração (opcional):**  
   Crie um arquivo `.env` na raiz do projeto para as variáveis de ambiente:
   ```dotenv
   TOKEN=seu_token_telegram
   GOOGLE_API_KEY=seu_token_gemini
   ```

3. **Construa as Imagens Docker:**
   ```bash
   docker-compose build 
   ```

4. **Execute o Container:**
   ```bash
   docker-compose up
   ```
   A api ficará disponível na porta 8000.




