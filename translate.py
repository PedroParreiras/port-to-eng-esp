import os
import openai
import json
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

def load_json(file_path):
    """
    Carrega um arquivo JSON. Se o arquivo não existir, retorna um dicionário vazio.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

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
    contendo apenas as chaves que foram alteradas.
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

def update_translations(current_pt, previous_en, previous_es, target_language):
    """
    Atualiza as traduções apenas para os textos que mudaram.
    Retorna o dicionário atualizado das traduções.
    """
    updated_translation = {}
    changes = find_changes(current_pt, previous_en if target_language.lower() == "inglês" else previous_es)
    
    for key, value in current_pt.items():
        if key in changes:
            # Traduzir apenas o texto que mudou
            translated = translate_text(value, target_language)
            updated_translation[key] = translated
        else:
            # Manter a tradução existente
            updated_translation[key] = previous_en.get(key, "") if target_language.lower() == "inglês" else previous_es.get(key, "")
        
        # Se o valor for um dicionário, aplicar a tradução recursivamente
        if isinstance(value, dict):
            nested_en = previous_en.get(key, {}) if target_language.lower() == "inglês" else previous_es.get(key, {})
            nested_es = previous_es.get(key, {}) if target_language.lower() == "espanhol" else previous_en.get(key, {})
            updated_translation[key] = update_translations(value, nested_en, nested_es, target_language)
    
    return updated_translation

def main():
    try:
        # Caminhos dos arquivos
        pt_file = 'pasta/arquivo_pt.json'
        en_file = 'pasta/arquivo_en.json'
        es_file = 'pasta/arquivo_es.json'

        print(f"Lendo o arquivo em português: {pt_file}")
        current_pt = load_json(pt_file)

        print(f"Lendo o arquivo de tradução anterior em Inglês: {en_file}")
        previous_en = load_json(en_file)

        print(f"Lendo o arquivo de tradução anterior em Espanhol: {es_file}")
        previous_es = load_json(es_file)

        print("Iniciando a tradução para Inglês...")
        translated_en = update_translations(current_pt, previous_en, previous_es, "Inglês")
        print("Tradução para Inglês concluída.")

        print("Iniciando a tradução para Espanhol...")
        translated_es = update_translations(current_pt, previous_en, previous_es, "Espanhol")
        print("Tradução para Espanhol concluída.")

        print("Escrevendo os arquivos traduzidos...")
        save_json(translated_en, en_file)
        save_json(translated_es, es_file)
        print("Arquivos traduzidos escritos com sucesso.")

    except Exception as e:
        print(f"Erro no script de tradução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
