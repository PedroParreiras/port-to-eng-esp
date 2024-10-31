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
    
    prompt = f"Translate the following text to {lang}. Provide only the translated text without any additional information:\n\n{text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3,
        )
        translated_text = response.choices[0].message['content'].strip()
        
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
            changes[key] = value
        else:
            if isinstance(value, dict) and isinstance(previous_data[key], dict):
                nested_changes = find_changes(value, previous_data[key])
                if nested_changes:
                    changes[key] = nested_changes
            elif value != previous_data[key]:
                changes[key] = value
    return changes

def update_translations(current_pt, previous_translations, target_language):
    """
    Atualiza as traduções para apenas os textos alterados e retorna um dicionário atualizado.
    """
    changes = find_changes(current_pt, previous_translations)
    updated_translation = previous_translations.copy()
    
    for key, value in changes.items():
        if isinstance(value, dict):
            # Recursivamente traduz dicionários aninhados
            updated_translation[key] = update_translations(value, previous_translations.get(key, {}), target_language)
        else:
            # Traduz somente o valor alterado
            translated_text = translate_text(value, target_language)
            updated_translation[key] = translated_text
    
    return updated_translation

def main():
    try:
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
        translated_en = update_translations(current_pt, previous_en, "Inglês")
        print("Tradução para Inglês concluída.")

        print("Iniciando a tradução para Espanhol...")
        translated_es = update_translations(current_pt, previous_es, "Espanhol")
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
