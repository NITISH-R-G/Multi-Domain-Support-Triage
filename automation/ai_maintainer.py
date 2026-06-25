import os
import json
import requests
from openai import OpenAI


def get_event_data(event_path):
    with open(event_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_ai_response(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "AI Maintainer: OpenAI API key is missing. Cannot generate a response."

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior staff engineer AI maintainer for the HackerRank Orchestrate repository. You review issues, pull requests, and answer questions. Be helpful, polite, and technical. If it's a pull request, evaluate code quality and architecture. If it's an issue, suggest fixes or ask clarifying questions. Keep it concise.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Maintainer: Error generating response: {str(e)}"


def post_comment(repo, issue_number, token, body):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"body": body}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 201:
            print("Successfully posted comment.")
        else:
            print(
                f"Failed to post comment. Status: {response.status_code}, Response: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Request failed when posting comment: {e}")


def extract_pr_details(event_data, action):
    if "pull_request" in event_data and action in ["opened", "edited"]:
        return (
            event_data["pull_request"]["number"],
            event_data["pull_request"]["title"],
            event_data["pull_request"]["body"] or "",
            "Pull Request",
        )
    return None


def extract_issue_only_details(event_data, action):
    if (
        "issue" in event_data
        and action in ["opened", "edited"]
        and "pull_request" not in event_data["issue"]
    ):
        return (
            event_data["issue"]["number"],
            event_data["issue"]["title"],
            event_data["issue"]["body"] or "",
            "Issue",
        )
    return None


def extract_comment_details(event_data, action):
    if "comment" in event_data and action == "created":
        if event_data["comment"]["user"]["login"] == "github-actions[bot]":
            return None
        return (
            event_data["issue"]["number"],
            event_data["issue"]["title"],
            event_data["comment"]["body"],
            "Comment",
        )
    return None


def extract_issue_details(event_data, action):
    pr_details = extract_pr_details(event_data, action)
    if pr_details:
        return pr_details

    issue_details = extract_issue_only_details(event_data, action)
    if issue_details:
        return issue_details

    comment_details = extract_comment_details(event_data, action)
    if comment_details:
        return comment_details

    return None, "", "", ""


def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")

    if not event_path or not repo or not token:
        print("Missing required environment variables.")
        return

    event_data = get_event_data(event_path)
    action = event_data.get("action")

    issue_number, title, body, event_type = extract_issue_details(event_data, action)

    if not issue_number:
        print("Could not determine issue number or unsupported event.")
        return

    prompt = f"Review the following {event_type}:\n\nTitle: {title}\n\nBody: {body}\n\nPlease provide a helpful response as the AI Maintainer."
    print(f"Generating response for {event_type} #{issue_number}...")
    ai_response = generate_ai_response(prompt)

    formatted_response = f"🤖 **AI Maintainer**\n\n{ai_response}"
    post_comment(repo, issue_number, token, formatted_response)


if __name__ == "__main__":
    main()
