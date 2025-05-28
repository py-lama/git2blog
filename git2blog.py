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
            'index_template': 'index.html',
            'repo_url': '',
            'issues_url': '',
            'pages_url': ''
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
        # Dane do linków
        repo_url = self.config.get('repo_url', '')
        git_platform = 'github' if 'github' in repo_url else 'gitlab' if 'gitlab' in repo_url else ''
        author = post['author']
        commit_hash = post['commit_hash']
        commit_url = f"{repo_url}/commit/{commit_hash}" if repo_url else None
        # Link do profilu autora (jeśli email/nick znany i platforma rozpoznana)
        author_profile = ''
        if git_platform == 'github' and author:
            author_profile = f"{repo_url.split('.com/')[0]}.com/{author}" if '/' not in author else f"{repo_url.split('.com/')[0]}.com/{author}"
        elif git_platform == 'gitlab' and author:
            author_profile = f"{repo_url.split('.com/')[0]}.com/{author}" if '/' not in author else f"{repo_url.split('.com/')[0]}.com/{author}"
        # Link do historii na daną datę
        date = post['date'][:10]
        history_url = f"{repo_url}/commits?since={date}&until={date}" if repo_url else None
        # Link do issues i pages (jeśli ustawione w config)
        issues_url = self.config.get('issues_url', f'{repo_url}/issues' if repo_url else '')
        pages_url = self.config.get('pages_url', '')

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
        .meta-links a {{ margin-right: 12px; color: #0066cc; text-decoration: none; }}
        .meta-links a:hover {{ color: #cc3300; }}
    </style>
</head>
<body>
    <div class="header">
        <h1><a href="index.html" style="text-decoration: none; color: inherit;">
            {self.config.get('blog_title', 'Blog')}
        </a></h1>
        <p>{self.config.get('blog_description', 'Blog generowany z Git')}</p>
        <div class="meta-links">
            {f'<a href="{repo_url}" target="_blank">Repozytorium</a>' if repo_url else ''}
            {f'<a href="{issues_url}" target="_blank">Issues</a>' if issues_url else ''}
            {f'<a href="{pages_url}" target="_blank">Strona projektu</a>' if pages_url else ''}
        </div>
    </div>

    <article>
        <h1>{post['title']}</h1>
        <div class="post-meta">
            Autor: {f'<a href="{author_profile}" target="_blank">{author}</a>' if author_profile else author}
            | Data: {f'<a href="{history_url}" target="_blank">{date}</a>' if history_url else date}
        </div>
        <div class="post-content">
            {post['content'].replace(chr(10), '<br>')}
        </div>
        <div class="commit-info">
            Commit: {f'<a href="{commit_url}" target="_blank">{commit_hash[:8]}</a>' if commit_url else commit_hash[:8]}
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
        repo_url = self.config.get('repo_url', '')
        issues_url = self.config.get('issues_url', f'{repo_url}/issues' if repo_url else '')
        pages_url = self.config.get('pages_url', '')
        posts_html = ""
        for i, post in enumerate(posts):
            filename = f"post_{i + 1}.html"
            author = post['author']
            commit_hash = post['commit_hash']
            # Linki jak w create_html_post
            git_platform = 'github' if 'github' in repo_url else 'gitlab' if 'gitlab' in repo_url else ''
            author_profile = ''
            if git_platform == 'github' and author:
                author_profile = f"{repo_url.split('.com/')[0]}.com/{author}" if '/' not in author else f"{repo_url.split('.com/')[0]}.com/{author}"
            elif git_platform == 'gitlab' and author:
                author_profile = f"{repo_url.split('.com/')[0]}.com/{author}" if '/' not in author else f"{repo_url.split('.com/')[0]}.com/{author}"
            date = post['date'][:10]
            history_url = f"{repo_url}/commits?since={date}&until={date}" if repo_url else None
            commit_url = f"{repo_url}/commit/{commit_hash}" if repo_url else None
            posts_html += f"""
            <article style="border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 20px;">
                <h2><a href="{filename}" style="text-decoration: none; color: #333;">{post['title']}</a></h2>
                <div style="color: #666; font-size: 0.9em; margin-bottom: 10px;">
                    {f'<a href="{author_profile}" target="_blank">{author}</a>' if author_profile else author} |
                    {f'<a href="{history_url}" target="_blank">{date}</a>' if history_url else date} |
                    {f'<a href="{commit_url}" target="_blank">{commit_hash[:8]}</a>' if commit_url else commit_hash[:8]}
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
        .meta-links a {{ margin-right: 12px; color: #0066cc; text-decoration: none; }}
        .meta-links a:hover {{ color: #cc3300; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.config.get('blog_title', 'Mój Blog Projektowy')}</h1>
        <p>{self.config.get('blog_description', 'Blog generowany automatycznie z historii Git')}</p>
        <div class="meta-links">
            {f'<a href="{repo_url}" target="_blank">Repozytorium</a>' if repo_url else ''}
            {f'<a href="{issues_url}" target="_blank">Issues</a>' if issues_url else ''}
            {f'<a href="{pages_url}" target="_blank">Strona projektu</a>' if pages_url else ''}
        </div>
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

    def group_commits_by_day(self, commits):
        """Grupuje commity według dnia"""
        grouped_commits = {}
        
        for commit in commits:
            # Wyciągnij datę z commita (tylko część daty bez czasu)
            date_str = commit['date'].split()[0]
            
            if date_str not in grouped_commits:
                grouped_commits[date_str] = []
                
            grouped_commits[date_str].append(commit)
            
        # Konwertuj na listę grup, posortowaną od najnowszej daty
        result = []
        for date_str in sorted(grouped_commits.keys(), reverse=True):
            commits_for_day = grouped_commits[date_str]
            # Dodaj datę jako metadane do grupy
            result.append({
                'date': date_str,
                'commits': commits_for_day,
                'count': len(commits_for_day)
            })
            
        return result
        
    def group_commits_by_count(self, commits, count):
        """Grupuje commity po określonej liczbie"""
        result = []
        
        for i in range(0, len(commits), count):
            group = commits[i:i+count]
            result.append({
                'date': group[0]['date'].split()[0],  # Data pierwszego commita w grupie
                'commits': group,
                'count': len(group)
            })
            
        return result
        
    def generate_blog_post_from_group(self, commit_group):
        """Generuje post na podstawie grupy commitów"""
        # Przygotuj zbiorczy opis wszystkich commitów w grupie
        commits_summary = ""
        for commit in commit_group['commits']:
            commits_summary += f"- {commit['subject']}\n"
            if commit['body']:
                # Dodaj wcięcie do treści commita
                body_indented = '  ' + commit['body'].replace('\n', '\n  ')
                commits_summary += f"{body_indented}\n"
        
        # Przygotuj prompt dla modelu
        prompt = f"""Napisz post na blog na podstawie poniższych commitów z dnia {commit_group['date']}. 
        Liczba commitów: {commit_group['count']}
        
        Commity:
        {commits_summary}
        
        Napisz szczegółowy post opisujący zmiany wprowadzone w tych commitach. 
        Uwzględnij kontekst techniczny i biznesowy zmian.
        Pisz w języku polskim, w stylu profesjonalnego bloga technicznego.
        """
        
        try:
            # Wywołaj model LLM
            content = self.call_ollama(prompt)
            
            # Wygeneruj tytuł
            title_prompt = f"Napisz krótki, zwięzły tytuł dla posta o następującej treści, nie dłuższy niż 10 słów: {content[:500]}..."
            title = self.call_ollama(title_prompt)
            
            # Przygotuj post
            return {
                'title': title,
                'date': commit_group['date'],
                'content': content,
                'author': self.config.get('author', 'Developer'),
                'commit_count': commit_group['count']
            }
            
        except Exception as e:
            print(f"❌ Błąd podczas generowania posta: {e}")
            # Zwróć podstawowy post w przypadku błędu
            return {
                'title': f"Aktualizacja z dnia {commit_group['date']}",
                'date': commit_group['date'],
                'content': f"W tym dniu wprowadzono {commit_group['count']} zmian.\n\n{commits_summary}",
                'author': self.config.get('author', 'Developer'),
                'commit_count': commit_group['count']
            }

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
        
        # Sprawdź metodę grupowania
        grouping_method = self.config.get('post_grouping', {}).get('method', 'commit')
        posts = []
        
        if grouping_method == 'day':
            # Grupuj commity według dni
            commit_groups = self.group_commits_by_day(commits)
            print(f"📅 Grupowanie według dni: {len(commit_groups)} grup")
            
            for i, group in enumerate(commit_groups):
                print(f"⏳ Generuję post {i + 1}/{len(commit_groups)}: Dzień {group['date']} ({group['count']} commitów)...")
                post = self.generate_blog_post_from_group(group)
                posts.append(post)
                
                # Zapisz post jako HTML
                post_html = self.create_html_post(post)
                post_file = self.output_dir / f"post_{i + 1}.html"
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(post_html)
                    
        elif grouping_method == 'count':
            # Grupuj commity po określonej liczbie
            commits_per_post = self.config.get('post_grouping', {}).get('commits_per_post', 3)
            commit_groups = self.group_commits_by_count(commits, commits_per_post)
            print(f"🔢 Grupowanie po {commits_per_post} commitów: {len(commit_groups)} grup")
            
            for i, group in enumerate(commit_groups):
                print(f"⏳ Generuję post {i + 1}/{len(commit_groups)}: Grupa {i+1} ({group['count']} commitów)...")
                post = self.generate_blog_post_from_group(group)
                posts.append(post)
                
                # Zapisz post jako HTML
                post_html = self.create_html_post(post)
                post_file = self.output_dir / f"post_{i + 1}.html"
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(post_html)
        else:
            # Standardowe generowanie - jeden commit, jeden post
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


def menu_create_config():
    print("\n🛠️ Kreator pliku konfiguracyjnego git2blog.yaml\n")
    blog_title = input("Tytuł bloga [Mój Blog Projektowy]: ") or "Mój Blog Projektowy"
    blog_description = input("Opis bloga [Blog generowany automatycznie z historii Git]: ") or "Blog generowany automatycznie z historii Git"
    author = input("Autor [Developer]: ") or "Developer"
    repo_url = input("URL repozytorium (np. https://github.com/uzytkownik/projekt): ")
    issues_url = input("URL issues (opcjonalnie): ")
    pages_url = input("URL GitHub/GitLab Pages (opcjonalnie): ")
    model = input("Model Ollama [llama3.2]: ") or "llama3.2"
    commit_limit = input("Limit commitów [50]: ") or "50"
    timeout = input("Timeout (sekundy) [120]: ") or "120"

    config = {
        'ollama_url': 'http://localhost:11434',
        'model': model,
        'timeout': int(timeout),
        'output_dir': 'blog',
        'template_dir': 'templates',
        'blog_title': blog_title,
        'blog_description': blog_description,
        'author': author,
        'posts_per_page': 10,
        'commit_limit': int(commit_limit),
        'ignore_merge_commits': True,
        'post_template': 'post.html',
        'index_template': 'index.html',
        'repo_url': repo_url,
        'issues_url': issues_url,
        'pages_url': pages_url
    }
    with open('git2blog.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    print("\n✅ Utworzono plik git2blog.yaml!")


def main():
    parser = argparse.ArgumentParser(description='git2blog - Generator bloga z Git + Ollama')
    parser.add_argument('--init', action='store_true', help='Utwórz domyślny plik konfiguracyjny')
    parser.add_argument('--config', default='git2blog.yaml', help='Ścieżka do pliku konfiguracyjnego')
    parser.add_argument('--menu', action='store_true', help='Uruchom kreator konfiguracji (interaktywny)')

    args = parser.parse_args()

    if args.menu:
        menu_create_config()
        return

    if args.init:
        git2blog = Git2Blog()
        git2blog.create_default_config()
        return

    git2blog = Git2Blog(args.config)
    git2blog.generate_blog()


if __name__ == "__main__":
    main()