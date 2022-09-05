import os
import face_recognition
import numpy
from DB.Db import mdbconn


def encodings_creation(root_path: str):

    # Recorre el directorio y agrega los paths a una lista
    photo_list = []
    photo_name = []
    for root, dirs, files in os.walk(root_path):
        for name in files:
            photo_list.append(f"{root}/{name}")
            photo_name.append(name)

    # Genera los encodings y los guarda en una carpeta
    for image_path, image_name in zip(photo_list, photo_name):
        # Carga la imgaen
        img = face_recognition.load_image_file(image_path)
        locations = face_recognition.face_locations(img)
        # Si encuentra caras en la imagen guarda los encodings,
        # si no encuentra menciona el nombre del que dio error
        if locations:
            tmp_img_encoding = face_recognition.face_encodings(img, locations)[0]
            name_no_ext = os.path.splitext(image_name)[0]
            if not os.path.exists(f"/home/felipe/PinballProject/FaceEncodings/{name_no_ext}"):
                os.mkdir(f"/home/felipe/PinballProject/FaceEncodings/{name_no_ext}")
            print(f"/home/felipe/PinballProject/FaceEncodings/{name_no_ext}")
            numpy.save(f"/home/felipe/PinballProject/FaceEncodings/{name_no_ext}/encoding{name_no_ext}", tmp_img_encoding)
        else:
            print(f"Error con {image_name}")


def encodings_upload():
    # Se Conecta a la base
    conn = mdbconn()
    cur = conn.cursor()
    # SQL statement
    sql = "INSERT INTO Players (Player, EncodingPath) VALUES (?, ?)"
    face_encodings_path = '/home/felipe/PinballProject/FaceEncodings'
    player_encoding_path = []
    for root, dirs, files in os.walk(face_encodings_path):
        for encodings in files:
            full_path = f"{root}/{encodings}"
            player_encoding_path.append(full_path)
    print(player_encoding_path)

    for path in player_encoding_path:
        # Separa el path segun las barras
        folder_parent_list = path.rsplit("/")
        # Busca la carpeta FaceEncodings y agarra la siguiente para sacar el nombre del jugador
        player_name_index = folder_parent_list.index("FaceEncodings") + 1
        player_name = folder_parent_list[player_name_index]
        cur.execute(sql, (player_name, path))
    conn.commit()
    conn.close()


def main():
    root_path = input("Ingrese la ruta absoluta de la carpeta que contenga las fotos\n(Enter para default):")
    if root_path == "":
        root_path = "/home/felipe/PinballProject/PinballFaces"
    encodings_creation(root_path)
    upload_confirm = input("¿Desea subir los nuevos encodings a la base de datos? [Y/N]")
    if upload_confirm.lower() == "y":
        encodings_upload()


if __name__ == '__main__':
    main()
