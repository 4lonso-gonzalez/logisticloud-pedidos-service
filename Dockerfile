# Etapa 1: Construcción y validación de dependencias
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Etapa 2: Imagen final liviana para producción
FROM python:3.11-slim
WORKDIR /app

# Usuario no-root por seguridad
RUN useradd -m appuser
COPY --from=builder /install /usr/local
COPY ./app ./app

USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]