# git2blog - Makefile dla automatyzacji zadań

.PHONY: help install test clean build deploy docs lint format

# Domyślny target
help:
	@echo "git2blog - Dostępne komendy:"
	@echo ""
	@echo "  install     Zainstaluj zależności"
	@echo "  test        Uruchom testy"
	@echo "  test-cov    Testy z pokryciem kodu"
	@echo "  lint        Sprawdź jakość kodu"
	@echo "  format      Formatuj kod (black, isort)"
	@echo "  clean       Usuń pliki tymczasowe"
	@echo "  build       Zbuduj pakiet do dystrybucji"
	@echo "  docs        Generuj dokumentację"
	@echo "  demo        Uruchom demo na przykładowych danych"
	@echo "  ollama      Sprawdź status Ollama"
	@echo "  timeout     Informacje o timeout dla Ollama (domyślnie 120s)"
	@echo "  cli-test     Testy CLI git2blog (menu/init/help itp.)"
	@echo "  patch-version  Zwiększ wersję patch"

# Instalacja środowiska
install:
	@echo "🔧 Instaluję zależności..."
	pip install -r requirements.txt
	pip install -e .

# Instalacja narzędzi deweloperskich
install-dev:
	@echo "🛠️ Instaluję narzędzia deweloperskie..."
	pip install black isort flake8 pytest coverage mypy
	pip install -r requirements.txt
	pip install -e .

# Testy
test:
	@echo "🧪 Uruchamiam testy..."
	python -m pytest tests/ -v

# Testy z pokryciem kodu
test-cov:
	@echo "📊 Testy z pokryciem kodu..."
	coverage run -m pytest tests/
	coverage report -m
	coverage html
	@echo "📋 Raport HTML: htmlcov/index.html"

# Testy CLI
cli-test:
	@echo "\U0001F50E Testy CLI git2blog..."
	pytest tests/test_cli.py -v

# Sprawdzanie jakości kodu
lint:
	@echo "🔍 Sprawdzam jakość kodu..."
	flake8 git2blog.py tests/ --max-line-length=100
	mypy git2blog.py --ignore-missing-imports

# Formatowanie kodu
format:
	@echo "✨ Formatuję kod..."
	black git2blog.py tests/ --line-length=100
	isort git2blog.py tests/ --profile=black

# Czyszczenie plików tymczasowych
clean:
	@echo "🧹 Czyszczę pliki tymczasowe..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Budowanie pakietu
build: clean
	@echo "📦 Buduję pakiet..."
	python setup.py sdist bdist_wheel
	@echo "✅ Pakiet gotowy w dist/"

