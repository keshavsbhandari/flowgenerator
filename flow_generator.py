bl_info = {
        "name":"FlowGenerator - Computer Vision Optical Flow Generator",
        "description":"Generate (Optical flow, Depth Map, Surface Normal, Occlusion Mask, Noisy Frames, Denoised Frames",
        "author":"Keshav Bhandari",
        "version":(1, 0),
        "blender":(2, 92, 0),
        "location":"PROPERTIES",
        "warning":"Experimental Content", 
        "support":"COMMUNITY",
        "category":"Render"
    }
    

import bpy
from math import pi as PI
from bpy.props import (StringProperty, PointerProperty)
from bpy.types import (Panel, PropertyGroup)

class MyProperties(bpy.types.PropertyGroup):
    my_path : bpy.props.StringProperty(name = "ROOT", subtype = "FILE_PATH")
    my_string : bpy.props.StringProperty(name = "Enter Path")
    resolution : bpy.props.IntProperty(name = "Resolution", soft_min = 100, soft_max  = 1000, default = 100)
    
    cube_width : bpy.props.IntProperty(name = "Cube width", soft_min = 128, soft_max  = 1024, default = 512)
    equi_width : bpy.props.IntProperty(name = "Equi Width", soft_min = 256, soft_max  = 2048, default = 1024)
    
    min_depth : bpy.props.FloatProperty(name = "Max Depth", soft_min = 0, soft_max  = 100000, default = 0.5)
    max_depth : bpy.props.FloatProperty(name = "Min Depth", soft_min = 0, soft_max  = 100000, default = 20.0)
    camera_list : bpy.props.EnumProperty(
                name = "Camera",
                description = "sample text",
                items = [("Camera_EQ_F", "Camera_EQ_F", "360 Camera syncing with F of cube face"),
                         ("Camera_EQ_B", "Camera_EQ_B", "360 Camera syncing with B of cube face"),
                         ("Camera_EQ_T", "Camera_EQ_T", "360 Camera syncing with T of cube face"),
                         ("Camera_EQ_D", "Camera_EQ_D", "360 Camera syncing with D of cube face"),
                         ("Camera_EQ_R", "Camera_EQ_R", "360 Camera syncing with R of cube face"),
                         ("Camera_EQ_L", "Camera_EQ_L", "360 Camera syncing with L of cube face"),
                         ("Camera_F", "Camera_F", "Perspective Camera - Face: F"),
                         ("Camera_B", "Camera_B", "Perspective Camera - Face: B"),
                         ("Camera_T", "Camera_T", "Perspective Camera - Face: T"),
                         ("Camera_D", "Camera_D", "Perspective Camera - Face: D"),
                         ("Camera_R", "Camera_R", "Perspective Camera - Face: R"),
                         ("Camera_L", "Camera_L", "Perspective Camera - Face: L"),]
                         )


class NODE_PT_MAINPANEL(bpy.types.Panel):
    bl_label = "Custom Node Group"
    bl_idname = "NODE_PT_MAINPANEL"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Set Flow Generator' 

    def mydraw(self, context):
        pass
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        layout.prop(mytool, "my_path")
        layout.prop(mytool, "resolution")
        layout.prop(mytool, "cube_width")
        layout.prop(mytool, "equi_width")
        layout.prop(mytool, "min_depth")
        layout.prop(mytool, "max_depth")
        layout.prop(mytool, "camera_list")
        
        row = layout.column()
        row.operator('node.test_operator')
        row.operator('node.set_camera')


