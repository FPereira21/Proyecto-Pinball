import os
from DB.Db import mdbconn


def main():
    # Se Conecta a la base
    conn = mdbconn()
    cur = conn.cursor()
    # SQL statement
    sql = "INSERT INTO Players (Player, EncodingPath) VALUES (?, ?)"
    face_encodings_path = '/home/felipe/FaceEncodings'
    players = []
    for root, dirs, files in os.walk(face_encodings_path):
        for encodings in files:
            full_path = f"{root}/{encodings}"
            players.append(full_path)
    print(players)

    for path in players:
        # Separa el path segun las barras
        folder_parent_list = path.rsplit("/")
        # Busca la carpeta FaceEncodings y agarra la siguiente para sacar el nombre del jugador
        player_name_index = folder_parent_list.index("FaceEncodings") + 1
        player_name = folder_parent_list[player_name_index]
        cur.execute(sql, (player_name, path))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
