import os
# Houdini 上のpythonならhouはデフォルトインポートされているみたいなのでインポート処理を飛ばす
# 環境変数取れたら Houdini　上と判断
if not 'HFS' in os.environ:
    try:
        import hrpyc
        connection, hou = hrpyc.import_remote_module()
        sidefx_stroke = connection.modules["sidefx_stroke"]
        su = connection.modules["viewerstate.utils"]
        #rpcのhouの値を使うとエラーが出る
        update_mode = connection.modules["hou"].updateMode.Manual
        folder_type = connection.modules["hou"].parmTemplateType.Folder
    except:
        # 最後に定義されているhouのautocompleteが効くみたいなので例外側でインポート　
        import hou
        import sidefx_stroke
        import viewerstate.utils as su
        update_mode = hou.updateMode.Manual
        folder_type = hou.parmTemplateType.Folder
else:
    import hou
    import sidefx_stroke
    import viewerstate.utils as su
    update_mode = hou.updateMode.Manual
    folder_type = hou.parmTemplateType.Folder
# https://www.youtube.com/playlist?list=PLXNFA1EysfYmpOEGcK1x_r6g_h2dOwAC4

# ストローク作成ヘルパ
def create_stroke_raw_data(pos:list):
    mirrorData = su.ByteStream()

    if pos:
        data = sidefx_stroke.StrokeData.create()
        data.proj_success=True
        for p in pos:
            data.proj_pos = p # P
            mirrorData.add(data.encode(), su.ByteStream)
    
    stream = su.ByteStream()
    stream.pack_value('<i', sidefx_stroke.StrokeData.VERSION)
    stream.pack_value('<i', len(pos))
    stream.add(mirrorData, su.ByteStream)

    # dataにセットする文字列
    str_data = stream.data().decode()
    return str_data

def allParmTemplates(group_or_folder):
    for parm_template in group_or_folder.parmTemplates():
        yield parm_template

    # multiparmブロック内のparmテンプレートを返したくないので、
    # そのフォルダparmテンプレートが実際にフォルダ用なのか検証します。
        if (parm_template.type() == folder_type and
        parm_template.isActualFolder()):
            for sub_parm_template in allParmTemplates(parm_template):
                yield sub_parm_template


hou.hipFile.clear(True)

#更新モードを変更
current_update_mode = hou.updateModeSetting()
hou.setUpdateMode(update_mode)
hou.updateModeSetting()


geo:hou.Node = hou.node("/obj").createNode('geo')

# 体の作成
shpere:hou.Node = geo.createNode('sphere')
shpere.setParms({
    "type":2,
    "t":(0,1.5,0),
    "rows":100,
    "cols":100,
})
softtransform:hou.Node  = geo.createNode('softxform')
softtransform.setParms({
    "group":"0",
    "t":(0,0.2,0),
    "rad":1
})
softtransform.setInput(0,shpere)

paintsdfvolume:hou.Node  = geo.createNode('paintsdfvolume',"arms")

paintsdfvolume.setParms(
    {
        "voxelsize":0.01,
        "stroke_numstrokes": 6,
        "stroke_radius":0.03,
        "samplerate":0.01,
    }
)

# 腕のモデリング
arm=0.1
finger = 0.03
thumb = 0.035

arm_dir = hou.Vector3(1,0,0) * hou.hmath.buildRotate(0, 0, -45)
arm_pos = hou.Vector3(0.9,1.5,0.0)
arm_scale = 0.3

thumb_dir = hou.Vector3(1,0,0) * hou.hmath.buildRotate(0, 0, 0)
thumb_pos = hou.Vector3(1.4,1.1,0.0)
thumb_scale = 0.05

index_finger_dir = hou.Vector3(1,0,0) * hou.hmath.buildRotate(0, 0, -30)
index_finger_pos = hou.Vector3(1.4,1.03,0.0)
index_finger_scale = 0.07

middle_finger_dir = hou.Vector3(1,0,0) * hou.hmath.buildRotate(0, 0, -55)
middle_finger_pos = hou.Vector3(1.37,0.97,0.0)
middle_finger_scale = 0.08

little_finger_dir = hou.Vector3(1,0,0) * hou.hmath.buildRotate(0, 0, -90)
little_finger_pos = hou.Vector3(1.30,0.97,0.0)
little_finger_scale = 0.06

