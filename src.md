git2blog/
├── git2blog.py              # Główny skrypt
├── requirements.txt         # Zależności Python
├── README.md                # Dokumentacja
├── setup.py                 # Instalator pakietu
├── git2blog.yaml            # Przykładowa konfiguracja
├── .gitignore              # Git ignore
├── LICENSE                  # Licencja MIT
├── templates/              # Szablony HTML
│   ├── base.html           # Bazowy template
│   ├── index.html          # Template strony głównej
│   ├── post.html           # Template posta
│   └── style.css           # Style CSS
├── examples/               # Przykłady użycia
│   ├── sample-config.yaml  # Przykładowa konfiguracja
│   └── sample-output/      # Przykład wygenerowanego bloga
│       ├── index.html
│       ├── post_1.html
│       └── style.css
├── tests/                  # Testy jednostkowe
│   ├── __init__.py
│   ├── test_git2blog.py
│   └── fixtures/
│       └── sample_commits.json
└── docs/                   # Dodatkowa dokumentacja
    ├── CHANGELOG.md
    ├── CONTRIBUTING.md
    └── API.md