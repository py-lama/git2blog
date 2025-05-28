#!/usr/bin/env python3
"""
git2blog - Generator bloga z historii Git używając Ollama LLM
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
import argparse
import yaml
from typing import List, Dict, Any


class Git2Blog:
    def __init__(self, config_path: str = "git2blog.yaml"):
        self.config = self.load_config(config_path)
        self.ollama_url = self.config.get('ollama_url', 'http://localhost:11434')
        self.model = self.config.get('model', 'llama3.2')
        self.output_dir = Path(self.config.get('output_dir', 'blog'))
        self.template_dir = Path(self.config.get('template_dir', 'templates'))

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Wczytuje konfigurację z pliku YAML"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def create_default_config(self):
        """Tworzy domyślny plik konfiguracyjny"""
        default_config = {
            'ollama_url': 'http://localhost:11434',
            'model': 'llama3.2',
            'output_dir': 'blog',
            'template_dir': 'templates',
            'blog_title': 'Mój Blog Projektowy',
            'blog_description': 'Blog generowany automatycznie z historii Git',
            'author': 'Developer',
            'posts_per_page': 10,
            'commit_limit': 50,
            'ignore_merge_commits': True,
            'post_template': 'post.html',
            'index_template': 'index.html'
        }

        with open('git2blog.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        print("✅ Utworzono domyślny plik konfiguracyjny: git2blog.yaml")

    def get_git_commits(self, limit: int = 50) -> List[Dict[str, str]]:
        """Pobiera listę commitów z repozytorium Git"""
        try:
            cmd = [
                'git', 'log',
                f'--max-count={limit}',
                '--pretty=format:%H|%an|%ae|%ad|%s|%b',
                '--date=iso'
            ]

            if self.config.get('ignore_merge_commits', True):
                cmd.append('--no-merges')

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

            if result.returncode != 0:
                raise Exception(f"Git error: {result.stderr}")

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('|', 5)
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'subject': parts[4],
                        'body': parts[5] if len(parts) > 5 else ''
                    })

            return commits

        except Exception as e:
            print(f"❌ Błąd podczas pobierania commitów: {e}")
            return []

    def call_ollama(self, prompt: str) -> str:
        """Wywołuje Ollama API z promptem"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                print(f"❌ Błąd Ollama API: {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            print(f"❌ Błąd połączenia z Ollama: {e}")
            return ""

    def generate_blog_post(self, commit: Dict[str, str]) -> Dict[str, str]:
        """Generuje post blogowy z commita"""
        prompt = f"""
Jesteś ekspertem w pisaniu postów blogowych o rozwoju oprogramowania. 
Na podstawie poniższego commita Git, napisz interesujący post blogowy w języku polskim.

COMMIT:
Autor: {commit['author']}
Data: {commit['date']}
Tytuł: {commit['subject']}
Opis: {commit['body']}

Napisz post blogowy który:
1. Ma atrakcyjny tytuł (różny od tytułu commita)
2. Wyjaśnia co zostało zrobione w przystępny sposób
3. Opisuje dlaczego ta zmiana była ważna
4. Ma ton conversational ale profesjonalny
5. Jest długości 200-400 słów

Zwróć tylko treść posta bez dodatkowych komentarzy.
"""

        content = self.call_ollama(prompt)
        if not content:
            # Fallback jeśli Ollama nie odpowiada
            content = f"""
# {commit['subject']}

**Autor:** {commit['author']}  
**Data:** {commit['date']}

{commit['body'] or 'Brak dodatkowego opisu dla tego commita.'}

*Ten post został wygenerowany automatycznie z historii Git.*
"""

        # Generuj tytuł posta
        title_prompt = f"""
Na podstawie tego commita Git, zaproponuj krótki, atrakcyjny tytuł posta blogowego w języku polskim (maksymalnie 60 znaków):

Commit: {commit['subject']}
Opis: {commit['body'][:100]}...

Zwróć tylko tytuł bez dodatkowych komentarzy.
"""

        title = self.call_ollama(title_prompt)
        if not title or len(title) > 100:
            title = commit['subject']

        return {
            'title': title,
            'content': content,
            'date': commit['date'],
            'author': commit['author'],
            'commit_hash': commit['hash']
        }

    def create_html_post(self, post: Dict[str, str]) -> str:
        """Tworzy HTML dla pojedynczego posta"""
        template = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']} - {self.config.get('blog_title', 'Blog')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ border-bottom: 1px solid #eee; margin-bottom: 30px; padding-bottom: 20px; }}
        .post-meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .post-content {{ font-size: 1.1em; }}
        .back-link {{ margin-top: 30px; }}
        .commit-info {{ background: #f5f5f5; padding: 10px; border-radius: 5px; 
                        font-family: monospace; font-size: 0.8em; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1><a href="index.html" style="text-decoration: none; color: inherit;">
            {self.config.get('blog_title', 'Blog')}
        </a></h1>
        <p>{self.config.get('blog_description', 'Blog generowany z Git')}</p>
    </div>

    <article>
        <h1>{post['title']}</h1>
        <div class="post-meta">
            Autor: {post['author']} | Data: {post['date'][:10]}
        </div>
        <div class="post-content">
            {post['content'].replace(chr(10), '<br>')}
        </div>
        <div class="commit-info">
            Commit: {post['commit_hash'][:8]}
        </div>
    </article>

    <div class="back-link">
        <a href="index.html">← Powrót do strony głównej</a>
    </div>
</body>
</html>
"""
        return template

    def create_index_page(self, posts: List[Dict[str, str]]) -> str:
        """Tworzy stronę główną bloga"""
        posts_html = ""
        for i, post in enumerate(posts):
            filename = f"post_{i + 1}.html"
            posts_html += f"""
            <article style="border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 20px;">
                <h2><a href="{filename}" style="text-decoration: none; color: #333;">{post['title']}</a></h2>
                <div style="color: #666; font-size: 0.9em; margin-bottom: 10px;">
                    {post['author']} | {post['date'][:10]}
                </div>
                <p>{post['content'][:200]}...</p>
                <a href="{filename}">Czytaj więcej →</a>
            </article>
            """

        template = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.get('blog_title', 'Blog')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 1px solid #eee; 
                   margin-bottom: 30px; padding-bottom: 20px; }}
        .posts {{ margin-top: 30px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; 
                   border-top: 1px solid #eee; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.config.get('blog_title', 'Mój Blog Projektowy')}</h1>
        <p>{self.config.get('blog_description', 'Blog generowany automatycznie z historii Git')}</p>
    </div>

    <div class="posts">
        {posts_html}
    </div>

    <div class="footer">
        <p>Blog wygenerowany automatycznie z historii Git przy użyciu git2blog</p>
        <p>Ostatnia aktualizacja: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
</body>
</html>
"""
        return template

    def generate_blog(self):
        """Główna funkcja generująca blog"""
        print("🚀 Rozpoczynam generowanie bloga...")

        # Sprawdź czy jesteśmy w repozytorium Git
        if not os.path.exists('.git'):
            print("❌ Nie znajdujesz się w repozytorium Git!")
            return

        # Sprawdź połączenie z Ollama
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                print("❌ Nie można połączyć się z Ollama!")
                return
        except:
            print("❌ Ollama nie jest dostępna! Upewnij się, że działa na localhost:11434")
            return

        # Pobierz commity
        commits = self.get_git_commits(self.config.get('commit_limit', 50))
        if not commits:
            print("❌ Nie znaleziono żadnych commitów!")
            return

        print(f"📝 Znaleziono {len(commits)} commitów")

        # Utwórz katalog wyjściowy
        self.output_dir.mkdir(exist_ok=True)

        # Generuj posty
        posts = []
        for i, commit in enumerate(commits):
            print(f"⏳ Generuję post {i + 1}/{len(commits)}: {commit['subject'][:50]}...")
            post = self.generate_blog_post(commit)
            posts.append(post)

            # Zapisz post jako HTML
            post_html = self.create_html_post(post)
            post_file = self.output_dir / f"post_{i + 1}.html"
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(post_html)

        # Utwórz stronę główną
        print("📄 Tworzę stronę główną...")
        index_html = self.create_index_page(posts)
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)

        print(f"✅ Blog wygenerowany! Otwórz {index_file} w przeglądarce.")
        print(f"📁 Pliki znajdują się w katalogu: {self.output_dir}")


def main():
    parser = argparse.ArgumentParser(description='git2blog - Generator bloga z Git + Ollama')
    parser.add_argument('--init', action='store_true', help='Utwórz domyślny plik konfiguracyjny')
    parser.add_argument('--config', default='git2blog.yaml', help='Ścieżka do pliku konfiguracyjnego')

    args = parser.parse_args()

    if args.init:
        git2blog = Git2Blog()
        git2blog.create_default_config()
        return

    git2blog = Git2Blog(args.config)
    git2blog.generate_blog()


if __name__ == "__main__":
    main()