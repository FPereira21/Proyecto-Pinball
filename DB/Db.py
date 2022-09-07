import sys
from urllib.request import Request, urlopen
import mariadb
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import numpy as np

CHANNEL_NAME = "general"


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
    text = ""
    entries = []
    cur.execute("SELECT Id, Player from Players ORDER BY Id ASC")
    player_id_list = [None]

    for Id, Player in cur:
        player_id_list.append(Player)

    cur.execute("SELECT * FROM Scoreboard ORDER BY Score DESC LIMIT 5")

    for PlayerId, Score, Date in cur:
        entries.append(f"{player_id_list[PlayerId]} - {Score} - {Date}")

    for entry in entries:
        text = text + entry + "\n"

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


def slack_detect_new_img() -> bool:
    """Recieve new list of links, compare with old, return text from new image if there is a new image"""
    # Carga el estado anterior de los links para compararlos con los nuevos
    # Si son iguales quiere decir que no se subieron imagenes.
    try:
        old_img_links = np.ndarray.tolist(np.load("/home/felipe/PinballProject/oldImgList.npy"))
    except OSError as e:
        print(e)
        old_img_links = []
    # Saca el token de la memoria
    slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
    new_img_links = get_img_links(chan_name=CHANNEL_NAME)
    if old_img_links != new_img_links:
        np.save("/home/felipe/PinballProject/oldImgList.npy", new_img_links)
        # Hace un request al link de la imagen con autencticacion el el header
        if new_img_links:
            req = Request(new_img_links[0])
        req.add_header('Authorization', f'Bearer {slack_bot_token}')
        # Lee la respuesta y la guarda como una imagen
        content = urlopen(req).read()
        f = open('/home/felipe/PinballProject/SlackImages/score.jpg', 'wb')
        f.write(content)
        f.close()
        print('True')
        return True
    else:
        print('False')
        return False


def check_for_highscore() -> bool:
    conn = mdbconn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Scoreboard ORDER BY Score DESC LIMIT 5")


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
    slack_detect_new_img()


if __name__ == "__main__":
    main()
