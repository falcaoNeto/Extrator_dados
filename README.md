# **Projeto Extrator de Dados**  

## **Extrator de Dados**  

Este projeto extrai dados pré-definidos pelo usuário, inicialmente de contas de água e notas fiscais.  
Os dados extraídos são armazenados em um banco de dados SQLite para análises futuras e para fornecer uma base de dados para um agente SQL, que utiliza LLM para responder perguntas de forma inteligente.  

---

## **Status do Projeto**  

🚧 Em desenvolvimento 🚧  

O projeto está em fase de desenvolvimento, com foco na adição de suporte para novos tipos de documentos e melhorias na extração de dados.  

---

## **Features**  

- ✅ **Extrair dados de uma foto de um documento**  
- ✅ **Extrair dados de várias fotos do mesmo documento**  
- ✅ **Extrair dados de um documento PDF**  
- ✅ **Responder perguntas sobre os dados armazenados no SQLite** por meio de um agente SQL que usa LLM  
- ✅ **Possibilidade de usar uma LLM local** para maior controle e privacidade  
- ✅ **Bot no Telegram:** A extração é feita pelo bot, facilitando o uso no dia a dia para usuários de dispositivos móveis.  
- ✅ **Contêinerização com Docker:** Facilita a instalação, o deploy e a escalabilidade da aplicação.  

---

## **Rotas da API**  

A seguir estão descritas as principais rotas implementadas:  

### **POST** `/uploadPhoto`  
- **Descrição:** Rota para receber uma imagem e extrair os textos.  
- **Parâmetros:** Arquivo de imagem enviado no corpo da requisição.  
- **Retorno:** Dados extraídos da imagem ou erro ao salvar.  

### **POST** `/uploadPhotos`  
- **Descrição:** Recebe múltiplas imagens e extrai os textos.  
- **Parâmetros:** Arquivo de imagem enviado no corpo da requisição.  
- **Retorno:** Dados extraídos das imagens ou erro ao salvar.  

### **POST** `/upload`  
- **Descrição:** Recebe um arquivo PDF e extrai as informações contidas.  
- **Parâmetros:** Arquivo PDF enviado no corpo da requisição.  
- **Retorno:** Dados extraídos do PDF ou erro ao salvar.  

### **POST** `/response`  
- **Descrição:** Envia uma mensagem para processamento pelo agente de IA.  
- **Parâmetros:** JSON contendo a mensagem a ser analisada.  
- **Retorno:** Resposta do agente.  

> **Observação:** As rotas acima são exemplos iniciais e podem ser expandidas conforme as necessidades do projeto.  

---

## **Tecnologias Utilizadas**  

O projeto foi desenvolvido com as seguintes tecnologias:  

- 🐍 **Python** – Linguagem principal do projeto  
- ⚡ **FastAPI** – Framework para o backend  
- 📄 **Docling** – Biblioteca para extração de texto de documentos PDF  
- 🔗 **LangChain** – Integração com LLMs para processamento de linguagem natural  
- 📢 **Python TelegramBot** – Biblioteca para integração com o Telegram  
- 🗄 **SQLite** – Banco de dados local para armazenar os dados extraídos  
- 🐳 **Docker** – Utilizado para contêinerização  

---

## **Como Rodar com uma LLM Local**  

Para o projeto, foi usado o **llama3.1:latest**.  

### **Passos para Configuração**  

1. **Baixe o Ollama para o seu sistema operacional:**  
   [Download Ollama](https://www.ollama.com/download)  

2. **Escolha o modelo a ser baixado:**  
   [Modelos disponíveis](https://www.ollama.com/library/llama3.1)  

3. **Baixe o modelo executando o comando:**  
   ```bash
   ollama pull llama3.1
   ```  

4. **Configure a LLM no código:**  
   ```python
   llm = LLM()
   llm.llm_instance("ollama")
   ```  

> **Atenção:** A qualidade da extração dos dados depende do modelo baixado.  
> **Atenção:** A extração de texto em imagens foi testada somente com o **Gemini**. É possível usar um modelo mais robusto.  

---

## **Como Executar o Projeto com Docker**  

Para rodar a aplicação, é necessário ter o **Docker** instalado. Não é necessário instalar outras dependências manualmente, pois o **Docker Compose** será usado para orquestrar a aplicação e suas dependências automaticamente.  

### **Passos para Execução**  

1. **Clone o Repositório:**  
   ```bash
   git clone https://github.com/falcaoNeto/Extrator_dados.git
   cd Extrator_dados
   ```  

2. **Crie o Arquivo de Configuração:**  
   Crie um arquivo `.env` na raiz do projeto para armazenar as variáveis de ambiente:  
   ```dotenv
   TOKEN=seu_token_telegram
   GOOGLE_API_KEY=seu_token_gemini
   ```  

3. **Construa as Imagens Docker:**  
   1. Certifique-se de que o **Docker** e o **Docker Compose** estão instalados.  
   2. No terminal, navegue até o diretório do projeto.  
   3. Execute o seguinte comando para construir a imagem:  
      ```bash
      docker-compose build
      ```  

4. **Execute o Container:**  
   ```bash
   docker-compose up
   ```  
   A API ficará disponível na porta **8000**.  

---

## **Atenção: Configuração para exposição da API**  

Para que o bot do Telegram envie requisições para a API, é necessário expô-la na internet na porta **8000**. Para isso, utilize o **ngrok**:  

1. **Execute o comando no terminal:**  
   ```bash
   ngrok http 8000
   ```  
- A API ficará exposta na porta 8000. 

---

## **Arquitetura do Projeto**  

O projeto segue o padrão **MVC (Model-View-Controller)**, organizado da seguinte forma:  

### **Model (Modelo)**  
- Contém as regras de negócio e as classes principais, como:  
  - `NotaFiscal`  
  - `ContaAgua`  
  - `ExtrairFoto`  
  - `LLM`  
  - Entre outras relacionadas à extração e processamento de dados  

### **View (Visão)**  
- Responsável pela interação com o usuário  
- Implementada via **bot do Telegram**, que serve como interface para acessar os dados extraídos  

### **Controller (Controle)**  
- Implementado com **FastAPI**, que gerencia as requisições e a lógica de controle  
- Define os endpoints e orquestra a extração e consulta de dados  

