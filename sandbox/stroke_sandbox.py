import os
# Houdini 上のpythonならhouはデフォルトインポートされているみたいなのでインポート処理を飛ばす
# 環境変数取れたら Houdini　上と判断
if not 'HFS' in os.environ:
    try:
        import hrpyc
        connection, hou = hrpyc.import_remote_module()
        sidefx_stroke = connection.modules["sidefx_stroke"]
        su = connection.modules["viewerstate.utils"]
    except:
        # 最後に定義されているhouのautocompleteが効くみたいなので例外側でインポート　
        import hou
        import sidefx_stroke
        import viewerstate.utils as su
else:
    import hou
    import sidefx_stroke
    import viewerstate.utils as su

hou.hipFile.clear(True)

#実データ部分
num = 3
mirrorData = su.ByteStream()
data = sidefx_stroke.StrokeData.create()
#data.pressure = 1.0
#data.dir = hou.Vector3(0.33,0.33,0.33)
data.proj_success=True # hit
#data.tilt = 90.0
#data.pos = hou.Vector3(0.6,0.6,0.6) # orig
#data.time = 1.0


xform1 = hou.hmath.buildRotate(0, 0, -45)
direction = hou.Vector3(1,0,0) * xform1
pos = hou.Vector3(0,1,0)
scale = 0.3

for i in range(num):
    data.proj_pos = pos # P
    mirrorData.add(data.encode(), su.ByteStream)
    pos += direction*scale


stream = su.ByteStream()
# RPC経由だとintのクラスの比較でエラーが出るので処理をコピー
#C:\Program Files\Side Effects Software\Houdini 19.0.589\houdini\python3.7libs\viewerstate\utils.py
#stream.add(sidefx_stroke.StrokeData.VERSION, int)
stream.pack_value('<i', sidefx_stroke.StrokeData.VERSION)
#stream.add(num, int)
stream.pack_value('<i', num)
stream.add(mirrorData, su.ByteStream)

# dataにセットする文字列
str_data = stream.data().decode()

geo:hou.Node = hou.node("/obj").createNode('geo')

paintsdfvolume:hou.Node  = geo.createNode('paintsdfvolume',"arms")

paintsdfvolume.setParms(
    {
        "stroke_numstrokes": 1,
        "stroke1_data": str_data,
    }
)