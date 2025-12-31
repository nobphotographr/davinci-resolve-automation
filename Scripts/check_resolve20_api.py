"""
DaVinci Resolve 20 API確認スクリプト
"""
import sys
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr


def main():
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Error: DaVinci Resolveに接続できません")
        return

    print("=" * 60)
    print(f"DaVinci Resolve {resolve.GetVersionString()} に接続")
    print("=" * 60)

    # プロジェクト確認
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()

    if project:
        print(f"\nプロジェクト: {project.GetName()}")
    else:
        print("\nプロジェクトが開かれていません")
        print("新規プロジェクトを作成します...")
        project = pm.CreateProject("LUT_Test_Resolve20")
        if project:
            print(f"プロジェクト '{project.GetName()}' を作成しました")

    # タイムライン確認
    timeline = project.GetCurrentTimeline() if project else None
    if timeline:
        print(f"タイムライン: {timeline.GetName()}")
        items = timeline.GetItemListInTrack("video", 1)
        if items:
            print(f"クリップ数: {len(items)}")

            # TimelineItemの新しいメソッドを確認
            clip = items[0]
            print("\n--- TimelineItem メソッド一覧 ---")
            methods = sorted([m for m in dir(clip) if not m.startswith('_')])

            # カテゴリ別に表示
            color_methods = [m for m in methods if any(x in m.lower() for x in ['color', 'grade', 'lut', 'cdl', 'node'])]
            print("\nカラー関連メソッド:")
            for m in color_methods:
                print(f"  {m}")

            # 新しいメソッドを探す
            print("\n全メソッド:")
            for m in methods:
                print(f"  {m}")
    else:
        print("タイムラインがありません")

    # Resolve オブジェクトの新しいメソッド
    print("\n--- Resolve メソッド一覧 ---")
    resolve_methods = sorted([m for m in dir(resolve) if not m.startswith('_')])
    for m in resolve_methods:
        print(f"  {m}")


if __name__ == "__main__":
    main()
