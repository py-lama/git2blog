# git2blog

Generator bloga z historii Git używający lokalnego modelu Ollama LLM.

## Funkcje

- 🤖 **AI-powered**: Używa Ollama do generowania interesujących postów z commitów Git
- 📝 **Automatyczna konwersja**: Przekształca suche commity w angażujące posty blogowe
- 🎨 **Gotowe szablony**: Generuje kompletny blog HTML gotowy do publikacji
- ⚙️ **Konfigurowalne**: Pełna personalizacja przez plik YAML
- 🔍 **Inteligentne filtrowanie**: Pomija merge commity i spam
- 🌍 **Polski interface**: Wszystko po polsku

## Wymagania

1. **Python 3.7+**
2. **Git** - repozytorium z historią commitów
3. **Ollama** - lokalny serwer LLM
   ```bash
   # Instalacja Ollama (Linux/macOS)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Uruchom model (np. llama3.2)
   ollama run llama3.2
   ```

## Instalacja

1. **Sklonuj/pobierz projekt**:
   ```bash
   mkdir git2blog && cd git2blog
   # Skopiuj git2blog.py do tego katalogu
   ```

2. **Zainstaluj zależności**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Utwórz konfigurację**:
   ```bash
   python git2blog.py --init
   ```

## Użycie

1. **Przejdź do swojego repozytorium Git**:
   ```bash
   cd /ścieżka/do/twojego/projektu
   ```

2. **Uruchom generator**:
   ```bash
   python /ścieżka/do/git2blog.py
   ```

3. **Otwórz wygenerowany blog**:
   ```bash
   open blog/index.html
   ```

## Konfiguracja

Edytuj `git2blog.yaml` aby dostosować:

```yaml
# Ollama settings
ollama_url: 'http://localhost:11434'
model: 'llama3.2'  # lub codellama, mistral, itp.
timeout: 120  # (opcjonalnie) czas oczekiwania na odpowiedź Ollama w sekundach

# Blog settings
blog_title: 'Mój Blog Projektowy'
blog_description: 'Blog generowany automatycznie z historii Git'
author: 'Twoje Imię'
output_dir: 'blog'

# Generation settings
commit_limit: 50              # Ile commitów przetworzyć
posts_per_page: 10           # Posty na stronę (przyszła funkcja)
ignore_merge_commits: true   # Pomijaj merge commity
```

## Nowości

- Domyślny timeout zapytań do Ollama został zwiększony do **120 sekund** (wcześniej 30s). Jeśli generacja posta trwa dłużej, nie przerywaj procesu od razu – większe modele mogą potrzebować więcej czasu.

## Przykładowe użycie

```bash
# W katalogu z twoim projektem Git
cd ~/moje-projekty/awesome-app

# Wygeneruj blog (domyślna konfiguracja)
python ~/git2blog/git2blog.py

# Użyj własnej konfiguracji
python ~/git2blog/git2blog.py --config custom-config.yaml

# Blog zostanie utworzony w katalogu ./blog/
ls blog/
# index.html  post_1.html  post_2.html  ...
```

## Struktura wyjściowa

```
blog/
├── index.html      # Strona główna z listą postów
├── post_1.html     # Najnowszy commit jako post
├── post_2.html     # Drugi commit
└── ...
```

## Dostępne modele Ollama

Popularne modele do wyboru:
- `llama3.2` - Szybki i dobry (domyślny)
- `codellama` - Specjalizuje się w kodzie
- `mistral` - Mały i efektywny
- `gemma` - Od Google

Zmień model w `git2blog.yaml`:
```yaml
model: 'codellama'
```

## Troubleshooting

### ❌ "Nie można połączyć się z Ollama"
```bash
# Sprawdź czy Ollama działa
curl http://localhost:11434/api/tags

# Jeśli nie, uruchom:
ollama serve
```

### ❌ "Nie znajdujesz się w repozytorium Git"
```bash
# Upewnij się że jesteś w katalogu z .git
ls -la | grep .git
```

### ❌ "Nie znaleziono żadnych commitów"
```bash
# Sprawdź historię Git
git log --oneline -10
```

### ❌ "Timeout podczas generowania posta lub długi czas oczekiwania"
Zwiększono domyślny timeout do 120 sekund. Jeśli nadal pojawia się timeout, sprawdź czy Twój model Ollama nie wymaga jeszcze więcej czasu lub zasobów.

Możesz też ustawić własny timeout (w pliku konfiguracyjnym lub przez zmienną środowiskową, jeśli obsługiwane):
```yaml
timeout: 180
```
lub:
```bash
export OLLAMA_TIMEOUT=180
```

## Planowane funkcje

- [ ] Obsługa markdown zamiast HTML
- [ ] Paginacja dla dużych blogów  
- [ ] Kategorie i tagi na podstawie ścieżek plików
- [ ] RSS feed
- [ ] Ciemny motyw
- [ ] Export do platform blogowych

## Licencja

Licencja: [Apache 2.0](LICENSE)

## Autor

Tom Sapletta — DevOps Engineer & Systems Architect