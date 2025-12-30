#!/usr/bin/env python3
"""
DaVinci Resolve プロジェクトクリーンアップスクリプト
LUT_Test_BRAW_* プロジェクトを削除
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
    print("🗑️  DaVinci Resolve プロジェクトクリーンアップ")
    print("=" * 70)

    # Resolveに接続
    print("\n[1/2] DaVinci Resolveに接続中...")
    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        print("❌ 接続失敗")
        sys.exit(1)
    print("✅ 接続成功")

    project_manager = resolve.GetProjectManager()

    # プロジェクトリストを取得
    print("\n[2/2] テストプロジェクトを検索・削除中...")

    # ルートフォルダに移動
    project_manager.GotoRootFolder()

    # プロジェクトリストを取得
    project_list = project_manager.GetProjectListInCurrentFolder()
    print(f"\n全プロジェクト数: {len(project_list)}")
    print("プロジェクト一覧:")
    for project_name in project_list:
        print(f"  - {project_name}")

    # 削除対象のパターン
    delete_patterns = ["LUT_Test_BRAW_", "LUT_Test_Project"]

    deleted_count = 0
    failed_count = 0
    skipped_count = 0

    print("\n削除開始...\n")

    for project_name in project_list:
        # パターンマッチ
        should_delete = False
        for pattern in delete_patterns:
            if pattern in project_name:
                should_delete = True
                break

        if should_delete:
            # 削除試行
            success = project_manager.DeleteProject(project_name)
            if success:
                print(f"✅ 削除成功: {project_name}")
                deleted_count += 1
            else:
                print(f"⚠️  削除失敗: {project_name}")
                failed_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 70)
    print("クリーンアップ完了")
    print("=" * 70)
    print(f"\n削除成功: {deleted_count}個")
    print(f"削除失敗: {failed_count}個")
    print(f"スキップ: {skipped_count}個")


if __name__ == "__main__":
    main()
