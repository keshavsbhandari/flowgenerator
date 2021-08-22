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
    
    max_depth : bpy.props.FloatProperty(name = "Max Depth", soft_min = 0, soft_max  = 100000, default = 100)
    min_depth : bpy.props.FloatProperty(name = "Min Depth", soft_min = 0, soft_max  = 100000, default = 0.05)
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
        #row.operator('node.set_camera')


class NODE_CAMERASETUP_PANEL(bpy.types.Panel):
    bl_label = "Camera Setup Node Group"
    bl_idname = "NODE_CAMERASETUP_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Camera Setup' 

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        layout.prop(mytool, "resolution")
        layout.prop(mytool, "cube_width")
        layout.prop(mytool, "equi_width")
        layout.prop(mytool, "min_depth")
        layout.prop(mytool, "max_depth")
        layout.prop(mytool, "camera_list")
        
        row = layout.column()
        #row.operator('node.test_operator')
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


        # # Lets Create Previous Collections
        # if bpy.data.collections.get("Camera_System") is not None:
        #     coll = bpy.data.collections.get("Camera_System")
        #     bpy.data.collections.remove(coll)

        # make specific camera activated
        mytool = scene.my_tool

        scene.world.mist_settings.start = mytool.min_depth
        scene.world.mist_settings.depth = mytool.max_depth

        out_node_list = ["normal","flow","depth","raw_flow"]

        #out_node_list = ["frame","depth","normal","flow","occlusion","noise"]

        for outnode in out_node_list:
            if scene.node_tree.nodes.get(outnode):
                nodex = scene.node_tree.nodes.get(outnode)  
                nodex.base_path = f'{mytool.my_path}/{outnode}/{mytool.camera_list}/'

        scene.render.filepath = f'{mytool.my_path}/frame/{mytool.camera_list}/'

        scene.render.resolution_percentage = mytool.resolution

        if "EQ" in mytool.camera_list:
            scene.render.resolution_x = mytool.equi_width
            scene.render.resolution_y = mytool.equi_width//2
        else:
            scene.render.resolution_x = mytool.cube_width
            scene.render.resolution_y = mytool.cube_width

        
        # cam = bpy.data.objects.get(mytool.camera_list)
        # if cam:
        #     scene.camera = cam
        #     return {"FINISHED"}
        
        #Lets create a camera collections first
        collnames, _ = zip(*bpy.data.collections.items())
        if "Camera_System" in collnames:
            cam_collections = bpy.data.collections.get("Camera_System")
        else:
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
        
        #bpy.data.objects.get("Camera_R")
        
        location = 0,0,0
        
        for cam_name in list_of_camera:
            cam = bpy.data.objects.get(cam_name)
            if cam:
                location = cam.location
                break
        
        # for camname, cam in bpy.data.cameras.items():
        #     if camname.split('.')[0] in list_of_camera:
        #         bpy.data.cameras.remove(cam)

        all_cameras = []

        if bpy.data.objects.items():    
            all_cameras, _  = zip(*bpy.data.objects.items())
            all_cameras = list(map(lambda x:x.split(".")[0], all_cameras))

        Cam_obj_EQ_F = bpy.data.objects.get("Camera_EQ_F")
        if "Camera_EQ_F" not in all_cameras:
            # EQUIRECTANGULAR FRONT
            Cam_EQ_F = bpy.data.cameras.new(name = "Camera_EQ_F")
            Cam_EQ_F.name = "Camera_EQ_F"
            Cam_obj_EQ_F = bpy.data.objects.new('Camera', Cam_EQ_F)
            Cam_obj_EQ_F.name = "Camera_EQ_F"
            Cam_obj_EQ_F.data.type = 'PANO'
            Cam_obj_EQ_F.data.cycles.panorama_type = "EQUIRECTANGULAR"
            Cam_obj_EQ_F.data.sensor_width = 50
            Cam_obj_EQ_F.rotation_euler = front
            Cam_obj_EQ_F.location = location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_F)

        
        Cam_obj_EQ_B = bpy.data.objects.get("Camera_EQ_B")
        if  "Camera_EQ_B" not in all_cameras:                
            # EQUIRECTANGULAR BACK
            Cam_EQ_B = bpy.data.cameras.new(name = "Camera_EQ_B")
            Cam_EQ_B.name = "Camera_EQ_B"
            Cam_obj_EQ_B = bpy.data.objects.new('Camera', Cam_EQ_B)
            Cam_obj_EQ_B.name = "Camera_EQ_B"
            Cam_obj_EQ_B.data.type = 'PANO'
            Cam_obj_EQ_B.data.cycles.panorama_type = "EQUIRECTANGULAR"
            Cam_obj_EQ_B.data.sensor_width = 50
            Cam_obj_EQ_B.rotation_euler = back
            Cam_obj_EQ_B.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_B)

        Cam_obj_EQ_T = bpy.data.objects.get("Camera_EQ_T")
        if "Camera_EQ_T" not in all_cameras:    
            # EQUIRECTANGULAR TOP
            Cam_EQ_T = bpy.data.cameras.new(name = "Camera_EQ_T")
            Cam_EQ_T.name = "Camera_EQ_T"
            Cam_obj_EQ_T = bpy.data.objects.new('Camera', Cam_EQ_T)
            Cam_obj_EQ_T.name = "Camera_EQ_T"
            Cam_obj_EQ_T.data.type = 'PANO'
            Cam_obj_EQ_T.data.cycles.panorama_type = "EQUIRECTANGULAR"
            Cam_obj_EQ_T.data.sensor_width = 50
            Cam_obj_EQ_T.rotation_euler = top
            Cam_obj_EQ_T.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_T)

        Cam_obj_EQ_D = bpy.data.objects.get("Camera_EQ_D")
        if "Camera_EQ_D" not in all_cameras:    
            # EQUIRECTANGULAR DOWN
            Cam_EQ_D = bpy.data.cameras.new(name = "Camera_EQ_D")
            Cam_EQ_D.name = "Camera_EQ_D"
            Cam_obj_EQ_D = bpy.data.objects.new('Camera', Cam_EQ_D)
            Cam_obj_EQ_D.name = "Camera_EQ_D"
            Cam_obj_EQ_D.data.type = 'PANO'
            Cam_obj_EQ_D.data.cycles.panorama_type = "EQUIRECTANGULAR"
            Cam_obj_EQ_D.data.sensor_width = 50
            Cam_obj_EQ_D.rotation_euler = down
            Cam_obj_EQ_D.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_D)


        Cam_obj_EQ_R = bpy.data.objects.get("Camera_EQ_R")
        if "Camera_EQ_R" not in all_cameras:    
            # EQUIRECTANGULAR RIGHT
            Cam_EQ_R = bpy.data.cameras.new(name = "Camera_EQ_R")
            Cam_EQ_R.name = "Camera_EQ_R"
            Cam_obj_EQ_R = bpy.data.objects.new('Camera', Cam_EQ_R)
            Cam_obj_EQ_R.name = "Camera_EQ_R"
            Cam_obj_EQ_R.data.type = 'PANO'
            Cam_obj_EQ_R.data.cycles.panorama_type = "EQUIRECTANGULAR"
            Cam_obj_EQ_R.data.sensor_width = 50
            Cam_obj_EQ_R.rotation_euler = right
            Cam_obj_EQ_R.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_R)

        Cam_obj_EQ_L = bpy.data.objects.get("Camera_EQ_L")
        if "Camera_EQ_L" not in all_cameras:    
            # EQUIRECTANGULAR LEFT
            Cam_EQ_L = bpy.data.cameras.new(name = "Camera_EQ_L")
            Cam_EQ_L.name = "Camera_EQ_L"
            Cam_obj_EQ_L = bpy.data.objects.new('Camera', Cam_EQ_L)
            Cam_obj_EQ_L.name = "Camera_EQ_L"
            Cam_obj_EQ_L.data.type = 'PANO'
            Cam_obj_EQ_L.data.cycles.panorama_type = "EQUIRECTANGULAR"
            Cam_obj_EQ_L.data.sensor_width = 50
            Cam_obj_EQ_L.rotation_euler = left
            Cam_obj_EQ_L.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_EQ_L)


        Cam_F = bpy.data.objects.get("Camera_F")
        if "Camera_F" not in all_cameras:    
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
            Cam_obj_F.data.sensor_width = 50
            Cam_obj_F.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_F)

        Cam_obj_B = bpy.data.objects.get("Camera_B")
        if "Camera_B" not in all_cameras:    
            # PERSPECTIVE BACK
            Cam_B = bpy.data.cameras.new(name = "Camera_B")
            Cam_B.name = "Camera_B"
            Cam_obj_B = bpy.data.objects.new('Camera', Cam_B)
            Cam_obj_B.name = "Camera_B"
            Cam_obj_B.data.lens = 25
            Cam_obj_B.data.clip_end = 1000
            Cam_obj_B.data.sensor_width = 50
            Cam_obj_B.rotation_euler = back
            Cam_obj_B.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_B)

        Cam_obj_T = bpy.data.objects.get("Camera_T")
        if "Camera_T" not in all_cameras:    
            # PERSPECTIVE TOP
            Cam_T = bpy.data.cameras.new(name = "Camera_T")
            Cam_T.name = "Camera_T"
            Cam_obj_T = bpy.data.objects.new('Camera', Cam_T)
            Cam_obj_T.name = "Camera_T"
            Cam_obj_T.data.lens = 25
            Cam_obj_T.data.clip_end = 1000
            Cam_obj_T.data.sensor_width = 50
            Cam_obj_T.rotation_euler = top
            Cam_obj_T.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_T)


        Cam_obj_D = bpy.data.objects.get("Camera_D")
        if "Camera_D" not in all_cameras:    
            # PERSPECTIVE DOWN
            Cam_D = bpy.data.cameras.new(name = "Camera_D")
            Cam_D.name = "Camera_D"
            Cam_obj_D = bpy.data.objects.new('Camera', Cam_D)
            Cam_obj_D.name = "Camera_D"
            Cam_obj_D.data.lens = 25
            Cam_obj_D.data.clip_end = 1000
            Cam_obj_D.data.sensor_width = 50
            Cam_obj_D.rotation_euler = down
            Cam_obj_D.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_D)


        Cam_obj_L = bpy.data.objects.get("Camera_L")
        if "Camera_L" not in all_cameras:    
            # PERSPECTIVE LEFT
            Cam_L = bpy.data.cameras.new(name = "Camera_L")
            Cam_L.name = "Camera_L"
            Cam_obj_L = bpy.data.objects.new('Camera', Cam_L)
            Cam_obj_L.name = "Camera_L"
            Cam_obj_L.data.lens = 25
            Cam_obj_L.data.clip_end = 1000
            Cam_obj_L.data.sensor_width = 50
            Cam_obj_L.rotation_euler = left
            Cam_obj_L.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_L)


        Cam_obj_R = bpy.data.objects.get("Camera_R")
        if "Camera_R" not in all_cameras:    
            # PERSPECTIVE RIGHT
            Cam_R = bpy.data.cameras.new(name = "Camera_R")
            Cam_R.name = "Camera_R"
            Cam_obj_R = bpy.data.objects.new('Camera', Cam_R)
            Cam_obj_R.name = "Camera_R"
            Cam_obj_R.data.lens = 25
            Cam_obj_R.data.clip_end = 1000
            Cam_obj_R.data.sensor_width = 50
            Cam_obj_R.rotation_euler = right
            Cam_obj_R.location = Cam_obj_EQ_F.location
            scene.collection.children['Camera_System'].objects.link(Cam_obj_R)
        scene.camera = bpy.data.objects.get(mytool.camera_list)
        
        return {'FINISHED'}


