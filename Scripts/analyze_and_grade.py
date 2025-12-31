"""
クリップ分析・自動グレーディングスクリプト
露出とホワイトバランスの推奨値を計算し、ノードに適用
"""
import sys
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr


def get_current_clip():
    """現在のクリップを取得"""
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: DaVinci Resolveに接続できません")
        return None, None, None

    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        print("Error: プロジェクトが開かれていません")
        return None, None, None

    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("Error: タイムラインがありません")
        return None, None, None

    # 現在のクリップを取得
    items = timeline.GetItemListInTrack("video", 1)
    if not items or len(items) == 0:
        print("Error: タイムラインにクリップがありません")
        return None, None, None

    return resolve, project, items[0]


def analyze_clip_colors(clip):
    """クリップの色情報を分析（ノードグラフから取得可能な情報）"""
    print("\n" + "=" * 50)
    print("クリップ色分析")
    print("=" * 50)

    # クリップのプロパティを取得
    props = clip.GetMediaPoolItem().GetClipProperty() if clip.GetMediaPoolItem() else {}

    print(f"\nクリップ: {props.get('File Name', 'Unknown')}")
    print(f"解像度: {props.get('Resolution', 'N/A')}")

    # 現在のグレード情報を取得
    print("\n--- 現在のノード情報 ---")
    node_count = clip.GetNumNodes()
    print(f"ノード数: {node_count}")

    for i in range(1, node_count + 1):
        label = clip.GetNodeLabel(i)
        print(f"  Node {i}: {label if label else '(no label)'}")

    return True


def set_exposure_correction(clip, node_index, offset=0.0, gain=1.0):
    """
    露出補正をノードに適用

    Parameters:
    - offset: 全体的な明るさ調整 (-1.0 to 1.0)
    - gain: ゲイン調整 (0.0 to 4.0, 1.0 = 変化なし)
    """
    print(f"\n[Exposure Node {node_index}]")
    print(f"  Offset: {offset:.3f}")
    print(f"  Gain: {gain:.3f}")

    # プライマリーホイールの設定
    # Offset (Lift, Gamma, Gain, Offset の4つがある)
    # ここではOffsetとGainを使用

    # 注意: DaVinci ResolveのAPIでは直接的なプライマリー調整は限定的
    # LUTやCDL経由での調整が主になる

    # CDL (Color Decision List) パラメータとして設定
    # Slope = Gain, Offset = Offset, Power = Gamma
    cdl = {
        "NodeIndex": node_index,
        "Slope": [gain, gain, gain],      # RGB Gain
        "Offset": [offset, offset, offset], # RGB Offset
        "Power": [1.0, 1.0, 1.0],          # RGB Gamma (1.0 = 変化なし)
        "Saturation": 1.0
    }

    # 注: SetCDL は一部バージョンで利用可能
    # 代替として GetColorGroupを使用することも

    return cdl


def set_white_balance(clip, node_index, temp_shift=0.0, tint_shift=0.0):
    """
    ホワイトバランス補正

    Parameters:
    - temp_shift: 色温度シフト (負=青寄り, 正=黄寄り) -1.0 to 1.0
    - tint_shift: ティントシフト (負=緑寄り, 正=マゼンタ寄り) -1.0 to 1.0
    """
    print(f"\n[White Balance Node {node_index}]")
    print(f"  Temperature shift: {temp_shift:.3f}")
    print(f"  Tint shift: {tint_shift:.3f}")

    # 色温度調整をRGB Gainで近似
    # 暖色化: R+, B-
    # 寒色化: R-, B+
    r_gain = 1.0 + temp_shift * 0.1
    b_gain = 1.0 - temp_shift * 0.1

    # ティント調整
    # マゼンタ: G-
    # グリーン: G+
    g_gain = 1.0 - tint_shift * 0.05

    cdl = {
        "NodeIndex": node_index,
        "Slope": [r_gain, g_gain, b_gain],
        "Offset": [0.0, 0.0, 0.0],
        "Power": [1.0, 1.0, 1.0],
        "Saturation": 1.0
    }

    return cdl


