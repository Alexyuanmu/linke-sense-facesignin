import cv2
import face_recognition
import sys
import numpy as np
import os
import sqlite3
from datetime import datetime

def print_usage():
    print "Usage:"
    print "\targ1: camera address (ip address or video path)"
    print "\targ2: place (techBuilding or library)"

def load_known_face_vectors(data_dir='./vector/', place='techBuilding/'):
    name2vectlist = {}
    for filename in os.listdir(data_dir+place):
        person_name = filename.split('_')[0]
        vect = np.load(data_dir+place+filename)
        if person_name not in name2vectlist:
            name2vectlist[person_name] = []
        name2vectlist[person_name].append(vect)
    return name2vectlist

def faceSignin(video, name2vectlist, visual=False):
    # connect to the database
    conn = sqlite3.connect("FaceSignin.db")

    #frame_num = 0
    count = 0
    scale = 2
    flag = True

    buff = {}

    while True:
        ret, frame = video.read()
        if not ret:
            print "Done."
            break
        if flag: # process this frame
            small_frame = cv2.resize(frame, (0, 0), fx=1./scale, fy=1./scale)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            face_distances = []
            for enc in face_encodings:
                face_name = "Unknown"
                #face_dist = 0.
                for person_name, vectlist in name2vectlist.items():
                    tolrance = 0.40
                    dist = face_recognition.face_distance(vectlist, enc)
                    '''
                    matches = [x<tolrance for x in dist]
                    #matches = face_recognition.compare_faces(vectlist, enc)
                    if True in matches:
                        face_name = person_name
                        face_dist = dist
                        break
                    '''
                    avg_dist = sum(dist)/len(dist)
                    if avg_dist < tolrance:
                        face_name = person_name
                        face_dist = avg_dist
                        break

                face_names.append(face_name)
                face_distances.append(face_dist)
                if face_name not in buff:
                    buff[face_name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if visual:
                for (top, right, bottom, left), name, dist in zip(face_locations, face_names, face_distances):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 1*scale
                    right *= 1*scale
                    bottom *= 1*scale
                    left *= 1*scale

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 15), font, 0.5, (255, 255, 255), 1)
                    cv2.putText(frame, "{:.2f}".format(dist), (left + 6, bottom - 2), font, 0.5, (255, 255, 255), 1)
        flag = not flag # skip one frame
        if visual:
            cv2.imshow('Face-Signin V_0.1', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        #frame_num += 1
        count += 1
        if count%(30*10)==0:
            # store records into database
            cursor = conn.cursor()
            for name_k,time_v in buff.items():
                if name_k == 'Unknown':
                    continue
                cursor.execute("INSERT INTO record (name,time) values (?,?)", (name_k, time_v))
                print "{} -- {}".format(name_k, time_v)
            cursor.close()
            conn.commit()
            count = 0
            buff = {}
    #return frame_num
    conn.close()

if __name__=='__main__':
    cam_addr = 'test.mp4'
    place = "techBuilding/"
    if len(sys.argv)==3:
        cam_addr = sys.argv[1]
        place = sys.argv[2]+'/'
    else:
        print_usage()
        sys.exit(0)
    video = cv2.VideoCapture(cam_addr)
    name2vectlist = load_known_face_vectors(place=place)
    faceSignin(video, name2vectlist, visual=False)