class NODE_OT_TEST(bpy.types.Operator):
    bl_label = "SetEnv"
    bl_idname = "node.test_operator"
    
    def execute(self, context):
        scene = context.scene

        # if scene.node_tree.nodes.get("render_layers_root") is None:
        #     #render layers
        #     #render_layers = scene.node_tree.nodes["Render Layers"]
        #     render_layers = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
        #     render_layers.name = "render_layers_root"
        #     render_layers.location = (0,400)

        if scene.use_nodes:
            render_layers = bpy.context.scene.node_tree.nodes.get("render_layers_root")
            if render_layers is None:    
                render_layers = bpy.context.scene.node_tree.nodes.new("CompositorNodeRLayers")
        else:
            scene.use_nodes = True
            render_layers = bpy.context.scene.node_tree.nodes.get("Render Layers")
        
        render_layers.name = "render_layers_root"
        render_layers.location = (0,400)

        #setup fiew things first
        try:
            scene.render.engine = 'crowdrender'
        except:
            scene.render.engine = 'CYCLES'
            
        # start indexing every objects for occlusion
        #-------------------------------------------
        # prior_selection = context.selected_objects
        # bpy.ops.object.select_all(action='SELECT')
        # selection = context.selected_objects

        # for i,obj in enumerate(selection):
        #     obj.select_set(True)
        #     #change '8' to whichever pass index you choose
        #     obj.pass_index = 8
        #     obj.select_set(False)

        # for obj in prior_selection:
        #     obj.select_set(True)
        
        # Finish setting up index for occlusion
        #-------------------------------------------
            
        
        scene.cycles.use_denoising = True
        layer_name,_ = scene.view_layers.items()[0]#layer_name should be "View Layer"
        scene.view_layers[layer_name].use_pass_combined = True
        scene.view_layers[layer_name].use_pass_mist = True
        scene.view_layers[layer_name].use_pass_normal = True
        scene.view_layers[layer_name].use_pass_vector = True
        scene.view_layers[layer_name].use_pass_object_index = True  
        
        
            
        
        
        mytool = scene.my_tool#note this mytool is referencing my_tool constructed on register function

        scene.render.resolution_percentage = mytool.resolution

        if "EQ" in mytool.camera_list:
            scene.render.resolution_x = mytool.equi_width
            scene.render.resolution_y = mytool.equi_width//2
        else:
            scene.render.resolution_x = mytool.cube_width
            scene.render.resolution_y = mytool.cube_width    
        
        #out_node_list = ["frame","depth","normal","flow","occlusion","noise"]
        out_node_list = ["normal","flow","depth","raw_flow"]

        for outnode in out_node_list:
            if scene.node_tree.nodes.get(outnode):
                nodex = scene.node_tree.nodes.get(outnode)  
                nodex.base_path = f'{mytool.my_path}/{outnode}/{mytool.camera_list}/'
        
        # if scene.node_tree.nodes.get("frame") is None:
        #     # for frame
        #     #----------------------------------------------
        #     frame = scene.node_tree.nodes.new('CompositorNodeOutputFile')
        #     frame.name = "frame"
        #     frame.width, frame.height = 500,100
        #     #frame.name , this can be changed by bpy.data.scenes['Scene'].node_tree.nodes["ImageX"]
        #     #frame.width, frame.height = 
        #     frame.location = (300,800)
        #     frame.base_path = f'{mytool.my_path}/frame/{mytool.camera_list}'
        #     frame.format.file_format = "PNG"
        #     frame.format.color_depth = "16"
        #     frame.format.compression = 0
        #     frame.format.color_mode = "RGB"
        #     #----------------------------------------------

        scene.render.filepath = f'{mytool.my_path}/frame/{mytool.camera_list}/'
        
        scene.world.mist_settings.start = mytool.min_depth
        scene.world.mist_settings.depth = mytool.max_depth
        
        # if scene.node_tree.nodes.get("mapper") is None:
        #     #for depth
        #     #----------------------------------------------
        #     mapper = scene.node_tree.nodes.new('CompositorNodeMapRange')
        #     mapper.name = "mapper"
        #     mapper.location = (300, 600)
        #     mapper.use_clamp = True
        #     #mapper.inputs[1].default_value = mytool.min_depth
        #     scene.world.mist_settings.start = mytool.min_depth
        #     scene.world.mist_settings.depth = mytool.max_depth
        #     #mapper.inputs[2].default_value = mytool.max_depth
        #     #mapper.inputs[3].default_value = 0
        #     #mapper.inputs[4].default_value = 1
            
        if scene.node_tree.nodes.get("depth") is None:
            #---create output-link
            depth = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            depth.name = "depth"
            depth.location = (300, 510)
            depth.width, depth.height = 500, 100
            depth.base_path = f'{mytool.my_path}/depth/{mytool.camera_list}/'
            depth.format.file_format = "OPEN_EXR"
            depth.format.color_mode = "RGB"
            depth.format.color_depth = "32"
            depth.format.exr_codec = 'ZIP'

        if scene.node_tree.nodes.get("raw_flow") is None:
            #---create output-link
            raw_flow = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            raw_flow.name = "raw_flow"
            raw_flow.location = (300, 100)
            raw_flow.width, depth.height = 500, 100
            raw_flow.base_path = f'{mytool.my_path}/raw_flow/{mytool.camera_list}/'
            raw_flow.format.file_format = "OPEN_EXR"
            raw_flow.format.color_mode = "RGBA"
            raw_flow.format.color_depth = "32"
            raw_flow.format.exr_codec = 'ZIP'

        
            
            
        # #create link
        # if scene.node_tree.nodes.get("depth") is not None:
        #     #mapper = scene.node_tree.nodes.get("mapper")
        #     depth = scene.node_tree.nodes.get("depth")
        #     link_to_depth = scene.node_tree.links.new
        #     link_to_depth(mapper.outputs[0], depth.inputs[0])
        #----------------------------------------------
        
        if scene.node_tree.nodes.get("normal") is None:
            #for normals
            #----------------------------------------------
            normal = scene.node_tree.nodes.new('CompositorNodeOutputFile')
            normal.name = "normal"
            normal.location = (300,400)
            normal.width, normal.height = 500,100
            normal.base_path = f'{mytool.my_path}/normal/{mytool.camera_list}/'
            normal.format.file_format = "OPEN_EXR"
            normal.format.color_mode = "RGBA"
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
            flow.base_path = f'{mytool.my_path}/flow/{mytool.camera_list}/'
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
        # if scene.node_tree.nodes.get("idmask") is None:
        #     #IDMASK
        #     idmask = scene.node_tree.nodes.new('CompositorNodeIDMask')
        #     idmask.name = "idmask"
        #     idmask.location = (300, 140)
        #     idmask.use_antialiasing = True
        #     idmask.index = 8
        
        # if scene.node_tree.nodes.get("occlusion") is None:
        #     # occlusion
        #     occlusion = scene.node_tree.nodes.new('CompositorNodeOutputFile')
        #     occlusion.name = "occlusion"
        #     occlusion.location = (500,140)
        #     occlusion.width, occlusion.height = 500,100
        #     occlusion.base_path = f'{mytool.my_path}/occlusion/{mytool.camera_list}/'
        #     occlusion.format.file_format = "OPEN_EXR"
        #     occlusion.format.color_mode = "RGBA"
        #     occlusion.format.color_depth = "32"
        #     occlusion.format.exr_codec = "NONE"
        
        # #LINK IDMASK WITH OCCLUSION
        # if (scene.node_tree.nodes.get("idmask") is not None) and (scene.node_tree.nodes.get("occlusion") is not None):
        #     idmask = scene.node_tree.nodes.get("idmask")
        #     occlusion = scene.node_tree.nodes.get("occlusion")
        #     link_mask_to_occlusion = scene.node_tree.links.new
        #     link_mask_to_occlusion(idmask.outputs[0], occlusion.inputs[0])
        # #----------------------------------------------
        
        
        #For noise
        #----------------------------------------------
        # if scene.node_tree.nodes.get("noise") is None:
        #     noise = scene.node_tree.nodes.new('CompositorNodeOutputFile')
        #     noise.name = "noise"
        #     noise.location = (300,0)
        #     noise.width, noise.height = 500,100
        #     noise.base_path = f'{mytool.my_path}/noise/{mytool.camera_list}/'
        #     noise.format.file_format = "PNG"
        #     noise.format.color_mode = "RGB"
        #     noise.format.color_depth = "16"
        
        # LETS DO SOME LINKING
        if scene.node_tree.nodes.get("render_layers_root") is not None:
            render_layers = scene.node_tree.nodes.get("render_layers_root")
            link = scene.node_tree.links.new
            # if scene.node_tree.nodes.get("frame") is not None:
            #     frame = scene.node_tree.nodes.get("frame")
            #     link(render_layers.outputs[0], frame.inputs[0])
            if scene.node_tree.nodes.get("depth") is not None:
                depth = scene.node_tree.nodes.get("depth")
                link(render_layers.outputs[3], depth.inputs[0])
            if scene.node_tree.nodes.get("normal") is not None:
                normal = scene.node_tree.nodes.get("normal")
                link(render_layers.outputs[4], normal.inputs[0])
            if scene.node_tree.nodes.get("seprgb") is not None:
                seprgb = scene.node_tree.nodes.get("seprgb")
                raw_flow = scene.node_tree.nodes.get("raw_flow")
                link(render_layers.outputs[5], seprgb.inputs[0])
                link(render_layers.outputs[5], raw_flow.inputs[0])
            # if scene.node_tree.nodes.get("idmask") is not None:
            #     idmask = scene.node_tree.nodes.get("idmask")
            #     link(render_layers.outputs[5], idmask.inputs[0])
            # if scene.node_tree.nodes.get("noise") is not None:
            #     noise = scene.node_tree.nodes.get("noise")
            #     link(render_layers.outputs[6], noise.inputs[0])
        
        return {'FINISHED'}

class ADD_TO_VIEW_PORT(NODE_PT_MAINPANEL):
    bl_space_type = 'VIEW_3D'
   
#classes = [MyProperties, CAMERA_SETUP, NODE_PT_MAINPANEL, ADD_TO_VIEW_PORT, NODE_OT_TEST]
classes = [MyProperties, CAMERA_SETUP, NODE_PT_MAINPANEL,NODE_CAMERASETUP_PANEL, NODE_OT_TEST]   
    
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
