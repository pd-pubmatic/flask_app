from openai import OpenAI

class OpenAIAssistant:
    def __init__(self, api_key, base_url):
        api_key = "sk-m83cURgJn-gZYK-sKukLUw"
        base_url = "https://llm.pubmatic.com/v1"
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
    def gpt_4_min_response(self,prompt):

        response = self.client.chat.completions.create(
            messages=prompt,
            model="(paid) gpt-4o-mini",
            temperature=0.5,
        )
        
        return response.choices[0].message.content.strip()

    def gpt_4_image_response(self,prompt):
                
        response = self.client.chat.completions.create(
            messages=prompt,
            model="(paid) gpt-4o",
            temperature=0.7,
        )
        
        return response.choices[0].message.content.strip()