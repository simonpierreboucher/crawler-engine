from flask import Flask, request, jsonify, send_from_directory
import subprocess
import time
import os

app = Flask(__name__)

# Variables globales pour suivre les métriques
class CrawlerMetrics:
    def __init__(self):
        self.urls_extracted = 0
        self.pages_extracted = 0
        self.pages_rewritten = 0
        self.url_processing_rate = 0
        self.content_processing_rate = 0
        self.rewrite_processing_rate = 0
        self.start_time = time.time()
        self.last_update_time = time.time()

    def update_metrics(self, url_extracted=False, page_extracted=False, page_rewritten=False):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        # Mise à jour des compteurs
        if url_extracted:
            self.urls_extracted += 1
        if page_extracted:
            self.pages_extracted += 1
        if page_rewritten:
            self.pages_rewritten += 1

        # Mettre à jour les taux (toutes les minutes)
        if elapsed_time > 0:
            self.url_processing_rate = self.urls_extracted / (elapsed_time / 60)
            self.content_processing_rate = self.pages_extracted / (elapsed_time / 60)
            self.rewrite_processing_rate = self.pages_rewritten / (elapsed_time / 60)

    def get_metrics(self):
        return {
            "urls_extracted": self.urls_extracted,
            "pages_extracted": self.pages_extracted,
            "pages_rewritten": self.pages_rewritten,
            "url_processing_rate": self.url_processing_rate,
            "content_processing_rate": self.content_processing_rate,
            "rewrite_processing_rate": self.rewrite_processing_rate
        }

metrics = CrawlerMetrics()

@app.route('/run-crawler', methods=['POST'])
def run_crawler():
    data = request.get_json()
    
    command = ["python", "crawler.py",
               "--start-url", data["start_url"],
               "--max-depth", str(data["max_depth"])]

    if data.get("use_playwright"):
        command.append("--use-playwright")
    if data.get("download_pdf"):
        command.append("--download-pdf")
    if data.get("download_doc"):
        command.append("--download-doc")
    if data.get("download_image"):
        command.append("--download-image")
    if data.get("download_other"):
        command.append("--download-other")

    if data.get("llm_provider"):
        command.extend(["--llm-provider", data["llm_provider"]])

    if data.get("openai_api_key"):
        # Le crawler attend une liste, on peut passer une clé unique
        command.extend(["--openai-api-keys", data["openai_api_key"]])

    if data.get("max_tokens"):
        command.extend(["--max-tokens", str(data["max_tokens"])])

    if data.get("max_urls"):
        command.extend(["--max-urls", str(data["max_urls"])])

    if data.get("output_dir"):
        command.extend(["--crawler-output-dir", data["output_dir"]])

    if data.get("checkpoint_file"):
        command.extend(["--checkpoint-file", data["checkpoint_file"]])

    if data.get("verbose"):
        command.append("--verbose")

    # Exécution de la commande
    subprocess.run(command, check=True)

    # Mettre à jour les métriques après exécution (exemple simple)
    metrics.update_metrics(url_extracted=True, page_extracted=True, page_rewritten=False)
    return jsonify({"status": "success"})


@app.route('/metrics', methods=['GET'])
def get_metrics():
    # Ici, vous pourriez mettre à jour les métriques à partir d'un autre système,
    # ou bien le crawler pourrait appeler une fonction. Pour l'instant, on retourne
    # simplement les métriques actuelles.
    return jsonify(metrics.get_metrics())

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == "__main__":
    # Lancez le serveur Flask
    # Accédez à l'interface sur http://127.0.0.1:5000/
    app.run(debug=True)
