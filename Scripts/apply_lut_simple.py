"""
シンプルなLUT適用スクリプト
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

    project = resolve.GetProjectManager().GetCurrentProject()
    timeline = project.GetCurrentTimeline()
    items = timeline.GetItemListInTrack("video", 1)

    if not items:
        print("No clips in timeline")
        return

    clip = items[0]

    # ノード情報
    print(f"Node count: {clip.GetNumNodes()}")
    for i in range(1, clip.GetNumNodes() + 1):
        label = clip.GetNodeLabel(i)
        print(f"  Node {i}: {label}")

    # LUTパス
    lut_path = r"F:\Github\davinci-resolve-automation\output\Original_Cinematic_Classic.cube"

    # ファイル存在確認
    if os.path.exists(lut_path):
        print(f"\nLUT file exists: {lut_path}")
    else:
        print(f"\nLUT file NOT found: {lut_path}")
        return

    # 各ノードにLUT適用を試行
    print("\nTrying to apply LUT to each node:")
    for node_idx in range(1, clip.GetNumNodes() + 1):
        result = clip.SetLUT(node_idx, lut_path)
        print(f"  Node {node_idx}: {'Success' if result else 'Failed'}")

    # 代替: タイムラインアイテムのLUT
    print("\nChecking available methods:")
    methods = [m for m in dir(clip) if not m.startswith('_')]
    lut_methods = [m for m in methods if 'lut' in m.lower() or 'LUT' in m]
    print(f"LUT-related methods: {lut_methods}")

    # 全メソッドも表示
    print(f"\nAll available methods on TimelineItem:")
    for m in sorted(methods):
        print(f"  {m}")


if __name__ == "__main__":
    main()
