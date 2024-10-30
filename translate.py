import os
import openai
import json
import sys
import subprocess
from dotenv import load_dotenv
from copy import deepcopy

# Carrega as variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

def get_previous_file_content(file_path):
    """
    Recupera o conteúdo do arquivo no último commit.
    Se não houver commits anteriores, retorna um dicionário vazio.
    """
    try:
        # Executa o comando git para obter o conteúdo do arquivo no último commit
        result = subprocess.run(
            ['git', 'show', 'HEAD~1:' + file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        # Se o arquivo não existir no último commit (primeiro commit), retorna vazio
        return {}
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do arquivo anterior: {e}")
        sys.exit(1)

def load_current_file(file_path):
    """
    Carrega o arquivo JSON atual.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"Erro: Arquivo {file_path} não encontrado.")
        sys.exit(1)

def save_json(data, file_path):
    """
    Salva um dicionário como um arquivo JSON.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def translate_text(text, target_language):
    """
    Traduz um texto para o idioma alvo utilizando a API do OpenAI.
    Retorna apenas o texto traduzido sem informações adicionais.
    """
    # Obtém a chave da API do ambiente
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        print("Erro: Chave da API do OpenAI não fornecida.")
        sys.exit(1)
    
    # Define o idioma de destino
    if target_language.lower() == "inglês":
        lang = "English"
    elif target_language.lower() == "espanhol":
        lang = "Spanish"
    else:
        print(f"Idioma alvo '{target_language}' não suportado.")
        sys.exit(1)
    
    # Modificação do prompt para solicitar apenas a tradução sem explicações
    prompt = f"Translate the following text to {lang}. Provide only the translated text without any additional information:\n\n{text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Escolha o modelo que preferir
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3,
        )
        translated_text = response.choices[0].message['content'].strip()
        
        # Remover possíveis quebras de linha ou espaços extras
        translated_text = translated_text.split('\n')[0].strip()
        
        return translated_text
    except Exception as e:
        print(f"Erro ao traduzir para {target_language}: {e}")
        sys.exit(1)

def find_changes(current_data, previous_data):
    """
    Compara os dados atuais com os dados anteriores e retorna um dicionário
    contendo apenas as chaves que foram adicionadas ou modificadas.
    """
    changes = {}
    for key, value in current_data.items():
        if key not in previous_data:
            # Nova chave adicionada
            changes[key] = value
        else:
            if isinstance(value, dict) and isinstance(previous_data[key], dict):
                # Recursivamente verificar mudanças em dicionários aninhados
                nested_changes = find_changes(value, previous_data[key])
                if nested_changes:
                    changes[key] = nested_changes
            else:
                if value != previous_data[key]:
                    changes[key] = value
    return changes

def update_translation(current_data, changes, target_language):
    """
    Atualiza as traduções apenas para os textos que mudaram.
    Retorna o dicionário atualizado das traduções.
    """
    updated_translation = deepcopy(current_data)
    
    for key, value in changes.items():
        if isinstance(value, dict):
            # Se o valor é um dicionário, aplicar a tradução recursivamente
            if key not in updated_translation or not isinstance(updated_translation[key], dict):
                updated_translation[key] = {}
            updated_translation[key] = update_translation(updated_translation.get(key, {}), value, target_language)
        elif isinstance(value, str):
            # Traduzir apenas o texto que mudou
            translated = translate_text(value, target_language)
            updated_translation[key] = translated
        else:
            # Se o valor não for um dicionário ou string, ignorar
            pass
    return updated_translation

def main():
    try:
        # Caminhos dos arquivos
        pt_file = 'pasta/arquivo_pt.json'
        en_file = 'pasta/arquivo_en.json'
        es_file = 'pasta/arquivo_es.json'

        print(f"Lendo o arquivo em português atual: {pt_file}")
        current_pt = load_current_file(pt_file)

        print(f"Lendo o arquivo em português anterior (último commit): {pt_file}")
        previous_pt = get_previous_file_content(pt_file)

        print("Identificando mudanças para Inglês...")
        changes_en = find_changes(current_pt, previous_pt)
        print(f"Número de entradas a traduzir para Inglês: {len(changes_en)}")

        print("Identificando mudanças para Espanhol...")
        changes_es = find_changes(current_pt, previous_pt)
        print(f"Número de entradas a traduzir para Espanhol: {len(changes_es)}")

        # Carregar traduções existentes
        previous_en = load_current_file(en_file) if os.path.exists(en_file) else {}
        previous_es = load_current_file(es_file) if os.path.exists(es_file) else {}

        # Atualizar traduções para Inglês
        if changes_en:
            print("Iniciando a tradução para Inglês...")
            translated_en = update_translation(previous_en, changes_en, "Inglês")
            print("Tradução para Inglês concluída.")
        else:
            print("Nenhuma tradução necessária para Inglês.")

        # Atualizar traduções para Espanhol
        if changes_es:
            print("Iniciando a tradução para Espanhol...")
            translated_es = update_translation(previous_es, changes_es, "Espanhol")
            print("Tradução para Espanhol concluída.")
        else:
            print("Nenhuma tradução necessária para Espanhol.")

        # Escrever os arquivos traduzidos
        if changes_en:
            print(f"Escrevendo o arquivo traduzido em Inglês: {en_file}")
            save_json(translated_en, en_file)

        if changes_es:
            print(f"Escrevendo o arquivo traduzido em Espanhol: {es_file}")
            save_json(translated_es, es_file)

        if not changes_en and not changes_es:
            print("Nenhuma tradução foi atualizada.")

    except Exception as e:
        print(f"Erro no script de tradução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
