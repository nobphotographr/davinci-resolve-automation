"""
フルオートグレーディング - 露出、WB、LUTを自動適用
"""
import sys
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr


def main():
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: DaVinci Resolveに接続できません")
        return False

    print(f"DaVinci Resolve {resolve.GetVersionString()} に接続")

    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        print("Error: プロジェクトが開かれていません")
        return False

    print(f"Project: {project.GetName()}")

    # LUTリストをリフレッシュ
    project.RefreshLUTList()

    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("Error: タイムラインがありません")
        return False

    items = timeline.GetItemListInTrack("video", 1)
    if not items:
        print("Error: クリップがありません")
        return False

    clip = items[0]
    print(f"\nClip: {clip.GetName()}")
    print(f"Nodes: {clip.GetNumNodes()}")

    # ノード構成を表示
    print("\n--- Current Node Structure ---")
    for i in range(1, clip.GetNumNodes() + 1):
        label = clip.GetNodeLabel(i)
        lut = clip.GetLUT(i)
        print(f"  Node {i}: {label if label else '(no label)'} | LUT: {lut if lut else 'None'}")

    print("\n" + "=" * 50)
    print("Applying Auto Grade")
    print("=" * 50)

    # ============================================
    # Node 2: Exposure (露出調整)
    # ============================================
    # この映像はBRAWで適正露出に近いので、わずかな調整
    # Slope > 1.0 で明るく、< 1.0 で暗く
    # この映像は少し暗めなので、わずかに持ち上げる
    exposure_cdl = {
        "NodeIndex": "2",
        "Slope": "1.05 1.05 1.05",    # 全体を5%明るく
        "Offset": "0.005 0.005 0.005", # シャドウを少し持ち上げ
        "Power": "1.0 1.0 1.0",        # ガンマは変更なし
        "Saturation": "1.0"
    }

    print("\n[Node 2: Exposure]")
    print(f"  Slope: {exposure_cdl['Slope']} (+5% brightness)")
    print(f"  Offset: {exposure_cdl['Offset']} (shadow lift)")

    result = clip.SetCDL(exposure_cdl)
    print(f"  Result: {'Success' if result else 'Failed'}")

    # ============================================
    # Node 3: White Balance (ホワイトバランス)
    # ============================================
    # Emerald Lake（エメラルド湖）の映像 - 自然な色味を維持
    # 青緑の水と空のコントラストを活かす
    # わずかに暖色寄りにしてゴールデンアワー風に
    wb_cdl = {
        "NodeIndex": "3",
        "Slope": "1.02 1.0 0.98",     # R+2%, B-2% で暖色化
        "Offset": "0.0 0.0 0.0",
        "Power": "1.0 1.0 1.0",
        "Saturation": "1.0"
    }

    print("\n[Node 3: White Balance]")
    print(f"  Slope: {wb_cdl['Slope']} (warm shift)")

    result = clip.SetCDL(wb_cdl)
    print(f"  Result: {'Success' if result else 'Failed'}")

    # ============================================
    # Node 4: LUT
    # ============================================
    lut_name = "Original_Cinematic_Classic.cube"

    print(f"\n[Node 4: LUT]")
    print(f"  Applying: {lut_name}")

    result = clip.SetLUT(4, lut_name)
    print(f"  Result: {'Success' if result else 'Failed'}")

    # ============================================
    # 結果確認
    # ============================================
    print("\n" + "=" * 50)
    print("Final Node Status")
    print("=" * 50)

    for i in range(1, clip.GetNumNodes() + 1):
        label = clip.GetNodeLabel(i)
        lut = clip.GetLUT(i)
        print(f"  Node {i}: {label if label else '(no label)'} | LUT: {lut if lut else 'None'}")

    print("\n[OK] Auto grade applied!")
    print("\nTips:")
    print("  - Ctrl+D: Toggle node on/off to compare")
    print("  - Shift+D: Bypass all grades")

    return True


if __name__ == "__main__":
    main()
