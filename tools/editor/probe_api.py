# Writes the editor-Python API surface the blockout script relies on (UE version-specific, so probed, not assumed).
import unreal, sys
out = open(sys.argv[-1] if sys.argv[-1].endswith(".txt") else "/tmp/probe.txt", "w")
for cls in ["LevelEditorSubsystem", "EditorActorSubsystem", "EditorAssetLibrary", "DataLayerEditorSubsystem", "WorldPartitionEditorSubsystem", "AssetToolsHelpers", "StaticMeshEditorSubsystem", "EditorLevelLibrary"]:
    c = getattr(unreal, cls, None)
    out.write("%s: %s\n\n" % (cls, [n for n in dir(c) if not n.startswith("_")] if c else "MISSING"))
for fn in ["LevelEditorSubsystem.new_level", "LevelEditorSubsystem.new_level_from_template", "EditorActorSubsystem.spawn_actor_from_class", "DataLayerEditorSubsystem.create_data_layer_instance"]:
    c, m = fn.split(".")
    f = getattr(getattr(unreal, c, None), m, None)
    out.write("DOC %s: %s\n\n" % (fn, f.__doc__ if f else "MISSING"))
out.close()
