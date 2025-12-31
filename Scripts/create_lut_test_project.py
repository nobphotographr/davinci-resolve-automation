"""
LUTテスト用プロジェクト作成スクリプト
"""
import sys
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr

def main():
    # DaVinci Resolveに接続
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: DaVinci Resolveに接続できません。起動しているか確認してください。")
        sys.exit(1)

    print(f"DaVinci Resolve {resolve.GetVersionString()} に接続しました")

    project_manager = resolve.GetProjectManager()

    # 新規プロジェクト作成
    project_name = "LUT_Test_Project"
    project = project_manager.CreateProject(project_name)

    if not project:
        # 既存プロジェクトがあれば開く
        print(f"プロジェクト '{project_name}' は既に存在するか作成できません。現在のプロジェクトを使用します。")
        project = project_manager.GetCurrentProject()
        if not project:
            print("Error: プロジェクトが開かれていません。")
            sys.exit(1)
    else:
        print(f"プロジェクト '{project_name}' を作成しました")

    media_pool = project.GetMediaPool()

    # メディアファイルをインポート
    media_path = r"C:\Users\nobuy\Downloads\The-End-of-the-World-Emerald-Lake-Original.braw"

    print(f"\nメディアをインポート中: {media_path}")
    imported = media_pool.ImportMedia([media_path])

    if imported and len(imported) > 0:
        print(f"  インポート成功: {len(imported)} ファイル")
        media_item = imported[0]

        # メディア情報を表示
        clip_props = media_item.GetClipProperty()
        print(f"\n--- クリップ情報 ---")
        print(f"  ファイル名: {clip_props.get('File Name', 'N/A')}")
        print(f"  解像度: {clip_props.get('Resolution', 'N/A')}")
        print(f"  フレームレート: {clip_props.get('FPS', 'N/A')}")
        print(f"  デュレーション: {clip_props.get('Duration', 'N/A')}")
        print(f"  コーデック: {clip_props.get('Video Codec', 'N/A')}")
    else:
        print("  メディアのインポートに失敗しました")
        print("  ファイルパスを確認してください")
        sys.exit(1)

    # タイムライン作成
    timeline_name = "LUT_Test_Timeline"
    timeline = media_pool.CreateEmptyTimeline(timeline_name)

    if timeline:
        print(f"\nタイムライン '{timeline_name}' を作成しました")

        # クリップをタイムラインに追加
        root_folder = media_pool.GetRootFolder()
        clips = root_folder.GetClipList()

        if clips and len(clips) > 0:
            media_pool.AppendToTimeline(clips)
            print(f"  クリップをタイムラインに追加しました")
    else:
        print("タイムラインの作成に失敗しました")

    # カラーページに移動
    resolve.OpenPage("color")
    print("\nカラーページに移動しました")

    # 現在のタイムライン情報
    current_timeline = project.GetCurrentTimeline()
    if current_timeline:
        clip_count = current_timeline.GetTrackCount("video")
        items = current_timeline.GetItemListInTrack("video", 1)
        print(f"\n--- タイムライン情報 ---")
        print(f"  タイムライン名: {current_timeline.GetName()}")
        print(f"  ビデオトラック数: {clip_count}")
        if items:
            print(f"  クリップ数: {len(items)}")

    print("\n" + "=" * 50)
    print("ノード構成の推奨")
    print("=" * 50)
    print("""
以下のノード構成を手動で作成してください：

  [Node 1: Exposure]     ノード1: 露出調整
       ↓
  [Node 2: WB]           ノード2: ホワイトバランス
       ↓
  [Node 3: LUT]          ノード3: LUT適用

作成手順：
1. カラーページでクリップを選択
2. 右クリック → ノードを追加 → シリアルノードを追加（2回）
3. 各ノードにラベルを付ける（右クリック → ノードラベル）
   - ノード1: "Exposure"
   - ノード2: "WB"
   - ノード3: "LUT"

ノード作成後、スクリプトでLUTを適用できます。
""")

    print("\n完了！")

if __name__ == "__main__":
    main()
