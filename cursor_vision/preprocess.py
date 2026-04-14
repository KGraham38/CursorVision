#Will prepare the eye feature vectors for the tensor flow model

class Preprocess:

    features = [
        "left_iris_x_ratio", "right_iris_x_ratio", "avg_iris_x_ratio",
        "left_iris_y_ratio", "right_iris_y_ratio", "avg_iris_y_ratio",
        "left_eye_aspect", "right_eye_aspect", "avg_eye_aspect",
        "head_horiz_offset_ratio","head_vert_offset_ratio", "face_aspect_ratio"]

    left_eye = {
        "iris": [468, 469, 470, 471, 472],
        "outer": 33, "inner": 133,
        "upper": 159, "lower": 145,
        "brow": [70, 63, 105, 66, 107],}

    right_eye = {
        "iris": [473, 474, 475, 476, 477],
        "outer": 263, "inner": 362,
        "upper": 386, "lower": 374,
        "brow": [336, 296, 334, 293, 300]}

    #To hopefully help correct for head position, may need a few additional points, we shall see
    tip_nose = 1
    face_left = 234
    face_right = 454
    forehead = 10
    chin = 152

    def __init__(self):