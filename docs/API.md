# git2blog API Documentation

Dokumentacja API i wewnętrznych funkcji git2blog.

## Klasa Git2Blog

### `__init__(config_path: str = "git2blog.yaml")`

Inicjalizuje instancję Git2Blog z konfiguracją z pliku YAML.

**Parametry:**
- `config_path` - ścieżka do pliku konfiguracyjnego

**Przykład:**
```python
from git2blog import Git2Blog

# Domyślna konfiguracja
git2blog = Git2Blog()

# Własny plik konfiguracji
git2blog = Git2Blog("custom-config.yaml")
```

### `load_config(config_path: str) -> Dict[str, Any]`

Wczytuje konfigurację z pliku YAML.

**Zwraca:** Słownik z konfiguracją lub pusty słownik jeśli plik nie istnieje.

### `create_default_config()`

Tworzy domyślny plik konfiguracyjny `git2blog.yaml`.

**Przykład:**
```python
git2blog = Git2Blog()
git2blog.create_default_config()
```

### `get_git_commits(limit: int = 50) -> List[Dict[str, str]]`

Pobiera listę commitów z lokalnego repozytorium Git.

**Parametry:**
- `limit` - maksymalna liczba commitów

**Zwraca:** Lista słowników z danymi commitów:
```python
[
    {
        'hash': 'abc123...',
        'author': 'Jan Kowalski',
        'email': 'jan@example.com', 
        'date': '2025-01-15 10:30:00',
        'subject': 'Tytuł commita',
        'body': 'Opis commita'
    }
]
```

### `call_ollama(prompt: str) -> str`

Wywołuje Ollama API z podanym promptem.

**Parametry:**
- `prompt` - tekst promptu dla AI

**Zwraca:** Wygenerowana odpowiedź lub pusty string w przypadku błędu.

**Przykład:**
```python
response = git2blog.call_ollama("Napisz post o commicie: dodaj funkcję X")
```

### `generate_blog_post(commit: Dict[str, str]) -> Dict[str, str]`

Generuje post blogowy z pojedynczego commita używając AI.

**Parametry:**
- `commit` - słownik z danymi commita

**Zwraca:** Słownik z wygenerowanym postem:
```python
{
    'title': 'Tytuł posta',
    'content': 'Treść posta...',
    'date': '2025-01-15 10:30:00',
    'author': 'Autor',
    'commit_hash': 'abc123'
}
```

### `create_html_post(post: Dict[str, str]) -> str`

Tworzy kompletny HTML dla pojedynczego posta.

**Parametry:**
- `post` - słownik z danymi posta

**Zwraca:** String z kompletnym kodem HTML.

### `create_index_page(posts: List[Dict[str, str]]) -> str`

Tworzy stronę główną bloga z listą wszystkich postów.

**Parametry:**
- `posts` - lista postów

**Zwraca:** String z kodem HTML strony głównej.

### `generate_blog()`

Główna funkcja generująca kompletny blog.

Wykonuje pełny workflow:
1. Sprawdza repozytorium Git
2. Testuje połączenie z Ollama
3. Pobiera commity
4. Generuje posty używając AI
5. Tworzy pliki HTML
6. Zapisuje na dysk

## Konfiguracja

### Struktura pliku YAML

```yaml
# Ustawienia Ollama
ollama_url: 'http://localhost:11434'
model: 'llama3.2'

# Ustawienia bloga
blog_title: 'Tytuł bloga'
blog_description: 'Opis bloga'
author: 'Autor'
output_dir: 'blog'

# Generowanie
commit_limit: 50
ignore_merge_commits: true
ignore_patterns:
  - '^WIP:'
  - '^TODO:'

# Motyw
theme:
  primary_color: '#2563eb'
  background_color: '#ffffff'
```

### Dostępne opcje konfiguracji

#### Ollama
- `ollama_url` - URL serwera Ollama (domyślnie `http://localhost:11434`)
- `model` - model AI do użycia (`llama3.2`, `codellama`, `mistral`, `gemma`)

#### Blog
- `blog_title` - tytuł bloga
- `blog_description` - opis bloga  
- `author` - autor bloga
- `output_dir` - katalog wyjściowy (domyślnie `blog`)
- `template_dir` - katalog z szablonami

#### Generowanie
- `commit_limit` - maksymalna liczba commitów (domyślnie 50)
- `posts_per_page` - posty na stronę (przyszła funkcja)
- `ignore_merge_commits` - pomijaj merge commity (domyślnie `true`)
- `ignore_empty_commits` - pomijaj puste commity
- `ignore_patterns` - lista wzorców regex do pomijania
- `min_commit_length` - minimalna długość opisu commita

#### AI
- `ai_instructions` - dodatkowe instrukcje dla AI
- `max_post_length` - maksymalna długość posta w słowach

## CLI Interface

### Argumenty linii komend

