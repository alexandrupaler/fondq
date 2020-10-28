### 1
For the situation where the Julia plugin is installed in PyCharm, edit 
`/home/username/.local/share/JetBrains/PyCharm..../julia-intellij/lib/julia-intellij-0.4.1.jar`
according to https://github.com/JuliaEditorSupport/julia-intellij/issues/446

### 2
Install PyCall in Julia - run this in the venv/conda used for fondq
```
using Pkg
dependencies = [
"PyCall",
]
Pkg.add(dependencies)
```