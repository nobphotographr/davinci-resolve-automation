# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **Setup Scripts** - Automated installation for all platforms
  - setup.sh - macOS and Linux setup script
  - setup.bat - Windows setup script
  - Automatic environment variable configuration
  - Sample LUT installation
  - Python and DaVinci Resolve API verification
  - Connection test to running DaVinci Resolve instance
- **LUT Installer** - Scripts/Utilities/lut_installer.py
  - Cross-platform LUT installation (macOS/Windows/Linux)
  - Support for .cube, .3dl, and .lut formats
  - Automatic LUT list refresh in DaVinci Resolve
  - Overwrite protection with --overwrite flag
  - Batch installation of multiple LUTs
  - Custom destination directory support
- CONTRIBUTING.md - ナレッジ追加ガイドライン
- GitHub Issue Template for knowledge additions
- CHANGELOG.md for tracking changes
- Advanced_Techniques.md - Community-discovered workarounds
  - Selected timeline clips workaround (using clip color)
  - Track iteration patterns
  - Batch operations on filtered clips
  - Fusion vs Python API comparison
  - Media pool recursive traversal patterns
  - Type-safe API wrapper examples
  - Credits to hitsugi_yukana, pedrolabonia, kayakfishingaddict
- Type_Safety_and_Best_Practices.md - Modern Python patterns
  - Type hints for DaVinci Resolve API
  - Property pattern implementation
  - Custom exception handling
  - Wrapper pattern best practices
  - Render job monitoring with progress display
  - pydavinci library integration guide

### Improved
- cleanup_projects.py - プロジェクト一覧表示機能追加
  - 削除前に全プロジェクトリストを表示
  - スキップしたプロジェクト数を集計
  - より詳細な実行結果レポート
- README.md - Installation and documentation updates
  - Added Quick Start section with automated setup instructions
  - Added platform-specific setup commands (macOS/Windows/Linux)
  - Reorganized installation flow for better user experience
  - Added Type Safety & Best Practices documentation link
  - Added Recommended Libraries section (pydavinci)
  - Enhanced Community Resources section
- Advanced_Techniques.md - Enhanced with modern patterns
  - Media pool recursive folder traversal
  - Bin management (get or create pattern)
  - Clip filtering by metadata
  - Type-safe wrapper implementation example
  - pydavinci library recommendation

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
