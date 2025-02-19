from typing import List
from src.agent import Agent
from src.utils import load_json
from src.utils import extract_text_from_url, DuckDuckGoSearchEngine
from src.prompt import *
import json
from collections import defaultdict

config = load_json("config.json")

agent = Agent(
    model="openai/gpt-4o-mini",
    source="openrouter",
    endpoint=config["openrouter"]["base_url"],
    api_key=config["openrouter"]["api_key"]
)

search_engine = DuckDuckGoSearchEngine(
    config["search_engine"]["google"]["api_key"],
    config["search_engine"]["google"]["cse_id"]
)

class Researcher:
    def __init__(
            self):
        self.agent = agent
        self.search_engine = search_engine
        self.jina_api_key = config["jina"]["api_key"]
        self.trajectories = defaultdict(lambda: defaultdict(dict))
    
    def __call__(self, query: str, width: int = 3, depth: int = 3) -> List[str]:
        plan = json.loads(self.plan(query))
        print(plan)
        for key, value in plan.items():
            for item in value:
                print(key, item)
                sub_query = agent.chat_completion(sub_query_prompt.format(query=query, section=key, subsection=item))
                print(sub_query)
                self.trajectories[key][item]["sub_query"] = sub_query
                search_results = self.search(sub_query)
                print(search_results[0])
                self.trajectories[key][item]["search_results"] = search_results
                top_1_url = search_results[0]["url"]
                top_1_content = self.read(top_1_url)
                print(top_1_content)
                self.trajectories[key][item]["knowledge"] = top_1_content
                generated_content = self.agent.chat_completion(general_prompt.format(query=query, user_input=top_1_content))
                print(generated_content)
                self.trajectories[key][item]["content"] = generated_content
        
        
        with open("demo/test.json", "w") as f:

            json.dump(self.trajectories, f, indent=4, ensure_ascii=False)
        self.markdown_content("demo/test.md")        # search_results = self.search(query, width, depth)
        # print(search_results)
        # return self.trajectories
    
    def markdown_content(self, path: str) -> str:
        markdown_content = ""
        for key, value in self.trajectories.items():
            markdown_content += f"# {key}\n"
            for item, content in value.items():
                markdown_content += f"## {item}\n"
                markdown_content += content["content"]
        with open(path, "w") as f:
            f.write(markdown_content)
        return markdown_content
    
    def search(self, query: str, width: int = 3, depth: int = 3) -> List[str]:
        search_results = self.search_engine.search(query)
        return search_results
    
    def read(self, url: str) -> str:
        text = extract_text_from_url(url, jina_api_key=self.jina_api_key)
        return text
    
    def plan(self, query: str, width: int = 3, depth: int = 3) -> List[str]:
        plan = self.agent.chat_completion(report_outline_prompt.format(query=query, width=width))
        return plan

    def summarize(self, urls: List[str]) -> str:
        pass

    def reflect(self, query: str, summary: str) -> str:
        pass
    

if __name__ == "__main__":
    researcher = Researcher()
    researcher("introduce deep research")    