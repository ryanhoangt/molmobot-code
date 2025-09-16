import os
from dotenv import load_dotenv
from browser_use_sdk import BrowserUse

load_dotenv()


client = BrowserUse(api_key=os.getenv("BROWSER_USE_API_KEY"))

task = client.tasks.create_task(
  llm="o3",
  task=f"""
You are a web search assistant.
  
I would like to buy a DJI Tello drone, but it seems to be out of stock in many places. Could you help me find a reliable online store that has it in stock and offers international shipping to the Vietnam? Please also provide the price and shipping cost.
"""
)

result = task.complete()
    
result.output