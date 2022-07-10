from functools import wraps, partial

import bpy
import easybpy as bm
import math
import mathutils

print("---------------------------------------")
epicBoneHIK = [

]
epicBoneHIKExtra = [
    "root",
    "pelvis",
    "thigh_l",
    "calf_l",
    "foot_l",
    "ball_l",
    "thigh_r",
    "calf_r",
    "foot_r",
    "ball_r",
    "spine_01",
    "spine_02",
    "spine_03",
    "neck_01",
    "head",
    "clavicle_l",
    "upperarm_l",
    "lowerarm_l",
    "hand_l",
    "thumb_01_l",
    "thumb_02_l",
    "thumb_03_l",
    "index_01_l",
    "index_02_l",
    "index_03_l",
    "middle_01_l",
    "middle_02_l",
    "middle_03_l",
    "ring_01_l",
    "ring_02_l",
    "ring_03_l",
    "pinky_01_l",
    "pinky_02_l",
    "pinky_03_l",
    "clavicle_r",
    "upperarm_r",
    "lowerarm_r",
    "hand_r",
    "thumb_01_r",
    "thumb_02_r",
    "thumb_03_r",
    "index_01_r",
    "index_02_r",
    "index_03_r",
    "middle_01_r",
    "middle_02_r",
    "middle_03_r",
    "ring_01_r",
    "ring_02_r",
    "ring_03_r",
    "pinky_01_r",
    "pinky_02_r",
    "pinky_03_r",

]

mmdBoneHIK = [
    ("左足", "pelvis"),
    ("左ひざ", "左足"),
    ("左足首", "左ひざ"),
    (None, "was_ball_l"),
    ("右足", "pelvis"),
    ("右ひざ", "右足"),
    ("右足首", "右ひざ"),
    (None, "was_ball_r"),
    ("上半身", "pelvis"),
    ("上半身2", "上半身"),
    (None, "was_spine_03"),
    ("首", "上半身2"),
    ("頭", "首"),
    ("左肩", "上半身2"),
    ("左腕", "左肩"),
    ("左ひじ", "左腕"),
    ("左手首", "左ひじ"),
    ("左親指０", "左手首"),
    ("左親指１", "左親指０"),
    ("左親指２", "左親指１"),
    ("左人指１", "左手首"),
    ("左人指２", "左人指１"),
    ("左人指３", "左人指２"),
    (u"左中指１", "左手首"),
    ("左中指２", "左中指１"),
    ("左中指３", "左中指２"),
    ("左薬指１", "左手首"),
    ("左薬指２", "左薬指１"),
    ("左薬指３", "左薬指２"),
    ("左小指１", "左手首"),
    ("左小指２", "左小指１"),
    ("左小指３", "左小指２"),
    ("右肩", "上半身2"),
    ("右腕", "右肩"),
    ("右ひじ", "右腕"),
    ("右手首", "右ひじ"),
    ("右親指０", "右手首"),
    ("右親指１", "右親指０"),
    ("右親指２", "右親指１"),
    ("右人指１", "右手首"),
    ("右人指２", "右人指１"),
    ("右人指３", "右人指２"),
    ("右中指１", "右手首"),
    ("右中指２", "右中指１"),
    ("右中指３", "右中指２"),
    ("右薬指１", "右手首"),
    ("右薬指２", "右薬指１"),
    ("右薬指３", "右薬指２"),
    ("右小指１", "右手首"),
    ("右小指２", "右小指１"),
    ("右小指３", "右小指２"),
]
SUFFIX = "_hikMark"
mmdBoneHIKExtra = [
    ("root", None),
    ("pelvis", "root"),
]


class CollectBoneInfo:

    def __init__(self):
        # get data
        self.bones = {}
        self.root = bpy.data.objects['Nico My Sweet Devil UR']
        self.arm_obj = bpy.data.objects[self.root.name + "_arm"]
        self.model_obj = bpy.data.objects[self.root.name + "_mesh"]

        self.store_bone_list_by_mmd_name()

    def store_bone_list_by_mmd_name(self):
        for bone in self.arm_obj.pose.bones:
            tracking_list = [i for i, j in mmdBoneHIK] + ["下半身"]
            if bone.name not in tracking_list:
                continue
            else:
                mmd_name = bone.mmd_bone.name_j
                self.bones[str(mmd_name)] = bone.name


INFO = CollectBoneInfo()


def hold_bone_layer(layer_id):
    def decorator_function(function):
        @wraps(function)
        def result(*args, **kwargs):
            activated = []
            for i in range(32):
                lyr = bpy.context.object.data.layers[i]
                if lyr or i == layer_id:
                    activated.append(lyr)
                else:
                    lyr = True
            try:
                return function(*args, **kwargs)
            finally:
                for lyr in bpy.context.object.data.layers:
                    if lyr not in activated:
                        lyr = False

        return result

    return decorator_function