class CAMERA_SETUP(bpy.types.Operator):
    #bpy.data.objects['Camera']
    bl_label = "Set Camera System"
    bl_idname = "node.set_camera"

    def execute(self, context):
        scene = context.scene
        # angles
        front = (PI/2, 0, -PI)
        back = (-PI/2, 0, -PI)
        top = (PI, 0, -PI)
        down = (0, 0, -PI)
        left = (PI/2, 0, -PI/2)
        right = (PI/2, 0, PI/2)


        # Lets Create Previous Collections
        if bpy.data.collections.get("Camera_System") is not None:
            coll = bpy.data.collections.get("Camera_System")
            bpy.data.collections.remove(coll)

        #Lets create a camera collections first
        cam_collections = bpy.data.collections.new(name = "Camera_System")
        cam_collections.name = "Camera_System"
        scene.collection.children.link(cam_collections)

        list_of_camera = [
                            "Camera_EQ_F", 
                            "Camera_EQ_B", 
                            "Camera_EQ_T", 
                            "Camera_EQ_D",
                            "Camera_EQ_R", 
                            "Camera_EQ_L",
                            "Camera_F",
                            "Camera_B",
                            "Camera_T",
                            "Camera_D",
                            "Camera_R",
                            "Camera_L",
                        ]
        
        # for cam_name in list_of_camera:
        #     if bpy.data.cameras.get(cam_name):    
        #         cam = bpy.data.cameras.get(cam_name)
        #         bpy.data.cameras.remove(cam)

        for camname, cam in bpy.data.cameras.items():
            if camname.split('.')[0] in list_of_camera:
                bpy.data.cameras.remove(cam)

        # EQUIRECTANGULAR FRONT
        Cam_EQ_F = bpy.data.cameras.new(name = "Camera_EQ_F")
        Cam_EQ_F.name = "Camera_EQ_F"
        Cam_obj_EQ_F = bpy.data.objects.new('Camera', Cam_EQ_F)
        Cam_obj_EQ_F.name = "Camera_EQ_F"
        Cam_obj_EQ_F.data.type = 'PANO'
        Cam_obj_EQ_F.data.cycles.panorama_type = "EQUIRECTANGULAR"
        Cam_obj_EQ_F.data.sensor_width = 50
        Cam_obj_EQ_F.rotation_euler = front
        scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_F)

        # EQUIRECTANGULAR BACK
        Cam_EQ_B = bpy.data.cameras.new(name = "Camera_EQ_B")
        Cam_EQ_B.name = "Camera_EQ_B"
        Cam_obj_EQ_B = bpy.data.objects.new('Camera', Cam_EQ_B)
        Cam_obj_EQ_B.name = "Camera_EQ_B"
        Cam_obj_EQ_B.data.type = 'PANO'
        Cam_obj_EQ_B.data.cycles.panorama_type = "EQUIRECTANGULAR"
        Cam_obj_EQ_B.data.sensor_width = 50
        Cam_obj_EQ_B.rotation_euler = back
        scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_B)

        # EQUIRECTANGULAR TOP
        Cam_EQ_T = bpy.data.cameras.new(name = "Camera_EQ_T")
        Cam_EQ_T.name = "Camera_EQ_T"
        Cam_obj_EQ_T = bpy.data.objects.new('Camera', Cam_EQ_T)
        Cam_obj_EQ_T.name = "Camera_EQ_T"
        Cam_obj_EQ_T.data.type = 'PANO'
        Cam_obj_EQ_T.data.cycles.panorama_type = "EQUIRECTANGULAR"
        Cam_obj_EQ_T.data.sensor_width = 50
        Cam_obj_EQ_T.rotation_euler = top
        scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_T)

        # EQUIRECTANGULAR DOWN
        Cam_EQ_D = bpy.data.cameras.new(name = "Camera_EQ_D")
        Cam_EQ_D.name = "Camera_EQ_D"
        Cam_obj_EQ_D = bpy.data.objects.new('Camera', Cam_EQ_D)
        Cam_obj_EQ_D.name = "Camera_EQ_D"
        Cam_obj_EQ_D.data.type = 'PANO'
        Cam_obj_EQ_D.data.cycles.panorama_type = "EQUIRECTANGULAR"
        Cam_obj_EQ_D.data.sensor_width = 50
        Cam_obj_EQ_D.rotation_euler = down
        scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_D)


        # EQUIRECTANGULAR RIGHT
        Cam_EQ_R = bpy.data.cameras.new(name = "Camera_EQ_R")
        Cam_EQ_R.name = "Camera_EQ_R"
        Cam_obj_EQ_R = bpy.data.objects.new('Camera', Cam_EQ_R)
        Cam_obj_EQ_R.name = "Camera_EQ_R"
        Cam_obj_EQ_R.data.type = 'PANO'
        Cam_obj_EQ_R.data.cycles.panorama_type = "EQUIRECTANGULAR"
        Cam_obj_EQ_R.data.sensor_width = 50
        Cam_obj_EQ_R.rotation_euler = right
        scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_R)

        # EQUIRECTANGULAR LEFT
        Cam_EQ_L = bpy.data.cameras.new(name = "Camera_EQ_L")
        Cam_EQ_L.name = "Camera_EQ_L"
        Cam_obj_EQ_L = bpy.data.objects.new('Camera', Cam_EQ_L)
        Cam_obj_EQ_L.name = "Camera_EQ_L"
        Cam_obj_EQ_L.data.type = 'PANO'
        Cam_obj_EQ_L.data.cycles.panorama_type = "EQUIRECTANGULAR"
        Cam_obj_EQ_L.data.sensor_width = 50
        Cam_obj_EQ_L.rotation_euler = left
        scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_L)


        # PERSPECTIVE FRONT
        Cam_F = bpy.data.cameras.new(name = "Camera_F")
        Cam_F.name = "Camera_F"
        Cam_F.name = "Camera_F"
        Cam_F.name = "Camera_F"
        Cam_obj_F = bpy.data.objects.new('Camera', Cam_F)
        Cam_obj_F.name = "Camera_F"
        Cam_obj_F.data.lens = 25
        Cam_obj_F.data.clip_end = 1000
        Cam_obj_F.data.sensor_width = 50
        Cam_obj_F.rotation_euler = front
        scene.collection.children['Camera_System'].objects.link(Cam_obj_F)

        # PERSPECTIVE BACK
        Cam_B = bpy.data.cameras.new(name = "Camera_B")
        Cam_B.name = "Camera_B"
        Cam_obj_B = bpy.data.objects.new('Camera', Cam_B)
        Cam_obj_B.name = "Camera_B"
        Cam_obj_B.data.lens = 25
        Cam_obj_B.data.clip_end = 1000
        Cam_obj_B.data.sensor_width = 50
        Cam_obj_B.rotation_euler = back
        scene.collection.children['Camera_System'].objects.link(Cam_obj_B)

        # PERSPECTIVE TOP
        Cam_T = bpy.data.cameras.new(name = "Camera_T")
        Cam_T.name = "Camera_T"
        Cam_obj_T = bpy.data.objects.new('Camera', Cam_T)
        Cam_obj_T.name = "Camera_T"
        Cam_obj_T.data.lens = 25
        Cam_obj_T.data.clip_end = 1000
        Cam_obj_T.data.sensor_width = 50
        Cam_obj_T.rotation_euler = top
        scene.collection.children['Camera_System'].objects.link(Cam_obj_T)


        # PERSPECTIVE DOWN
        Cam_D = bpy.data.cameras.new(name = "Camera_D")
        Cam_D.name = "Camera_D"
        Cam_obj_D = bpy.data.objects.new('Camera', Cam_D)
        Cam_obj_D.name = "Camera_D"
        Cam_obj_D.data.lens = 25
        Cam_obj_D.data.clip_end = 1000
        Cam_obj_D.data.sensor_width = 50
        Cam_obj_D.rotation_euler = down
        scene.collection.children['Camera_System'].objects.link(Cam_obj_D)


        # PERSPECTIVE LEFT
        Cam_L = bpy.data.cameras.new(name = "Camera_L")
        Cam_L.name = "Camera_L"
        Cam_obj_L = bpy.data.objects.new('Camera', Cam_L)
        Cam_obj_L.name = "Camera_L"
        Cam_obj_L.data.lens = 25
        Cam_obj_L.data.clip_end = 1000
        Cam_obj_L.data.sensor_width = 50
        Cam_obj_L.rotation_euler = left
        scene.collection.children['Camera_System'].objects.link(Cam_obj_L)


        # PERSPECTIVE RIGHT
        Cam_R = bpy.data.cameras.new(name = "Camera_R")
        Cam_R.name = "Camera_R"
        Cam_obj_R = bpy.data.objects.new('Camera', Cam_R)
        Cam_obj_R.name = "Camera_R"
        Cam_obj_R.data.lens = 25
        Cam_obj_R.data.clip_end = 1000
        Cam_obj_R.data.sensor_width = 50
        Cam_obj_R.rotation_euler = right
        scene.collection.children['Camera_System'].objects.link(Cam_obj_R)



        # make specific camera activated
        mytool = scene.my_tool

        cam = bpy.data.objects[mytool.camera_list]
        scene.camera = cam


        scene.render.resolution_percentage = mytool.resolution

        if "EQ" in mytool.camera_list:
            scene.render.resolution_x = mytool.equi_width
            scene.render.resolution_y = mytool.equi_width//2
        else:
            scene.render.resolution_x = mytool.cube_width
            scene.render.resolution_y = mytool.cube_width  

        

        
        return {'FINISHED'}


