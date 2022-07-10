import bpy
import easybpy as bm
from functools import wraps

print("---------------------------------------")
epicBoneHIK = [
    "pelvis",

]

mmdBoneHIK = [
    "上半身",
    "左足",
]
SUFFIX = "_hikMark"


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
            if bone.name not in mmdBoneHIK:
                continue
            else:
                mmd_name = bone.mmd_bone.name_j
                self.bones[str(mmd_name)] = bone


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
def create_insufficient_bones(suffix=True):
    # pelvis bone
    name = "pelvis"
    pelvis = _add_bone(name, suffix)
    spine_root = INFO.bones["上半身"]
    _match_bone(pelvis, spine_root)
    left_thigh = INFO.bones["左足"]
    _, y, z = left_thigh.matrix.translation
    pelvis.head = (0, y, z)
    pelvis.tail = spine_root.matrix.translation


@edit_mode(INFO.arm_obj)
def test():
    armData = INFO.arm_obj.pose
    bb = _add_bone("test")
    tt = armData.bones["左腕"]
    _match_bone(bb, tt)


create_insufficient_bones()