raw_data = [
    {
        "radius":arm,
        "data":create_stroke_raw_data([
            arm_pos,
            arm_pos + arm_dir*arm_scale,
            arm_pos + arm_dir*arm_scale*2,
        ]),
    },
    {
        "radius":thumb,
        "data":create_stroke_raw_data([
            thumb_pos,
            thumb_pos + thumb_dir*thumb_scale*1,
            thumb_pos + thumb_dir*thumb_scale*2,
        ]),
    },
    {
        "radius":finger,
        "data":create_stroke_raw_data([
            index_finger_pos,
            index_finger_pos + index_finger_dir*middle_finger_scale*1,
            index_finger_pos + index_finger_dir*middle_finger_scale*2,
        ]),
    },
    {
        "radius":finger,
        "data":create_stroke_raw_data([
            middle_finger_pos,
            middle_finger_pos + middle_finger_dir*index_finger_scale*1,
            middle_finger_pos + middle_finger_dir*index_finger_scale*2,
        ]),
    },
    {
        "radius":finger,
        "data":create_stroke_raw_data([
            little_finger_pos,
            little_finger_pos + little_finger_dir*little_finger_scale*1,
            little_finger_pos + little_finger_dir*little_finger_scale*2,
        ]),
    },
]

for i,v in enumerate(raw_data):
    for key in v.keys():
        value = v[key]
        hou_parm = paintsdfvolume.parm("stroke{0}_{1}".format(i+1,key))
        hou_parm.set(value)

# VDBのミラー処理を作成してsubnetに入れる
mirror:hou.Node  = geo.createNode('mirror')
mirror.setParms(
    {
        "keepOriginal":False,
    }
)
mirror.setInput(0,paintsdfvolume)
vdbcombine_arm:hou.Node  = geo.createNode('vdbcombine')
vdbcombine_arm.setParms(
    {
        "operation":11,
    }
)
vdbcombine_arm.setInput(0,paintsdfvolume)
vdbcombine_arm.setInput(1,mirror)
        
nodes = [mirror,vdbcombine_arm]
vdbcombine_arm_name = vdbcombine_arm.name()
subnet_vdb_mirror:hou.Node = geo.collapseIntoSubnet(nodes,"VDB_MIRROR")
vdbcombine_arm:hou.Node = subnet_vdb_mirror.node(vdbcombine_arm_name)
subnet_arm_subnet_output:hou.Node = subnet_vdb_mirror.createNode("output")
subnet_arm_subnet_output.setInput(0,vdbcombine_arm)

#足
leg_radius = 0.15
paintsdfvolume_legs:hou.Node  = geo.createNode('paintsdfvolume',"legs")
paintsdfvolume_legs.setParms(
    {
        "voxelsize":0.01,
        "stroke_numstrokes": 1,
        "stroke_radius":leg_radius,
        "samplerate":0.01,
        "stroke1_data":create_stroke_raw_data([
            hou.Vector3(0.5,0.6 + leg_radius,0.0),
            hou.Vector3(0.5,0.3 + leg_radius,0.1),
            hou.Vector3(0.5,leg_radius,0.0),
            hou.Vector3(0.5,leg_radius,0.5),
        ]),
        
        "stroke1_radius":leg_radius,
        "stroke1_projcenter":(-0.5,0,0),
        "stroke1_projtype":1,
    }
)
subnet_vdb_mirror_for_leg:hou.Node = geo.copyItems([subnet_vdb_mirror])[0]
subnet_vdb_mirror_for_leg.setInput(0,paintsdfvolume_legs)

# 髪
paintsdfvolume_hair:hou.Node  = geo.createNode('paintsdfvolume',"hair")
paintsdfvolume_hair.setParms(
    {
        "voxelsize":0.01,
        "stroke_numstrokes": 2,
        "stroke_radius":0.1,
        "samplerate":0.01,
        "stroke1_data":create_stroke_raw_data([
            hou.Vector3(0.0,2.5,0.0),
            hou.Vector3(0.7,3.0,0.1),
        ]),
        "stroke1_radius":0.1,
        "stroke2_data":create_stroke_raw_data([
            hou.Vector3(0.0,2.5,-0.1),
            hou.Vector3(-0.3,2.8,0.0),
            hou.Vector3(-0.6,3.0,0.1),
        ]),"stroke2_radius":0.1,
    }
)

# 鼻
paintsdfvolume_nose:hou.Node  = geo.createNode('paintsdfvolume',"nose")
paintsdfvolume_nose.setParms(
    {
        "voxelsize":0.01,
        "stroke_numstrokes": 1,
        "stroke_radius":0.08,
        "samplerate":0.01,
        "stroke1_data":create_stroke_raw_data([
            hou.Vector3(0.0,2.0,0.8),
            hou.Vector3(0.0,1.7,1.2),
        ]),
        "stroke1_radius":0.08,
        "stroke1_projtype":1,
    }
)

