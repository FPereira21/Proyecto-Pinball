from Db import mdbconn
from SlackBot.PostMessage import post_leaderboard


def add_score(playerid, points: int):
    """Add score to Pinball database."""
    conn = mdbconn()
    cur = conn.cursor()
    cur.execute("INSERT INTO Scoreboard (PersonID, Score) VALUES (?, ?)", (playerid, points))
    conn.commit()
    cur.execute("SELECT PersonID, Score FROM Scoreboard LIMIT 5")
    for person_id, score in cur:
        if points > score:
            print("WOWZAS")
            post_leaderboard()
            break

    conn.close()


def main():
    # ^ Insercion manual de puntos
    conn = mdbconn()
    cur = conn.cursor()
    exit_loop = True

    while exit_loop:
        playerid = input("Ingresar la ID del usurario\nSi no la sabe, escribir '?':  ")
        if playerid == "?":
            cur.execute("SELECT Id, Player FROM Players")
            for (Id, Player) in cur:
                print(f"Id: {Id} , Jugador: {Player}")
        else:
            playerscore = input("Escribe el puntaje para asignar al jugador:  ")
            add_score(playerid, int(playerscore))
        loopcond = input("Presione la tecla 'q' para salir  ")
        if loopcond.lower() == "q":
            exit_loop = False
    conn.close()


if __name__ == '__main__':
    main()
