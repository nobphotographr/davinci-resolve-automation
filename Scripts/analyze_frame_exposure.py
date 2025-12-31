"""
フレーム解析による露出・色温度推定スクリプト

タイムラインのクリップからフレームを書き出し、
画像解析で露出とホワイトバランスの推奨値を計算します。

使用方法:
    python analyze_frame_exposure.py

必要なライブラリ:
    pip install pillow numpy

出力:
    - 推奨CDL値（Slope, Offset）
    - 解析レポート
"""
import sys
import os
import tempfile
import numpy as np

sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install pillow")
    sys.exit(1)


def analyze_image_exposure(image_path):
    """
    画像の露出を解析し、調整値を推奨

    Returns:
        dict: 解析結果と推奨CDL値
    """
    img = Image.open(image_path)
    img_array = np.array(img, dtype=np.float32) / 255.0

    # RGB平均値
    r_mean = np.mean(img_array[:, :, 0])
    g_mean = np.mean(img_array[:, :, 1])
    b_mean = np.mean(img_array[:, :, 2])

    # 輝度計算 (Rec.709)
    luminance = 0.2126 * r_mean + 0.7152 * g_mean + 0.0722 * b_mean

    # ヒストグラム解析
    gray = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]

    # シャドウ・ミッドトーン・ハイライトの分布
    shadows = np.mean(gray < 0.25)      # 暗部の割合
    midtones = np.mean((gray >= 0.25) & (gray <= 0.75))  # 中間調の割合
    highlights = np.mean(gray > 0.75)   # 明部の割合

    # 露出評価
    # 理想的なミッドグレーは約0.18（18%グレー）〜0.5
    target_luminance = 0.35  # やや明るめをターゲット

    exposure_diff = target_luminance - luminance

    # 露出調整用Slope計算
    if luminance > 0.01:  # ゼロ除算防止
        exposure_slope = min(max(target_luminance / luminance, 0.5), 2.0)
    else:
        exposure_slope = 1.5

    # シャドウが多すぎる場合はOffsetで持ち上げ
    shadow_offset = 0.0
    if shadows > 0.4:  # 40%以上がシャドウ
        shadow_offset = min((shadows - 0.3) * 0.05, 0.03)

    return {
        "r_mean": r_mean,
        "g_mean": g_mean,
        "b_mean": b_mean,
        "luminance": luminance,
        "shadows_ratio": shadows,
        "midtones_ratio": midtones,
        "highlights_ratio": highlights,
        "recommended_slope": round(exposure_slope, 3),
        "recommended_offset": round(shadow_offset, 4)
    }


def analyze_white_balance(image_path):
    """
    画像のホワイトバランスを解析し、調整値を推奨

    Returns:
        dict: 解析結果と推奨CDL値
    """
    img = Image.open(image_path)
    img_array = np.array(img, dtype=np.float32) / 255.0

    r_mean = np.mean(img_array[:, :, 0])
    g_mean = np.mean(img_array[:, :, 1])
    b_mean = np.mean(img_array[:, :, 2])

    # グレーワールド仮定による補正
    # 理想的にはR=G=Bに近づける
    avg_all = (r_mean + g_mean + b_mean) / 3.0

    if r_mean > 0.01:
        r_correction = avg_all / r_mean
    else:
        r_correction = 1.0

    if g_mean > 0.01:
        g_correction = avg_all / g_mean
    else:
        g_correction = 1.0

    if b_mean > 0.01:
        b_correction = avg_all / b_mean
    else:
        b_correction = 1.0

    # 補正値を穏やかに（極端な補正を避ける）
    r_slope = min(max(r_correction, 0.8), 1.2)
    g_slope = min(max(g_correction, 0.9), 1.1)  # Gは基準なので控えめ
    b_slope = min(max(b_correction, 0.8), 1.2)

    # 色温度の推定
    # R > B なら暖色、R < B なら寒色
    if r_mean > b_mean * 1.1:
        color_temp = "warm"
        temp_description = "暖色系（オレンジ寄り）"
    elif b_mean > r_mean * 1.1:
        color_temp = "cool"
        temp_description = "寒色系（ブルー寄り）"
    else:
        color_temp = "neutral"
        temp_description = "ニュートラル"

    return {
        "r_mean": r_mean,
        "g_mean": g_mean,
        "b_mean": b_mean,
        "color_temperature": color_temp,
        "temp_description": temp_description,
        "recommended_r_slope": round(r_slope, 3),
        "recommended_g_slope": round(g_slope, 3),
        "recommended_b_slope": round(b_slope, 3)
    }


def export_frame_from_timeline(clip, frame_offset=0, output_path=None):
    """
    タイムラインからフレームを書き出し（簡易版）

    注意: DaVinci ResolveのAPIではフレームの直接書き出しは制限があるため、
    デリバーページでのスチル書き出しか、GrabStillを使用します。

    実際の運用では、手動でスチルを保存するか、
    レンダリング機能を使ってフレームを書き出してください。
    """
    # GrabStillはGalleryにスチルを保存する
    # 直接ファイルパスへの書き出しはAPIでは難しい
    return None


