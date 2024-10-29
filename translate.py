import os
import openai

def translate_text(text, target_language):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Traduza o seguinte texto para {target_language}:\n\n{text}"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.3,
    )
    return response.choices[0].text.strip()

def main():
    # Caminhos dos arquivos
    pt_file = 'pasta/arquivo_pt.md'
    en_file = 'pasta/arquivo_en.md'
    es_file = 'pasta/arquivo_es.md'

    # Ler o conteúdo do arquivo em português
    with open(pt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Traduzir cada linha e atualizar os arquivos correspondentes
    with open(en_file, 'w', encoding='utf-8') as en, open(es_file, 'w', encoding='utf-8') as es:
        for line in lines:
            translated_en = translate_text(line, "Inglês")
            translated_es = translate_text(line, "Espanhol")
            en.write(translated_en + '\n')
            es.write(translated_es + '\n')

if __name__ == "__main__":
    main()
