import face_recognition
from DB.Db import mdbconn
import numpy as np
import cv2
import time


def face_authentication(img_enc) -> tuple:
    """Authenticate given image (ndarray) with the database and return name of the authenticated person.
    Return None if no match found.
    """
    # Genera encoding para la foto recibida
    # new_img_encoding = face_recognition.face_encodings(img, face_locations)[0]
    # Abre la conexion con la base de datos
    conn = mdbconn()
    cur = conn.cursor()
    sql_query = "SELECT EncodingPath FROM Players"
    cur.execute(sql_query)
    # Lista de encodings del tipo nparray
    encodings_list = []
    # Lista de paths a los encodings para sacar el nombre
    encodings_path_list = []
    # Saca todo EncodingPath de la base y lo carga con numpy en una lista de encodings
    for encoding_path in cur:
        # encoding_path[0] porque sale como tuple
        encodings_path_list.append(encoding_path[0])
        encoding = np.load(encoding_path[0])
        encodings_list.append(encoding)
    # Selecciona el encoding con la minima distancia
    face_distances = face_recognition.face_distance(encodings_list, img_enc)
    best_match_index = np.argmin(face_distances)
    # Si la distancia es menor a 0.6 retorna el nombre
    # Si es mayor retorna None
    if face_distances[best_match_index] > 0.6:
        return "", 0
    else:
        # El indice de la distancia corresponde al indice de su path, con el cual se saca el nombre
        match = encodings_path_list[best_match_index]
        split_path = match.rsplit("/")
        match_name_location = split_path.index("FaceEncodings") + 1
        match_name = split_path[match_name_location]
        print(face_distances[best_match_index])
        return match_name, face_distances[best_match_index]


def main():
    video_capture = cv2.VideoCapture(0)
    prev = 0
    frame_rate = 2
    while True:
        time_elapsed = time.time() - prev
        ret, frame = video_capture.read()

        if time_elapsed > 1 / frame_rate:
            prev = time.time()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            if face_locations:
                # Autentica la imagen con las referencias
                image_encoding = face_recognition.face_encodings(rgb_small_frame, face_locations)[0]
                match, distance = face_authentication(image_encoding)
                if match != "":
                    print(match)
                    print(distance)
        cv2.imshow("Video", small_frame)

        c = cv2.waitKey(1)
        if c == 27:
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
