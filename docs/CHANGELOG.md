# Changelog

Wszystkie istotne zmiany w projekcie git2blog będą dokumentowane w tym pliku.

Format bazuje na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt używa [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planowane
- Paginacja dla dużych blogów
- Obsługa markdown zamiast HTML
- RSS feed
- Kategorie i tagi na podstawie ścieżek plików
- Export do platform blogowych (Ghost, WordPress)
- Ciemny motyw (automatyczne przełączanie)
- Obsługa wielu języków

## [1.0.0] - 2025-01-28

### Dodane
- 🎉 **Pierwsza wersja git2blog**
- Automatyczne generowanie bloga z commitów Git
- Integracja z lokalnym Ollama LLM
- Konfigurowalne szablony HTML/CSS
- Responsive design dla urządzeń mobilnych
- System konfiguracji przez YAML
- Filtrowanie commitów (merge commits, wzorce)
- Wsparcie dla wielu modeli AI (llama3.2, codellama, mistral)
- Kompletne testy jednostkowe
- Dokumentacja w języku polskim

### Techniczne
- Python 3.7+ support
- Requests library dla API calls
- PyYAML dla konfiguracji
- Subprocess dla Git integration
- Pathlib dla cross-platform paths

### Szablony
- Nowoczesny, czysty design
- CSS Grid/Flexbox layouts
- Inter font family
- Hover effects i animacje
- Print-friendly styles
- Accessibility support (WCAG guidelines)

## Konwencje wersjonowania

- **MAJOR** (X.0.0): Zmiany niekompatybilne wstecz
- **MINOR** (0.X.0): Nowe funkcje kompatybilne wstecz  
- **PATCH** (0.0.X): Poprawki błędów kompatybilne wstecz

## Kategorie zmian

- **Dodane** - nowe funkcje
- **Zmienione** - zmiany w istniejących funkcjach
- **Przestarzałe** - funkcje które będą usunięte
- **Usunięte** - usunięte funkcje
- **Poprawione** - poprawki błędów
- **Bezpieczeństwo** - zmiany związane z bezpieczeństwem