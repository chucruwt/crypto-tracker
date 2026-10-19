#!/usr/bin/env python3
"""
Rastreador de Preços de Criptomoedas
=====================================
Script que consulta a API pública e gratuita da CoinGecko para obter:
  - Preço atual de BTC, ETH e SOL em USD e BRL
  - Variação percentual nas últimas 24 horas

Requisitos atendidos:
  1. Requisição HTTP via API CoinGecko /simple/price
  2. Tratamento robusto de exceções (rede, timeout, rate limit)
  3. Cores ANSI para variação 24h (verde = positivo, vermelho = negativo)
  4. Tabela formatada manualmente (sem pandas / tabulate / rich)
"""

import requests

# --- Configurações da API CoinGecko -------------------------------------------

# A documentação oficial indica o endpoint base:
#   https://api.coingecko.com/api/v3/
#
# O endpoint /simple/price retorna o preço atual de uma ou mais moedas
# conforme consultado por ID. Sua estrutura de URL é:
#
#   https://api.coingecko.com/api/v3/simple/price
#       ?ids=<comma-separated coin ids>
#       &vs_currencies=<comma-separated fiat codes>
#       &include_24hr_change=true
#
# Parêmtros:
#   ids                    : identificadores das moedas (bitcoin,ethereum,solana)
#   vs_currencies          : moedas fiat de referência (usd,brl)
#   include_24hr_change    : inclui a variação % de 24h no resultado
#
# Exemplo de URL completa usada neste script:
#   https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,brl&include_24hr_change=true
#
# Nota sobre a parametrização:
#   - O parametro correto na API atual é `include_24hr_change` (e não
#     `include_24hr_price_change`, que era usado por endpoints onchain
#     específicos).
#   - Quando ativado, a API inclui as chaves `usd_24h_change` e
#     `brl_24h_change` no JSON retornado, contendo a variação percentual
#     de 24h para cada moeda fiat.
API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Identificadores reconhecidos pela CoinGecko (não são tickers, são IDs)
COIN_IDS = ["bitcoin", "ethereum", "solana"]

# Símbolos amigáveis para exibição na tabela
COIN_SYMBOLS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}

# Moedas fiat para conversão
VS_CURRENCIES = ["usd", "brl"]

# Timeout (segundos) para evitar que o script fique bloqueado indefinidamente
REQUEST_TIMEOUT = 15


# --- Códigos de cores ANSI ----------------------------------------------------

class Colors:
    """Códigos de escape ANSI para colorir a saída no terminal."""
    GREEN = "\033[92m"   # positivo
    RED = "\033[91m"     # negativo
    RESET = "\033[0m"    # restaura a cor padrão


# --- Funções auxiliares -------------------------------------------------------

def build_url():
    """Constrói a URL da API com os parâmetros de consulta."""
    ids_param = ",".join(COIN_IDS)
    vs_param = ",".join(VS_CURRENCIES)
    url = (
        f"{API_URL}?ids={ids_param}"
        f"&vs_currencies={vs_param}"
        f"&include_24hr_change=true"
    )
    return url


def fetch_prices():
    """
    Executa a chamada HTTP GET à API da CoinGecko.

    Retorna:
        dict | None : o JSON decodificado, ou None em caso de falha.

    Tratamento de exceções:
        - requests.exceptions.Timeout       : servidor não respondeu a tempo
        - requests.exceptions.ConnectionError: falha de rede / DNS / conexão
        - requests.exceptions.HTTPError      : código de status HTTP inesperado
        - requests.exceptions.RequestException: categoria-mãe de todas as falhas
          (captura qualquer outro erro da biblioteca requests)
    """
    url = build_url()
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        # raise_for_status() dispara HTTPError para respostas 4xx/5xx
        # (ex.: 429 = rate limit excedido)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}Erro: a requisição excedeu o tempo limite de "
              f"{REQUEST_TIMEOUT}s.{Colors.RESET}")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}Erro: falha de conexão. Verifique sua conexão "
              f"de rede.{Colors.RESET}")
    except requests.exceptions.HTTPError as http_err:
        # O código 429 é o rate-limit da CoinGecko (sem chave, limite livre)
        if response.status_code == 429:
            print(f"{Colors.RED}Erro: limite de requisições (rate limit) da "
                  f"API da CoinGecko excedido. Tente novamente em alguns "
                  f"segundos.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Erro HTTP {response.status_code}: "
                  f"{http_err}{Colors.RESET}")
    except requests.exceptions.RequestException as e:
        # Categoria genérica — captura qualquer outro erro da requests
        print(f"{Colors.RED}Erro na requisição: {e}{Colors.RESET}")
    return None


