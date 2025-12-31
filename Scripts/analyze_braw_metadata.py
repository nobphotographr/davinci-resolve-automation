"""
BRAWメタデータ解析による露出・WB推定スクリプト

Blackmagic RAW (.braw) ファイルのメタデータ（ISO、WB設定等）を
読み取り、適切な露出・ホワイトバランス調整値を計算します。

使用方法:
    python analyze_braw_metadata.py

出力:
    - BRAWメタデータ情報
    - 推奨CDL値（Slope, Offset）
"""
import sys
import os

sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")


# 標準的なカメラ設定の基準値
REFERENCE_ISO = 400        # ネイティブISOの基準
REFERENCE_WB_TEMP = 5600   # デイライト基準


def calculate_exposure_from_iso(iso, target_iso=REFERENCE_ISO):
    """
    ISO値から露出調整量を計算

    Args:
        iso: クリップのISO値
        target_iso: 目標ISO（基準値）

    Returns:
        float: Slope値（露出調整係数）
    """
    if iso <= 0:
        return 1.0

    # ISO比から露出差を計算
    # ISO 800 → ISO 400 なら 0.5倍明るく（=暗いので明るくする）
    # 実際にはノイズとダイナミックレンジの関係で単純ではないが、
    # 簡易的に計算
    stops_diff = (iso / target_iso)

    # 1段ごとに約20%の調整
    # 高ISOほど少し暗くする傾向（ノイズ軽減のため）
    if iso > target_iso:
        # 高ISO: やや暗くして持ち上げを減らす
        slope = 1.0 - (stops_diff - 1) * 0.05
    else:
        # 低ISO: やや明るくする余裕がある
        slope = 1.0 + (1 - stops_diff) * 0.1

    return max(0.7, min(1.3, slope))


def calculate_wb_from_temp(color_temp, tint=0, target_temp=REFERENCE_WB_TEMP):
    """
    色温度からホワイトバランス調整値を計算

    Args:
        color_temp: 撮影時の色温度（K）
        tint: ティント値（緑-マゼンタ）
        target_temp: 目標色温度

    Returns:
        tuple: (r_slope, g_slope, b_slope)
    """
    if color_temp <= 0:
        return (1.0, 1.0, 1.0)

    # 色温度の差分を計算
    temp_ratio = target_temp / color_temp

    # 色温度が低い（暖色）→ 青を足す
    # 色温度が高い（寒色）→ 赤を足す
    if color_temp < target_temp:
        # 撮影時が暖色設定 → 実際は寒色に写る → 暖色に補正
        # Red+, Blue-
        r_slope = 1.0 + (temp_ratio - 1) * 0.15
        b_slope = 1.0 - (temp_ratio - 1) * 0.15
    else:
        # 撮影時が寒色設定 → 実際は暖色に写る → 寒色に補正
        # Red-, Blue+
        r_slope = 1.0 - (1 - temp_ratio) * 0.15
        b_slope = 1.0 + (1 - temp_ratio) * 0.15

    g_slope = 1.0

    # ティント補正
    if tint != 0:
        # 正のティント → マゼンタ寄り（G-）
        # 負のティント → グリーン寄り（G+）
        g_slope = 1.0 - tint * 0.001

    # 範囲制限
    r_slope = max(0.85, min(1.15, r_slope))
    g_slope = max(0.95, min(1.05, g_slope))
    b_slope = max(0.85, min(1.15, b_slope))

    return (round(r_slope, 3), round(g_slope, 3), round(b_slope, 3))


def get_clip_metadata(clip):
    """
    クリップからメタデータを取得

    Args:
        clip: TimelineItem object

    Returns:
        dict: メタデータ情報
    """
    media_pool_item = clip.GetMediaPoolItem()
    if not media_pool_item:
        return {}

    metadata = {}

    # 取得可能なメタデータキー
    metadata_keys = [
        "Camera Type",
        "Camera Manufacturer",
        "ISO",
        "White Point (Kelvin)",
        "White Balance Tint",
        "Exposure Compensation",
        "Shutter",
        "Aperture",
        "Focal Length",
        "Distance",
        "Lens Type",
        "Resolution",
        "Frame Rate",
        "Bit Depth",
        "Codec",
        "File Name",
        "File Path",
        "Date Modified",
        "Duration",
        "Gamma Notes",  # Color Space情報
        "Data Level",
        "Input Color Space",
        "Input Gamma",
        "PAR Notes",
        "Reel Name",
        "Scene",
        "Shot",
        "Take",
        "Good Take",
        "Comments",
        "Description",
        "Keywords",
    ]

    for key in metadata_keys:
        value = media_pool_item.GetMetadata(key)
        if value:
            metadata[key] = value

    # ClipPropertyからも取得
    clip_properties = [
        "Alpha mode",
        "Angle",
        "Audio Bit Depth",
        "Audio Ch",
        "Audio Codec",
        "Audio Offset",
        "Bit Depth",
        "Camera #",
        "Clip Color",
        "Clip Name",
        "Data Level",
        "Date Added",
        "Date Created",
        "Date Modified",
        "Drop frame",
        "Duration",
        "Embedded Audio",
        "End",
        "End TC",
        "FPS",
        "Format",
        "Frame Rate",
        "Frames",
        "Good Take",
        "H-FLIP",
        "IDT",
        "In",
        "Input Color Space",
        "Input Gamma",
        "Input LUT",
        "Noise Reduction",
        "Offline Reference",
        "Out",
        "PAR",
        "Proxy",
        "Proxy Media Path",
        "Resolution",
        "Reel Name",
        "Sharpness",
        "Shot",
        "Start",
        "Start TC",
        "Super Scale",
        "Type",
        "Usage",
        "V-FLIP",
        "Video Codec"
    ]

    for prop in clip_properties:
        value = media_pool_item.GetClipProperty(prop)
        if value and prop not in metadata:
            metadata[f"Prop:{prop}"] = value

    return metadata


