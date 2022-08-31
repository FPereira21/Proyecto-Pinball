import os
import face_recognition
import numpy


def main():
    root_path = input("Ingrese la ruta absoluta de la carpeta que contenga las fotos\n(Enter para default):")
    if root_path == "":
        root_path = "/home/felipe/PinballFaces"
    # Recorre el directorio
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
        # Si encuentra caras en la imagen guarda los encodings
        # Si no encuentra menciona el nombre del que dio error
        if locations:
            tmp_img_encoding = face_recognition.face_encodings(img, locations)[0]
            name_no_ext = os.path.splitext(image_name)[0]
            if not os.path.exists(f"/home/felipe/FaceEncodings/{name_no_ext}"):
                os.mkdir(f"/home/felipe/FaceEncodings/{name_no_ext}")
            print(f"/home/felipe/FaceEncodings/{name_no_ext}")
            numpy.save(f"/home/felipe/FaceEncodings/{name_no_ext}/encoding{name_no_ext}", tmp_img_encoding)
        else:
            print(f"Error con {image_name}")


if __name__ == '__main__':
    main()
