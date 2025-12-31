"""
LUT適用方法のテスト - 様々な方法を試す
"""
import sys
import os
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr


def main():
    resolve = dvr.scriptapp("Resolve")
    project = resolve.GetProjectManager().GetCurrentProject()
    timeline = project.GetCurrentTimeline()
    items = timeline.GetItemListInTrack("video", 1)

    if not items:
        print("No clips")
        return

    clip = items[0]
    print(f"Clip: {clip.GetName()}")
    print(f"Nodes: {clip.GetNumNodes()}")

    lut_path = r"F:\Github\davinci-resolve-automation\output\Original_Cinematic_Classic.cube"

    # パスの正規化を試す
    lut_path_normalized = os.path.normpath(lut_path)
    lut_path_forward = lut_path.replace("\\", "/")

    print(f"\nOriginal path: {lut_path}")
    print(f"Normalized: {lut_path_normalized}")
    print(f"Forward slash: {lut_path_forward}")

    # 各パス形式で試す
    print("\n--- Testing different path formats ---")

    for node_idx in [1, 4]:
        print(f"\nNode {node_idx}:")

        # 方法1: 通常パス
        result = clip.SetLUT(node_idx, lut_path)
        print(f"  Backslash path: {result}")

        # 方法2: フォワードスラッシュ
        result = clip.SetLUT(node_idx, lut_path_forward)
        print(f"  Forward slash: {result}")

        # 方法3: 正規化パス
        result = clip.SetLUT(node_idx, lut_path_normalized)
        print(f"  Normalized: {result}")

    # GetLUTを試す
    print("\n--- Checking current LUT on nodes ---")
    for i in range(1, clip.GetNumNodes() + 1):
        current_lut = clip.GetLUT(i)
        print(f"  Node {i} LUT: {current_lut}")

    # プロジェクト設定のLUTパス確認
    print("\n--- Project LUT settings ---")
    settings = project.GetSetting()
    if settings:
        lut_settings = {k: v for k, v in settings.items() if 'lut' in k.lower()}
        for k, v in lut_settings.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
