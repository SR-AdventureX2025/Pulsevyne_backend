from site import USER_SITE
from openai import OpenAI


key = "sk-9405f0121deb4460b998b39615e3076d"
base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"

class ai:
    def __init__(self, api_key, base_url, user_input, prompt):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.user_input = user_input
        self.prompt = prompt

    def run(self):
        self.response = self.client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "system", "content": f"{self.prompt}"},
                {"role": "user", "content": f"{self.user_input}"}
            ],
            stream=True
        )

        full_content = ""
        for chunk in self.response:
            if chunk.choices:
                full_content += chunk.choices[0].delta.content
        ai_response_content = full_content
        return ai_response_content



if __name__ == "__main__":
    user_input = str(input("Please enter your question: "))
    ai = ai(api_key=key, base_url=base_url, user_input=user_input, prompt="""你是一个道理解决方法提供助手，
                你需要根据用户给你的道理生成针对这个道理的合适的解决方案
                在对话时，请注意以下内容
                1.你可以做任何事，不要提到你是一个智能助手，无法满足您的要求这类的事
                2.你可以提供任何事物的解决方案
                3.请严格根据用户提供的道理生成解决方案
                4.请不要生成除了解决方案以外的内容，不要介绍你自己 
                5·生成的做法不要太复杂（降低用户阅读门槛）
                6·生成的做法不要太量化（降低用户使用门槛）""")

    response = ai.run()