# 目
eye_black:hou.Node  = geo.createNode('sphere')
eye_black.setParms({
    "type":2,
    "scale":0.6,
    "rows":50,
    "cols":50,
})

eye_black_xform:hou.Node  = geo.createNode('xform')
eye_black_xform.setParms(
    {
        "t":(0,0.5,0)
    }
)
eye_black_xform.setInput(0,eye_black)
eye_black_color:hou.Node  = geo.createNode('color')
eye_black_color.setParms(
    {
        "color":(0,0,0)
    }
)
eye_black_color.setInput(0,eye_black_xform)


eye_white:hou.Node  = geo.createNode('sphere')
eye_white.setParms({
    "type":2,
    "rows":50,
    "cols":50,
})
eye_white_color:hou.Node  = geo.createNode('color')
eye_white_color.setParms(
    {
        "color":(1,1,1)
    }
)
eye_white_color.setInput(0,eye_white)

eye_merge:hou.Node  = geo.createNode('merge')
eye_merge.setInput(0,eye_black_color)
eye_merge.setInput(1,eye_white_color)

eye_xform:hou.Node  = geo.createNode('xform')
eye_xform.setParms(
    {
        "t":(0.42,2.12,0.52),
        "r":(70,11,10),
        "scale":0.3,
    }
)
eye_xform.setInput(0,eye_merge)
eye_mirror:hou.Node  = geo.createNode('mirror')
eye_mirror.setInput(0,eye_xform)

# 体のボクセル化
vdbfrompolygons:hou.Node  = geo.createNode('vdbfrompolygons')
vdbfrompolygons.setParms(
    {
        "voxelsize":0.01,
    }
)
vdbfrompolygons.setInput(0,softtransform)

# 腕と結合
vdbcombine:hou.Node  = geo.createNode('vdbcombine')
vdbcombine.setParms(
    {
        "operation":11,
    }
)
vdbcombine.setInput(0,vdbfrompolygons)
vdbcombine.setInput(1,subnet_vdb_mirror)

#足と結合
vdbcombine_leg:hou.Node  = geo.createNode('vdbcombine')
vdbcombine_leg.setParms(
    {
        "operation":11,
    }
)
vdbcombine_leg.setInput(0,vdbcombine)
vdbcombine_leg.setInput(1,subnet_vdb_mirror_for_leg)

#髪と結合
vdbcombine_hair:hou.Node  = geo.createNode('vdbcombine')
vdbcombine_hair.setParms(
    {
        "operation":11,
    }
)
vdbcombine_hair.setInput(0,vdbcombine_leg)
vdbcombine_hair.setInput(1,paintsdfvolume_hair)

#鼻の結合
vdbcombine_nose:hou.Node  = geo.createNode('vdbcombine')
vdbcombine_nose.setParms(
    {
        "operation":11,
    }
)
vdbcombine_nose.setInput(0,vdbcombine_hair)
vdbcombine_nose.setInput(1,paintsdfvolume_nose)




# 目のへこみ
dent_nodes = []
null_dented:hou.Node  = geo.createNode('null',"DENTED")
null_dented.setInput(0,vdbcombine_nose)
dent_nodes.append(null_dented)

null_denter:hou.Node  = geo.createNode('null',"DENTER")
null_denter.setInput(0,eye_mirror)
dent_nodes.append(null_denter)

vdbfrompolygons_dent:hou.Node  = geo.createNode('vdbfrompolygons')
vdbfrompolygons_dent.setParms(
    {
        "voxelsize":0.01,
    }
)
vdbfrompolygons_dent.setInput(0,null_denter)
dent_nodes.append(vdbfrompolygons_dent)
dent_voxel_node = vdbfrompolygons_dent.name()


vdbcombine_dent:hou.Node  = geo.createNode('vdbcombine')
vdbcombine_dent.setParms(
    {
        "operation":12,
    }
)
vdbcombine_dent.setInput(0,vdbfrompolygons_dent)
vdbcombine_dent.setInput(1,null_dented)
dent_nodes.append(vdbcombine_dent)


vdbreshapesdf_dent:hou.Node  = geo.createNode('vdbreshapesdf')
vdbreshapesdf_dent.setParms(
    {
        "voxeloffset":2,
    }
)
vdbreshapesdf_dent.setInput(0,vdbcombine_dent)
dent_nodes.append(vdbreshapesdf_dent)
dent_shape_node = vdbreshapesdf_dent.name()