# Publikacja na PyPI (test)
publish-test: build
	@echo "🚀 Publikuję na PyPI (test)..."
	pip install twine
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Publikacja na PyPI (produkcja)
publish: patch-version
	@echo "🚀 Publikuję na PyPI..."
	pip install twine
	twine upload dist/*

# Sprawdzenie Ollama
ollama:
	@echo "🤖 Sprawdzam status Ollama..."
	@curl -s http://localhost:11434/api/tags || echo "❌ Ollama niedostępna na localhost:11434"
	@echo ""
	@echo "Dostępne modele:"
	@curl -s http://localhost:11434/api/tags | python -m json.tool 2>/dev/null || echo "Brak połączenia z Ollama"

# Demo na przykładowych danych
demo:
	@echo "🎬 Uruchamiam demo..."
	@if [ ! -d ".git" ]; then \
		echo "⚠️ Nie jesteś w repozytorium Git. Tworzę przykładowe..."; \
		git init .; \
		git config user.name "Demo User"; \
		git config user.email "demo@example.com"; \
		echo "# Demo Project" > README.md; \
		git add README.md; \
		git commit -m "Initial commit"; \
		echo "print('Hello git2blog!')" > main.py; \
		git add main.py; \
		git commit -m "Dodaj główny skrypt aplikacji"; \
		echo "## Funkcje\n- Feature A\n- Feature B" >> README.md; \
		git add README.md; \
		git commit -m "Rozszerz dokumentację o listę funkcji"; \
	fi
	python git2blog.py --init
	@echo "📝 Wygenerowano przykładową konfigurację"
	@echo "🚀 Uruchamiam generator bloga..."
	python git2blog.py
	@echo "✅ Demo zakończone! Sprawdź blog/ katalog"

# Tworzenie przykładowego projektu Git
init-example:
	@echo "📁 Tworzę przykładowy projekt Git..."
	mkdir -p example-project
	cd example-project && \
	git init && \
	git config user.name "Przykładowy Developer" && \
	git config user.email "dev@example.com" && \
	echo "# Przykładowy Projekt" > README.md && \
	git add README.md && \
	git commit -m "Początkowy commit z README" && \
	echo "def hello():\n    print('Hello World!')" > main.py && \
	git add main.py && \
	git commit -m "Dodaj funkcję hello world" && \
	echo "## Instalacja\npip install ." >> README.md && \
	git add README.md && \
	git commit -m "Dodaj instrukcje instalacji" && \
	echo "# TODO\n- [ ] Dodać testy\n- [ ] Dokumentacja" > TODO.md && \
	git add TODO.md && \
	git commit -m "Dodaj listę zadań do wykonania" && \
	mkdir tests && \
	echo "import unittest\nfrom main import hello" > tests/test_main.py && \
	git add tests/ && \
	git commit -m "Dodaj podstawowe testy jednostkowe"
	@echo "✅ Przykładowy projekt utworzony w example-project/"

# Generowanie dokumentacji
docs:
	@echo "📚 Generuję dokumentację..."
	@echo "=== README.md ===" && cat README.md
	@echo ""
	@echo "=== CHANGELOG.md ===" && head -20 docs/CHANGELOG.md
	@echo ""
	@echo "📖 Pełna dokumentacja w docs/"

# Uruchomienie rozwojowe
dev: install-dev
	@echo "🔧 Środowisko deweloperskie gotowe!"
	@echo "Dostępne komendy:"
	@echo "  make test     - testy"
	@echo "  make lint     - jakość kodu"
	@echo "  make format   - formatowanie"
	@echo "  make demo     - uruchom demo"

# Sprawdzenie wszystkiego przed commitem
check: format lint test
	@echo "✅ Wszystkie sprawdzenia przeszły pomyślnie!"

# Instalacja Ollama (Linux/macOS)
install-ollama:
	@echo "🤖 Instaluję Ollama..."
	curl -fsSL https://ollama.ai/install.sh | sh
	@echo "⬇️ Pobieram model llama3.2..."
	ollama pull llama3.2
	@echo "✅ Ollama zainstalowana i gotowa!"

# Konfiguracja Git hooks
install-hooks:
	@echo "🪝 Instaluję Git hooks..."
	@echo "#!/bin/sh\nmake check" > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "✅ Git hooks zainstalowane!"

# Status środowiska
status:
	@echo "📊 Status środowiska git2blog:"
	@echo ""
	@echo "Python:" && python --version
	@echo "Git:" && git --version
	@echo "Ollama:" && (curl -s http://localhost:11434/api/tags >/dev/null && echo "✅ Działa" || echo "❌ Niedostępna")
	@echo ""
	@echo "Zainstalowane pakiety:"
	@pip list | grep -E "(requests|PyYAML|pytest|black)" || echo "Brak wymaganych pakietów"

# Backup konfiguracji
backup-config:
	@echo "💾 Tworzę backup konfiguracji..."
	@if [ -f "git2blog.yaml" ]; then \
		cp git2blog.yaml git2blog.yaml.backup.$(shell date +%Y%m%d_%H%M%S); \
		echo "✅ Backup utworzony"; \
	else \
		echo "⚠️ Brak pliku konfiguracji do backupu"; \
	fi

# Aktualizacja zależności
update:
	@echo "⬆️ Aktualizuję zależności..."
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

# Wszystko w jednym - pełny setup
setup: install-dev install-ollama init-example
	@echo "🎉 Pełny setup git2blog zakończony!"
	@echo ""
	@echo "Następne kroki:"
	@echo "1. cd example-project"
	@echo "2. make demo"
	@echo "3. Otwórz blog/index.html w przeglądarce"

# Timeout info
timeout:
	@echo "\nDomyślny timeout zapytań do Ollama to 120 sekund. Możesz to zmienić w git2blog.yaml (timeout: 180) lub przez zmienną środowiskową OLLAMA_TIMEOUT.\n"

# Zwiększ wersję patch
.PHONY: patch-version

patch-version:
	@echo "Aktualna wersja: $$(grep __version__ version.py | cut -d'"' -f2)"
	@old_ver=$$(grep __version__ version.py | cut -d'"' -f2); \
	major=$$(echo $$old_ver | cut -d. -f1); \
	minor=$$(echo $$old_ver | cut -d. -f2); \
	patch=$$(echo $$old_ver | cut -d. -f3); \
	new_patch=$$(($$patch + 1)); \
	new_ver="$$major.$$minor.$$new_patch"; \
	sed -i "s/__version__ = \".*\"/__version__ = \"$$new_ver\"/" version.py; \
	echo "Nowa wersja: $$new_ver";
	@git add version.py
	@git commit -m "Bump patch version to $$(grep __version__ version.py | cut -d'"' -f2)"