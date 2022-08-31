import sys
import mariadb


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


def main():
    conn = mdbconn()
    # Crea un cursor para recorrer la base de datos
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pinball.Players")
    for (Id, Player, ImgPath) in cur:
        print(f"Id: {Id}, Nombre Jugador: {Player}, ImgPath: {ImgPath}")
    conn.close()


if __name__ == "__main__":
    main()
