def check_visibility(landmarks: list) :
    th_visible = 0.3
    all_visible = True
    for landmark in landmarks :
        if landmark.visibility <= th_visible :
            all_visible = False
    
    return all_visible