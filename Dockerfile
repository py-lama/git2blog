# Dockerfile
FROM python:3.11-slim

# Ustawienia
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Zainstaluj Git
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY git2blog.py .
COPY templates/ templates/
COPY examples/ examples/

# Utwórz katalogi robocze
RUN mkdir -p /workspace /app/blog

# Port dla prostego serwera HTTP (opcjonalnie)
EXPOSE 8000

# Entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["--help"]

---

# docker-entrypoint.sh
#!/bin/bash
set -e

# Funkcja pomocy
show_help() {
    echo "git2blog Docker Container"
    echo ""
    echo "Użycie:"
    echo "  docker run -v /ścieżka/do/repo:/workspace git2blog [opcje]"
    echo ""
    echo "Opcje:"
    echo "  --help          Pokaż pomoc"
    echo "  --init          Utwórz domyślną konfigurację"
    echo "  --generate      Wygeneruj blog (domyślne)"
    echo "  --serve         Wygeneruj blog i uruchom serwer"
    echo "  --demo          Utwórz przykładowy projekt i blog"
    echo ""
    echo "Przykłady:"
    echo "  # Wygeneruj blog z lokalnego repo"
    echo "  docker run -v \$PWD:/workspace git2blog --generate"
    echo ""
    echo "  # Utwórz konfigurację"
    echo "  docker run -v \$PWD:/workspace git2blog --init"
    echo ""
    echo "  # Wygeneruj i uruchom serwer"
    echo "  docker run -p 8000:8000 -v \$PWD:/workspace git2blog --serve"
}

# Sprawdź czy Ollama jest dostępna
check_ollama() {
    echo "🤖 Sprawdzam połączenie z Ollama..."
    if curl -s http://host.docker.internal:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama dostępna"
        return 0
    elif curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama dostępna (service)"
        return 0
    else
        echo "❌ Ollama niedostępna!"
        echo "   Uruchom: ollama serve"
        echo "   Lub użyj docker-compose.yml z usługą Ollama"
        return 1
    fi
}

# Przejdź do workspace
cd /workspace

case "$1" in
    --help)
        show_help
        ;;
    --init)
        echo "📝 Tworzę domyślną konfigurację..."
        python /app/git2blog.py --init
        echo "✅ Konfiguracja utworzona w git2blog.yaml"
        ;;
    --generate)
        check_ollama
        echo "🚀 Generuję blog..."
        python /app/git2blog.py
        echo "✅ Blog wygenerowany w katalogu blog/"
        ;;
    --serve)
        check_ollama
        echo "🚀 Generuję blog..."
        python /app/git2blog.py
        echo "🌐 Uruchamiam serwer HTTP na porcie 8000..."
        cd blog
        python -m http.server 8000 --bind 0.0.0.0
        ;;
    --demo)
        echo "🎬 Tworzę demo..."
        # Utwórz przykładowe repo jeśli nie istnieje
        if [ ! -d ".git" ]; then
            git init .
            git config user.name "Demo User"
            git config user.email "demo@git2blog.local"
            echo "# Demo Project\nProjekt demonstracyjny git2blog" > README.md
            git add README.md
            git commit -m "Initial commit z README"
            echo "print('Hello from git2blog demo!')" > app.py
            git add app.py
            git commit -m "Dodaj główny plik aplikacji"
            echo "## Funkcje\n- Automatyczne generowanie bloga\n- Integracja z AI" >> README.md
            git add README.md
            git commit -m "Rozszerz dokumentację projektu"
        fi

        # Utwórz konfigurację
        python /app/git2blog.py --init

        # Sprawdź Ollama i wygeneruj
        if check_ollama; then
            python /app/git2blog.py
            echo "🌐 Uruchamiam serwer demo na porcie 8000..."
            cd blog
            python -m http.server 8000 --bind 0.0.0.0
        else
            echo "⚠️ Demo bez AI - używam przykładowych danych"
            # Tutaj można dodać fallback z przykładowymi postami
        fi
        ;;
    *)
        # Domyślnie generuj blog
        check_ollama
        python /app/git2blog.py "$@"
        ;;
esac

---

# docker-compose.yml
version: '3.8'

services:
  git2blog:
    build: .
    volumes:
      - .:/workspace
      - ./blog:/app/blog
    ports:
      - "8000:8000"
    depends_on:
      - ollama
    environment:
      - OLLAMA_URL=http://ollama:11434
    command: --serve

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=24h
    command: >
      sh -c "ollama serve &
             sleep 10 &&
             ollama pull llama3.2 &&
             wait"

volumes:
  ollama_data:

---

# .dockerignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Git2blog output
blog/
generated/
output/

# Local configs
*.local.yaml
config.local.yaml