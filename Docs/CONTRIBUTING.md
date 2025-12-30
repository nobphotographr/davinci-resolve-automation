# Contributing to DaVinci Resolve Automation

## ナレッジ追加のガイドライン

このリポジトリは、DaVinci Resolve自動化の実践的な知識を蓄積・共有するためのものです。

### ナレッジ追加の基準

以下のいずれかに該当する場合、ナレッジとして追加を検討してください:

#### ✅ 追加すべき内容

1. **APIの新発見**
   - 公式ドキュメントに記載されていない機能
   - 動作が明確でない機能の検証結果
   - 例: Color Version Management API (`AddVersion`, `LoadVersionByName`)

2. **実用的なワークフロー**
   - 実際のプロジェクトで動作確認済み
   - 再現可能な手順
   - 例: DRXテンプレート + LUT適用の完全自動化

3. **問題と解決策**
   - 遭遇したエラーと解決方法
   - APIの制限事項とワークアラウンド
   - 例: Custom/サブフォルダのLUTが認識されない問題

4. **パフォーマンス最適化**
   - バッチ処理の効率化
   - 不要なページ遷移の削減
   - 例: 複数クリップへの一括グレード適用

5. **クロスプラットフォーム対応**
   - macOS/Windows/Linux間の差異
   - パス処理の違い
   - 例: 環境変数の設定方法

#### ❌ 追加を避けるべき内容

1. **公式ドキュメントの再掲**
   - 単なる公式APIの翻訳
   - 既知の情報の繰り返し

2. **未検証の内容**
   - 動作確認していない推測
   - 他のソースからのコピー（検証なし）

3. **プロジェクト固有すぎる内容**
   - 特定の環境でしか動作しない
   - 汎用性がない

### ナレッジ追加のワークフロー

#### 1. 実験プロジェクトで検証

```bash
# cinematic-lut-analyzerで新しいアイデアをテスト
cd ~/Projects/cinematic-lut-analyzer
# スクリプト作成・実行・検証
```

#### 2. 動作確認

- DaVinci Resolveで実際に動作するか確認
- エラーハンドリングが適切か確認
- 複数のクリップ/プロジェクトで再現性を確認

#### 3. ドキュメント化

以下のいずれかに追加:

**新しいスクリプトの場合:**
```bash
# Scripts/ 配下に配置
Scripts/ColorGrading/     # カラーグレーディング関連
Scripts/ProjectManagement/ # プロジェクト管理関連
Scripts/Utilities/         # ユーティリティ
```

**ベストプラクティスの場合:**
- `Docs/Best_Practices.md` に追記

**API制限・回避策の場合:**
- `Docs/Limitations.md` に追記

**新機能の発見の場合:**
- `Docs/API_Reference.md` に追記

#### 4. コミット

```bash
cd ~/Projects/davinci-resolve-automation

# 変更を追加
git add .

# わかりやすいコミットメッセージ
git commit -m "Add: LUT batch comparison workflow

- 複数LUTの一括比較スクリプト追加
- Color Version APIを活用
- 実行時間を50%短縮

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# プッシュ
git push origin main
```

### ドキュメント構成

#### Docs/Best_Practices.md

実践的なパターンとストラテジー:
- DRXテンプレート戦略
- LUT管理
- パフォーマンス最適化
- エラーハンドリング

#### Docs/Limitations.md

API制限とワークアラウンド:
- できないこと一覧
- 各制限の回避策
- プラットフォーム間の差異

#### Docs/API_Reference.md

API仕様とサンプルコード:
- メソッド一覧
- パラメータ詳細
- 実用例

### スクリプトの品質基準

#### 必須要素

1. **ヘッダーコメント**
```python
#!/usr/bin/env python3
"""
スクリプト名と目的の簡潔な説明

詳細な説明（必要に応じて）
"""
```

2. **エラーハンドリング**
```python
if not project:
    print("❌ プロジェクトが開かれていません")
    sys.exit(1)
```

3. **進捗表示**
```python
print("[1/4] DaVinci Resolveに接続中...")
print("✅ 接続成功")
```

4. **検証済みのパス**
```python
# ❌ ハードコード
lut_dir = "/Users/nobu/..."

# ✅ 汎用的
lut_dir = os.path.expanduser("~/Projects/...")
```

### テンプレート構成

#### DRXテンプレート

- 目的を明確にする（ファイル名とディレクトリ）
- README追加（各ノードの役割説明）
- 複数バリエーション作成（シンプル版、標準版、高度版）

例:
```
Templates/DRX/
├── README.md
├── simple_2node.drx          # 初心者向け
├── standard_4node.drx        # 標準（推奨）
└── advanced_parallel.drx     # パラレルノード含む
```

### コミュニティ貢献

#### Issue作成

- バグ報告
- 機能リクエスト
- ドキュメント改善提案

#### Pull Request

1. Forkしてブランチ作成
2. 変更を加える
3. 動作確認
4. PRを作成（詳細な説明付き）

### 参考資料

追加すべき情報源:
- 公式フォーラムの有用な投稿
- X-Raym等のコミュニティスクリプト
- 個人的な実験結果

### バージョン管理

- スクリプトにバージョン情報は不要（Gitで管理）
- 大きな変更の場合はGitタグを使用
- CHANGELOG.md で変更履歴を管理（今後追加予定）

## 質問・フィードバック

- GitHub Issues で質問・提案を歓迎
- 実験的な内容もまずは共有してください
- コミュニティで検証・改善していきましょう