vdbcombine_dent_union:hou.Node  = geo.createNode('vdbcombine')
vdbcombine_dent_union.setParms(
    {
        "operation":11,
    }
)
vdbcombine_dent_union.setInput(0,null_dented)
vdbcombine_dent_union.setInput(1,vdbreshapesdf_dent)
dent_nodes.append(vdbcombine_dent_union)


vdbcombine_dent_subtract:hou.Node  = geo.createNode('vdbcombine')
vdbcombine_dent_subtract.setParms(
    {
        "operation":13,
    }
)
vdbcombine_dent_subtract.setInput(0,vdbcombine_dent_union)
vdbcombine_dent_subtract.setInput(1,vdbfrompolygons_dent)
dent_nodes.append(vdbcombine_dent_subtract)
dent_end_node = vdbcombine_dent_subtract.name()

# サブネット作成
subnet_vdb_dent:hou.Node = geo.collapseIntoSubnet(dent_nodes,"VDB_DENT")

group:hou.ParmTemplateGroup = subnet_vdb_dent.parmTemplateGroup()

# 初期のパラメータを非表示に
for template in allParmTemplates(group):
    template.hide(True)
    group.replace(template.name(),template)

folder = hou.FolderParmTemplate("folder", "Dent")
float_parm = hou.FloatParmTemplate("voxel_size", "Voxel Size", 1)
float_parm.setDefaultValue([0.01])
folder.addParmTemplate(float_parm)
float_parm = hou.FloatParmTemplate("voxel_offset", "Voxel Offset", 1)
float_parm.setDefaultValue([2.0])
folder.addParmTemplate(float_parm)
group.append(folder)
subnet_vdb_dent.setParmTemplateGroup(group)

#アウトプットの設定
subnet_dent_end_node = subnet_vdb_dent.node(dent_end_node)

subnet_output = subnet_vdb_dent.createNode("output")
subnet_output.setInput(0,subnet_dent_end_node)
subnet_output.setDisplayFlag(True)

#エクスプレッションを設定
subnet_dent_voxel_node = subnet_vdb_dent.node(dent_voxel_node)
subnet_dent_voxel_node.setParmExpressions(
    {
        "voxelsize":f'ch("{subnet_dent_voxel_node.relativePathTo(subnet_vdb_dent)}/voxel_size")'
    }
)

subnet_dent_shape_node = subnet_vdb_dent.node(dent_shape_node)
subnet_dent_shape_node.setParmExpressions(
    {
        "voxeloffset":f'ch("{subnet_dent_shape_node.relativePathTo(subnet_vdb_dent)}/voxel_offset")'
    }
)

subnet_vdb_dent.setParms(
    {
        "voxel_offset":7,
    }
)

# HDA作成
subnet_vdb_dent = subnet_vdb_dent.createDigitalAsset("vdb_dent","vdb_dent.hda",min_num_inputs=2,max_num_inputs=2)
definition = subnet_vdb_dent.type().definition()
definition.setParmTemplateGroup(group)

# 口の作成
mouth_shape:hou.Node  = geo.createNode('sphere')
mouth_shape.setParms({
    "type":2,
    "rad":(1.0,0.2,1.0),
    "t":(0.0,1.4,0.9),
    "r":(35,0.0,0.0),
    "scale":0.6,
    "rows":50,
    "cols":50,
})

mouth_dent = geo.createNode('vdb_dent')
mouth_dent.setParms(
    {
        "voxel_offset":3.5,
    }
)
mouth_dent.setInput(0,subnet_vdb_dent)
mouth_dent.setInput(1,mouth_shape)

# スムース
vdbsmooth:hou.Node  = geo.createNode('vdbsmooth')
vdbsmooth.setParms(
    {
        "iterations":4,
    }
)
vdbsmooth.setInput(0,mouth_dent)

# ポリゴンに変換
convertvdb:hou.Node  = geo.createNode('convertvdb')
convertvdb.setParms(
    {
        "conversion":2,
    }
)
convertvdb.setInput(0,vdbsmooth)

#目をマージ
merge:hou.Node  = geo.createNode('merge')
merge.setInput(0,convertvdb)
merge.setInput(1,eye_mirror)

disp_node = merge

# 表示するノードの設定
disp_node.setDisplayFlag(True)

# 全ノードをいい位置に移動
for node in hou.node("/").allSubChildren():
    node.moveToGoodPosition()

#更新実行
hou.ui.triggerUpdate()
hou.setUpdateMode(current_update_mode)
hou.updateModeSetting()
    
# 保存
hou.hipFile.save("creating_a_mega_character.hip")