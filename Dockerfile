# Dockerfile — Container para o Rastreador de Preços de Criptomoedas
# =====================================================
# Imagem base oficial do Python (slim = mais leve que a full)
# Python 3.11 + apenas as libs essenciais do Debian
FROM python:3.11-slim

# Evita que o Python crie arquivos .pyc desnecessários e
# força o buffer de saída para stdout (necessário para ver
# logs em containers)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia o requirements.txt separadamente primeiro para
# aproveitar o cache de camadas do Docker (o download das
# dependências só será refeito se o requirements mudar)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o script do rastreador para dentro do container
COPY price_tracker.py .

# Executa o script automaticamente ao iniciar o container
# (ENTRYPOINT em vez de CMD para garantir que o script
# sempre rode, mesmo se argumentos forem passados)
ENTRYPOINT ["python", "price_tracker.py"]