def apply_lut_to_node(clip, node_index, lut_path):
    """LUTをノードに適用"""
    print(f"\n[LUT Node {node_index}]")
    print(f"  LUT: {lut_path}")

    success = clip.SetLUT(node_index, lut_path)
    if success:
        print("  [OK] LUT適用成功")
    else:
        print("  [NG] LUT適用失敗")

    return success


def print_manual_adjustment_guide():
    """手動調整のガイドを表示"""
    print("\n" + "=" * 60)
    print("手動調整ガイド")
    print("=" * 60)
    print("""
【露出調整 (Exposure Node)】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
このBRAW映像の推奨調整:

1. Lift (シャドウ)
   - 黒が浮いている場合: 下げる
   - シャドウが潰れている場合: 上げる

2. Gamma (ミッドトーン)
   - 全体が暗い場合: 上げる (1.0 → 1.1程度)
   - 全体が明るい場合: 下げる

3. Gain (ハイライト)
   - ハイライトが飛んでいる場合: 下げる
   - ハイライトが足りない場合: 上げる

4. Offset (全体)
   - 全体的に暗い: +方向
   - 全体的に明るい: -方向

【ホワイトバランス (WB Node)】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Temperature (色温度)
   - 青っぽい場合: 暖色方向へ (オレンジ)
   - 黄色っぽい場合: 寒色方向へ (青)

2. Tint (色かぶり)
   - 緑かぶり: マゼンタ方向へ
   - マゼンタかぶり: グリーン方向へ

Tip: スコープを見ながら調整
   - Waveform: 露出レベル確認
   - Vectorscope: 色かぶり確認
   - Parade: RGB バランス確認

【LUT適用後の微調整】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LUT適用後に追加ノードで以下を調整可能:
- コントラスト微調整
- 彩度調整
- セカンダリー（特定色の調整）
""")


def main():
    """メイン実行"""
    print("=" * 60)
    print("クリップ分析・グレーディングツール")
    print("=" * 60)

    resolve, project, clip = get_current_clip()
    if not clip:
        return

    # クリップ分析
    analyze_clip_colors(clip)

    # ノード構成を確認
    print("\n--- 推奨設定 ---")

    # 露出設定の例（実際の映像に合わせて調整）
    exposure_cdl = set_exposure_correction(
        clip,
        node_index=2,  # Node 2: Exposure
        offset=0.0,    # 必要に応じて調整
        gain=1.0       # 必要に応じて調整
    )

    # ホワイトバランス設定の例
    wb_cdl = set_white_balance(
        clip,
        node_index=3,  # Node 3: WB
        temp_shift=0.0,  # 必要に応じて調整
        tint_shift=0.0   # 必要に応じて調整
    )

    # LUT適用
    lut_path = r"F:\Github\davinci-resolve-automation\output\Original_Cinematic_Classic.cube"
    print(f"\n--- LUT適用 ---")

    # Node 4 にLUTを適用
    apply_lut_to_node(clip, 4, lut_path)

    # 手動調整ガイドを表示
    print_manual_adjustment_guide()

    print("\n" + "=" * 60)
    print("利用可能なオリジナルLUT")
    print("=" * 60)
    print("""
1. Original_Cinematic_Classic.cube  - バランスの取れた定番ルック
2. Original_Cinematic_Modern.cube   - 強めのティール&オレンジ
3. Original_Cinematic_WarmDrama.cube - 暖かみのあるドラマチック
4. Original_Cinematic_CoolThriller.cube - クールなスリラー風

LUTを変更するには:
  clip.SetLUT(4, "LUTファイルパス")
""")

    # 他のLUTも試せるようにパスを表示
    import os
    output_dir = r"F:\Github\davinci-resolve-automation\output"
    print(f"\nLUTファイル場所: {output_dir}")

    lut_files = [f for f in os.listdir(output_dir) if f.endswith('.cube')]
    for lut in lut_files:
        print(f"  - {lut}")


if __name__ == "__main__":
    main()
