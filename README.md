# houdini_rpc_root

## 実行方法
基本はVisual Studio Code で記述して F5 で実行する
そのためにまずHoudini側の Python Source Editor で以下を実行しておく
```
import hrpyc
hrpyc.start_server()
```