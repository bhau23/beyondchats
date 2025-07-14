import os
import praw
import google.generativeai as genai
from dotenv import load_dotenv
import argparse
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=gemini_api_key)

def get_reddit_instance():
    """Initializes and returns a PRAW Reddit instance."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        raise ValueError("Reddit API credentials not found in .env file")

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

def get_user_data(reddit, username, limit=100):
    """
    Scrapes comments and posts for a given Reddit user.

    Args:
        reddit: An authenticated PRAW Reddit instance.
        username: The Reddit username to scrape.
        limit: The maximum number of items to fetch for comments and posts.

    Returns:
        A dictionary containing the user's comments and posts.
    """
    redditor = reddit.redditor(username)
    data = {"comments": [], "posts": []}

    try:
        # Scrape comments
        for comment in redditor.comments.new(limit=limit):
            data["comments"].append({
                "body": comment.body,
                "permalink": f"https://www.reddit.com{comment.permalink}"
            })

        # Scrape posts
        for submission in redditor.submissions.new(limit=limit):
            data["posts"].append({
                "title": submission.title,
                "selftext": submission.selftext,
                "permalink": f"https://www.reddit.com{submission.permalink}"
            })
    except Exception as e:
        print(f"Error fetching data for user {username}: {e}")
        return None

    return data

def generate_user_persona(user_data, username):
    """
    Generates a user persona based on scraped Reddit data using the Gemini API.

    Args:
        user_data: A dictionary containing the user's comments and posts.
        username: The Reddit username.

    Returns:
        A string containing the generated user persona.
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Prepare the data for the prompt
    comments_text = "\n".join([f"- {c['body']} (Source: {c['permalink']})" for c in user_data["comments"]])
    posts_text = "\n".join([f"- {p['title']}: {p['selftext']} (Source: {p['permalink']})" for p in user_data["posts"]])

    prompt = f"""
    Based on the following Reddit comments and posts from the user '{username}', please create a detailed user persona.
    The persona should include characteristics like their interests, hobbies, approximate age, profession (if discernible), and communication style.
    For each characteristic you identify, you MUST cite the specific post or comment permalink that provided the evidence.

    **Comments:**
    {comments_text}

    **Posts:**
    {posts_text}

    **Output Format:**

    **User Persona for /u/{username}**

    **1. Characteristic:** [Description of characteristic]
       - **Citation:** [Permalink to the source comment or post]

    **2. Characteristic:** [Description of characteristic]
       - **Citation:** [Permalink to the source comment or post]

    ...and so on.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating user persona: {e}")
        return None

def save_persona_to_file(username, persona_text):
    """
    Saves the user persona to a text file.

    Args:
        username: The Reddit username, used for the filename.
        persona_text: The text of the user persona.
    """
    filename = f"{username}_persona.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(persona_text)
        print(f"Successfully saved persona to {filename}")
    except IOError as e:
        print(f"Error saving persona to file: {e}")

def extract_username_from_url(url):
    """Extracts the Reddit username from a profile URL."""
    try:
        # Handles URLs like https://www.reddit.com/user/username/
        return url.strip('/').split('/')[4]
    except IndexError:
        print("Error: Invalid Reddit user URL format.")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a user persona from a Reddit profile URL.")
    parser.add_argument("url", help="The Reddit user's profile URL.")
    parser.add_argument("--limit", type=int, default=100, help="The number of posts/comments to fetch.")
    args = parser.parse_args()

    username = extract_username_from_url(args.url)
    
    if username:
        reddit = get_reddit_instance()
        user_data = get_user_data(reddit, username, args.limit)

        if user_data:
            print(f"Successfully fetched data for user: {username}")
            print(f"Found {len(user_data['comments'])} comments and {len(user_data['posts'])} posts.")

            persona = generate_user_persona(user_data, username)
            if persona:
                print("\n--- Generated User Persona ---")
                print(persona)
                save_persona_to_file(username, persona)
            else:
                print("Could not generate user persona.")
        else:
            print(f"Failed to fetch data for user: {username}")