def analyze_braw_metadata(clip):
    """
    BRAWクリップのメタデータを解析し、推奨調整値を計算

    Args:
        clip: TimelineItem object

    Returns:
        dict: 解析結果と推奨CDL値
    """
    metadata = get_clip_metadata(clip)

    print("\n" + "="*60)
    print("BRAW Metadata Analysis")
    print("="*60)

    # 取得したメタデータを表示
    print("\n[Raw Metadata]")
    if not metadata:
        print("  No metadata available")
        return None

    for key, value in sorted(metadata.items()):
        print(f"  {key}: {value}")

    # ISO取得
    iso = None
    iso_str = metadata.get("ISO", "")
    if iso_str:
        try:
            iso = int(iso_str.replace("ISO", "").strip())
        except:
            pass

    # 色温度取得
    color_temp = None
    temp_str = metadata.get("White Point (Kelvin)", "")
    if temp_str:
        try:
            color_temp = int(temp_str.replace("K", "").strip())
        except:
            pass

    # ティント取得
    tint = 0
    tint_str = metadata.get("White Balance Tint", "")
    if tint_str:
        try:
            tint = float(tint_str)
        except:
            pass

    print("\n" + "-"*60)
    print("[Extracted Values]")
    print(f"  ISO: {iso if iso else 'Not found'}")
    print(f"  Color Temperature: {color_temp if color_temp else 'Not found'}K")
    print(f"  Tint: {tint}")

    # 推奨値計算
    print("\n" + "-"*60)
    print("[Calculated Adjustments]")

    # 露出調整
    if iso:
        exposure_slope = calculate_exposure_from_iso(iso)
        print(f"\n  ISO-based Exposure:")
        print(f"    Current ISO: {iso}")
        print(f"    Reference ISO: {REFERENCE_ISO}")
        print(f"    Recommended Slope: {exposure_slope:.3f}")
    else:
        exposure_slope = 1.0
        print(f"\n  ISO not found, using default Slope: 1.0")

    # WB調整
    if color_temp:
        r_slope, g_slope, b_slope = calculate_wb_from_temp(color_temp, tint)
        print(f"\n  Temperature-based WB:")
        print(f"    Current Temp: {color_temp}K")
        print(f"    Reference Temp: {REFERENCE_WB_TEMP}K")
        print(f"    Recommended RGB Slope: {r_slope} {g_slope} {b_slope}")
    else:
        r_slope, g_slope, b_slope = 1.0, 1.0, 1.0
        print(f"\n  Color temperature not found, using neutral WB")

    # CDL出力
    print("\n" + "="*60)
    print("Recommended CDL Values")
    print("="*60)

    exposure_cdl = {
        "NodeIndex": "2",
        "Slope": f"{exposure_slope:.3f} {exposure_slope:.3f} {exposure_slope:.3f}",
        "Offset": "0.0 0.0 0.0",
        "Power": "1.0 1.0 1.0",
        "Saturation": "1.0"
    }

    wb_cdl = {
        "NodeIndex": "3",
        "Slope": f"{r_slope} {g_slope} {b_slope}",
        "Offset": "0.0 0.0 0.0",
        "Power": "1.0 1.0 1.0",
        "Saturation": "1.0"
    }

    print(f"""
[Node 2: Exposure]
exposure_cdl = {{
    "NodeIndex": "2",
    "Slope": "{exposure_slope:.3f} {exposure_slope:.3f} {exposure_slope:.3f}",
    "Offset": "0.0 0.0 0.0",
    "Power": "1.0 1.0 1.0",
    "Saturation": "1.0"
}}

[Node 3: White Balance]
wb_cdl = {{
    "NodeIndex": "3",
    "Slope": "{r_slope} {g_slope} {b_slope}",
    "Offset": "0.0 0.0 0.0",
    "Power": "1.0 1.0 1.0",
    "Saturation": "1.0"
}}
""")

    return {
        "metadata": metadata,
        "iso": iso,
        "color_temp": color_temp,
        "tint": tint,
        "exposure_slope": exposure_slope,
        "wb_slopes": (r_slope, g_slope, b_slope),
        "cdl_exposure": exposure_cdl,
        "cdl_wb": wb_cdl
    }


def main():
    """メイン処理"""
    import DaVinciResolveScript as dvr

    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: Cannot connect to DaVinci Resolve")
        return False

    print(f"Connected to DaVinci Resolve {resolve.GetVersionString()}")

    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        print("Error: No project open")
        return False

    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("Error: No timeline")
        return False

    print(f"Project: {project.GetName()}")
    print(f"Timeline: {timeline.GetName()}")

    items = timeline.GetItemListInTrack("video", 1)
    if not items:
        print("Error: No clips in timeline")
        return False

    clip = items[0]
    print(f"\nAnalyzing clip: {clip.GetName()}")

    # メタデータ解析
    result = analyze_braw_metadata(clip)

    if result:
        # CDLを適用するか確認
        apply = input("\nApply these CDL values to current clip? (y/n): ").strip().lower()

        if apply == 'y':
            print("\nApplying CDL values...")

            # 露出CDL適用
            exp_result = clip.SetCDL(result['cdl_exposure'])
            print(f"  Exposure (Node 2): {'Success' if exp_result else 'Failed'}")

            # WB CDL適用
            wb_result = clip.SetCDL(result['cdl_wb'])
            print(f"  White Balance (Node 3): {'Success' if wb_result else 'Failed'}")

            print("\n[OK] CDL values applied based on BRAW metadata!")

    return True


if __name__ == "__main__":
    main()