def format_price(value, currency):
    """
    Formata um valor numérico como string monetária.

    Para BRL:  prefere símbolo R$ e separador decimal ','.
    Para USD:  prefere símbolo $ e separador decimal '.'.
    """
    if currency == "usd":
        return f"$ {value:,.2f}"
    elif currency == "brl":
        # Formata com ponto como milhar e vírgula como decimal
        s = f"R$ {value:,.2f}"
        # A formatação padrão usa . para milhar e , para decimal;
        # aqui invertemos para o padrão brasileiro
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    return str(value)


def format_change(value):
    """
    Formata a variação percentual com cor ANSI.

    Positivo  -> verde (com sinal +)
    Negativo  -> vermelho (com sinal -)
    Zero      -> sem cor (com sinal +)
    """
    if value > 0:
        return (f"{Colors.GREEN}+{value:.2f}%{Colors.RESET}")
    elif value < 0:
        return (f"{Colors.RED}{value:.2f}%{Colors.RESET}")
    else:
        return f"+{value:.2f}%"


def print_table(data):
    """
    Exibe os dados em formato de tabela alinhada manualmente.

    A lógica de alinhamento usa str.ljust() / str.rjust() para garantir
    que as colunas fiquem uniformes, independentemente do conteúdo.
    Nenhuma biblioteca externa de formatação é utilizada.

    Estrutura do JSON retornado pela CoinGecko:

        {
          "bitcoin": {
            "usd": 81941.0,
            "brl": 412443.0,
            "usd_24h_change": 1.43,
            "brl_24h_change": 0.85
          },
          "ethereum": { ... },
          "solana":   { ... }
        }

    Cada chave de moeda contém, para cada moeda fiat:
      - "<fiat>"              : preço atual
      - "<fiat>_24h_change"    : variação percentual 24h
    """
    if data is None:
        print("Nenhum dado para exibir.")
        return

    # Cabeçalho da tabela
    header = f"{'Moeda':<10} {'Preço (USD)':<18} {'Preço (BRL)':<18} {'Var. 24h':<12}"
    print(header)
    print("-" * len(header))

    for coin_id in COIN_IDS:
        symbol = COIN_SYMBOLS.get(coin_id, coin_id.upper())
        coin_data = data.get(coin_id, {})

        # Desmembra o JSON acessando as chaves individuais.
        # Exemplo: data["bitcoin"]["usd"], data["bitcoin"]["brl"],
        #           data["bitcoin"]["usd_24h_change"]
        price_usd = coin_data.get("usd")
        price_brl = coin_data.get("brl")
        change_usd = coin_data.get("usd_24h_change")
        change_brl = coin_data.get("brl_24h_change")

        # Se alguma chave está ausente, o coin pode ser inválido
        if price_usd is None or price_brl is None:
            print(f"{symbol:<10} {'(não disponível)':<18} "
                  f"{'(não disponível)':<18} {'(n/a)':<12}")
            continue

        usd_str = format_price(price_usd, "usd").ljust(18)
        brl_str = format_price(price_brl, "brl").ljust(18)

        # A variação percentual é a mesma para USD e BRL (baseada no preço
        # da moeda em relação àquela fiat). Usamos o valor de BRL para
        # exibição principal, colorido conforme positivo/negativo.
        change_str = format_change(change_brl) if change_brl is not None else "N/A"

        print(f"{symbol:<10} {usd_str} {brl_str} {change_str}")

    print()  # linha em branco final


# --- Programa principal -------------------------------------------------------

def main():
    print("=" * 54)
    print("  RASTREADOR DE PREÇOS — CoinGecko API")
    print("=" * 54)
    print()

    data = fetch_prices()

    if data is not None:
        print_table(data)
    else:
        print(f"{Colors.RED} Não foi possível obter os dados. "
              f"Tente novamente mais tarde.{Colors.RESET}")


if __name__ == "__main__":
    main()
