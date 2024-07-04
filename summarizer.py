from openai import OpenAI
import os

def text_summ(prompt):
    OPENAI_KEY= os.getenv('OPENAI')
    client = OpenAI(api_key=OPENAI_KEY)
    
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      response_format={ "type": "json_object" },
      messages=[
        {"role": "system", "content": "You are a powerful summarizer that cleans a text paragraph and return its summary in json"},
        {"role": "user", "content": prompt}
      ]
    )
    return (response.choices[0].message.content)