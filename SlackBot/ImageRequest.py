import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def main():
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)

    conversation_history = []
    channel_name = 'general'
    conversation_id = None
    try:
        for result in client.conversations_list():
            if conversation_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    conversation_id = channel["id"]
                    print(f"Found conversation id: {conversation_id}")
                    break
    except SlackApiError as e:
        print(f"Error: {e}")
    try:
        history = client.conversations_history(channel=conversation_id)
        conversation_history = history["messages"]
        for el in conversation_history:
            print(el)
    except SlackApiError as e:
        print(f"Error creating Conversation: {e}")


if __name__ == '__main__':
    main()
