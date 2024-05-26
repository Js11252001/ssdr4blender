# -*- coding: utf-8 -*-
"""
Porting to Blender: tamachan devil.tamachan@gmail.com

Original version:
 SSDR4Maya
 __author__ = "Tomohiko Mukai <contact@mukai-lab.org>"
 __status__ = "1st release"
 __version_ = "0.1"
 __date__ = "06 Jul 2016"
 
  Implementaion of "Smooth Skin Decomposition with Rigid Bones" for Maya 2016
  
  Reference:
    - Binh Huy Le and Zhigang Deng, Smooth Skinning Decomposition with Rigid Bones, ACM Transactions on Graphics, 31(6), 199:1--199:10, 2012.
    - Binh Huy Le and Zhigang Deng, Robust and Accurate Skeletal Rigging from Mesh Sequences, ACM Transactions on Graphics,33(4), 84:1--84:10, 2014.
"""

import sys
import os
import math
from ctypes import *
import bpy
import mathutils
from mathutils import *
import bpy_extras
import pickle
import platform

bl_info = {
    "name": "SSDR4Blender",
    "description": "SSDR4Blender",
    "author": "tamachan (Porting)",
    "version": (0, 1),
    "blender": (2, 85, 0),
    "support": "COMMUNITY",
    "category": "Animation"
}

