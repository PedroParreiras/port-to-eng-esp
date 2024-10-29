import os
import openai
import json
import sys

def translate_text(text, target_language):
    print(f"Traduzindo para {target_language}: {text}")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Traduza o seguinte texto para {target_language}:\n\n{text}"

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.3,
        )
        return response.choices[0].text.strip()
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
