# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Python application that pulls a low-quality prompt from LangSmith Prompt Hub, optimizes it using prompt engineering techniques, pushes it back, and evaluates it using LLM-as-Judge metrics. The task is converting bug reports into user stories (Portuguese language output).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill in API keys
```

Required `.env` variables: `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB`, `OPENAI_API_KEY` or `GOOGLE_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL`.

## Commands

```bash
# Run the full workflow in order:
python src/pull_prompts.py    # Pull v1 prompt from LangSmith Hub
python src/push_prompts.py    # Push optimized v2 prompt to LangSmith Hub (public)
python src/evaluate.py        # Evaluate against dataset, print metric scores

# Tests
pytest tests/test_prompts.py -v --tb=short
pytest tests/test_prompts.py -v -k "test_name"  # single test
```

## Architecture

**Data flow:** LangSmith Hub → `prompts/bug_to_user_story_v1.yml` → manual optimization → `prompts/bug_to_user_story_v2.yml` → LangSmith Hub (published as `{USERNAME}/bug_to_user_story_v2`) → evaluation.

**Key files:**
- [src/evaluate.py](src/evaluate.py) — orchestrates evaluation: loads `datasets/bug_to_user_story.jsonl` (15 examples), creates LangSmith dataset, pulls prompt from Hub, runs up to 10 examples, computes 5 metrics, compares against 0.9 threshold
- [src/metrics.py](src/metrics.py) — 7 LLM-as-Judge functions: `evaluate_f1_score`, `evaluate_clarity`, `evaluate_precision`, plus 4 domain-specific: `evaluate_tone_score`, `evaluate_acceptance_criteria_score`, `evaluate_user_story_format_score`, `evaluate_completeness_score`
- [src/utils.py](src/utils.py) — shared helpers: `get_llm()` / `get_eval_llm()` (selects OpenAI or Google based on env), `validate_prompt_structure()`, `extract_json_from_response()`
- [src/pull_prompts.py](src/pull_prompts.py) and [src/push_prompts.py](src/push_prompts.py) — skeletons using `langchain.hub.pull()` / `langchain.hub.push()`
- [prompts/bug_to_user_story_v1.yml](prompts/bug_to_user_story_v1.yml) — initial low-quality prompt (input variable: `{bug_report}`)
- [datasets/bug_to_user_story.jsonl](datasets/bug_to_user_story.jsonl) — 15 examples with `inputs.bug_report`, `outputs`, `metadata.complexity`

**Metrics pattern:** All metric functions call the eval LLM with a judge prompt, then `extract_json_from_response()` to parse the score (0–1 float). Scores are averaged per metric across examples.

## Success Criteria

All 4 domain metrics must reach ≥ 0.9: Tone, Acceptance Criteria, User Story Format, Completeness. The average must also be ≥ 0.9.

## Prompt v2 Requirements

`validate_prompt_structure()` enforces: required fields present, no `[TODO]` placeholders, minimum 2 techniques listed in YAML metadata. Accepted techniques: Few-shot Learning, Chain of Thought, Tree of Thought, Skeleton of Thought, ReAct, Role Prompting.

## Tests (tests/test_prompts.py)

Six tests are required (stubs exist, need implementation): `test_prompt_has_system_prompt`, `test_prompt_has_role_definition`, `test_prompt_mentions_format`, `test_prompt_has_few_shot_examples`, `test_prompt_no_todos`, `test_minimum_techniques`. All load from `prompts/bug_to_user_story_v2.yml`.
