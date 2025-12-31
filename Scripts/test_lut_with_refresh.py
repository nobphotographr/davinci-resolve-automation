"""
LUT適用テスト - RefreshLUTList付き
"""
import sys
import os
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr


def main():
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: DaVinci Resolve not connected")
        return

    print(f"Connected to: DaVinci Resolve {resolve.GetVersionString()}")

    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()

    if not project:
        print("No project open")
        return

    print(f"Project: {project.GetName()}")

    # LUTリストをリフレッシュ
    print("\nRefreshing LUT list...")
    project.RefreshLUTList()
    print("LUT list refreshed!")

    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("No timeline")
        return

    items = timeline.GetItemListInTrack("video", 1)
    if not items:
        print("No clips")
        return

    clip = items[0]
    print(f"\nClip: {clip.GetName()}")
    print(f"Nodes: {clip.GetNumNodes()}")

    # LUTファイル名（フルパスではなくファイル名のみ）
    lut_filename = "Original_Cinematic_Classic.cube"
    lut_fullpath = r"F:\Github\davinci-resolve-automation\output\Original_Cinematic_Classic.cube"

    print(f"\n--- Testing LUT application ---")
    print(f"LUT filename: {lut_filename}")
    print(f"LUT fullpath: {lut_fullpath}")

    # 方法1: ファイル名のみ（ResolveのLUTディレクトリにある場合）
    print("\n1. Using filename only:")
    for node_idx in [1, 4]:
        result = clip.SetLUT(node_idx, lut_filename)
        print(f"   Node {node_idx}: {'Success' if result else 'Failed'}")

    # 方法2: フルパス
    print("\n2. Using full path:")
    for node_idx in [1, 4]:
        result = clip.SetLUT(node_idx, lut_fullpath)
        print(f"   Node {node_idx}: {'Success' if result else 'Failed'}")

    # 方法3: フォワードスラッシュ
    lut_forward = lut_fullpath.replace("\\", "/")
    print(f"\n3. Using forward slashes: {lut_forward}")
    for node_idx in [1, 4]:
        result = clip.SetLUT(node_idx, lut_forward)
        print(f"   Node {node_idx}: {'Success' if result else 'Failed'}")

    # 現在のLUTを確認
    print("\n--- Current LUT on nodes ---")
    for i in range(1, clip.GetNumNodes() + 1):
        lut = clip.GetLUT(i)
        print(f"  Node {i}: {lut if lut else '(none)'}")

    # CDL適用テスト
    print("\n--- Testing CDL application ---")
    cdl_map = {
        "NodeIndex": "2",
        "Slope": "1.1 1.0 0.95",
        "Offset": "0.01 0.0 -0.01",
        "Power": "1.0 1.0 1.0",
        "Saturation": "1.0"
    }
    result = clip.SetCDL(cdl_map)
    print(f"CDL to Node 2: {'Success' if result else 'Failed'}")


if __name__ == "__main__":
    main()
