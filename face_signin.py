import cv2
import face_recognition
import sys
import numpy as np
import os

def print_usage():
    print "Usage:"
    print "\targ1: camera address"

def load_known_face_vectors(data_dir='./vector/', place='techBuilding/'):
    name2vectlist = {}
    for filename in os.listdir(data_dir+place):
        person_name = filename.split('_')[0]
        vect = np.load(data_dir+place+filename)
        if person_name not in name2vectlist:
            name2vectlist[person_name] = []
        name2vectlist[person_name].append(vect)
    return name2vectlist

def faceSignin(video, name2vectlist):
    frame_num = 0
    scale = 4
    flag = True
    while True:
        ret, frame = video.read()
        if not ret:
            print "Done."
            return frame_num
        if flag:
            small_frame = cv2.resize(frame, (0, 0), fx=1./scale, fy=1./scale)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            face_distances = []
            for enc in face_encodings:
                face_name = "Unknown"
                face_dist = 0.
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
        #flag = not flag

        cv2.imshow('Face-Signin V_0.1', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_num += 1

    return frame_num

if __name__=='__main__':
    cam_addr = 'test.mp4'
    if len(sys.argv)==2:
        cam_addr = sys.argv[1]
    elif len(sys.argv)>2:
        print_usage()
    video = cv2.VideoCapture(cam_addr)
    name2vectlist = load_known_face_vectors(place='library/')
    total_frame_num = faceSignin(video, name2vectlist)
    print "{} frames processed in all.".format(total_frame_num)
