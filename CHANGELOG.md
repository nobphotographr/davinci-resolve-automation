# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- CONTRIBUTING.md - ナレッジ追加ガイドライン
- GitHub Issue Template for knowledge additions
- CHANGELOG.md for tracking changes

### Improved
- cleanup_projects.py - プロジェクト一覧表示機能追加
  - 削除前に全プロジェクトリストを表示
  - スキップしたプロジェクト数を集計
  - より詳細な実行結果レポート

## [1.0.0] - 2025-01-XX

### Added
- Initial repository structure
- Scripts for color grading automation
  - lut_comparison.py - Color version management for A/B testing
  - apply_drx_template.py - DRX template application
- Project management utilities
  - auto_project_setup.py - Automated project creation
  - cleanup_projects.py - Batch project cleanup
- Comprehensive documentation
  - API_Reference.md - Complete API documentation
  - Best_Practices.md - Proven patterns and strategies
  - Limitations.md - Known limitations with workarounds
- DRX template examples
  - braw_cinematic_base.drx - 4-node structure
- Example LUT files
  - Classic_Cinema_Custom.cube
  - Teal_Orange_Custom.cube
- MIT License

[Unreleased]: https://github.com/nobphotographr/davinci-resolve-automation/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/nobphotographr/davinci-resolve-automation/releases/tag/v1.0.0
