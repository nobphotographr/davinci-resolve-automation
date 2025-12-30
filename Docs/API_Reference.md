# DaVinci Resolve 自動化ナレッジベース

## 参考資料

### 公式
- [DaVinci Resolve Scripting README](file:///Library/Application%20Support/Blackmagic%20Design/DaVinci%20Resolve/Developer/Scripting/README.txt)
- [非公式APIドキュメント](https://extremraym.com/cloud/resolve-scripting-doc/)

### 日本語記事
- [DaVinci Resolve 起動時スクリプト自動実行](https://zenn.dev/hitsugi_yukana/articles/536b36e1c97315)

## APIの制限と回避策

### ✅ できること

1. **プロジェクト・タイムライン管理**
   - プロジェクト作成・削除
   - タイムライン作成・編集
   - クリップ追加・削除

2. **カラーグレーディング（限定的）**
   - LUT適用・削除: `TimelineItem.SetLUT(nodeIndex, lutPath)`
   - CDL値設定: `TimelineItem.SetCDL({"NodeIndex": "1", "Slope": "1.2 1.2 1.2", ...})`
   - DRX適用: `Graph.ApplyGradeFromDRX(path, gradeMode)`

3. **レンダリング**
   - レンダージョブ作成・実行
   - 設定変更

### ❌ できないこと

1. **ノードグラフ構築**
   - シリアルノード追加: API不存在
   - パラレルノード追加: API不存在
   - ノード削除: API不存在
   - **回避策**: DRXテンプレート使用

2. **詳細なカラー調整**
   - プライマリーホイール調整: API不存在
   - カーブ編集: API不存在
   - パワーウィンドウ: API不存在
   - **回避策**: CDLで基本調整、またはDRX

3. **エフェクト追加**
   - OpenFX/ResolveFX追加: API不存在
   - **回避策**: DRXテンプレートに含める

## ベストプラクティス

### 1. DRXテンプレート戦略

複雑なノード構成は手動で作成 → DRXとして保存 → API経由で適用

```python
# DRXテンプレート適用
graph = timeline_item.GetNodeGraph()
graph.ApplyGradeFromDRX("path/to/template.drx", 0)  # gradeMode=0: No keyframes
```

**利点**:
- 任意の複雑なノード構成を再現可能
- UI操作が不要
- バッチ処理に最適

### 2. Lua ↔ Python 連携

起動時自動化には`.scriptlib` (Lua) → Python スクリプト呼び出し

```lua
-- .scriptlib ファイル内
fusion:RunScript("!Py3: /path/to/script.py")
```

**使用例**:
- DaVinci Resolve起動時にLUT自動配置
- プロジェクトテンプレート自動読み込み

### 3. LUTパス管理

**問題**: `Custom`サブフォルダがAPI経由で認識されない

**解決策**: マスターLUTディレクトリに直接配置

```python
lut_master_dir = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
shutil.copy2(source_lut, lut_master_dir)

# ファイル名のみで参照可能
timeline_item.SetLUT(1, "Classic_Cinema_Custom.cube")
```

### 4. プロジェクト取得のタイミング

**注意**: 起動時スクリプト（.scriptlib）では`GetCurrentProject()`が空を返す

**回避策**: プロジェクトマネージャー表示後に実行するスクリプトを別途用意

### 5. データ永続化

**制限**: `fusion:SetData()`は基本型のみ

```lua
-- ✅ OK
fusion:SetData("last_used_lut", "Classic_Cinema_Custom.cube")
fusion:SetData("render_count", 42)

-- ❌ NG
fusion:SetData("complex_object", some_instance)  -- 取り出せない
```

## 実践例：自動LUTセットアップ

### ディレクトリ構造

```
~/Projects/cinematic-lut-analyzer/
├── output/                          # 生成したLUT
│   ├── Classic_Cinema_Custom.cube
│   └── Teal_Orange_Custom.cube
├── templates/                       # DRXテンプレート
│   └── braw_cinematic_base.drx
└── scripts/
    ├── resolve_full_auto_lut_test.py  # 完全自動化
    ├── apply_drx_template.py          # DRX適用
    └── cleanup_projects.py            # プロジェクト削除
```

### 自動化フロー

1. **LUT生成**: `generator/lut_generator.py`
2. **LUT配置**: マスターLUTディレクトリにコピー
3. **プロジェクト作成**: ユニーク名で作成
4. **メディア読み込み**: BRAW素材追加
5. **DRXテンプレート適用**: 4ノード構成 + LUT
6. **完了**: Colorページで確認可能

## 制限事項のまとめ

| 操作 | API | 回避策 |
|------|-----|--------|
| ノード追加 | ❌ | DRXテンプレート |
| カーブ調整 | ❌ | DRXテンプレート |
| LUT適用 | ✅ | `SetLUT()` |
| CDL調整 | ✅ | `SetCDL()` |
| エフェクト追加 | ❌ | DRXテンプレート |
| レンダリング | ✅ | `AddRenderJob()` |
| プロジェクト管理 | ✅ | `CreateProject()` 等 |

## 今後の展開

1. **複数DRXテンプレート作成**
   - シンプル版（1-2ノード）
   - 標準版（4ノード）- 現在実装済み
   - 高度版（10+ノード、パラレル構成）

2. **起動時自動化**
   - `.scriptlib`でLUT自動配置
   - プロジェクトテンプレート自動読み込み

3. **バッチ処理**
   - 複数クリップに同じグレード適用
   - 複数LUTの一括テスト・比較

## 参考コマンド

### Python APIパス（macOS）
```bash
RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
```

### scriptlibパス（macOS）
```bash
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/
```

### LUTパス（macOS）
```bash
/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/
```
