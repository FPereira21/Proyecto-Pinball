from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from DB.Db import mdbconn


def main():

    # Lista para contener a todos los nombres
    members = []

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

    try:
        slackrp = client.users_list()  # Recibe un objeto del tipo slack response
        for member in slackrp.data['members']:  # Agarra el JSON con el .data
            members.append(member['real_name'])  # Guarda en una lista el nombre real de cada usuario
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")

    # Conecta con la base de datos
    conn = mdbconn()

    # Crea un cursor para moverse en la base y ejecutar los comandos
    cur = conn.cursor()
    for nombre in members:
        cur.execute("INSERT INTO Pinball.Jugadores (Jugador) VALUES (?)", [nombre])

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
