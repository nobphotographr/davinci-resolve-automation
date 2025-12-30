#!/usr/bin/env python3
"""
DRXテンプレート適用スクリプト

事前に作成したノード構成（DRXファイル）を適用します
"""

import sys
import os

# DaVinci Resolve API のパスを設定
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
RESOLVE_SCRIPT_LIB = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"

os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB
sys.path.append(f"{RESOLVE_SCRIPT_API}/Modules")

try:
    import DaVinciResolveScript as dvr_script
except ImportError as e:
    print(f"❌ DaVinci Resolve APIのインポートに失敗: {e}")
    sys.exit(1)


def main():
    """メイン処理"""
    print("=" * 70)
    print("🎨 DRXテンプレート適用ツール")
    print("=" * 70)

    # Resolveに接続
    print("\n[1/5] DaVinci Resolveに接続中...")
    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        print("❌ 接続失敗")
        sys.exit(1)
    print("✅ 接続成功")

    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()

    if not project:
        print("❌ プロジェクトが開かれていません")
        sys.exit(1)

    print(f"\n現在のプロジェクト: {project.GetName()}")

    # タイムラインアイテムを取得
    print("\n[2/5] タイムラインアイテムを取得中...")
    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("❌ タイムラインがありません")
        sys.exit(1)

    timeline_items = timeline.GetItemListInTrack("video", 1)
    if not timeline_items or len(timeline_items) == 0:
        print("❌ タイムラインアイテムがありません")
        sys.exit(1)

    first_item = timeline_items[0]
    print(f"✅ タイムラインアイテム取得完了: {len(timeline_items)}個")

    # ノードグラフを取得
    print("\n[3/5] ノードグラフを取得中...")
    graph = first_item.GetNodeGraph()
    if not graph:
        print("❌ ノードグラフの取得失敗")
        sys.exit(1)

    current_nodes = graph.GetNumNodes()
    print(f"✅ 現在のノード数: {current_nodes}")

    # DRXファイルパス
    drx_path = os.path.expanduser("~/Projects/cinematic-lut-analyzer/templates/braw_cinematic_base.drx")

    print(f"\n[4/5] DRXテンプレートを確認中...")
    if not os.path.exists(drx_path):
        print(f"❌ DRXファイルが見つかりません: {drx_path}")
        print("\n以下の手順でDRXファイルを作成してください:")
        print("1. DaVinci ResolveのColorページでノード構成を作成")
        print("2. ギャラリーでGrab Still")
        print("3. スチルをExport → .drx形式で保存")
        print(f"4. 保存先: {drx_path}")
        sys.exit(1)

    print(f"✅ DRXファイル確認: {drx_path}")

    # DRXテンプレートを適用
    print(f"\n[5/5] DRXテンプレートを適用中...")

    # gradeMode:
    # 0 - "No keyframes"（キーフレームなし）
    # 1 - "Source Timecode aligned"（ソースタイムコードに合わせる）
    # 2 - "Start Frames aligned"（開始フレームに合わせる）
    grade_mode = 0  # キーフレームなし

    success = graph.ApplyGradeFromDRX(drx_path, grade_mode)

    if success:
        print("✅ DRXテンプレート適用成功")

        # 適用後のノード数を確認
        new_nodes = graph.GetNumNodes()
        print(f"\n適用後のノード数: {new_nodes}")

        # 各ノードのラベルを表示
        print("\nノード構成:")
        for i in range(1, new_nodes + 1):
            label = graph.GetNodeLabel(i)
            lut = graph.GetLUT(i)
            if lut:
                print(f"  ノード{i}: {label} (LUT: {lut})")
            else:
                print(f"  ノード{i}: {label}")
    else:
        print("❌ DRXテンプレート適用失敗")
        print("DRXファイルが正しい形式か確認してください")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✨ 完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