class ssdrBuildCmd(bpy.types.Operator):
    bl_idname = "object.ssdr"
    bl_label = "SSDR"
    bl_options = {'REGISTER', 'UNDO'}

    numMinBones: bpy.props.IntProperty(name="MinBones", default=16, min=1, max=100)
    numMaxIterations: bpy.props.IntProperty(name="MaxIterations", default=20, min=1, max=100)
    numMaxInfluences: bpy.props.IntProperty(name="MaxInfluences", default=2, min=1, max=100)

    def execute(self, context):
        if platform.system() != 'Windows':
            self.report({'ERROR'}, "Not supported OS.")
            return {'CANCELLED'}
        
        is_64bits = sys.maxsize > 2**32
        dll_dir = os.path.dirname(os.path.abspath(__file__))
        if is_64bits:
            dll_path = os.path.join(dll_dir, "ssdr64.dll")
        else:
            dll_path = os.path.join(dll_dir, "ssdr.dll")
        if not os.path.exists(dll_path):
            self.report({'ERROR'}, "DLL file not found.")
            return {'CANCELLED'}
        
        ssdr = CDLL(dll_path)
        ssdr.build.argtypes = [c_int, c_int, c_int, POINTER(c_float), POINTER(c_float), c_int, c_int]
        ssdr.build.restype = c_double
        ssdr.getSkinningWeight.argtypes = []
        ssdr.getSkinningWeight.restype = POINTER(c_double)
        ssdr.getSkinningIndex.argtypes = []
        ssdr.getSkinningIndex.restype = POINTER(c_int)
        ssdr.getNumBones.argtypes = []
        ssdr.getNumBones.restype = c_int
        ssdr.getBoneTranslation.argtypes = [c_int, c_int]
        ssdr.getBoneTranslation.restype = POINTER(c_float)
        ssdr.getBoneRotation.argtypes = [c_int, c_int]
        ssdr.getBoneRotation.restype = POINTER(c_float)
        ssdr.freeRetArr.argtypes = [c_void_p]
        ssdr.freeRetArr.restype = None

        bpy.ops.object.duplicate()
        o = bpy.context.active_object
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        numVertices = len(o.data.vertices)
        if self.numMinBones > numVertices:
            self.numMinBones = numVertices

        start_frame = bpy.context.scene.frame_start
        end_frame = bpy.context.scene.frame_end
        numFrames = end_frame - start_frame + 1
        bpy.context.scene.frame_set(0)

        bindVertices = []
        animVertices = []
        for v in o.data.vertices:
            v2 = v.co
            bindVertices += [v2[0], v2[1], v2[2]]
            animVertices += [v2[0], v2[1], v2[2]]

        for f in range(start_frame, end_frame + 1):
            bpy.context.scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            eval_obj = o.evaluated_get(dg)
            cur_mesh = eval_obj.to_mesh()
            for v in cur_mesh.vertices:
                v2 = v.co
                animVertices += [v2[0], v2[1], v2[2]]
            eval_obj.to_mesh_clear()

        bpy.context.scene.frame_set(start_frame)
        
        bindVerticesC = (c_float * len(bindVertices))(*bindVertices)
        animVerticesC = (c_float * len(animVertices))(*animVertices)
        p_bindVerticesC = cast(pointer(bindVerticesC), POINTER(c_float))
        p_animVerticesC = cast(pointer(animVerticesC), POINTER(c_float))
        rmse = ssdr.build(c_int(self.numMinBones), c_int(self.numMaxInfluences), c_int(self.numMaxIterations), p_bindVerticesC, p_animVerticesC, c_int(numVertices), c_int(numFrames + 1))
        
        numBones = ssdr.getNumBones()
        self.report({'INFO'}, f'RMSE = {rmse}, #Bones = {numBones}')

        skinningWeight = ssdr.getSkinningWeight()
        skinningIndex = ssdr.getSkinningIndex()

        o.modifiers.clear()
        for f in range(start_frame, end_frame + 1):
            bpy.context.scene.frame_set(f)
            for shape in o.data.shape_keys.key_blocks:
                shape.value = 0.0
                shape.keyframe_insert("value", frame=f)
        bpy.context.scene.frame_set(start_frame)
        for f in range(start_frame, end_frame + 1)[::-1]:
            bpy.context.scene.frame_set(f)
            bpy.ops.object.shape_key_clear()
            o.animation_data_clear()
        
        bpy.ops.object.shape_key_remove(all=True)

        arm = bpy.data.armatures.new('SSDRRigData')
        armObj = bpy.data.objects.new('SSDRRig', arm)
        armObj.matrix_world = o.matrix_world
        scn = bpy.context.collection
        scn.objects.link(armObj)
        bpy.context.view_layer.objects.active = armObj
        bpy.ops.object.editmode_toggle()

        bones = []
        for i in range(numBones):
            bone = arm.edit_bones.new('SSDR' + str(i))
            bone.head = (0, 0, 0)
            bone.tail = (0, 0, 1)
            bone.matrix = Matrix()
            bones.append(bone)

        mesh_obj = bpy.data.objects.get(o.name)

        vgroups = []
        for i in range(numBones):
            bone = bones[i]
            grp = mesh_obj.vertex_groups.new(name=bone.name)
            vgroups.append(grp)

        idx = 0
        for i in range(numVertices):
            for k in range(self.numMaxInfluences):
                weight = skinningWeight[idx]
                if weight != 0.0:
                    vgroups[skinningIndex[idx]].add([i], skinningWeight[idx], 'REPLACE')
                idx += 1

        ssdr.freeRetArr(skinningWeight)
        ssdr.freeRetArr(skinningIndex)

        mod = mesh_obj.modifiers.new('SSDRArm', 'ARMATURE')
        mod.object = armObj
        mod.use_bone_envelopes = False
        mod.use_vertex_groups = True

        bpy.context.view_layer.objects.active = armObj
        bpy.ops.object.mode_set(mode='POSE')
        for f2 in range(start_frame, end_frame + 1):
            bpy.context.scene.frame_set(f2)
            f = f2 - start_frame + 1
            for b in range(numBones):
                pbone = armObj.pose.bones[b]
                t = ssdr.getBoneTranslation(b, f)
                q = ssdr.getBoneRotation(b, f)

                pbone.location = Vector((t[0], t[1], t[2]))
                pbone.rotation_mode = 'QUATERNION'
                pbone.rotation_quaternion = Quaternion((q[3], q[0], q[1], q[2]))

                pbone.keyframe_insert(data_path='location', frame=f2)
                pbone.keyframe_insert(data_path='rotation_quaternion', frame=f2)

                ssdr.freeRetArr(t)
                ssdr.freeRetArr(q)

        del ssdr
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ssdrBuildCmd.bl_idname)

def register():
    bpy.utils.register_class(ssdrBuildCmd)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ssdrBuildCmd)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
