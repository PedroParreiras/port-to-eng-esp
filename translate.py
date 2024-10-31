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
        
        # Remover possíveis quebras de linha ou espaços extras (Removido o truncamento)
        # translated_text = translated_text.split('\n')[0].strip()
        
        return translated_text
    except Exception as e:
        print(f"Erro ao traduzir para {target_language}: {e}")
        sys.exit(1)

def find_changes(current_data, previous_data, parent_key=''):
    """
    Compara os dados atuais com os dados anteriores e retorna um dicionário
    contendo apenas as chaves que foram alteradas.
    """
    changes = {}
    for key, value in current_data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if key not in previous_data:
            # Nova chave adicionada
            changes[key] = value
            print(f"Nova chave adicionada: {full_key}")
        else:
            if isinstance(value, dict) and isinstance(previous_data[key], dict):
                # Recursivamente verificar mudanças em dicionários aninhados
                nested_changes = find_changes(value, previous_data[key], full_key)
                if nested_changes:
                    changes[key] = nested_changes
            else:
                if value != previous_data[key]:
                    changes[key] = value
                    print(f"Chave alterada: {full_key}")
    return changes

def update_translations(current_pt, changes, previous_translation, target_language):
    """
    Atualiza as traduções apenas para os textos que mudaram.
    Modifica o dicionário de tradução existente diretamente.
    """
    for key, value in changes.items():
        if isinstance(value, dict):
            # Se for um dicionário aninhado, garantir que exista na tradução
            if key not in previous_translation or not isinstance(previous_translation[key], dict):
                previous_translation[key] = {}
            # Recursivamente atualizar traduções aninhadas
            update_translations(current_pt[key], value, previous_translation[key], target_language)
        else:
            # Traduz somente o valor alterado
            translated_text = translate_text(value, target_language)
            print(f"Traduzindo '{value}' para {target_language}: '{translated_text}'")
            previous_translation[key] = translated_text

def main():
    try:
        # Caminhos dos arquivos
        pt_file = 'pasta/arquivo_pt.json'
        previous_pt_file = 'pasta/previous_pt.json'
        en_file = 'pasta/arquivo_en.json'
        es_file = 'pasta/arquivo_es.json'

        print(f"Lendo o arquivo em português atual: {pt_file}")
        current_pt = load_json(pt_file)

        print(f"Lendo o arquivo em português anterior: {previous_pt_file}")
        previous_pt = load_json(previous_pt_file)

        # Identificar as mudanças no arquivo português
        print("Identificando mudanças no arquivo em português...")
        changes = find_changes(current_pt, previous_pt)

        if not changes:
            print("Nenhuma alteração detectada no arquivo em português. Nenhuma tradução será atualizada.")
            sys.exit(0)
        else:
            print(f"Detectadas {len(changes)} alterações no arquivo em português.")

        # Carregar os arquivos de tradução
        print(f"Lendo o arquivo de tradução anterior em Inglês: {en_file}")
        previous_en = load_json(en_file)

        print(f"Lendo o arquivo de tradução anterior em Espanhol: {es_file}")
        previous_es = load_json(es_file)

        # Atualizar traduções para Inglês
        if changes:
            print("Iniciando a tradução para Inglês...")
            update_translations(current_pt, changes, previous_en, "Inglês")
            print("Tradução para Inglês concluída.")

            # Atualizar traduções para Espanhol
            print("Iniciando a tradução para Espanhol...")
            update_translations(current_pt, changes, previous_es, "Espanhol")
            print("Tradução para Espanhol concluída.")

            # Salvar os arquivos de tradução atualizados
            print("Escrevendo os arquivos traduzidos...")
            save_json(previous_en, en_file)
            save_json(previous_es, es_file)
            print("Arquivos traduzidos escritos com sucesso.")

            # Atualizar o arquivo de referência do português
            print("Atualizando o arquivo de referência do português...")
            save_json(current_pt, previous_pt_file)
            print("Arquivo de referência do português atualizado.")
        else:
            print("Nenhuma tradução foi atualizada.")

    except Exception as e:
        print(f"Erro no script de tradução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
