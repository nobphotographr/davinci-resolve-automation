"""
DaVinci Resolve 20 セットアップスクリプト
"""
import sys
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr


def main():
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: DaVinci Resolveに接続できません")
        return

    print(f"DaVinci Resolve {resolve.GetVersionString()} に接続")

    pm = resolve.GetProjectManager()

    # 既存のLUT_Test_Projectを開く
    project = pm.LoadProject("LUT_Test_Project")
    if not project:
        # なければ新規作成
        project = pm.CreateProject("LUT_Test_Project")
        if not project:
            project = pm.GetCurrentProject()

    print(f"プロジェクト: {project.GetName()}")

    media_pool = project.GetMediaPool()

    # メディアプールの内容確認
    root = media_pool.GetRootFolder()
    clips = root.GetClipList()

    print(f"\nメディアプール内クリップ数: {len(clips) if clips else 0}")

    if clips:
        for clip in clips:
            props = clip.GetClipProperty()
            print(f"  - {props.get('File Name', 'Unknown')}")
    else:
        # クリップがない場合はインポート
        print("\nメディアをインポート中...")
        media_path = r"C:\Users\nobuy\Downloads\The-End-of-the-World-Emerald-Lake-Original.braw"
        imported = media_pool.ImportMedia([media_path])
        if imported:
            print(f"  インポート成功: {len(imported)} ファイル")
            clips = imported
        else:
            print("  インポート失敗")
            return

    # タイムライン確認
    timeline = project.GetCurrentTimeline()
    if not timeline:
        timelines = project.GetTimelineCount()
        if timelines > 0:
            timeline = project.GetTimelineByIndex(1)
            project.SetCurrentTimeline(timeline)
        else:
            # タイムライン作成
            timeline = media_pool.CreateEmptyTimeline("LUT_Test_Timeline")
            if timeline and clips:
                media_pool.AppendToTimeline(clips)

    if timeline:
        print(f"\nタイムライン: {timeline.GetName()}")
        items = timeline.GetItemListInTrack("video", 1)
        if items:
            print(f"クリップ数: {len(items)}")

            # クリップのノード情報
            clip = items[0]
            node_count = clip.GetNumNodes()
            print(f"\nノード数: {node_count}")
            for i in range(1, node_count + 1):
                label = clip.GetNodeLabel(i)
                print(f"  Node {i}: {label if label else '(no label)'}")

            # LUT適用テスト
            print("\n--- LUT適用テスト ---")
            lut_path = r"F:\Github\davinci-resolve-automation\output\Original_Cinematic_Classic.cube"

            # ノード4にLUT適用（LUTノードがある場合）
            if node_count >= 4:
                result = clip.SetLUT(4, lut_path)
                print(f"Node 4 LUT適用: {'成功' if result else '失敗'}")

            # ノード1にも試す
            result = clip.SetLUT(1, lut_path)
            print(f"Node 1 LUT適用: {'成功' if result else '失敗'}")

    # カラーページに移動
    resolve.OpenPage("color")
    print("\nカラーページに移動しました")


if __name__ == "__main__":
    main()
