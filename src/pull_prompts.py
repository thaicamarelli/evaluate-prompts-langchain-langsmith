"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith(prompt_path: str, output_filename: str = None):
    """
    Faz pull de qualquer prompt do LangSmith Hub e salva localmente em YAML.

    Args:
        prompt_path: Caminho do prompt no Hub (ex: "usuario/nome-do-prompt")
        output_filename: Nome do arquivo de saída (opcional, usa o nome do prompt por padrão)

    Returns:
        True se sucesso, False caso contrário
    """
    print_section_header(f"Fazendo pull do prompt: {prompt_path}")

    try:
        prompt = hub.pull(prompt_path)
    except Exception as e:
        print(f"Erro ao fazer pull do prompt '{prompt_path}': {e}")
        return False

    system_prompt_text = ""
    user_prompt_text = ""

    for message in prompt.messages:
        role = message.__class__.__name__.lower()
        text = message.prompt.template if hasattr(message, "prompt") else str(message)
        if "system" in role:
            system_prompt_text = text
        elif "human" in role:
            user_prompt_text = text

    prompt_key = prompt_path.split("/")[-1]
    prompt_data = {
        prompt_key: {
            "description": f"Prompt {prompt_key} importado do LangSmith Hub",
            "system_prompt": system_prompt_text,
            "user_prompt": user_prompt_text,
            "source": prompt_path,
        }
    }

    filename = output_filename or f"{prompt_key}.yml"
    output_path = Path(__file__).parent.parent / "prompts" / filename
    if save_yaml(prompt_data, str(output_path)):
        print(f"✓ Prompt salvo em: {output_path}")
        return True

    return False


def main():
    required_vars = ["LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith(
        prompt_path="leonanluppi/bug_to_user_story_v1",
        output_filename="bug_to_user_story_v1.yml",
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
