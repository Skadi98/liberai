import face_recognition #importa o módulo face_recognition
import cv2 #importa o módulo cv2
from datetime import datetime, timedelta #importa do módulo datetime as libs datetime e timedelta
import numpy as np #importa o módulo numpy como np
import platform #importa o módulo platform
import pickle #importa o módulo pickle
import database as db

know_face_encodings = []
know_face_metadata= []
data = db.database()


#Função depreciada com o uso de BD
def salvar_faces_conhecidas():  # Define a função que salva os encodings e os metadados de cada rosto, de maneira binária, em um arquivo de dados .dat
     with open("faces_conhecidas.dat", "wb") as face_data_file: 
        face_data = [know_face_encodings, know_face_metadata] 
        pickle.dump(face_data, face_data_file) #pickle é um módulo para manipulação de binários em python
        #assumindo 1:1 encoding e metadata
        count = 0
        for dat in know_face_encodings:
            data.write_Encoding(dat,know_face_metadata[count]['data_do_cadastro'],know_face_metadata[count]['nome'],know_face_metadata[count]['matricula'])
            count += 1
        print("Backup realizado.")

def carregar_faces_conhecidas(): # Define a função que carrega da base de dados a codificação facial e os metadados faciais
    global know_face_encodings, know_face_metadata

    try: # tenta abrir o arquivo
        with open("faces_conhecidas.dat", "rb") as face_data_file:
      #      know_face_encodings, know_face_metadata = pickle.load(face_data_file)
            #Leitura do banco que carrega encoding como chave do dic e metadados como conteudos
            data.read_ALL_Encoding()
            know_face_encodings = data.encoding
            know_face_metadata = data.metadata
            print("Sucesso ao importar dados.")
    except FileNotFoundError as e:
        print("Não foi possível encontrar o arquivo com dados, iniciando com um arquivo vazio.")
        pass

def registrar_nova_face(face_encoding, face_image): # Adiciona nova pessoa a nossa lista de faces conhecidas
    
    know_face_encodings.append(face_encoding) #Adiciona a codificação do facial ao vetor de codificações global.

    matricula = float(input("Insira a matricula: "))
    nome_aluno = input("Insira nome do aluno:")
    know_face_metadata.append({
        "data_do_cadastro": datetime.now(),
        "face_image": face_image,
        "matricula": matricula,
        "nome": nome_aluno,
    })
    data.write_Encoding(encode_A=face_encoding,photo=face_image,name=nome_aluno,register=matricula)
    

def lookup_known_face(face_encoding):
    
    metadata = None

    if len(know_face_encodings) == 0:
        return metadata

    face_distances = face_recognition.face_distance(
        know_face_encodings, 
        face_encoding
    )

    best_match_index = np.argmin(face_distances)

    if face_distances[best_match_index] < 0.55:
        metadata = know_face_metadata[best_match_index]
        metadata["data_do_cadastro"] = datetime.now()

    return metadata

def main_loop():

    video_capture = cv2.VideoCapture(0)

    while True:
        
    
        ret, frame = video_capture.read()

        small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame [:,:,::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_labels = []

        for face_location, face_encoding in zip(face_locations, face_encodings):
            
            metadata = lookup_known_face(face_encoding)

            
            if metadata is not None:
                
                face_label= metadata['nome']             
            
            else:
                face_label = "Desconhecido"

                top, right, bottom, left = face_location
                face_image = small_frame[top:bottom, left:right]
                face_image = cv2.resize(face_image, (150, 150))
                request = input("Deseja cadastrar novo usuário?")

                if (request == "sim") | (request == "s"):

                    registrar_nova_face(face_encoding,face_image)

                else:
                        
                    print("Usuário não será cadastrado")
                        
                    face_label = "Desconhecido"

                    top, right, bottom, left = face_location
                    face_image = small_frame[top:bottom, left:right]
                    face_image = cv2.resize(face_image, (150, 150))
            

                

            face_labels.append(face_label)  

        for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
            
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left,top), (right,bottom), (0,0,255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, face_label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            salvar_faces_conhecidas()
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    carregar_faces_conhecidas()
    #salvar_faces_conhecidas()
    main_loop()
                

