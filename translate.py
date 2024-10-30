import os
import openai
import json
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

def translate_text(text, target_language):
    # Obtém a chave da API do ambiente
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        print("Erro: Chave da API do OpenAI não fornecida.")
        sys.exit(1)
    
    print(f"Chave da API obtida: {openai.api_key[:4]}****")  # Imprime apenas os primeiros 4 caracteres para segurança
    
    print(f"Traduzindo para {target_language}: {text}")
    
    # Define o idioma de destino
    if target_language.lower() == "inglês":
        lang = "English"
    elif target_language.lower() == "espanhol":
        lang = "Spanish"
    else:
        print(f"Idioma alvo '{target_language}' não suportado.")
        sys.exit(1)
    
    prompt = f"Translate the following text to {lang}:\n\n{text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Escolha o modelo que preferir
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
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

def translate_dict(data, target_language):
    if isinstance(data, dict):
        return {k: translate_dict(v, target_language) for k, v in data.items()}
    elif isinstance(data, list):
        return [translate_dict(item, target_language) for item in data]
    elif isinstance(data, str):
        return translate_text(data, target_language)
    else:
        return data

def main():
    try:
        # Caminhos dos arquivos
        pt_file = 'pasta/arquivo_pt.json'
        en_file = 'pasta/arquivo_en.json'
        es_file = 'pasta/arquivo_es.json'

        print(f"Lendo o arquivo em português: {pt_file}")
        with open(pt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("Iniciando a tradução para Inglês...")
        translated_en = translate_dict(data, "Inglês")
        print("Tradução para Inglês concluída.")

        print("Iniciando a tradução para Espanhol...")
        translated_es = translate_dict(data, "Espanhol")
        print("Tradução para Espanhol concluída.")

        print("Escrevendo os arquivos traduzidos...")
        with open(en_file, 'w', encoding='utf-8') as f_en, open(es_file, 'w', encoding='utf-8') as f_es:
            json.dump(translated_en, f_en, ensure_ascii=False, indent=2)
            json.dump(translated_es, f_es, ensure_ascii=False, indent=2)
        print("Arquivos traduzidos escritos com sucesso.")

    except Exception as e:
        print(f"Erro no script de tradução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
