import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from DB.Db import mdbconn


def send_to(channel: str, text):
    """Send message to a channel in slack."""
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)
    try:
        response = client.chat_postMessage(channel=f"{channel}", text=f"{text}")
        assert response["message"]["text"] == f"{text}"
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")


def post_leaderboard():
    """Post first 5 elements from leaderboard to slack as message."""
    conn = mdbconn()
    cur = conn.cursor()
    entries = []
    cur.execute("SELECT Id, Player from Players ORDER BY Id ASC")
    # Mas prolijo con diccionarion capaz
    player_id_list = [None]
    for Id, Player in cur:
        player_id_list.append(Player)
    cur.execute("SELECT * FROM Scoreboard ORDER BY Score DESC LIMIT 5")
    for PlayerId, Score, Date in cur:
        # print(f"{PlayerId} :: {Score}")
        entries.append(f"{player_id_list[PlayerId]} - {Score}")
        text = ""
    for e in entries:
        text = text + e + "\n"
    send_to("#random", text)
    print(text)
    conn.close()


def get_img_links():
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)

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
        history = client.conversations_history(channel=conversation_id, limit=10)
        conversation_history = history["messages"]

        for element in conversation_history:
            print(element.get("files")[0].get("url_private"))
    except SlackApiError as e:
        print(f"Error creating Conversation: {e}")


def main():
    get_img_links()
    # client = WebClient(token=slack_token)
    # try:
    #     response = client.chat_postMessage(channel="#random", text="Hello World!")
    #     assert response["message"]["text"] == "Hello World!"
    # except SlackApiError as e:
    #     assert e.response["ok"] is False
    #     assert e.response["error"]
    #     print(f"Got an error: {e.response['error']}")
    # send_to("random", "Holis")


if __name__ == '__main__':
    main()
