FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -ms /bin/bash newuser
# Nadajemy nowemu użytkownikowi prawa do folderu /app, żeby mógł tu zapisać CSV
RUN chown newuser:newuser /app 

# Kopiujemy OBA pliki (skrypt i konfigurację)
COPY --chown=newuser:newuser main.py config.json ./

USER newuser

CMD ["python", "-u", "main.py"]