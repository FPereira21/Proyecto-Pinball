import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from DB.Db import mdbconn


def send_to(channel: str, text):
    """Send message to a channel in slack."""
    # ~~ANIMALADA~~
    TEMP = "xoxb-3946243101063-3960962126851-kbN69OEFt4jFDgxMrU780O4l"
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_token = TEMP
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


def main():
    TEMP = "xoxb-3946243101063-3960962126851-kbN69OEFt4jFDgxMrU780O4l"
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_token = TEMP
    # client = WebClient(token=slack_token)
    # try:
    #     response = client.chat_postMessage(channel="#random", text="Hello World!")
    #     assert response["message"]["text"] == "Hello World!"
    # except SlackApiError as e:
    #     assert e.response["ok"] is False
    #     assert e.response["error"]
    #     print(f"Got an error: {e.response['error']}")
    # send_to("random", "Holis")
    post_leaderboard()


if __name__ == '__main__':
    main()
