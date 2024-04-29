tools = [
    {
        "type": "function",
        "function": {
            "name": "search_forum",
            "description": "Retrieves a list of posts from a forum for the given search parameters. The search parameters should include the search query and additional parameters such as: category, order, minimum views, and maximum views. The tool will return a list of posts based on the search query and additional parameters. It should be used when the user asks to start monitoring the forum.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to be used to search for posts in the forum.",
                    },
                    "order": {
                        "type": "string",
                        "description": "The order in which the posts should be sorted. Possible values are: latest, likes, views, latest_topic.",
                    },
                    "min_views": {
                        "type": "number",
                        "description": "The minimum number of views a post should have to be included in the search results.",
                    },
                    "max_views": {
                        "type": "number",
                        "description": "The maximum number of views a post should have to be included in the search results.",
                    },
                },
                "required": ["query", "order", "min_views", "max_views", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_post",
            "description": "Retrieves the details of a specific post from the forum. The tool should take the post ID as input and return the details of the post including the content, author, date, and other relevant information. It should be used when the user asks to read a specific post.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "number",
                        "description": "The ID of the post to be read.",
                    },
                },
                "required": ["post_id"]
            }
        }
    }
]
