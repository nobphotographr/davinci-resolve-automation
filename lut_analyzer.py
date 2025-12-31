"""
LUT Analyzer - Cinematic LUT分析・オリジナルLUT生成ツール
"""
import os
import numpy as np
from pathlib import Path
import json
from typing import List, Dict, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class CubeLUT:
    """3D CUBE LUTの読み込みと解析"""

    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.title = ""
        self.size = 0
        self.domain_min = [0.0, 0.0, 0.0]
        self.domain_max = [1.0, 1.0, 1.0]
        self.data = None

        if filepath:
            self.load(filepath)

    def load(self, filepath: str):
        """CUBEファイルを読み込む"""
        self.filepath = filepath
        data_lines = []

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith('TITLE'):
                    self.title = line.split('"')[1] if '"' in line else line.split()[1]
                elif line.startswith('LUT_3D_SIZE'):
                    self.size = int(line.split()[1])
                elif line.startswith('DOMAIN_MIN'):
                    self.domain_min = [float(x) for x in line.split()[1:4]]
                elif line.startswith('DOMAIN_MAX'):
                    self.domain_max = [float(x) for x in line.split()[1:4]]
                else:
                    # データ行
                    try:
                        values = [float(x) for x in line.split()[:3]]
                        if len(values) == 3:
                            data_lines.append(values)
                    except ValueError:
                        continue

        if self.size == 0:
            # サイズが指定されていない場合、データ数から推測
            self.size = int(round(len(data_lines) ** (1/3)))

        self.data = np.array(data_lines).reshape(self.size, self.size, self.size, 3)
        return self

    def save(self, filepath: str, title: str = "Generated LUT"):
        """CUBEファイルとして保存"""
        with open(filepath, 'w') as f:
            f.write(f'TITLE "{title}"\n')
            f.write(f'LUT_3D_SIZE {self.size}\n')
            f.write(f'DOMAIN_MIN {self.domain_min[0]:.6f} {self.domain_min[1]:.6f} {self.domain_min[2]:.6f}\n')
            f.write(f'DOMAIN_MAX {self.domain_max[0]:.6f} {self.domain_max[1]:.6f} {self.domain_max[2]:.6f}\n')
            f.write('\n')

            for b in range(self.size):
                for g in range(self.size):
                    for r in range(self.size):
                        rgb = self.data[r, g, b]
                        f.write(f'{rgb[0]:.6f} {rgb[1]:.6f} {rgb[2]:.6f}\n')

    def get_transform(self, r: float, g: float, b: float) -> Tuple[float, float, float]:
        """入力RGB値に対する出力RGB値を取得（線形補間）"""
        # 正規化
        r_idx = r * (self.size - 1)
        g_idx = g * (self.size - 1)
        b_idx = b * (self.size - 1)

        # 整数インデックス
        r0, g0, b0 = int(r_idx), int(g_idx), int(b_idx)
        r1, g1, b1 = min(r0 + 1, self.size - 1), min(g0 + 1, self.size - 1), min(b0 + 1, self.size - 1)

        # 補間係数
        rf, gf, bf = r_idx - r0, g_idx - g0, b_idx - b0

        # トリリニア補間
        c000 = self.data[r0, g0, b0]
        c001 = self.data[r0, g0, b1]
        c010 = self.data[r0, g1, b0]
        c011 = self.data[r0, g1, b1]
        c100 = self.data[r1, g0, b0]
        c101 = self.data[r1, g0, b1]
        c110 = self.data[r1, g1, b0]
        c111 = self.data[r1, g1, b1]

        c00 = c000 * (1 - rf) + c100 * rf
        c01 = c001 * (1 - rf) + c101 * rf
        c10 = c010 * (1 - rf) + c110 * rf
        c11 = c011 * (1 - rf) + c111 * rf

        c0 = c00 * (1 - gf) + c10 * gf
        c1 = c01 * (1 - gf) + c11 * gf

        c = c0 * (1 - bf) + c1 * bf

        return tuple(c)

    def analyze(self) -> Dict:
        """LUTの特性を分析"""
        # アイデンティティLUT（変換なし）を生成
        identity = np.zeros_like(self.data)
        for r in range(self.size):
            for g in range(self.size):
                for b in range(self.size):
                    identity[r, g, b] = [r / (self.size - 1), g / (self.size - 1), b / (self.size - 1)]

        # 差分
        diff = self.data - identity

        # チャンネル別の統計
        stats = {
            'filename': os.path.basename(self.filepath) if self.filepath else 'Unknown',
            'size': self.size,
            'channels': {}
        }

        channel_names = ['R', 'G', 'B']
        for i, name in enumerate(channel_names):
            channel_diff = diff[:, :, :, i]
            stats['channels'][name] = {
                'mean_shift': float(np.mean(channel_diff)),
                'std': float(np.std(channel_diff)),
                'min_shift': float(np.min(channel_diff)),
                'max_shift': float(np.max(channel_diff))
            }

        # 全体的な特性
        stats['contrast'] = float(np.std(self.data))
        stats['saturation_boost'] = self._calc_saturation_change(identity)
        stats['color_temperature'] = self._estimate_color_temp()
        stats['shadow_lift'] = float(np.mean(self.data[:self.size//4, :self.size//4, :self.size//4]))
        stats['highlight_roll'] = float(np.mean(self.data[3*self.size//4:, 3*self.size//4:, 3*self.size//4:]))

        return stats

    def _calc_saturation_change(self, identity) -> float:
        """彩度の変化を計算"""
        # サンプルポイントでの彩度変化を計算
        sample_points = []
        for i in range(1, self.size - 1, 2):
            for j in range(1, self.size - 1, 2):
                for k in range(1, self.size - 1, 2):
                    orig = identity[i, j, k]
                    trans = self.data[i, j, k]

                    # 彩度計算（max - min）
                    orig_sat = np.max(orig) - np.min(orig)
                    trans_sat = np.max(trans) - np.min(trans)

                    if orig_sat > 0.01:
                        sample_points.append(trans_sat / orig_sat)

        return float(np.mean(sample_points)) if sample_points else 1.0

    def _estimate_color_temp(self) -> str:
        """色温度の傾向を推定"""
        # グレー軸の変化を見る
        mid = self.size // 2
        gray_point = self.data[mid, mid, mid]

        # R-Bの差で温度を推定
        rb_diff = gray_point[0] - gray_point[2]

        if rb_diff > 0.03:
            return "warm"
        elif rb_diff < -0.03:
            return "cool"
        else:
            return "neutral"


class LUTAnalyzer:
    """複数LUTの分析と新LUT生成"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.luts: List[CubeLUT] = []
        self.analysis_results: List[Dict] = []

    def find_cinematic_luts(self) -> List[str]:
        """Cinematic系のLUTフォルダを特定"""
        keywords = ['cine', 'film', 'movie', 'drama', 'hollywood', 'cinema']
        cinematic_folders = []

        for folder in self.base_path.iterdir():
            if folder.is_dir():
                folder_lower = folder.name.lower()
                if any(kw in folder_lower for kw in keywords):
                    cinematic_folders.append(folder.name)

        return sorted(cinematic_folders)

    def load_luts_from_folders(self, folder_names: List[str], max_per_folder: int = 5):
        """指定フォルダからLUTを読み込む"""
        for folder_name in folder_names:
            folder_path = self.base_path / folder_name
            if not folder_path.exists():
                continue

            cube_files = list(folder_path.rglob('*.cube'))[:max_per_folder]

            for cube_file in cube_files:
                try:
                    lut = CubeLUT(str(cube_file))
                    self.luts.append(lut)
                    print(f"Loaded: {cube_file.name}")
                except Exception as e:
                    print(f"Error loading {cube_file}: {e}")

    def analyze_all(self) -> List[Dict]:
        """全LUTを分析"""
        self.analysis_results = []
        for lut in self.luts:
            try:
                stats = lut.analyze()
                self.analysis_results.append(stats)
            except Exception as e:
                print(f"Error analyzing {lut.filepath}: {e}")
        return self.analysis_results

    def get_cinematic_characteristics(self) -> Dict:
        """Cinematic LUTの共通特性を抽出"""
        if not self.analysis_results:
            self.analyze_all()

        # 各特性の統計
        characteristics = {
            'r_shift': [],
            'g_shift': [],
            'b_shift': [],
            'contrast': [],
            'saturation': [],
            'shadow_lift': [],
            'highlight_roll': [],
            'color_temp': {'warm': 0, 'cool': 0, 'neutral': 0}
        }

        for result in self.analysis_results:
            characteristics['r_shift'].append(result['channels']['R']['mean_shift'])
            characteristics['g_shift'].append(result['channels']['G']['mean_shift'])
            characteristics['b_shift'].append(result['channels']['B']['mean_shift'])
            characteristics['contrast'].append(result['contrast'])
            characteristics['saturation'].append(result['saturation_boost'])
            characteristics['shadow_lift'].append(result['shadow_lift'])
            characteristics['highlight_roll'].append(result['highlight_roll'])
            characteristics['color_temp'][result['color_temperature']] += 1

        # 統計量を計算
        summary = {}
        for key in ['r_shift', 'g_shift', 'b_shift', 'contrast', 'saturation', 'shadow_lift', 'highlight_roll']:
            values = characteristics[key]
            summary[key] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values))
            }

        summary['color_temp_distribution'] = characteristics['color_temp']
        summary['total_luts_analyzed'] = len(self.analysis_results)

        return summary

    def generate_cinematic_lut(self,
                               size: int = 33,
                               contrast: float = 1.1,
                               saturation: float = 0.95,
                               shadow_lift: float = 0.02,
                               highlight_roll: float = 0.98,
                               teal_orange: float = 0.3,
                               warmth: float = 0.1) -> CubeLUT:
        """
        オリジナルのCinematic LUTを生成

        Parameters:
        -----------
        size: LUTサイズ（17, 33, 65など）
        contrast: コントラスト強度（1.0 = 変化なし）
        saturation: 彩度（1.0 = 変化なし、0.95 = やや控えめ）
        shadow_lift: シャドウの持ち上げ量
        highlight_roll: ハイライトのロールオフ（1.0以下で抑制）
        teal_orange: ティール&オレンジの強度（0-1）
        warmth: 暖色寄り（正）/ 寒色寄り（負）
        """
        lut = CubeLUT()
        lut.size = size
        lut.data = np.zeros((size, size, size, 3))

        for r_idx in range(size):
            for g_idx in range(size):
                for b_idx in range(size):
                    # 正規化された入力値
                    r = r_idx / (size - 1)
                    g = g_idx / (size - 1)
                    b = b_idx / (size - 1)

                    # 輝度計算
                    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b

                    # 1. コントラスト調整（S字カーブ）
                    r = self._apply_contrast(r, contrast)
                    g = self._apply_contrast(g, contrast)
                    b = self._apply_contrast(b, contrast)

                    # 2. シャドウリフト
                    r = r + shadow_lift * (1 - r)
                    g = g + shadow_lift * (1 - g)
                    b = b + shadow_lift * (1 - b)

                    # 3. ハイライトロールオフ
                    if r > 0.5:
                        r = 0.5 + (r - 0.5) * highlight_roll
                    if g > 0.5:
                        g = 0.5 + (g - 0.5) * highlight_roll
                    if b > 0.5:
                        b = 0.5 + (b - 0.5) * highlight_roll

                    # 4. 彩度調整
                    new_lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
                    r = new_lum + (r - new_lum) * saturation
                    g = new_lum + (g - new_lum) * saturation
                    b = new_lum + (b - new_lum) * saturation

                    # 5. ティール&オレンジ
                    if teal_orange > 0:
                        # シャドウにティール（青緑）
                        shadow_mask = 1 - min(lum * 2, 1)
                        b = b + teal_orange * 0.05 * shadow_mask
                        g = g + teal_orange * 0.02 * shadow_mask

                        # ハイライト/ミッドトーンにオレンジ
                        highlight_mask = max(lum * 2 - 1, 0)
                        r = r + teal_orange * 0.04 * highlight_mask
                        g = g + teal_orange * 0.02 * highlight_mask

                    # 6. 全体的な色温度
                    r = r + warmth * 0.02
                    b = b - warmth * 0.02

                    # クリッピング
                    r = max(0, min(1, r))
                    g = max(0, min(1, g))
                    b = max(0, min(1, b))

                    lut.data[r_idx, g_idx, b_idx] = [r, g, b]

        return lut

    def _apply_contrast(self, value: float, contrast: float) -> float:
        """S字カーブでコントラスト調整"""
        # 中点を0.5として、コントラストを調整
        value = value - 0.5
        value = value * contrast
        # 緩やかなS字カーブ
        if abs(value) > 0.5:
            sign = 1 if value > 0 else -1
            value = sign * (0.5 + (abs(value) - 0.5) * 0.8)
        return value + 0.5

    def visualize_analysis(self, output_path: str = None):
        """分析結果を可視化"""
        if not self.analysis_results:
            print("No analysis results to visualize")
            return

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))

        # 1. RGB シフト分布
        r_shifts = [r['channels']['R']['mean_shift'] for r in self.analysis_results]
        g_shifts = [r['channels']['G']['mean_shift'] for r in self.analysis_results]
        b_shifts = [r['channels']['B']['mean_shift'] for r in self.analysis_results]

        axes[0, 0].boxplot([r_shifts, g_shifts, b_shifts], labels=['R', 'G', 'B'])
        axes[0, 0].set_title('RGB Channel Shifts')
        axes[0, 0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        # 2. コントラスト分布
        contrasts = [r['contrast'] for r in self.analysis_results]
        axes[0, 1].hist(contrasts, bins=20, edgecolor='black')
        axes[0, 1].set_title('Contrast Distribution')
        axes[0, 1].set_xlabel('Contrast')

        # 3. 彩度分布
        saturations = [r['saturation_boost'] for r in self.analysis_results]
        axes[0, 2].hist(saturations, bins=20, edgecolor='black')
        axes[0, 2].set_title('Saturation Boost Distribution')
        axes[0, 2].set_xlabel('Saturation Multiplier')

        # 4. シャドウ vs ハイライト
        shadows = [r['shadow_lift'] for r in self.analysis_results]
        highlights = [r['highlight_roll'] for r in self.analysis_results]
        axes[1, 0].scatter(shadows, highlights, alpha=0.6)
        axes[1, 0].set_xlabel('Shadow Lift')
        axes[1, 0].set_ylabel('Highlight Roll')
        axes[1, 0].set_title('Shadow vs Highlight')

        # 5. 色温度分布
        temps = [r['color_temperature'] for r in self.analysis_results]
        temp_counts = {'warm': temps.count('warm'), 'neutral': temps.count('neutral'), 'cool': temps.count('cool')}
        axes[1, 1].bar(temp_counts.keys(), temp_counts.values(), color=['#FF6B35', '#808080', '#4A90D9'])
        axes[1, 1].set_title('Color Temperature Distribution')

        # 6. R-B相関
        axes[1, 2].scatter(r_shifts, b_shifts, alpha=0.6)
        axes[1, 2].set_xlabel('R Shift')
        axes[1, 2].set_ylabel('B Shift')
        axes[1, 2].set_title('R-B Correlation (Warm/Cool)')
        axes[1, 2].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[1, 2].axvline(x=0, color='gray', linestyle='--', alpha=0.5)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to: {output_path}")

        # plt.show()  # Disabled for non-interactive mode
        plt.close(fig)
        return fig


def main():
    """メイン実行"""
    # LUTフォルダのパス
    LUT_BASE_PATH = r"F:\MA_LUT"
    OUTPUT_DIR = r"F:\Github\davinci-resolve-automation\output"

    # 出力ディレクトリ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("LUT Analyzer - Cinematic Style Analysis")
    print("=" * 60)

    # 1. アナライザー初期化
    analyzer = LUTAnalyzer(LUT_BASE_PATH)

    # 2. Cinematic系フォルダを検索
    print("\n[1] Searching for Cinematic LUT folders...")
    cinematic_folders = analyzer.find_cinematic_luts()
    print(f"Found {len(cinematic_folders)} Cinematic-related folders:")
    for folder in cinematic_folders:
        print(f"  - {folder}")

    # 3. LUT読み込み
    print(f"\n[2] Loading LUTs from folders...")
    analyzer.load_luts_from_folders(cinematic_folders, max_per_folder=3)
    print(f"Total LUTs loaded: {len(analyzer.luts)}")

    # 4. 分析実行
    print(f"\n[3] Analyzing LUTs...")
    analyzer.analyze_all()

    # 5. Cinematic特性の抽出
    print(f"\n[4] Extracting Cinematic characteristics...")
    characteristics = analyzer.get_cinematic_characteristics()

    # 結果を表示
    print("\n" + "=" * 60)
    print("CINEMATIC LUT CHARACTERISTICS SUMMARY")
    print("=" * 60)
    print(f"\nTotal LUTs analyzed: {characteristics['total_luts_analyzed']}")
    print(f"\nColor Temperature Distribution:")
    for temp, count in characteristics['color_temp_distribution'].items():
        print(f"  {temp}: {count} ({count/characteristics['total_luts_analyzed']*100:.1f}%)")

    print(f"\nChannel Shifts (mean ± std):")
    print(f"  R: {characteristics['r_shift']['mean']:.4f} ± {characteristics['r_shift']['std']:.4f}")
    print(f"  G: {characteristics['g_shift']['mean']:.4f} ± {characteristics['g_shift']['std']:.4f}")
    print(f"  B: {characteristics['b_shift']['mean']:.4f} ± {characteristics['b_shift']['std']:.4f}")

    print(f"\nContrast: {characteristics['contrast']['mean']:.4f} ± {characteristics['contrast']['std']:.4f}")
    print(f"Saturation: {characteristics['saturation']['mean']:.4f} ± {characteristics['saturation']['std']:.4f}")
    print(f"Shadow Lift: {characteristics['shadow_lift']['mean']:.4f} ± {characteristics['shadow_lift']['std']:.4f}")
    print(f"Highlight Roll: {characteristics['highlight_roll']['mean']:.4f} ± {characteristics['highlight_roll']['std']:.4f}")

    # 6. 分析結果をJSONで保存
    analysis_file = os.path.join(OUTPUT_DIR, "cinematic_analysis.json")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(characteristics, f, indent=2, ensure_ascii=False)
    print(f"\nAnalysis saved to: {analysis_file}")

    # 7. 可視化
    print(f"\n[5] Generating visualization...")
    viz_file = os.path.join(OUTPUT_DIR, "cinematic_analysis.png")
    analyzer.visualize_analysis(viz_file)

    # 8. オリジナルLUT生成
    print(f"\n[6] Generating original Cinematic LUTs...")

    # バリエーション1: Classic Cinematic
    lut1 = analyzer.generate_cinematic_lut(
        size=33,
        contrast=1.15,
        saturation=0.92,
        shadow_lift=0.015,
        highlight_roll=0.95,
        teal_orange=0.4,
        warmth=0.05
    )
    lut1_path = os.path.join(OUTPUT_DIR, "Original_Cinematic_Classic.cube")
    lut1.save(lut1_path, "Original Cinematic Classic")
    print(f"  Generated: {lut1_path}")

    # バリエーション2: Modern Film
    lut2 = analyzer.generate_cinematic_lut(
        size=33,
        contrast=1.2,
        saturation=0.88,
        shadow_lift=0.025,
        highlight_roll=0.92,
        teal_orange=0.5,
        warmth=-0.05
    )
    lut2_path = os.path.join(OUTPUT_DIR, "Original_Cinematic_Modern.cube")
    lut2.save(lut2_path, "Original Cinematic Modern")
    print(f"  Generated: {lut2_path}")

    # バリエーション3: Warm Drama
    lut3 = analyzer.generate_cinematic_lut(
        size=33,
        contrast=1.1,
        saturation=0.95,
        shadow_lift=0.02,
        highlight_roll=0.96,
        teal_orange=0.2,
        warmth=0.15
    )
    lut3_path = os.path.join(OUTPUT_DIR, "Original_Cinematic_WarmDrama.cube")
    lut3.save(lut3_path, "Original Cinematic Warm Drama")
    print(f"  Generated: {lut3_path}")

    # バリエーション4: Cool Thriller
    lut4 = analyzer.generate_cinematic_lut(
        size=33,
        contrast=1.25,
        saturation=0.85,
        shadow_lift=0.01,
        highlight_roll=0.90,
        teal_orange=0.6,
        warmth=-0.1
    )
    lut4_path = os.path.join(OUTPUT_DIR, "Original_Cinematic_CoolThriller.cube")
    lut4.save(lut4_path, "Original Cinematic Cool Thriller")
    print(f"  Generated: {lut4_path}")

    print("\n" + "=" * 60)
    print("COMPLETED!")
    print("=" * 60)
    print(f"\nOutput files saved to: {OUTPUT_DIR}")
    print("  - cinematic_analysis.json (分析結果)")
    print("  - cinematic_analysis.png (可視化)")
    print("  - Original_Cinematic_Classic.cube")
    print("  - Original_Cinematic_Modern.cube")
    print("  - Original_Cinematic_WarmDrama.cube")
    print("  - Original_Cinematic_CoolThriller.cube")


if __name__ == "__main__":
    main()
