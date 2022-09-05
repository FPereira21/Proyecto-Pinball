import sys
import mariadb
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def mdbconn():
    """Establish connection to mariadb Pinball database, returns connection object."""
    try:
        conn = mariadb.connect(
            user="felipe",
            password="password",
            host="localhost",
            port=3306,
            database="Pinball"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB platform: {e}")
        sys.exit(1)
    return conn


def add_score(playerid, points: int):
    """Add score to Pinball database."""
    conn = mdbconn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Scoreboard (PersonID, Score) VALUES (?, ?)", (playerid, points))
    conn.commit()
    cur.execute("SELECT PersonID, Score FROM Scoreboard LIMIT 5")
    for person_id, score in cur:
        if points > score:
            post_leaderboard()
            break

    conn.close()


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


def get_img_links(chan_name: str) -> list:
    """Request all conversations from a select channel in Slack API, return only the image links."""
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=slack_token)
    channel_name = chan_name
    conversation_id = None

    image_links = []
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
            # element.get devuelve None si no encuentra la entrada
            if element.get("files"):
                image_links.append(element.get("files")[0].get("url_private"))

    except SlackApiError as e:
        print(f"Error creating Conversation: {e}")
    return image_links


def main():
    # Insercion manual de puntos
    # conn = mdbconn()
    # cur = conn.cursor()
    # exit_loop = True
    #
    # while exit_loop:
    #     playerid = input("Ingresar la ID del usurario\nSi no la sabe, escribir '?':  ")
    #     if playerid == "?":
    #         cur.execute("SELECT Id, Player FROM Players")
    #         for (Id, Player) in cur:
    #             print(f"Id: {Id} , Jugador: {Player}")
    #     else:
    #         playerscore = input("Escribe el puntaje para asignar al jugador:  ")
    #         add_score(playerid, int(playerscore))
    #     loopcond = input("Presione la tecla 'q' para salir  ")
    #     if loopcond.lower() == "q":
    #         exit_loop = False
    # conn.close()
    get_img_links()


if __name__ == "__main__":
    main()