class NODE_OT_TEST(bpy.types.Operator):
    bl_label = "SetEnv"
    bl_idname = "node.test_operator"
    
    def execute(self, context):
        scene = context.scene
        scene.use_nodes = True     
        #setup fiew things first
        try:
            scene.render.engine = 'crowdrender'
        except:
            scene.render.engine = 'CYCLES'
            
        # start indexing every objects for occlusion
        #-------------------------------------------
        prior_selection = context.selected_objects
        bpy.ops.object.select_all(action='SELECT')
        selection = context.selected_objects

        for obj in selection:
            obj.select_set(True)
            #change '8' to whichever pass index you choose
            obj.pass_index = 8
            obj.select_set(False)

        for obj in prior_selection:
            obj.select_set(True)
        
        # Finish setting up index for occlusion
        #-------------------------------------------
            
        
        scene.cycles.use_denoising = True
        scene.view_layers["View Layer"].use_pass_combined = True
        scene.view_layers["View Layer"].use_pass_combined = True
        scene.view_layers["View Layer"].use_pass_normal = True
        scene.view_layers["View Layer"].use_pass_vector = True
        scene.view_layers["View Layer"].use_pass_object_index = True  
        
        if scene.node_tree.nodes.get("render_layers_root") is None:
            #render layers
            #render_layers = scene.node_tree.nodes["Render Layers"]
            render_layers = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
            render_layers.name = "render_layers_root"
            render_layers.location = (0,400)
            
        
        
        mytool = scene.my_tool#note this mytool is referencing my_tool constructed on register function

        scene.render.resolution_percentage = mytool.resolution

        if "EQ" in mytool.camera_list:
            scene.render.resolution_x = mytool.equi_width
            scene.render.resolution_y = mytool.equi_width//2
        else:
            scene.render.resolution_x = mytool.cube_width
            scene.render.resolution_y = mytool.cube_width    
        
        out_node_list = ["frame","depth","normal","flow","occlusion","noise"]

        for outnode in out_node_list:
            if scene.node_tree.nodes.get(outnode):
                nodex = scene.node_tree.nodes.get(outnode)  
                nodex.base_path = f'{mytool.my_path}/{outnode}/{mytool.camera_list}'
        
        if scene.node_tree.nodes.get("frame") is None:
            # for frame
            #----------------------------------------------
            frame = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            frame.name = "frame"
            frame.width, frame.height = 500,100
            #frame.name , this can be changed by bpy.data.scenes['Scene'].node_tree.nodes["ImageX"]
            #frame.width, frame.height = 
            frame.location = (300,800)
            frame.base_path = f'{mytool.my_path}/frame/{mytool.camera_list}'
            frame.format.file_format = "PNG"
            frame.format.color_depth = "16"
            frame.format.compression = 0
            frame.format.color_mode = "RGB"
            #----------------------------------------------
        
        
        if scene.node_tree.nodes.get("mapper") is None:
            #for depth
            #----------------------------------------------
            mapper = scene.node_tree.nodes.new('CompositorNodeMapRange')
            mapper.name = "mapper"
            mapper.location = (300, 600)
            mapper.use_clamp = True
            mapper.inputs[1].default_value = mytool.min_depth
            mapper.inputs[2].default_value = mytool.max_depth
            mapper.inputs[3].default_value = 0
            mapper.inputs[4].default_value = 1
            
        if scene.node_tree.nodes.get("depth") is None:
            #---create output-link
            depth = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            depth.name = "depth"
            depth.location = (500, 600)
            depth.width, depth.height = 500, 100
            depth.base_path = f'{mytool.my_path}/depth/{mytool.camera_list}'
            depth.format.file_format = "OPEN_EXR"
            depth.format.color_mode = "RGB"
            depth.format.color_depth = "32"
            depth.format.exr_codec = 'ZIP'
            
            
        #create link
        if (scene.node_tree.nodes.get("mapper") is not None) and (scene.node_tree.nodes.get("depth") is not None):
            mapper = scene.node_tree.nodes.get("mapper")
            depth = scene.node_tree.nodes.get("depth")
            link_to_depth = scene.node_tree.links.new
            link_to_depth(mapper.outputs[0], depth.inputs[0])
        #----------------------------------------------
        
        if scene.node_tree.nodes.get("normal") is None:
            #for normals
            #----------------------------------------------
            normal = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            normal.name = "normal"
            normal.location = (300,400)
            normal.width, normal.height = 500,100
            normal.base_path = f'{mytool.my_path}/normal/{mytool.camera_list}'
            normal.format.file_format = "OPEN_EXR"
            normal.format.color_mode = "RGB"
            normal.format.color_depth = "32"
            normal.format.exr_codec = 'ZIP'    
            #----------------------------------------------
        
        if scene.node_tree.nodes.get("seprgb") is None:
            #for flows
            #----------------------------------------------
            #separate rgb
            seprgb = scene.node_tree.nodes.new('CompositorNodeSepRGBA')
            seprgb.name = "seprgb"
            seprgb.location = (300, 290)
                
        if scene.node_tree.nodes.get("combrgb") is None:
            #combine rgb
            combrgb = scene.node_tree.nodes.new('CompositorNodeCombRGBA')
            combrgb.name = "combrgb"
            combrgb.location = (500, 290)
        
        #link rgb
        if (scene.node_tree.nodes.get("seprgb") is not None) and (scene.node_tree.nodes.get("combrgb") is not None):
            seprgb = scene.node_tree.nodes.get("seprgb")
            combrgb = scene.node_tree.nodes.get("combrgb")
            sep_comb_rgb_link = scene.node_tree.links.new
            sep_comb_rgb_link(seprgb.outputs[0], combrgb.inputs[0])
            sep_comb_rgb_link(seprgb.outputs[1], combrgb.inputs[1])
            sep_comb_rgb_link(seprgb.outputs[2], combrgb.inputs[2])
            sep_comb_rgb_link(seprgb.outputs[3], combrgb.inputs[3])
            
        if scene.node_tree.nodes.get("flow") is None:
            #flow output
            flow = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            flow.name = "flow"
            flow.location = (650,290)
            flow.width, flow.height = 500,100
            flow.base_path = f'{mytool.my_path}/flow/{mytool.camera_list}'
            flow.format.file_format = "OPEN_EXR"
            flow.format.color_mode = "RGBA"
            flow.format.color_depth = "32"
            flow.format.exr_codec = "NONE"
            flow.format.use_zbuffer = False
        

        if (scene.node_tree.nodes.get("combrgb") is not None) and (scene.node_tree.nodes.get("flow") is not None):
            #link rgb to flow
            combrgb = scene.node_tree.nodes.get("combrgb")
            flow = scene.node_tree.nodes.get("flow")
            rgb_to_flow_link = scene.node_tree.links.new
            rgb_to_flow_link(combrgb.outputs[0], flow.inputs[0])
        #----------------------------------------------
        
        
        #for occlusions
        #----------------------------------------------
        if scene.node_tree.nodes.get("idmask") is None:
            #IDMASK
            idmask = scene.node_tree.nodes.new('CompositorNodeIDMask')
            idmask.name = "idmask"
            idmask.location = (300, 140)
            idmask.use_antialiasing = True
            idmask.index = 8
        
        if scene.node_tree.nodes.get("occlusion") is None:
            # occlusion
            occlusion = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            occlusion.name = "occlusion"
            occlusion.location = (500,140)
            occlusion.width, occlusion.height = 500,100
            occlusion.base_path = f'{mytool.my_path}/occlusion/{mytool.camera_list}'
            occlusion.format.file_format = "OPEN_EXR"
            occlusion.format.color_mode = "RGBA"
            occlusion.format.color_depth = "32"
            occlusion.format.exr_codec = "NONE"
        
        #LINK IDMASK WITH OCCLUSION
        if (scene.node_tree.nodes.get("idmask") is not None) and (scene.node_tree.nodes.get("occlusion") is not None):
            idmask = scene.node_tree.nodes.get("idmask")
            occlusion = scene.node_tree.nodes.get("occlusion")
            link_mask_to_occlusion = scene.node_tree.links.new
            link_mask_to_occlusion(idmask.outputs[0], occlusion.inputs[0])
        #----------------------------------------------
        
        
        #For noise
        #----------------------------------------------
        if scene.node_tree.nodes.get("noise") is None:
            noise = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            noise.name = "noise"
            noise.location = (300,0)
            noise.width, noise.height = 500,100
            noise.base_path = f'{mytool.my_path}/noise/{mytool.camera_list}'
            noise.format.file_format = "PNG"
            noise.format.color_mode = "RGB"
            noise.format.color_depth = "16"
        
        # LETS DO SOME LINKING
        if scene.node_tree.nodes.get("render_layers_root") is not None:
            render_layers = scene.node_tree.nodes.get("render_layers_root")
            link = scene.node_tree.links.new
            if scene.node_tree.nodes.get("frame") is not None:
                frame = scene.node_tree.nodes.get("frame")
                link(render_layers.outputs[0], frame.inputs[0])
            if scene.node_tree.nodes.get("mapper") is not None:
                mapper = scene.node_tree.nodes.get("mapper")
                link(render_layers.outputs[2], mapper.inputs[0])
            if scene.node_tree.nodes.get("normal") is not None:
                normal = scene.node_tree.nodes.get("normal")
                link(render_layers.outputs[3], normal.inputs[0])
            if scene.node_tree.nodes.get("seprgb") is not None:
                seprgb = scene.node_tree.nodes.get("seprgb")
                link(render_layers.outputs[4], seprgb.inputs[0])
            if scene.node_tree.nodes.get("idmask") is not None:
                idmask = scene.node_tree.nodes.get("idmask")
                link(render_layers.outputs[5], idmask.inputs[0])
            if scene.node_tree.nodes.get("noise") is not None:
                noise = scene.node_tree.nodes.get("noise")
                link(render_layers.outputs[6], noise.inputs[0])
        
        return {'FINISHED'}

class ADD_TO_VIEW_PORT(NODE_PT_MAINPANEL):
    bl_space_type = 'VIEW_3D'
   
classes = [MyProperties, CAMERA_SETUP, NODE_PT_MAINPANEL, ADD_TO_VIEW_PORT, NODE_OT_TEST]   
    
def register():
    for cl in classes:
        bpy.utils.register_class(cl)
        bpy.types.Scene.my_tool = bpy.props.PointerProperty(type = MyProperties) 
    
def unregister():
    for cl in classes:            
        bpy.utils.unregister_class(cl)
        del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()
