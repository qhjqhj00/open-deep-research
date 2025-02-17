import json
import pickle
import pandas as pd
import pathlib
import os
import requests
import duckduckgo_search as DDGS
from typing import Optional
import re
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def save_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            json.dump(item, file, ensure_ascii=False)
            file.write('\n')

def load_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_txt(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def load_pickle(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)

def save_pickle(data, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)

def csv2json(file_path, sep=','):
    df = pd.read_csv(file_path, sep=sep, engine='python')
    json_data = df.to_dict(orient='records')
    return json_data

def json2csv(json_list, out_path):
    df = pd.DataFrame(json_list)
    df.to_csv(out_path, index=False)

def makedirs(path):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return path

class DuckDuckGoSearchEngine:
    def __init__(self, api_key, cse_id, cache_file="data/search_cache.pkl"):
        self._cache_file = cache_file
        self._cache = None
        self._api_key = api_key
        self._cse_id = cse_id

        if os.path.exists(self._cache_file):
            self._cache = load_pickle(self._cache_file)
        else:
            self._cache = {}

    def search(self, query):
        require_search = True
        result_list = []
        if self._cache:
            if query in self._cache:
                print(f"Use cached results for {query}...")
                result_list = self._cache[query]
                require_search = False
        if require_search:
            query_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={self._api_key}&cx={self._cse_id}"
            response = requests.get(query_url)
            response.raise_for_status()
            response_json = response.json()
            for item in response_json.get("items", []):
                title = item.get("title")
                link = item.get("link")
                snippet = item.get("snippet")
                
                result_list.append({
                    "title": title,
                    "snippet": snippet,
                    "url": link
                })
            self._cache[query] = result_list
            save_pickle(self._cache, self._cache_file)

        return result_list

def extract_text_from_url(url, use_jina=True, jina_api_key=None, snippet: Optional[str] = None):
    if use_jina:
        jina_headers = {
            'Authorization': f'Bearer {jina_api_key}',
            'X-Return-Format': 'markdown',
            # 'X-With-Links-Summary': 'true'
        }
        response = requests.get(f'https://r.jina.ai/{url}', headers=jina_headers).text
        pattern = r"\(https?:.*?\)|\[https?:.*?\]"
        text = re.sub(pattern, "", response).replace('---','-').replace('===','=').replace('   ',' ').replace('   ',' ')
        return text
    else:
        raise NotImplementedError("Not implemented yet")
    