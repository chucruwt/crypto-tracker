# 📈 Crypto Tracker CLI

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![API](https://img.shields.io/badge/API-CoinGecko-yellow.svg)

Um utilitário de linha de comando (CLI) rápido, resiliente e minimalista para rastreamento de criptomoedas em tempo real. Desenvolvido em Python puro (com suporte total a Docker), este script consome a API pública da CoinGecko para exibir as cotações atuais e variações de 24 horas das principais criptomoedas do mercado.

---

## ✨ Funcionalidades Principais

- **Multi-Moeda:** Retorna cotações simultâneas em Dólares (USD) e Reais (BRL).
- **Sem Dependências Visuais:** Renderização de tabelas e cores ANSI (verde/vermelho para variações) feitas 100% com código nativo (manipulação de strings), sem depender de bibliotecas como `pandas` ou `tabulate`.
- **Resiliência de Rede:** Tratamento robusto de exceções (`Timeout`, `ConnectionError`, `HTTPError`), incluindo captura amigável para o limite de requisições (*Rate Limit* - código 429) da CoinGecko.
- **Containerizado:** Pronto para ser executado em qualquer ambiente isolado via Docker, sem necessidade de instalar dependências na máquina host.

---

## 🚀 Como Executar (Recomendado: Docker)

A maneira mais limpa de testar a aplicação é utilizando o Docker. Isso garante que o seu ambiente Python global não seja afetado.

### Pré-requisitos
- [Docker](https://www.docker.com/get-started) (Daemon em execução)
- Git

### Passos
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU_USUARIO/crypto-tracker.git
   cd crypto-tracker
   ```

2. **Faça o build da imagem:**
   ```bash
   docker build -t crypto-tracker .
   ```

3. **Execute o container:**
   ```bash
   docker run --rm crypto-tracker
   ```
   *(A flag `--rm` garante que o container seja deletado automaticamente após exibir a tabela, economizando espaço em disco).*

---

## 💻 Como Executar (Local / Nativamente)

Se preferir rodar o código diretamente na sua máquina, certifique-se de ter o Python 3.11+ instalado.

1. **Clone o repositório e acesse a pasta:**
   ```bash
   git clone https://github.com/SEU_USUARIO/crypto-tracker.git
   cd crypto-tracker
   ```

2. **Crie e ative um ambiente virtual (Opcional, porém recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o script:**
   ```bash
   python price_tracker.py
   ```

---

## 📂 Estrutura do Projeto

```text
crypto-tracker/
├── Dockerfile            # Receita de infraestrutura (Python slim, cache de dependências)
├── price_tracker.py      # Script principal com a lógica da API e renderização
├── requirements.txt      # Dependências fixadas (apenas 'requests')
└── README.md             # Esta documentação
```

---

## ⚠️ Notas sobre a API

Este projeto utiliza o *Free Tier* (camada gratuita) do [CoinGecko API v3](https://docs.coingecko.com/reference/explore-api-v3). 
* Não é necessária a utilização de chaves de autenticação (*API Keys*).
* A API gratuita possui um limite rigoroso de requisições por minuto. Caso execute o script múltiplas vezes em rápida sucessão, o programa identificará o erro `HTTP 429` e o alertará amigavelmente.

---

## 📝 Licença

Desenvolvido para fins educacionais e de portfólio. Sinta-se livre para clonar, modificar e utilizar o código conforme necessário sob a licença MIT.
