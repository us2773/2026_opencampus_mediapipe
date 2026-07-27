def check_visibility(landmarks: list) :
    all_visible = True
    for landmark in landmarks :
        if landmark.visibility <= 0.7 :
            all_visible = False
    
    return all_visible