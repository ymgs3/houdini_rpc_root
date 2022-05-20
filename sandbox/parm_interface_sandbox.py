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

#https://qiita.com/MIN0NIUM/items/e23a5b3b62b344b621f5
#https://www.sidefx.com/ja/docs/houdini/hom/hou/Node.html#parmTemplateGroup


hou.hipFile.clear(True)

node = hou.node("/obj").createNode("geo").createNode("null")
group = node.parmTemplateGroup()
folder = hou.FolderParmTemplate("folder", "My Parms")
folder.addParmTemplate(hou.FloatParmTemplate("myparm", "My Parm", 1))
group.append(folder)
node.setParmTemplateGroup(group)