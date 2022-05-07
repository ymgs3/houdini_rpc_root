import os
# Houdini 上のpythonならhouはデフォルトインポートされているみたいなのでインポート処理を飛ばす
# 環境変数取れたら Houdini　上と判断
if not 'HFS' in os.environ:
    try:
        import hrpyc
        connection, hou = hrpyc.import_remote_module()
        inlinecpp = connection.modules["inlinecpp"]
    except:
        # 最後に定義されているhouのautocompleteが効くみたいなので例外側でインポート　
        import hou
        import inlinecpp

mymodule = inlinecpp.createLibrary(
     name="cpp_string_library",
     includes="#include <UT/UT_String.h>",
     function_sources=[
 """
bool matchesPattern(const char *str, const char *pattern)
{
    return UT_String(str).multiMatch(pattern);
}
"""])

print(mymodule._shared_object_path())
string = "one"
for pattern in "o*", "x*", "^o*":
     print(repr(string), "matches", repr(pattern), ":")
     print(mymodule.matchesPattern(string, pattern))