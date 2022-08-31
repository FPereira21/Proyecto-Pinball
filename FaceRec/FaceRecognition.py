import face_recognition
from DB.Db import mdbconn
import numpy as np


def face_authentication(img: np.ndarray) -> str:
    """Authenticate given image (ndarray) with the database and return name of the authenticated person.
    Always returns something.
    """
    new_img_encoding = face_recognition.face_encodings(img)[0]

    conn = mdbconn()
    cur = conn.cursor()
    sql_query = "SELECT EncodingPath FROM Players"
    cur.execute(sql_query)
    encodings_list = []
    encodings_path_list = []
    for encoding_path in cur:
        # encoding_path[0] porque sale como tuple
        encodings_path_list.append(encoding_path[0])
        encoding = np.load(encoding_path[0])
        encodings_list.append(encoding)
    face_distances = face_recognition.face_distance(encodings_list, new_img_encoding)
    best_match_index = np.argmin(face_distances)
    match = encodings_path_list[best_match_index]
    split_path = match.rsplit("/")
    match_name_location = split_path.index("FaceEncodings") + 1
    match_name = split_path[match_name_location]
    return match_name


def main():
    pinie = face_recognition.load_image_file("/home/felipe/PinballFaces/Riki/Riki.jpg")
    face_authentication(pinie)


if __name__ == '__main__':
    main()
