# this program is to check how good the user's form is during exercise

# while the user switches between different poses we expect the error to be high
# we record the pose, as well as what exercise matches best
# we record a rep once the pose reaches above or below a certain threshold
# and we calculate the error of each pose
# for best results we assume the optimal performace at each rep, so we take the maximum

# exercise database format:
# dictionary of entries
# key = name of exercise
# data = dictionary containing up and down position

import math

# tolerance values for checking if a given pose is correct or if it is random noise
max_err = 1

# check one pose against another and return the difference
# also normalise to accommodate for changes in position and distance
def compare_poses(pose1, pose2):
    # pose 1 is the pose to be checked against
    # pose 2 is the pose from the camera
    # first normalise the torsos into the same position
    # torso = average of hips (joints 11 and 12) and shoulders (joints 5 and 6)
    torso_1 = (
        0.25*(pose1[5][0] + pose1[6][0] + pose1[11][0] + pose1[12][0]),
        0.25*(pose1[5][1] + pose1[6][1] + pose1[11][1] + pose1[12][1])
    )
    torso_2 = (
        0.25*(pose2[5][0] + pose2[6][0] + pose2[11][0] + pose2[12][0]),
        0.25*(pose2[5][1] + pose2[6][1] + pose2[11][1] + pose2[12][1])
    )
    # move both models' torsos to the origin
    for joint in range(len(pose1)):
        pose1[joint][0] -= torso_1[0]
        pose1[joint][1] -= torso_1[1]
        pose2[joint][0] -= torso_2[0]
        pose2[joint][1] -= torso_2[1]
    # also ensure both models are the same size
    # torsos are roughly rectangular, so we use width (between hips) x height (left hip to left shoulder)
    torso_1_size = abs((pose1[12][0] - pose1[11][0]) * (pose1[11][0] - pose1[5][0]))
    torso_2_size = abs((pose2[12][0] - pose2[11][0]) * (pose2[11][0] - pose2[5][0]))
    # area scale factor (torso 2 size = torso 1 size * ASF)
    ASF = torso_2_size / torso_1_size
    LSF = ASF ** 0.5
    # multiply pose 1 by the LSF in order to match pose 2
    for joint in range(len(pose1)):
        pose1[joint][0] *= LSF
        pose1[joint][1] *= LSF
    # now the poses are comparable
    diff = []
    # diff is such that pose2 + diff = pose1
    # this lets us generate tips on how to improve
    for joint in range(len(pose1)):
        diff.append(tuple([
            pose1[joint][0] - pose2[joint][0],
            pose1[joint][1] - pose2[joint][1]
        ]))
    # mean squared error
    E = sum([(d[0]**2 + d[1]**2) for d in diff])/len(diff)
    return E, diff

# check pose against an exercise and return the prediction, difference and error
# confidence = 1/error
def make_prediction(exercise, pose):
    # best matching pose
    best_pose = ""
    best_diff = []
    min_err = -1
    for pose_key in exercise.keys():
        # i.e. up and down position
        exercise_pose = exercise[pose_key]
        E, diff = compare_poses(exercise_pose, pose)
        if min_err == -1 or E<min_err:
            best_pose = pose_key
            best_diff = diff
            min_err = E
    if min_err < max_err:
        return best_pose, best_diff, min_err
    return "", [], -1

# generate suggestions based on the diff
def generate_suggestion(diff):
    KEYPOINT_DICT = {
        'nose': 0,
        'left_eye': 1,
        'right_eye': 2,
        'left_ear': 3,
        'right_ear': 4,
        'left_shoulder': 5,
        'right_shoulder': 6,
        'left_elbow': 7,
        'right_elbow': 8,
        'left_wrist': 9,
        'right_wrist': 10,
        'left_hip': 11,
        'right_hip': 12,
        'left_knee': 13,
        'right_knee': 14,
        'left_ankle': 15,
        'right_ankle': 16
    }
    max_diff = ()
    max_err = -1
    joint_to_improve = 0
    for joint in range(len(diff)):
        joint_diff = diff[joint]
        if (joint_diff[0] ** 2 + joint_diff[1] ** 2) > max_err:
            max_err =  joint_diff[0] ** 2 + joint_diff[1] ** 2
            max_diff = max_err
            joint_to_improve = joint
    # now we have the joint we need to improve the most
    suggestion = "Move your "+KEYPOINT_DICT[joint_to_improve].replace("_", " ")+" to the "
    if max_diff[1] < 0:
        suggestion += "left and "
    if max_diff[1] > 0:
        suggestion += "right and "
    if max_diff[0] < 0:
        suggestion += "up"
    if max_diff[0] > 0:
        suggestion += "down"
    return suggestion
