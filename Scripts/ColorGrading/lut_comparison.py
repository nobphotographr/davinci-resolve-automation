#!/usr/bin/env python3
"""
DaVinci Resolve LUT比較スクリプト

複数のLUTをカラーバージョンとして作成し、
UI上で簡単に切り替えて比較できるようにします。
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
    print("🎨 LUT比較バージョン作成ツール")
    print("=" * 70)

    # Resolveに接続
    print("\n[1/4] DaVinci Resolveに接続中...")
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

    # LUTリスト更新
    print("\n[2/4] LUTリストを更新中...")
    project.RefreshLUTList()

    # タイムラインアイテムを取得
    print("\n[3/4] タイムラインアイテムを取得中...")
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

    # LUT定義
    luts_to_test = [
        {
            "version_name": "Classic_Cinema",
            "lut_path": "Classic_Cinema_Custom.cube",
            "description": "クラシックシネマLUT（Shadow Blue, Highlight Orange）"
        },
        {
            "version_name": "Teal_Orange",
            "lut_path": "Teal_Orange_Custom.cube",
            "description": "ティール&オレンジLUT（モダンハリウッドスタイル）"
        },
        {
            "version_name": "No_LUT",
            "lut_path": "",
            "description": "LUTなし（オリジナル）"
        }
    ]

    # バージョン作成
    print("\n[4/4] カラーバージョンを作成中...")

    version_type = 0  # 0 = ローカルバージョン

    for lut_config in luts_to_test:
        version_name = lut_config["version_name"]
        lut_path = lut_config["lut_path"]
        description = lut_config["description"]

        print(f"\n  バージョン '{version_name}' を作成中...")
        print(f"    説明: {description}")

        # 既存バージョンをチェック
        existing_versions = first_item.GetVersionNameList(version_type)

        if existing_versions and version_name in existing_versions:
            print(f"    ⚠️  既存のバージョンを削除中...")
            first_item.DeleteVersionByName(version_name, version_type)

        # 新規バージョン作成
        success = first_item.AddVersion(version_name, version_type)
        if not success:
            print(f"    ❌ バージョン作成失敗")
            continue

        # バージョンを読み込み
        success = first_item.LoadVersionByName(version_name, version_type)
        if not success:
            print(f"    ❌ バージョン読み込み失敗")
            continue

        # LUTを適用（LUTパスが空でない場合）
        if lut_path:
            # ノード4にLUT適用（DRXテンプレート使用時）
            num_nodes = first_item.GetNumNodes()
            lut_node = min(4, num_nodes) if num_nodes else 1

            success = first_item.SetLUT(lut_node, lut_path)
            if success:
                print(f"    ✅ バージョン作成完了（LUT: {lut_path}）")
            else:
                print(f"    ⚠️  LUT適用失敗: {lut_path}")
        else:
            # LUTなしバージョン（すべてのノードからLUTを削除）
            num_nodes = first_item.GetNumNodes()
            if num_nodes:
                for i in range(1, num_nodes + 1):
                    first_item.SetLUT(i, "")
            print(f"    ✅ バージョン作成完了（LUTなし）")

    # 最初のバージョンに戻す
    first_version = luts_to_test[0]["version_name"]
    first_item.LoadVersionByName(first_version, version_type)

    print("\n" + "=" * 70)
    print("✨ 完了")
    print("=" * 70)
    print("\n作成されたカラーバージョン:")
    for lut_config in luts_to_test:
        print(f"  - {lut_config['version_name']}: {lut_config['description']}")

    print("\nDaVinci Resolveでの使い方:")
    print("1. Colorページでクリップを選択")
    print("2. 右側のパレット上部で「バージョン」ドロップダウンから選択")
    print("3. リアルタイムでLUTの違いを確認できます")


if __name__ == "__main__":
    main()
