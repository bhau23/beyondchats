# Reddit User Persona Generator

This script generates a user persona based on a Reddit user's profile, analyzing their comments and posts. It uses the Reddit API to fetch data and a large language model (Gemini) to build the persona.

## Features

- Scrapes a user's latest comments and posts.
- Generates a detailed user persona with citations.
- Outputs the persona to a text file named `{username}_persona.txt`.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/reddit-persona-generator.git
    cd reddit-persona-generator
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    Create a file named `.env` in the root of the project and add the following credentials:
    ```
    REDDIT_CLIENT_ID=your_reddit_client_id
    REDDIT_CLIENT_SECRET=your_reddit_client_secret
    REDDIT_USER_AGENT=your_reddit_user_agent
    GEMINI_API_KEY=your_gemini_api_key
    ```
    - To get Reddit API credentials, create an app on the [Reddit apps page](https://www.reddit.com/prefs/apps).
    - To get a Gemini API key, visit the [Google AI for Developers](https://aistudio.google.com/app/apikey) page.

## Usage

Run the script from the command line, passing the Reddit user's profile URL as an argument:

```bash
python main.py <reddit_profile_url>
```

**Example:**

```bash
python main.py https://www.reddit.com/user/kojied/
```

This will create a file named `kojied_persona.txt` in the project directory with the generated user persona.

### Optional Arguments

-   `--limit`: Specify the number of comments and posts to fetch. The default is 100.
    ```bash
    python main.py https://www.reddit.com/user/kojied/ --limit 50
