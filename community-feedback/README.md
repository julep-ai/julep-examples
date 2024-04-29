# AI Dungeon Master for Dungeons & Dragons

## Introduction
This project is an example using the Julep Platform to make an Community Feedback Bot for your Discourse Communities. Julep allows stateful interaction as well as function calling between the user and the agent automatically


By [Philip](https://github.com/alt-glitch)


## Running the project
### 1. Install the dependencies

```python
poetry install
```

### 2. Get your API key
Navigate to https://platform.julep.ai to get your API key.

Copy `.env.example` to `.env` and set the API key there.

### 3. Run the project
```bash
chainlit run app.py
```