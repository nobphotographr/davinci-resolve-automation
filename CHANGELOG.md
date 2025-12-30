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
- **Batch Grade Application** - Scripts/ColorGrading/batch_grade_apply.py
  - Command-line batch grading tool
  - Apply DRX templates, LUTs, and CDL to multiple clips
  - Flexible clip targeting (all clips, specific track, by color)
  - Combine multiple operations in single command
  - Node-specific LUT/CDL application
  - Support for all CDL parameters (Slope, Offset, Power, Saturation)
- **Timeline Analyzer** - Scripts/Utilities/timeline_analyzer.py
  - Comprehensive timeline statistics display
  - Track structure analysis (video/audio track counts)
  - Clip distribution by track and color
  - LUT usage analysis (unique LUTs, usage count)
  - Node statistics (max nodes, average nodes per clip)
  - Duration calculation with timecode formatting
  - Detailed per-clip information mode
  - JSON export for programmatic access
- **Render Queue Manager** - Scripts/Utilities/render_manager.py
  - View render queue status and job details
  - Add render jobs with preset configurations
  - 7 built-in presets (ProRes, H.264/H.265, DNxHR)
  - Start rendering with progress monitoring
  - Real-time progress display with ETA calculation
  - Clear completed/failed jobs from queue
  - Custom output directory support
- **Media Pool Organizer** - Scripts/Utilities/media_pool_organizer.py
  - Comprehensive media pool statistics (clips, bins, codecs, resolutions)
  - Visual tree display of bin structure
  - Auto-organize clips by resolution or codec
  - Search clips by name across all bins
  - Recursive folder traversal (implements Advanced_Techniques pattern)
  - Clean up empty bins with dry-run mode
  - Get-or-create bin pattern for safe folder management
- **Metadata Manager** - Scripts/Utilities/metadata_manager.py
  - List metadata for media pool and timeline clips
  - Export metadata to CSV or JSON with optional properties
  - Import metadata from CSV files
  - Bulk set metadata fields with search filtering
  - Find clips by metadata values
  - Supports both MediaPoolItem and TimelineItem APIs
  - Common metadata fields (Scene, Shot, Take, Keywords, etc.)
- **Project Backup Manager** - Scripts/Utilities/project_backup.py
  - Automated project backup with timestamp naming
  - Backup with notes/descriptions in filename
  - List all available backups with size and date
  - Automatic retention policy (keep N most recent)
  - Clean old backups with dry-run mode
  - Restore projects from backup files
  - Default backup location (~/DaVinci_Resolve_Backups)
  - Custom backup directory support
- **Troubleshooting Guide** - Docs/Troubleshooting.md
  - Connection issues and solutions
  - Environment setup problems
  - Script execution errors
  - API-specific issues (LUT, metadata, render)
  - Platform-specific issues (macOS, Windows, Linux)
  - Performance optimization tips
  - Quick diagnostic checklist
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
