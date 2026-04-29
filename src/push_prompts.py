"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    repo_full_name = f"{username}/{prompt_name}"

    print_section_header(f"Fazendo push do prompt: {repo_full_name}")

    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    try:
        hub.push(repo_full_name, prompt_template, new_repo_is_public=True)
        print(f"Prompt publicado com sucesso: {repo_full_name}")
        return True
    except Exception as e:
        print(f"Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    prompts_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    data = load_yaml(str(prompts_path))
    if not data:
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_key)
    if not prompt_data:
        print(f"Chave '{prompt_key}' não encontrada no YAML.")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("Prompt validado com sucesso.")

    success = push_prompt_to_langsmith(prompt_key, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
