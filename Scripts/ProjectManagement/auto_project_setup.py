#!/usr/bin/env python3
"""
DaVinci Resolve 完全自動LUTテストスクリプト

自動化内容:
1. プロジェクト作成
2. カラーマネジメント設定（BRAW → Rec.709）
3. BRAW素材読み込み
4. タイムライン作成
5. クリップ配置
6. Colorページに移動
7. ノードにLUT適用
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
    print("DaVinci Resolveが起動していることを確認してください。")
    sys.exit(1)


def main():
    """メイン処理"""
    print("=" * 80)
    print("🎬 DaVinci Resolve 完全自動LUTテスト")
    print("=" * 80)

    # 1. Resolveに接続
    print("\n[1/9] DaVinci Resolveに接続中...")
    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        print("❌ 接続失敗。Resolveが起動していることを確認してください。")
        sys.exit(1)
    print("✅ 接続成功")

    project_manager = resolve.GetProjectManager()

    # ユニークなプロジェクト名を生成
    import time
    timestamp = int(time.time())
    project_name = f"LUT_Test_BRAW_{timestamp}"

    # 2. 新規プロジェクト作成
    print(f"\n[2/9] プロジェクト '{project_name}' を作成中...")
    project = project_manager.CreateProject(project_name)
    if not project:
        print("❌ プロジェクト作成失敗")
        sys.exit(1)
    print("✅ プロジェクト作成完了")

    # 3. カラーマネジメント設定
    print("\n[3/9] カラーマネジメントを設定中（BRAW → Rec.709）...")
    # Color Science: DaVinci YRGB Color Managed
    success1 = project.SetSetting("colorScienceMode", "davinciYRGBColorManaged")
    # Timeline Color Space: Rec.709
    success2 = project.SetSetting("timelineColorSpaceTag", "Rec.709-A")

    if success1 and success2:
        print("✅ カラーマネジメント設定完了")
        print("   Color Science: DaVinci YRGB Color Managed")
        print("   Timeline Color Space: Rec.709-A")
    else:
        print("⚠️  カラーマネジメント設定が一部失敗（続行します）")

    # 4. BRAW素材を読み込み
    print("\n[4/9] BRAW素材を読み込み中...")
    media_storage = resolve.GetMediaStorage()
    media_pool = project.GetMediaPool()
    root_folder = media_pool.GetRootFolder()

    braw_path = os.path.expanduser("~/Downloads/The-End-of-the-World-Train-Original.braw")
    if not os.path.exists(braw_path):
        print(f"❌ BRAWファイルが見つかりません: {braw_path}")
        sys.exit(1)

    media_storage.AddItemListToMediaPool([braw_path])
    clips = root_folder.GetClipList()

    if not clips:
        print("❌ 素材の読み込み失敗")
        sys.exit(1)
    print(f"✅ 素材読み込み完了: {len(clips)}個のクリップ")

    # 5. タイムライン作成
    print("\n[5/9] タイムラインを作成中...")
    timeline = media_pool.CreateEmptyTimeline("LUT_Test_Timeline")
    if not timeline:
        print("❌ タイムライン作成失敗")
        sys.exit(1)
    print("✅ タイムライン作成完了")

    # 6. クリップをタイムラインに追加
    print("\n[6/9] クリップをタイムラインに追加中...")
    media_pool.AppendToTimeline(clips)
    project.SetCurrentTimeline(timeline)
    print("✅ クリップ追加完了")

    # 7. Colorページに移動
    print("\n[7/9] Colorページに移動中...")
    resolve.OpenPage("color")
    print("✅ Colorページに移動完了")

    # 8. タイムラインアイテムを取得
    print("\n[8/9] タイムラインアイテムを取得中...")
    timeline_items = timeline.GetItemListInTrack("video", 1)

    if not timeline_items or len(timeline_items) == 0:
        print("❌ タイムラインアイテムが見つかりません")
        sys.exit(1)

    first_item = timeline_items[0]
    print(f"✅ タイムラインアイテム取得完了: {len(timeline_items)}個")

    # 9. DRXテンプレート適用（ノード構成 + LUT）
    print("\n[9/9] DRXテンプレートを適用中...")

    # LUTリストを更新（重要！）
    print("   LUTリストを更新中...")
    project.RefreshLUTList()

    # LUTファイルをマスターディレクトリにコピー（Customフォルダは認識されないため）
    import shutil
    lut_source_dir = os.path.expanduser("~/Projects/cinematic-lut-analyzer/output")
    lut_master_dir = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"

    print("   LUTをマスターディレクトリにコピー中...")
    for lut_file in ["Classic_Cinema_Custom.cube", "Teal_Orange_Custom.cube"]:
        src = os.path.join(lut_source_dir, lut_file)
        dst = os.path.join(lut_master_dir, lut_file)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"     コピー: {lut_file}")

    # DRXテンプレートパス
    drx_path = os.path.expanduser("~/Projects/cinematic-lut-analyzer/templates/braw_cinematic_base.drx")

    if not os.path.exists(drx_path):
        print(f"   ⚠️  DRXファイルが見つかりません: {drx_path}")
        print("   代わりにノード1にLUTを直接適用します...")

        # フォールバック: ノード1に直接LUT適用
        success = first_item.SetLUT(1, "Classic_Cinema_Custom.cube")
        if success:
            print(f"   ✅ LUT適用成功: Classic_Cinema_Custom.cube")
            applied_luts = ["Classic_Cinema_Custom.cube"]
        else:
            print(f"   ❌ LUT適用失敗")
            applied_luts = []
    else:
        # DRXテンプレートを適用
        print(f"   DRXテンプレート適用中...")
        graph = first_item.GetNodeGraph()
        success = graph.ApplyGradeFromDRX(drx_path, 0)  # gradeMode=0: No keyframes

        if success:
            print(f"   ✅ DRXテンプレート適用成功")

            # 適用後のノード構成を表示
            num_nodes = first_item.GetNumNodes()  # TimelineItemから取得
            if num_nodes:
                print(f"   ノード数: {num_nodes}")
                for i in range(1, num_nodes + 1):
                    label = first_item.GetNodeLabel(i)
                    lut = first_item.GetLUT(i)
                    if lut:
                        print(f"     ノード{i}: {label} (LUT: {lut})")
                    else:
                        print(f"     ノード{i}: {label}")

                applied_luts = [first_item.GetLUT(4)] if num_nodes >= 4 else []
            else:
                print(f"   ⚠️  ノード数の取得失敗")
                applied_luts = []
        else:
            print(f"   ❌ DRXテンプレート適用失敗")
            applied_luts = []

    if not applied_luts:
        print("   ❌ すべてのLUT適用に失敗")
        print("   手動でLUTを適用してください:")
        print("   1. Colorページでノードを選択")
        print("   2. 右クリック → 3D LUT → Custom → LUTを選択")
    else:
        print(f"\n✅ LUT '{applied_luts[0]}' が適用されました")

    # 完了
    print("\n" + "=" * 80)
    print("✨ セットアップ完了")
    print("=" * 80)
    print(f"\nプロジェクト: {project_name}")
    print(f"タイムライン: LUT_Test_Timeline")
    print(f"カラースペース: Blackmagic Design → Rec.709")
    print(f"適用LUT: {applied_luts[0] if applied_luts else '手動で適用が必要'}")
    print("\nDaVinci Resolveで確認してください:")
    print("- Colorページで映像を確認")
    print("- LUTのオン/オフで効果を確認")
    print("- 別のLUTに切り替えて比較")


if __name__ == "__main__":
    main()
