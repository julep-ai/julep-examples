# %%
import requests
import aiohttp
import os
from dotenv import find_dotenv, load_dotenv
from typing import Literal
import chainlit as cl
from prompts import INSTRUCTIONS, SITUATION_PROMPT
from tools import tools
from julep import Client
import json
from pprint import pprint

load_dotenv(".env")
api_key = os.environ.get("JULEP_API_KEY")
base_url = os.environ.get("JULEP_API_URL")

COMMUNITY_URL = "https://community.openai.com/"
client = Client(api_key=api_key, base_url=base_url)


# %%
def retrieve_agent():
    agents = client.agents.list(metadata_filter={"name": "Archy"})
    if not agents:
        print("[!] Creating a new agent")
        agent = create_agent()
        return agent
    else:
        return agents[0]


def create_agent():
    agent = client.agents.create(
        name="Archy",
        about="An agent that posts and comments on Discourse forums by filtering for the provided topic",
        instructions=INSTRUCTIONS,
        model="gpt-4",
        default_settings={
            "temperature": 0.5,
            "top_p": 1,
            "min_p": 0.01,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "length_penalty": 1.0,
        },
        metadata={"name": "Archy"},
        tools=tools,
        max_tokens=8192
    )
    return agent


def retrieve_session(agent_id, user_id):
    sessions = client.sessions.list(
        metadata_filter={"agent_id": agent_id, "user_id": user_id}
    )
    if not sessions:
        print("[!] Creating a new session")
        session = create_session(agent_id, user_id)
        return session
    else:
        return sessions[0]


def create_session(agent_id: str, user_id: str):
    session = client.sessions.create(
        user_id=user_id,
        agent_id=agent_id,
        situation=SITUATION_PROMPT,
        metadata={"agent_id": agent_id, "user_id": user_id},
    )
    return session


def retrieve_user():
    users = client.users.list(metadata_filter={"name": "Sid"})
    if not users:
        print("[!] Creating a new user")
        user = create_user()
        return user
    else:
        return users[0]


def create_user():
    user = client.users.create(
        name="Sid",
        about="A product engineer at Acme, working with Archy to validate and improve the product",
        metadata={"name": "Sid"},
    )
    return user


# %%
@cl.on_chat_start
def chat_start():
    agent = retrieve_agent()
    user = retrieve_user()
    session = retrieve_session(agent.id, user.id)

    cl.user_session.set("agent_id", agent.id)
    cl.user_session.set("user_id", user.id)
    cl.user_session.set("session_id", session.id)

    print("[!] A new chat session has been started")
    print(f"Agent: {agent.id}")
    print(f"Session: {session.id}")
    print(f"User: {user.id}")


@cl.on_message
async def on_message(message: cl.Message):
    session_id = cl.user_session.get("session_id")
    response = client.sessions.chat(
        session_id=session_id,
        messages=[{"role": "user", "content": message.content}],
        recall=True,
        remember=True,
    )
    agent_response = response.response[0][0]
    if agent_response.role.value == "assistant":
        await cl.Message(content=agent_response.content).send()
    elif agent_response.role.value == "function_call":
        tool_call = json.loads(agent_response.content)
        args = json.loads(
            tool_call.get("arguments", "{}")
        )  # Parse the JSON string into a dictionary
        tool = tool_call.get("name", "")
        if tool == "search_forum":
            pprint(tool_call)
            posts = await search(**args)
            tool_response = client.sessions.chat(
                session_id=session_id,
                messages=[{"role": "assistant", "content": json.dumps(posts)}],
                recall=True,
                remember=True,
            )
            await cl.Message(content=tool_response.response[0][0].content).send()
        elif tool == "read_post":
            pprint(tool_call)
            post = await read_post(**args)
            tool_response = client.sessions.chat(
                session_id=session_id,
                messages=[{"role": "assistant", "content": json.dumps(post)}],
                recall=True,
                remember=True
            )
            await cl.Message(content=tool_response.response[0][0].content).send()


@cl.step
async def read_post(post_id: int):
    res = requests.get(f"{COMMUNITY_URL}/posts/{post_id}.json", allow_redirects=True)
    post = res.json()
    filtered_post = {
        key: post[key] for key in ["id", "username", "raw", "topic_slug"]
    }
    filtered_post["url"] = f"{COMMUNITY_URL}/p/{post['id']}"
    return filtered_post


@cl.step
async def search(
    query: str,
    order: Literal["latest", "likes", "views", "latest_topic"],
    max_views: int = 10000,
    min_views: int = 500,
    category: str = None,
):
    res = requests.get(
        url=f"{COMMUNITY_URL}/search.json",
        params={
            "q": query,
            "category": category,
            "order": order,
            "min_views": min_views,
            "max_views": max_views,
        },
    )
    filtered_posts = {"posts": []}
    posts = res.json()
    # await parse_search_results(res.json())
    for post in posts.get("posts", []):
        filtered_post = {
            key: post[key] for key in ["id", "blurb", "like_count", "username"] if key in post
        }
        filtered_post["url"] = f"{COMMUNITY_URL}/p/{post['id']}"
        filtered_posts["posts"].append(filtered_post)
    return filtered_posts


#####
# - it will extensively ask what you exactly you need to search for
# - it will extensively ask what you exactly need to post about
# - comes up with good keywords and filters
# - gets approval from user (advanced) and corrects the filters
# - searches for posts with the filter.
# - compiles a list of viable posts to read
# - reads each post and comes up with a viable response to it
# - gives the post + response to the user
# - posts the response to the post
#####


####
# THOUGHTS
# - prototyping prompts is harder because constantly updating or deleting/creating a new agent/session is annoying
# - need to create an agent/session for each prompt and then test it
# - either keep updating the agent/session or create a new one for each prompt and delete the older
####

# %%