def analyze_clip_with_manual_frame(image_path):
    """
    手動で保存したフレーム画像を解析

    Args:
        image_path: 解析する画像ファイルのパス

    Returns:
        dict: 露出とWBの推奨CDL値
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return None

    print(f"\n{'='*60}")
    print(f"Analyzing: {os.path.basename(image_path)}")
    print('='*60)

    # 露出解析
    exposure = analyze_image_exposure(image_path)
    print("\n[Exposure Analysis]")
    print(f"  Luminance: {exposure['luminance']:.3f}")
    print(f"  Shadows:   {exposure['shadows_ratio']*100:.1f}%")
    print(f"  Midtones:  {exposure['midtones_ratio']*100:.1f}%")
    print(f"  Highlights:{exposure['highlights_ratio']*100:.1f}%")
    print(f"\n  Recommended Slope:  {exposure['recommended_slope']}")
    print(f"  Recommended Offset: {exposure['recommended_offset']}")

    # WB解析
    wb = analyze_white_balance(image_path)
    print("\n[White Balance Analysis]")
    print(f"  R mean: {wb['r_mean']:.3f}")
    print(f"  G mean: {wb['g_mean']:.3f}")
    print(f"  B mean: {wb['b_mean']:.3f}")
    print(f"  Color Temperature: {wb['temp_description']}")
    print(f"\n  Recommended R Slope: {wb['recommended_r_slope']}")
    print(f"  Recommended G Slope: {wb['recommended_g_slope']}")
    print(f"  Recommended B Slope: {wb['recommended_b_slope']}")

    # CDL形式で出力
    print("\n" + "="*60)
    print("Recommended CDL Values for DaVinci Resolve")
    print("="*60)

    # 露出用CDL（Node 2想定）
    exp_slope = exposure['recommended_slope']
    exp_offset = exposure['recommended_offset']
    print(f"""
[Node 2: Exposure]
exposure_cdl = {{
    "NodeIndex": "2",
    "Slope": "{exp_slope} {exp_slope} {exp_slope}",
    "Offset": "{exp_offset} {exp_offset} {exp_offset}",
    "Power": "1.0 1.0 1.0",
    "Saturation": "1.0"
}}
""")

    # WB用CDL（Node 3想定）
    print(f"""[Node 3: White Balance]
wb_cdl = {{
    "NodeIndex": "3",
    "Slope": "{wb['recommended_r_slope']} {wb['recommended_g_slope']} {wb['recommended_b_slope']}",
    "Offset": "0.0 0.0 0.0",
    "Power": "1.0 1.0 1.0",
    "Saturation": "1.0"
}}
""")

    return {
        "exposure": exposure,
        "white_balance": wb,
        "cdl_exposure": {
            "NodeIndex": "2",
            "Slope": f"{exp_slope} {exp_slope} {exp_slope}",
            "Offset": f"{exp_offset} {exp_offset} {exp_offset}",
            "Power": "1.0 1.0 1.0",
            "Saturation": "1.0"
        },
        "cdl_wb": {
            "NodeIndex": "3",
            "Slope": f"{wb['recommended_r_slope']} {wb['recommended_g_slope']} {wb['recommended_b_slope']}",
            "Offset": "0.0 0.0 0.0",
            "Power": "1.0 1.0 1.0",
            "Saturation": "1.0"
        }
    }


def main():
    """メイン処理"""
    import DaVinciResolveScript as dvr

    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: Cannot connect to DaVinci Resolve")
        return

    print(f"Connected to DaVinci Resolve {resolve.GetVersionString()}")

    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        print("Error: No project open")
        return

    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("Error: No timeline")
        return

    print(f"Project: {project.GetName()}")
    print(f"Timeline: {timeline.GetName()}")

    # 解析対象の画像パス
    # 実際の運用では、以下のいずれかの方法でフレームを取得:
    # 1. カラーページで Grab Still → ギャラリーからエクスポート
    # 2. デリバーページで特定フレームをスチル出力
    # 3. 別途撮影した参照画像を使用

    print("\n" + "="*60)
    print("Frame Analysis for Exposure/WB Detection")
    print("="*60)
    print("""
このスクリプトは画像ファイルを解析して、
露出とホワイトバランスの推奨CDL値を計算します。

使用方法:
1. DaVinci Resolveでカラーページを開く
2. 解析したいフレームで右クリック → Grab Still
3. ギャラリーでスチルを右クリック → Export
4. 保存した画像ファイルのパスを入力

または、クリップのサムネイルやプロキシを直接解析することも可能です。
""")

    # デモ用: ユーザー入力でパスを受け取る
    image_path = input("\nEnter image path to analyze (or 'demo' for demo mode): ").strip()

    if image_path.lower() == 'demo':
        # デモ用のテスト画像を生成
        print("\n[Demo Mode] Creating test image...")
        demo_path = os.path.join(tempfile.gettempdir(), "demo_frame.png")

        # やや暗めで暖色の画像を生成（テスト用）
        demo_array = np.zeros((100, 100, 3), dtype=np.uint8)
        demo_array[:, :, 0] = 100  # R
        demo_array[:, :, 1] = 80   # G
        demo_array[:, :, 2] = 60   # B

        Image.fromarray(demo_array).save(demo_path)
        image_path = demo_path
        print(f"Demo image created: {demo_path}")

    if image_path and os.path.exists(image_path):
        result = analyze_clip_with_manual_frame(image_path)

        if result:
            # CDLを適用するか確認
            apply = input("\nApply these CDL values to current clip? (y/n): ").strip().lower()

            if apply == 'y':
                items = timeline.GetItemListInTrack("video", 1)
                if items:
                    clip = items[0]

                    print("\nApplying CDL values...")

                    # 露出CDL適用
                    exp_result = clip.SetCDL(result['cdl_exposure'])
                    print(f"  Exposure (Node 2): {'Success' if exp_result else 'Failed'}")

                    # WB CDL適用
                    wb_result = clip.SetCDL(result['cdl_wb'])
                    print(f"  White Balance (Node 3): {'Success' if wb_result else 'Failed'}")

                    print("\n[OK] CDL values applied!")
                else:
                    print("Error: No clips in timeline")
    else:
        print(f"Error: File not found: {image_path}")


if __name__ == "__main__":
    main()
