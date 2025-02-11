# prompt/prompt_loader.py
import os
import json

def load_prompt(prompt_filename: str, prompt_dir: str = "./prompt") -> str:
    """
    주어진 파일 이름의 프롬프트 텍스트를 prompt 폴더에서 읽어 반환합니다.
    예) "summarization_positive_prompt.txt"
    """
    file_path = os.path.join(prompt_dir, prompt_filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_fewshot(fewshot_filename: str, prompt_dir: str = "./prompt") -> list:
    """
    주어진 파일 이름의 few-shot 예시를 JSON 파일로부터 읽어 반환합니다.
    예) "summarization_positive_fewshot.json"
    """
    file_path = os.path.join(prompt_dir, fewshot_filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
