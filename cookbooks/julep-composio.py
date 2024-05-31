import os
import textwrap
from julep import Client
from dotenv import load_dotenv
import json
from composio_julep import Action, ComposioToolSet, App

load_dotenv()
toolset = ComposioToolSet()
composio_tools = toolset.get_actions(
    actions=[Action.GITHUB_ACTIVITY_LIST_REPO_S_STARRED_BY_AUTHENTICATED_USER]
)
client = Client(
    api_key=""
)

name = "Sawradip"
about = "Sawradip is a software developer with a passion for solving complex problems and a keen interest in AI. You have the ability to write code and execute it."
default_settings = {
    "temperature": 0.7,
    "top_p": 1,
    "min_p": 0.01,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "length_penalty": 1.0,
    "max_tokens": 2000,
}

agent = client.agents.create(
    name=name,
    about=about,
    default_settings=default_settings,
    model="gpt-4-turbo",
    tools=composio_tools,
)


user = client.users.create(
    name="Jessica",
    about="Tech recruiter specializing in identifying talented developers.",
)

situation_prompt = """Jessica, a tech recruiter, is conducting an interview with Sawradip, a promising software developer. They discuss various technical topics, with a focus on problem-solving and algorithm design."""

session = client.sessions.create(
    user_id=user.id, agent_id=agent.id, situation=situation_prompt
)

user_msg = "Can you get all starred repos for me"

response = client.sessions.chat(
    session_id=session.id,
    messages=[
        {
            "role": "user",
            "content": user_msg,
            "name": "Jessica",
        }
    ],
    recall=True,
    remember=True,
)


response = toolset.handle_tool_calls(client, session.id, response)  #
print(response.response[0][0].content)