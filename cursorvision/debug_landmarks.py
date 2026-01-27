#Kody Graham
#1/26/2026
#This file will be the foundation for my FaceMesh landmarks

import mediapipe as mp

#Setup FaceMesh
mediapipe_face = mp.solutions.face_mesh

#Landmarks
NOSE_TIP= 1

LEFT_EYE_OUTSIDE = 38
LEFT_EYE_INSIDE = 138

RIGHT_EYE_OUTSIDE = 360
RIGHT_EYE_INSIDE = 260

LEFT_IRIS = list(range(468, 475))
RIGHT_IRIS = list(range(476, 480))


