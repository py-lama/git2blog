# Wkład w rozwój git2blog

Dziękujemy za zainteresowanie rozwojem git2blog! 🎉

## Jak zacząć

1. **Fork repozytorium** na GitHub
2. **Sklonuj** swój fork lokalnie:
   ```bash
   git clone https://github.com/TWOJA_NAZWA/git2blog.git
   cd git2blog
   ```
3. **Utwórz branch** dla swojej funkcji:
   ```bash
   git checkout -b feature/nowa-funkcja
   ```

## Środowisko deweloperskie

### Wymagania
- Python 3.7+
- Ollama (do testów z AI)
- Git

### Instalacja
```bash
# Utwórz wirtualne środowisko
python -m venv venv
source venv/bin/activate  # Linux/macOS
# lub
venv\Scripts\activate     # Windows

# Zainstaluj zależności
pip install -r requirements.txt

# Zainstaluj w trybie developerskim
pip install -e .
```

### Uruchomienie testów
```bash
# Wszystkie testy
python -m pytest tests/ -v

# Tylko testy jednostkowe
python -m unittest tests.test_git2blog -v

# Z pokryciem kodu
pip install coverage
coverage run -m pytest tests/
coverage report -m
```

## Guidelines

### Styl kodu
- **PEP 8** - standard formatowania Python
- **Type hints** - używaj gdzie to możliwe
- **Docstrings** - dokumentuj funkcje i klasy
- **Nazwy zmiennych** - po polsku w komentarzach, po angielsku w kodzie

```python
def generate_blog_post(commit: Dict[str, str]) -> Dict[str, str]:
    """
    Generuje post blogowy z commita Git.
    
    Args:
        commit: Słownik z danymi commita
        
    Returns:
        Słownik z wygenerowanym postem
    """
    pass
```

### Commitowanie
Używamy [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Nowe funkcje
git commit -m "feat: dodaj obsługę markdown w postach"

# Poprawki błędów  
git commit -m "fix: napraw błąd parsowania dat commitów"

# Dokumentacja
git commit -m "docs: aktualizuj README z nowymi przykładami"

# Refactoring
git commit -m "refactor: przenieś logikę HTML do osobnego modułu"

# Testy
git commit -m "test: dodaj testy dla generatora RSS"
```

### Typy commitów
- `feat:` - nowa funkcja
- `fix:` - poprawka błędu
- `docs:` - zmiany w dokumentacji
- `style:` - formatowanie, brak zmian w logice
- `refactor:` - refactoring kodu
- `test:` - dodanie/poprawienie testów
- `chore:` - zmiany w narzędziach, konfiguracji

## Co można rozwijać

### 🔥 Priorytetowe funkcje
- **Paginacja** - dla blogów z dużą liczbą postów
- **RSS feed** - export do czytników RSS
- **Markdown support** - jako alternatywa dla HTML
- **Kategorie/tagi** - na podstawie ścieżek plików w commitach

### 🚀 Średni priorytet
- **Ciemny motyw** - automatyczne przełączanie
- **SEO optimization** - meta tags, structured data
- **Export** - do platform blogowych (Ghost, WordPress)
- **Obsługa wielu repozytoriów** - agregacja commitów

### 💡 Pomysły na przyszłość
- **AI summaries** - podsumowania tygodniowe/miesięczne
- **Code highlights** - syntax highlighting w postach
- **Comments system** - integracja z Disqus/utterances
- **Analytics** - Google Analytics, Plausible

## Proces review

1. **Utwórz Pull Request** z opisem zmian
2. **Dodaj testy** dla nowych funkcji
3. **Sprawdź** że wszystkie testy przechodzą
4. **Zaktualizuj dokumentację** jeśli potrzeba
5. **Czekaj na review** - odpowiadamy w ciągu 2-3 dni

### Template PR
```markdown
## Opis zmian
Krótki opis co zostało dodane/zmienione.

## Typ zmiany
- [ ] Bug fix
- [ ] Nowa funkcja  
- [ ] Breaking change
- [ ] Dokumentacja

## Testy
- [ ] Dodano testy dla nowych funkcji
- [ ] Wszystkie testy przechodzą
- [ ] Przetestowano ręcznie

## Checklist
- [ ] Kod zgodny z PEP 8
- [ ] Dodano docstrings
- [ ] Zaktualizowano CHANGELOG.md
- [ ] Dokumentacja aktualna
```

## Zgłaszanie błędów

### Template issue
```markdown
**Opis błędu**
Jasny opis co się dzieje.

**Kroki do reprodukcji**
1. Przejdź do '...'
2. Kliknij na '....'
3. Zauważ błąd

**Oczekiwane zachowanie**
Co powinno się stać.

**Screenshots/Logi**
Jeśli aplikable, dodaj screenshots lub logi.

**Środowisko:**
- OS: [np. Ubuntu 22.04]
- Python: [np. 3.9.7]
- git2blog: [np. 1.0.0]
- Ollama model: [np. llama3.2]
```

## Pytania i pomoc

- 💬 **Discussions** - ogólne pytania o użytkowanie
- 🐛 **Issues** - błędy i propozycje funkcji
- 📧 **Email** - kontakt bezpośredni dla poważnych problemów

## Licencja

Poprzez wkład w projekt akceptujesz że twój kod będzie dostępny na licencji MIT.

---

**Dzięki za wkład w rozwój git2blog!** 🚀