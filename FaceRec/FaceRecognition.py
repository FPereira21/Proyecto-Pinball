import face_recognition
from DB.Db import mdbconn
import numpy as np
import cv2
import time
from TextRec.OCR import score_listening_mode


def face_authentication(img_enc) -> tuple:
    """Authenticate faces from the given image (ndarray) with the database and return name and distance
    of the authenticated person.
    Return None if no match found.
    """
    # Abre la conexion con la base de datos
    conn = mdbconn()
    cur = conn.cursor()
    sql_query = "SELECT Id, EncodingPath FROM Players"
    cur.execute(sql_query)
    # Lista de encodings del tipo nparray
    encodings_list = []
    # Lista de paths a los encodings para sacar el nombre
    encodings_path_list = []
    # Saca el EncodingPath de los Players de la base y carga los .npy en encoding_list
    for player_id, encoding_path in cur:
        encodings_path_list.append([player_id, encoding_path])
        encoding = np.load(encoding_path)
        encodings_list.append(encoding)
    # Selecciona el encoding con la minima distancia
    face_distances = face_recognition.face_distance(encodings_list, img_enc)
    best_match_index = np.argmin(face_distances)
    # Si la distancia es menor a 0.6 retorna el nombre
    # Si es mayor retorna None
    if face_distances[best_match_index] > 0.6:
        return "", -1
    else:
        # El indice de la distancia corresponde al indice de su path, con el cual se saca el nombre
        print(encodings_path_list[best_match_index])
        match_path = encodings_path_list[best_match_index][1]
        split_path = match_path.rsplit("/")
        match_name_location = split_path.index("FaceEncodings") + 1
        match_name = split_path[match_name_location]
        print(face_distances[best_match_index])
        # Retorna el nombre del match y su id
        return match_name, encodings_path_list[best_match_index][0]


def main():
    # Activa la camara y setea los fps
    video_capture = cv2.VideoCapture(0)
    prev = 0
    frame_rate = 1

    while True:
        # Siempre lee la camara para no llenar el buffer
        time_elapsed = time.time() - prev
        ret, frame = video_capture.read()
        # Si pasan 1/fps segundos busca las posiciones de las carask
        if time_elapsed > 1 / frame_rate:
            prev = time.time()
            # Achica el tamanio de la imagen y la convierte de BGR a RGB porque cv2 es alto ladilla
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            # Si detecta caras en la imagen, le aplica el reconocimiento
            if face_locations:
                # Autentica la imagen con las referencias
                current_image_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)[0]
                match, player_id = face_authentication(current_image_encodings)
                if match != "":
                    score_listening_mode(player_id)
                    print(match)
                    print(player_id)

        for (top, right, bottom, left) in face_locations:
            top *= 4
            right *= 4
            left *= 4
            bottom *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, match, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

        cv2.imshow("Video", frame)

        c = cv2.waitKey(1)
        if c == 27:
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