def edit_mode(obj):
    def decorator_function(function):
        @wraps(function)
        def result(*args, **kwargs):
            current_mode = bpy.context.mode
            if current_mode.startswith("EDIT"):
                current_mode = "EDIT"
            else:
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bm.select_object(obj)
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            try:
                return function(*args, **kwargs)
            finally:
                if not current_mode.startswith("EDIT"):
                    bpy.ops.object.mode_set(mode=current_mode, toggle=False)

        return result

    return decorator_function


def _change_bone_layer(bone, target_layer):
    activated = []
    for lyr_id, lyr in enumerate(bone.layers):
        if lyr:
            activated.append(lyr_id)
    if target_layer in activated:
        activated.remove(target_layer)
    bone.layers[target_layer] = True
    for lyr in activated:
        bone.layers[lyr] = False
    bone.layers.update()


@edit_mode(INFO.arm_obj)
def _add_bone(new_bone_name, layer_id=16, suffix=True):
    edit_bones = INFO.arm_obj.data.edit_bones
    final_name = new_bone_name + int(suffix) * SUFFIX
    new_bone = edit_bones.new(final_name)
    new_bone.head = (0, 0, 0)
    new_bone.tail = (0, 0, 1)
    _change_bone_layer(new_bone, layer_id)
    return new_bone


@edit_mode(INFO.arm_obj)
@hold_bone_layer(16)
def _match_bone(source, target_pose_bone):
    obj = INFO.arm_obj
    target_matrix = obj.matrix_world @ target_pose_bone.matrix
    target_tail = target_pose_bone.tail
    source.matrix = target_matrix
    source.tail = target_tail
    source.layers.update()


@edit_mode(INFO.arm_obj)
@hold_bone_layer(16)
def _match_bone_rotation(source, target_bone):
    obj = INFO.arm_obj
    target_matrix = obj.matrix_world @ target_bone.matrix
    loc = source.matrix.decompose()[0]
    _, rot, sca = target_matrix.decompose()
    new_matrix = mathutils.Matrix.LocRotScale(loc, rot, sca)
    source.matrix = new_matrix
    source.layers.update()


@edit_mode(INFO.arm_obj)
def get_bone(bone_name, mode="data"):
    # mode = ["data","pose","edit"]
    if mode == "data":
        return INFO.arm_obj.data.bones[bone_name]
    elif mode == "pose":
        return INFO.arm_obj.pose.bones[bone_name]
    elif mode == "edit":
        return INFO.arm_obj.data.edit_bones[bone_name]


get_pose_bone = partial(get_bone, mode="pose")

get_edit_bone = partial(get_bone, mode="edit")


@edit_mode(INFO.arm_obj)
def create_insufficient_bones(suffix=True):
    # root bone
    name = "root"
    root = _add_bone(name, suffix)
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.1)
    INFO.bones[name] = root.name
    # pelvis bone
    name = "pelvis"
    pelvis = _add_bone(name, suffix)
    _match_bone(pelvis, get_pose_bone(INFO.bones["上半身"]))
    _, y, z = get_pose_bone(INFO.bones["左足"]).matrix.translation
    pelvis.head = (0, y, z)
    pelvis.tail = get_pose_bone(INFO.bones["下半身"]).head
    pelvis.parent = root
    INFO.bones[name] = pelvis.name


FORCE_CONNECT = ["上半身", "上半身2", "首", "頭",
                 "左ひざ", "左足首", "右ひざ", "右足首",
                 "左腕", "左ひじ", "左手首", "右腕", "右ひじ", "右手首",
                 "左親指１", "左親指２", "右親指１", "右親指２",
                 "左人指２", "左人指３", "右人指２", "右人指３",
                 "左中指２", "左中指３", "右中指２", "右中指３",
                 "左薬指２", "左薬指３", "右薬指２", "右薬指３",
                 "左小指２", "左小指３", "右小指２", "右小指３"
                 ]


@edit_mode(INFO.arm_obj)
def create_HIK_marking_bones(suffix=True):
    for bone_name, parent_name in mmdBoneHIK:
        if bone_name:
            mmd_bone = get_pose_bone(INFO.bones[bone_name])
            new_bone = _add_bone(bone_name, suffix)
            _match_bone(new_bone, mmd_bone)
            if parent_name:
                parent_edit_bone = get_edit_bone(parent_name + int(suffix) * SUFFIX)
                new_bone.parent = parent_edit_bone
                if bone_name in FORCE_CONNECT:
                    new_bone.use_connect = True
            if "手首" in bone_name:
                _match_bone_rotation(new_bone, new_bone.parent)


create_insufficient_bones()
create_HIK_marking_bones()