```bash
git2blog [opcje]
```

**Opcje:**
- `--init` - utwórz domyślną konfigurację
- `--config PATH` - użyj konkretnego pliku konfiguracji
- `--help` - pokaż pomoc

**Przykłady:**
```bash
# Utwórz konfigurację
git2blog --init

# Wygeneruj blog z domyślną konfiguracją
git2blog

# Użyj własnej konfiguracji
git2blog --config my-config.yaml
```

## API Ollama

git2blog komunikuje się z Ollama przez REST API.

### Endpoint: `/api/generate`

**Request:**
```json
{
  "model": "llama3.2",
  "prompt": "Tekst promptu...",
  "stream": false
}
```

**Response:**
```json
{
  "response": "Wygenerowana odpowiedź...",
  "done": true
}
```

### Sprawdzanie dostępnych modeli

**Endpoint:** `/api/tags`

**Response:**
```json
{
  "models": [
    {
      "name": "llama3.2:latest",
      "modified_at": "2025-01-15T10:30:00Z",
      "size": 1234567890
    }
  ]
}
```

## Obsługa błędów

### Typowe błędy i rozwiązania

#### `Git error: not a git repository`
**Przyczyna:** Skrypt nie jest uruchomiony w repozytorium Git  
**Rozwiązanie:** Przejdź do katalogu z `.git` lub wykonaj `git init`

#### `Nie można połączyć się z Ollama`
**Przyczyna:** Ollama nie jest uruchomiona  
**Rozwiązanie:** `ollama serve` lub sprawdź URL w konfiguracji

#### `Model not found`
**Przyczyna:** Wybrany model nie jest zainstalowany  
**Rozwiązanie:** `ollama pull <model_name>`

#### `Permission denied`
**Przyczyna:** Brak uprawnień do zapisu w katalogu wyjściowym  
**Rozwiązanie:** Sprawdź uprawnienia lub zmień `output_dir`

## Rozszerzanie funkcjonalności

### Dodawanie nowych modeli AI

```python
# W metodzie call_ollama
def call_ollama(self, prompt: str) -> str:
    # Możesz dodać różne prompty dla różnych modeli
    if self.model.startswith('codellama'):
        prompt = f"As a coding expert, {prompt}"
    elif self.model.startswith('mistral'):
        prompt = f"In a concise way, {prompt}"
    
    # Reszta logiki...
```

### Tworzenie własnych szablonów

Stwórz nowe pliki w katalogu `templates/`:
- `custom-post.html` - szablon posta
- `custom-index.html` - szablon strony głównej  
- `custom-style.css` - własne style

Następnie zaktualizuj konfigurację:
```yaml
post_template: 'custom-post.html'
index_template: 'custom-index.html'
```

### Dodawanie filtrów commitów

```python
def should_ignore_commit(self, commit: Dict[str, str]) -> bool:
    """Sprawdza czy commit powinien być pominięty"""
    subject = commit['subject'].lower()
    
    # Twoje własne reguły
    if 'wip' in subject or 'temp' in subject:
        return True
        
    if len(commit['body']) < 10:
        return True
        
    return False
```

## Performance

### Optymalizacja prędkości

1. **Limit commitów** - ustaw rozumny `commit_limit`
2. **Cache odpowiedzi** - zapisuj odpowiedzi AI do pliku
3. **Batch processing** - grupuj podobne commity
4. **Asynchroniczne wywołania** - użyj `asyncio` dla równoległych zapytań

### Monitoring użycia

```python
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_ollama(self, prompt: str) -> str:
    start_time = time.time()
    response = # ... wywołanie API
    duration = time.time() - start_time
    
    logger.info(f"Ollama call took {duration:.2f}s, "
                f"prompt length: {len(prompt)}, "
                f"response length: {len(response)}")
    
    return response
```

## Bezpieczeństwo

### Uwagi bezpieczeństwa

- **Nie commituj** plików z tokenami API
- **Waliduj** dane wejściowe przed wysłaniem do AI
- **Ograniczaj** dostęp do plików konfiguracji
- **Sprawdzaj** uprawnienia katalogów wyjściowych

### Przykład walidacji

```python
def validate_commit(self, commit: Dict[str, str]) -> bool:
    """Waliduje dane commita przed wysłaniem do AI"""
    required_fields = ['hash', 'author', 'subject']
    
    for field in required_fields:
        if not commit.get(field):
            return False
            
    # Sprawdź długość
    if len(commit['subject']) > 200:
        return False
        
    # Sprawdź niebezpieczne znaki
    dangerous_chars = ['<script>', '<?php', '${']
    text = commit['subject'] + commit.get('body', '')
    
    for char in dangerous_chars:
        if char in text.lower():
            return False
            
    return True
```

---

**Masz pytania o API?** Utwórz issue na GitHubie lub sprawdź kod źródłowy w `git2blog.py`.