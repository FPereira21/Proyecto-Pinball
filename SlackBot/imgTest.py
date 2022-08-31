import face_recognition
import urllib.request


img = face_recognition.load_image_file("/home/felipe/Downloads/Fort.jpg")
face_location = face_recognition.face_locations(img)
img_encoding = face_recognition.face_encodings(img, face_location)[0]
known_img = face_recognition.load_image_file("/home/felipe/Downloads/download.jpeg")
known_img_enc = face_recognition.face_encodings(known_img)[0]

face_dist = face_recognition.face_distance([img_encoding], known_img_enc)
print(float(face_dist[0]))
