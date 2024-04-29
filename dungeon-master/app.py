import chainlit as cl
from julep import AsyncClient
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(".env")
api_key = os.environ.get("JULEP_API_KEY")
base_url = os.environ.get("JULEP_API_URL")

client = AsyncClient(api_key=api_key, base_url=base_url)


async def retrieve_agent():
    agents = await client.agents.list(metadata_filter={"role": "GM"})
    if not agents:
        print("[!] Creating a new agent")
        agent = await create_agent()
        return agent
    else:
        return agents[0]


async def create_agent():
    agent = await client.agents.create(
        name="The GM",
        about="The GM is a veteran game master for the tabletop role playing games Dungeons and Dragons 5th Edition, Call of Cthulhu 7th edition, Starfinder, Pathfinder 2nd Edition, Age of Sigmar Soulbound, Shadowrun, Cyberpunk, Vampire the Masquerade and many more. The GM has been running games for over 10 years and has a passion for creating immersive and engaging stories for their players. The GM is excited to bring their storytelling skills to the world of AI and help users create their own epic adventures.",
        default_settings={
            "frequency_penalty": 0.0,
            "length_penalty": 1.0,
            "presence_penalty": 0.0,
            "repetition_penalty": 1.0,
            "temperature": 0.75,
            "top_p": 1.0,
            "min_p": 0.01,
        },
        model="gpt-4-turbo",
        instructions=[
            "You will first ask what system to play and what theme the user would like to play",
            "You will prepare a campaign complete with story, NPCs, quests and encounters",
            "Your story will start from level 1 and go up to level 5",
            "At the start of the game you will introduce the players to the world and the story",
            "Depending on the system, you will ask the user to create an appropriate character and provide a backstory",
            "You may suggest a pre-generated character for the user to play",
            "You will always ask the user what they would like to do next and provide options for them to choose from",
            "You will do the dice rolls and provide the results of their actions to the user",
            "You will adjust the story based on the user's actions and choices",
            "Your story will end with a final boss fight and a conclusion to the story",
        ],
        metadata={"role": "GM"}
    )
    return agent


async def retrieve_session(agent_id, user_id):
    sessions = await client.sessions.list(
        metadata_filter={"agent_id": agent_id, "user_id": user_id}
    )
    if not sessions:
        print("[!] Creating a new session")
        session = await create_session(agent_id, user_id)
        return session
    else:
        return sessions[0]


async def create_session(agent_id: str, user_id: str):
    session = await client.sessions.create(
        user_id=user_id,
        agent_id=agent_id,
        situation="You are starting a new campaign. What system would you like to play and what theme would you like to explore?",
    )
    return session


async def retrieve_user():
    users = await client.users.list(metadata_filter={"name": "John"})
    if not users:
        print("[!] Creating a new user")
        user = await create_user()
        return user
    else:
        return users[0]


async def create_user():
    user = await client.users.create(
        name="John",
        about="TTRPG player",
        metadata={"name": "John"}
    )
    return user


@cl.on_chat_start
async def start():
    agent = await retrieve_agent()
    user = await retrieve_user()
    session = await retrieve_session(agent.id, user.id)
    cl.user_session.set("agent_id", agent.id)
    cl.user_session.set("user_id", user.id)
    cl.user_session.set("session_id", session.id)

    response = await client.sessions.chat(
        session_id=session.id,
        messages=[
            {
                "content": "Greet the user and ask what TTRPG system they would like to play or ask to continue from a previous campaign",
                "role": "system",
            }
        ],
        recall=True,
        remember=True,
        max_tokens=1000,
    )
    await cl.Message(
        content=response.response[0][0].content,
    ).send()


@cl.on_message
async def main(message: cl.Message):
    session_id = cl.user_session.get("session_id")
    response = await client.sessions.chat(
        session_id=session_id,
        messages=[{"content": message.content, "role": "user"}],
        recall=True,
        remember=True,
        max_tokens=1000,
    )
    print(response.response[0][0].content)
    # Send a response back to the user
    await cl.Message(
        content=response.response[0][0].content,
    ).send()
