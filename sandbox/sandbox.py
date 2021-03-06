import os
# Houdini 上のpythonならhouはデフォルトインポートされているみたいなのでインポート処理を飛ばす
# 環境変数取れたら Houdini　上と判断
if not 'HFS' in os.environ:
    try:
        import hrpyc
        connection, hou = hrpyc.import_remote_module()
        stroketoolutils = connection.modules["stroketoolutils"]
    except:
        # 最後に定義されているhouのautocompleteが効くみたいなので例外側でインポート　
        import hou

# https://www.youtube.com/playlist?list=PLXNFA1EysfYmpOEGcK1x_r6g_h2dOwAC4

vol:hou.SopNode = hou.node("/obj/geo1/paintsdfvolume1")
parm:hou.Parm =  vol.parm("stroke6_data")
parm.asCode()
print(parm.asCode())