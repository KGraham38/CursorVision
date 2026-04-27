#Going to use this class for better feature extraction for both the calibration and the tensorflow training, basically just going to try to make preprocess.py more straight forward

def norm_x(x_value, frame_width):
    if frame_width <= 1:
        return 0.0
    return float(x_value) / float(frame_width-1)

def norm_y(y_value, frame_height):
    if frame_height <= 1:
        return 0.0
    return float(y_value) / float(frame_height-1)

def build_feature_dict(look_direction, face_landmarks, frame_shape):
    frame_height, frame_width = frame_shape[:2]
    data = look_direction.landmark_features(face_landmarks,frame_width,frame_height)

    current_horizontal_position = float(data["average_horizontal"])
    current_vertical_position = float(data["average_vertical"])

    if look_direction.neutral_horizontal_pos is None:
        look_horizontal = 0.0
    else:
        look_horizontal = current_horizontal_position - float(look_direction.neutral_horizontal_pos)

    if look_direction.neutral_vertical_pos is None:
        look_vertical = 0.0
    else:
        look_vertical = current_vertical_position - float(look_direction.neutral_vertical_pos)

    if abs(look_horizontal) < look_direction.deadzone:
        look_horizontal = 0.0
    if abs(look_vertical) < look_direction.deadzone:
        look_vertical = 0.0

    boost_h = look_horizontal * (1 + 2.2 * abs(look_horizontal))
    boost_v = look_vertical * (1 + 2.2 * abs(look_vertical))

    centered_x = int(data["centered"][0])
    centered_y = int(data["centered"][1])

    raw_target_x = int(centered_x +boost_h * look_direction.horizontal_multiplier)
    raw_target_y = int(centered_y + boost_v * look_direction.vertical_multiplier)

    raw_target_x = max(0, min(frame_width-1, raw_target_x))
    raw_target_y = max(0, min(frame_height-1, raw_target_y))

    left_iris_x = int(data["left_iris"][0])
    left_iris_y = int(data["left_iris"][1])
    right_iris_x = int(data["right_iris"][0])
    right_iris_y = int(data["right_iris"][1])

    left_mid_x = int(data["left_mid"][0])
    left_mid_y = int(data["left_mid"][1])
    right_mid_x = int(data["right_mid"][0])
    right_mid_y = int(data["right_mid"][1])

    left_brow_x = int(data["left_brow"][0])
    left_brow_y = int(data["left_brow"][1])
    right_brow_x = int(data["right_brow"][0])
    right_brow_y = int(data["right_brow"][1])

    return {
        "average_horizontal": current_horizontal_position,
        "average_vertical": current_vertical_position,
        "look_horizontal": float(look_horizontal),
        "look_vertical": float(look_vertical),
        "centered_x": centered_x,
        "centered_y": centered_y,
        "centered_x_norm": norm_x(centered_x, frame_width),
        "centered_y_norm": norm_y(centered_y, frame_height),
        "raw_target_x": raw_target_x,
        "raw_target_y": raw_target_y,
        "raw_target_x_norm": norm_x(raw_target_x, frame_width),
        "raw_target_y_norm": norm_y(raw_target_y, frame_height),
        "left_iris_x": left_iris_x,
        "left_iris_y": left_iris_y,
        "left_iris_x_norm": norm_x(left_iris_x, frame_width),
        "left_iris_y_norm": norm_y(left_iris_y, frame_height),
        "right_iris_x": right_iris_x,
        "right_iris_y": right_iris_y,
        "right_iris_x_norm": norm_x(right_iris_x, frame_width),
        "right_iris_y_norm": norm_y(right_iris_y, frame_height),
        "left_mid_x": left_mid_x,
        "left_mid_y": left_mid_y,
        "left_mid_x_norm": norm_x(left_mid_x, frame_width),
        "left_mid_y_norm": norm_y(left_mid_y, frame_height),
        "right_mid_x": right_mid_x,
        "right_mid_y": right_mid_y,
        "right_mid_x_norm": norm_x(right_mid_x, frame_width),
        "right_mid_y_norm": norm_y(right_mid_y, frame_height),
        "left_brow_x": left_brow_x,
        "left_brow_y": left_brow_y,
        "left_brow_x_norm": norm_x(left_brow_x, frame_width),
        "left_brow_y_norm": norm_y(left_brow_y, frame_height),
        "right_brow_x": right_brow_x,
        "right_brow_y": right_brow_y,
        "right_brow_x_norm": norm_x(right_brow_x, frame_width),
        "right_brow_y_norm": norm_y(right_brow_y, frame_height),
    }