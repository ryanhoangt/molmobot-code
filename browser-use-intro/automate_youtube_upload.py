from browser_use import Agent, ChatOpenAI, Browser
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def main():
    task = "I have a video at /Users/hoang/Developer/molmobot-code/browser-use-intro/video.mp4 file in the current directory, could you please help me upload it to my YouTube channel as a short video? I have logged in for you. Please set it to Private and add some dummy title and description so I can adjust later."
    
    # Connect to the existing Chrome browser
    browser = Browser(
        cdp_url='http://localhost:9222'
    )
    llm = ChatOpenAI(model="o3")
    agent = Agent(task=task, llm=llm, browser=browser)

    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())