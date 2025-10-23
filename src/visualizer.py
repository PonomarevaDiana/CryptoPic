import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any


class CryptoVisualizer:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.metrics_dir = self.results_dir / "metrics"
        self.tables_dir = self.results_dir / "tables"
        self.histograms_dir = self.results_dir / "histograms"
        self.comparative_dir = self.results_dir / "comparative_charts"

        for directory in [self.tables_dir, self.histograms_dir, self.comparative_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        plt.style.use("seaborn-v0_8")
        self.colors = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FECA57",
            "#FF9FF3",
            "#54A0FF",
            "#5F27CD",
            "#00D2D3",
            "#FF9F43",
        ]

    def load_metrics_data(self) -> Dict[str, Any]:
        metrics_data = {}

        metric_files = list(self.metrics_dir.glob("*metrics.json"))

        for file_path in metric_files:
            image_type = file_path.stem.replace("_metrics", "")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metrics_data[image_type] = {"main": data, "key_sensitivity": None}
                    print(f"   Loaded: {image_type}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        return metrics_data

    def save_table_as_image(
        self,
        table_data: List[List],
        title: str,
        filename: str,
        headers: List[str] = None,
    ):
        if not table_data:
            print(f"Нет данных для таблицы: {title}")
            return

        n_rows = len(table_data)
        n_cols = len(table_data[0]) if table_data else 0

        fig_width = max(14, n_cols * 3.0)
        fig_height = max(10, n_rows * 1.5)

        plt.figure(figsize=(fig_width, fig_height))
        plt.axis("off")
        plt.title(title, fontsize=18, fontweight="bold", pad=25)

        if headers:
            table = plt.table(
                cellText=table_data,
                colLabels=headers,
                cellLoc="center",
                loc="center",
                bbox=[0.1, 0.1, 0.8, 0.8],
            )
        else:
            table = plt.table(
                cellText=table_data,
                cellLoc="center",
                loc="center",
                bbox=[0.1, 0.1, 0.8, 0.8],
            )

        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 1.8)

        table.auto_set_column_width([i for i in range(n_cols)])

        if headers:
            for i in range(len(headers)):
                table[(0, i)].set_facecolor("#4CAF50")
                table[(0, i)].set_text_props(weight="bold", color="white", fontsize=13)

        for i in range(len(table_data)):
            row_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            for j in range(n_cols):
                if headers:
                    table_cell = table[(i + 1, j)]
                else:
                    table_cell = table[(i, j)]
                table_cell.set_facecolor(row_color)

        filepath = self.tables_dir / f"{filename}.png"
        plt.savefig(
            filepath,
            dpi=150,
            bbox_inches="tight",
            facecolor="white",
            pad_inches=0.8,
        )
        plt.close()

        print(f"  Таблица сохранена: {filepath}")
        return filepath

    # СРАВНИТЕЛЬНЫЕ ТАБЛИЦЫ ДЛЯ ОТДЕЛЬНЫХ МЕТОДОВ
    def create_entropy_comparison_table(self, metrics_data: Dict[str, Any]):
        """Создает сравнительную таблицу энтропии"""
        table_data = []

        for image_name, data in metrics_data.items():
            main_data = data["main"]
            if not main_data:
                continue

            entropy_data = main_data["entropy"]
            improvement = entropy_data["improvement"]
            improvement_color = "🟢" if improvement > 0 else "🔴"

            table_data.append(
                [
                    image_name,
                    f"{entropy_data['original']:.6f}",
                    f"{entropy_data['encrypted']:.6f}",
                    f"{improvement:+.6f}",
                ]
            )

        headers = [
            "Изображение",
            "Энтропия исходная",
            "Энтропия зашифрованная",
            "Улучшение",
        ]

        filename = "entropy_comparison"
        title = "СРАВНИТЕЛЬНАЯ ТАБЛИЦА ЭНТРОПИИ"
        self.save_table_as_image(table_data, title, filename, headers)

    def create_security_metrics_comparison_table(self, metrics_data: Dict[str, Any]):
        """Создает сравнительную таблицу метрик безопасности"""
        table_data = []

        for image_name, data in metrics_data.items():
            main_data = data["main"]
            if not main_data:
                continue

            npcr_uaci = main_data["npcr_uaci"]
            avalanche = main_data["avalanche_effect"]
            table_data.append(
                [
                    image_name,
                    f"{npcr_uaci['npcr']:.4f}%",
                    f"{npcr_uaci['uaci']:.4f}%",
                    f"{avalanche:.4f}%",
                ]
            )

        headers = [
            "Изображение",
            "NPCR",
            "UACI",
            "Avalanche",
        ]

        filename = "security_metrics_comparison"
        title = "СРАВНИТЕЛЬНАЯ ТАБЛИЦА МЕТРИК БЕЗОПАСНОСТИ"
        self.save_table_as_image(table_data, title, filename, headers)

    def create_correlation_comparison_table(self, metrics_data: Dict[str, Any]):
        """Создает сравнительную таблицу корреляции"""
        table_data = []

        for image_name, data in metrics_data.items():
            main_data = data["main"]
            if not main_data:
                continue

            correlations = main_data["correlations"]
            avg_improvement = (
                correlations["horizontal"]["reduction"]
                + correlations["vertical"]["reduction"]
                + correlations["diagonal"]["reduction"]
            ) / 3

            table_data.append(
                [
                    image_name,
                    f"{correlations['horizontal']['original']:.6f}",
                    f"{correlations['horizontal']['encrypted']:.6f}",
                    f"{correlations['horizontal']['reduction']:+.6f}",
                    f"{correlations['vertical']['original']:.6f}",
                    f"{correlations['vertical']['encrypted']:.6f}",
                    f"{correlations['vertical']['reduction']:+.6f}",
                    f"{correlations['diagonal']['original']:.6f}",
                    f"{correlations['diagonal']['encrypted']:.6f}",
                    f"{correlations['diagonal']['reduction']:+.6f}",
                    f"{avg_improvement:+.6f}",
                ]
            )

        headers = [
            "Изображение",
            "Гориз. исход",
            "Гориз. шифр",
            "Гориз. улучш",
            "Верт. исход",
            "Верт. шифр",
            "Верт. улучш",
            "Диаг. исход",
            "Диаг. шифр",
            "Диаг. улучш",
            "Сред. улучш",
        ]

        filename = "correlation_comparison"
        title = "СРАВНИТЕЛЬНАЯ ТАБЛИЦА КОРРЕЛЯЦИИ"
        self.save_table_as_image(table_data, title, filename, headers)

    def create_file_size_comparison_table(self, metrics_data: Dict[str, Any]):
        """Создает сравнительную таблицу размеров файлов"""
        table_data = []

        for image_name, data in metrics_data.items():
            main_data = data["main"]
            if not main_data:
                continue

            file_sizes = main_data["file_sizes"]
            size_change = file_sizes["encrypted_bytes"] - file_sizes["original_bytes"]
            size_change_percent = (size_change / file_sizes["original_bytes"]) * 100

            table_data.append(
                [
                    image_name,
                    f"{file_sizes['original_bytes']:,}".replace(",", " "),
                    f"{file_sizes['encrypted_bytes']:,}".replace(",", " "),
                    f"{size_change:+,}".replace(",", " "),
                    f"{size_change_percent:+.2f}%",
                ]
            )

        headers = [
            "Изображение",
            "Исходный размер (байт)",
            "Зашифрованный размер (байт)",
            "Изменение размера",
            "Изменение (%)",
        ]

        filename = "file_size_comparison"
        title = "СРАВНИТЕЛЬНАЯ ТАБЛИЦА РАЗМЕРОВ ФАЙЛОВ"
        self.save_table_as_image(table_data, title, filename, headers)

    def create_encryption_methods_comparison_table(self, metrics_data: Dict[str, Any]):
        """Сравнительная таблица по методам шифрования"""
        methods_data = {}

        for image_name, data in metrics_data.items():
            main_data = data["main"]
            if not main_data:
                continue
            parts = image_name.split("_")
            if len(parts) >= 2:
                method = parts[-1]
                image_base = "_".join(parts[:-1])

                if method not in methods_data:
                    methods_data[method] = {}

                methods_data[method][image_base] = main_data

        for method, images_data in methods_data.items():
            table_data = []

            for image_name, main_data in images_data.items():
                entropy_data = main_data["entropy"]
                npcr_uaci = main_data["npcr_uaci"]
                avalanche = main_data["avalanche_effect"]

                table_data.append(
                    [
                        image_name,
                        f"{entropy_data['encrypted']:.4f}",
                        f"{npcr_uaci['npcr']:.2f}%",
                        f"{npcr_uaci['uaci']:.2f}%",
                        f"{avalanche:.2f}%",
                        f"{main_data['correlations']['horizontal']['encrypted']:.4f}",
                    ]
                )

            if table_data:
                headers = [
                    "Изображение",
                    "Энтропия",
                    "NPCR",
                    "UACI",
                    "Avalanche",
                    "Корреляция",
                ]

                filename = f"encryption_method_{method}"
                title = f"СРАВНЕНИЕ МЕТОДА ШИФРОВАНИЯ: {method.upper()}"
                self.save_table_as_image(table_data, title, filename, headers)

    def generate_comparative_tables(self, metrics_data: Dict[str, Any]):
        """Генерирует все сравнительные таблицы"""
        print(" Generating comparative tables...")

        self.create_entropy_comparison_table(metrics_data)
        self.create_security_metrics_comparison_table(metrics_data)
        self.create_correlation_comparison_table(metrics_data)
        self.create_file_size_comparison_table(metrics_data)
        self.create_encryption_methods_comparison_table(metrics_data)

        print(" All comparative tables generated successfully!")

    def create_summary_dashboard(self, metrics_data: Dict[str, Any]):
        """Создает сводные дашборды для всех изображений с правильными отступами"""
        print(f"  Создание дашбордов для {len(metrics_data)} изображений...")

        for image_name, data in metrics_data.items():
            main_data = data["main"]
            if not main_data:
                continue
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 7))  # Шире и ниже
            fig.suptitle(
                f"СВОДНЫЙ ДАШБОРД - {image_name.upper()}",
                fontsize=18,
                fontweight="bold",
                y=0.98,
            )

            entropy_data = main_data["entropy"]
            categories_entropy = ["Оригинал", "Шифр"]
            values_entropy = [entropy_data["original"], entropy_data["encrypted"]]

            bars_entropy = ax1.bar(
                categories_entropy,
                values_entropy,
                color=["#FF6B6B", "#4ECDC4"],
                alpha=0.8,
                width=0.6,
            )

            ax1.set_ylabel("Энтропия (биты)", fontsize=12)
            ax1.set_title("ЭНТРОПИЯ ШЕННОНА", fontweight="bold", fontsize=14, pad=15)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis="both", which="major", labelsize=11)

            max_entropy = max(values_entropy)
            text_offset_entropy = max_entropy * 0.08

            for bar, value in zip(bars_entropy, values_entropy):
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + text_offset_entropy,
                    f"{value:.3f}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=11,
                )

            ax1.axhline(
                y=8.0, color="red", linestyle="--", alpha=0.5, label="Идеал (8.0)"
            )

            npcr_uaci = main_data["npcr_uaci"]
            avalanche = main_data["avalanche_effect"]

            security_metrics = ["NPCR", "UACI", "Avalanche"]
            security_values = [npcr_uaci["npcr"], npcr_uaci["uaci"], avalanche]
            security_ideals = [99.6, 33.4, 50.0]

            x_security = np.arange(len(security_metrics))
            bars_security = ax2.bar(
                x_security,
                security_values,
                color=["#45B7D1", "#96CEB4", "#FECA57"],
                alpha=0.8,
                width=0.6,
            )

            ax2.set_ylabel("Процент (%)", fontsize=12)
            ax2.set_title(
                "МЕТРИКИ БЕЗОПАСНОСТИ", fontweight="bold", fontsize=14, pad=15
            )
            ax2.set_xticks(x_security)
            ax2.set_xticklabels(security_metrics, fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis="both", which="major", labelsize=11)

            max_security = max(security_values)
            text_offset_security = max_security * 0.03

            for i, (value, ideal) in enumerate(zip(security_values, security_ideals)):
                color = "green" if abs(value - ideal) < (ideal * 0.1) else "red"
                ax2.axhline(y=ideal, color=color, linestyle="--", alpha=0.7)
                ax2.text(
                    i,
                    ideal + text_offset_security * 0.5,
                    f"Идеал: {ideal}%",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color=color,
                    fontweight="bold",
                )

            for bar, value in zip(bars_security, security_values):
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + text_offset_security,
                    f"{value:.2f}%",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=11,
                )

            correlations = main_data["correlations"]

            directions = [
                "Гориз.",
                "Верт.",
                "Диаг.",
            ]
            original_corr = [
                correlations["horizontal"]["original"],
                correlations["vertical"]["original"],
                correlations["diagonal"]["original"],
            ]
            encrypted_corr = [
                correlations["horizontal"]["encrypted"],
                correlations["vertical"]["encrypted"],
                correlations["diagonal"]["encrypted"],
            ]

            x_corr = np.arange(len(directions))
            width = 0.35

            bars_corr1 = ax3.bar(
                x_corr - width / 2,
                original_corr,
                width,
                label="Оригинал",
                color="#FF6B6B",
                alpha=0.8,
            )
            bars_corr2 = ax3.bar(
                x_corr + width / 2,
                encrypted_corr,
                width,
                label="Шифр",
                color="#4ECDC4",
                alpha=0.8,
            )

            ax3.set_ylabel("Коэффициент корреляции", fontsize=12)
            ax3.set_title(
                "КОРРЕЛЯЦИЯ СОСЕДНИХ ПИКСЕЛЕЙ", fontweight="bold", fontsize=14, pad=15
            )
            ax3.set_xticks(x_corr)
            ax3.set_xticklabels(directions, fontsize=11)
            ax3.legend(fontsize=11)
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(axis="both", which="major", labelsize=11)
            ax3.axhline(y=0, color="black", linewidth=0.8)

            max_corr = max(max(original_corr), max(encrypted_corr))
            min_corr = min(min(original_corr), min(encrypted_corr))
            text_offset_corr = (max_corr - min_corr) * 0.05

            for bar, value in zip(bars_corr1, original_corr):
                ax3.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + text_offset_corr,
                    f"{value:.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold",
                )
            for bar, value in zip(bars_corr2, encrypted_corr):
                ax3.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + text_offset_corr,
                    f"{value:.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold",
                )

            plt.tight_layout(pad=4.0)
            filename = self.histograms_dir / f"{image_name}_dashboard.png"
            plt.savefig(
                filename,
                dpi=150,
                bbox_inches="tight",
                facecolor="white",
                pad_inches=1.0,
            )
            plt.close()
            print(f"    ✅ Дашборд создан: {filename}")

    def create_comparative_summary_chart(self, metrics_data: Dict[str, Any]):
        """Создает сравнительный график всех изображений с правильными отступами"""
        if not metrics_data:
            print("  ❌ Нет данных для сравнительного графика")
            return

        print(
            f"  Создание сравнительного анализа для {len(metrics_data)} изображений..."
        )

        images = list(metrics_data.keys())

        entropy_improvements = []
        npcr_values = []
        uaci_values = []
        avalanche_values = []
        correlation_reductions = []

        for image_name in images:
            main_data = metrics_data[image_name]["main"]
            if main_data:
                entropy_improvements.append(main_data["entropy"]["improvement"])
                npcr_values.append(main_data["npcr_uaci"]["npcr"])
                uaci_values.append(main_data["npcr_uaci"]["uaci"])
                avalanche_values.append(main_data["avalanche_effect"])
                correlations = main_data["correlations"]
                avg_corr_reduction = (
                    correlations["horizontal"]["reduction"]
                    + correlations["vertical"]["reduction"]
                    + correlations["diagonal"]["reduction"]
                ) / 3
                correlation_reductions.append(avg_corr_reduction)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(22, 16))
        fig.suptitle(
            "СРАВНИТЕЛЬНЫЙ АНАЛИЗ ВСЕХ ИЗОБРАЖЕНИЙ",
            fontsize=20,
            fontweight="bold",
            y=0.98,
        )

        x = np.arange(len(images))
        bar_width = 0.5

        bars1 = ax1.bar(
            x, entropy_improvements, color="#FF6B6B", alpha=0.8, width=bar_width
        )
        ax1.set_ylabel("Улучшение энтропии", fontsize=13)
        ax1.set_title("УЛУЧШЕНИЕ ЭНТРОПИИ", fontweight="bold", fontsize=15, pad=20)
        ax1.set_xticks(x)
        ax1.set_xticklabels(images, rotation=45, ha="right", fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis="both", which="major", labelsize=11)

        if entropy_improvements:
            max_entropy_imp = max(entropy_improvements)
            min_entropy_imp = min(entropy_improvements)
            y_range_entropy = max_entropy_imp - min_entropy_imp
            text_offset_entropy = y_range_entropy * 0.12 if y_range_entropy > 0 else 0.1

            ax1.set_ylim(
                min_entropy_imp - y_range_entropy * 0.15,
                max_entropy_imp + y_range_entropy * 0.15,
            )

            for bar, value in zip(bars1, entropy_improvements):
                color = "green" if value > 0 else "red"
                y_pos = (
                    bar.get_height() + text_offset_entropy * 0.3
                    if value >= 0
                    else bar.get_height() - text_offset_entropy * 0.3
                )
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    y_pos,
                    f"{value:+.3f}",
                    ha="center",
                    va="bottom" if value >= 0 else "top",
                    fontweight="bold",
                    fontsize=10,
                    color=color,
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white",
                        alpha=0.8,
                        edgecolor="none",
                    ),
                )

        bars2 = ax2.bar(x, npcr_values, color="#45B7D1", alpha=0.8, width=bar_width)
        ax2.set_ylabel("NPCR (%)", fontsize=13)
        ax2.set_title("NPCR", fontweight="bold", fontsize=15, pad=20)
        ax2.set_xticks(x)
        ax2.set_xticklabels(images, rotation=45, ha="right", fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis="both", which="major", labelsize=11)
        ax2.axhline(y=99.6, color="red", linestyle="--", alpha=0.7, label="Идеал")

        if npcr_values:
            max_npcr = max(npcr_values)
            min_npcr = min(npcr_values)
            y_range_npcr = max_npcr - min_npcr
            text_offset_npcr = y_range_npcr * 0.08 if y_range_npcr > 0 else 2

            ax2.set_ylim(min_npcr - y_range_npcr * 0.1, max_npcr + y_range_npcr * 0.1)

            for bar, value in zip(bars2, npcr_values):
                color = "green" if value > 99 else "red"
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + text_offset_npcr * 0.3,
                    f"{value:.2f}%",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                    color=color,
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white",
                        alpha=0.8,
                        edgecolor="none",
                    ),
                )

        bars3 = ax3.bar(x, uaci_values, color="#96CEB4", alpha=0.8, width=bar_width)
        ax3.set_ylabel("UACI (%)", fontsize=13)
        ax3.set_title("UACI", fontweight="bold", fontsize=15, pad=20)
        ax3.set_xticks(x)
        ax3.set_xticklabels(images, rotation=45, ha="right", fontsize=11)
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis="both", which="major", labelsize=11)
        ax3.axhline(y=33.4, color="red", linestyle="--", alpha=0.7, label="Идеал")

        if uaci_values:
            max_uaci = max(uaci_values)
            min_uaci = min(uaci_values)
            y_range_uaci = max_uaci - min_uaci
            text_offset_uaci = y_range_uaci * 0.08 if y_range_uaci > 0 else 1

            ax3.set_ylim(min_uaci - y_range_uaci * 0.1, max_uaci + y_range_uaci * 0.1)

            for bar, value in zip(bars3, uaci_values):
                color = "green" if abs(value - 33.4) < 5 else "red"
                ax3.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + text_offset_uaci * 0.3,
                    f"{value:.2f}%",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                    color=color,
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white",
                        alpha=0.8,
                        edgecolor="none",
                    ),
                )
        bars4 = ax4.bar(
            x, correlation_reductions, color="#FECA57", alpha=0.8, width=bar_width
        )
        ax4.set_ylabel("Улучшение корреляции", fontsize=13)
        ax4.set_title(
            "СРЕДНЕЕ УЛУЧШЕНИЕ КОРРЕЛЯЦИИ", fontweight="bold", fontsize=15, pad=20
        )
        ax4.set_xticks(x)
        ax4.set_xticklabels(images, rotation=45, ha="right", fontsize=11)
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(axis="both", which="major", labelsize=11)

        if correlation_reductions:
            max_corr_red = max(correlation_reductions)
            min_corr_red = min(correlation_reductions)
            y_range_corr = max_corr_red - min_corr_red
            text_offset_corr = y_range_corr * 0.12 if y_range_corr > 0 else 0.1

            ax4.set_ylim(
                min_corr_red - y_range_corr * 0.15, max_corr_red + y_range_corr * 0.15
            )

            for bar, value in zip(bars4, correlation_reductions):
                color = "green" if value > 0 else "red"
                y_pos = (
                    bar.get_height() + text_offset_corr * 0.3
                    if value >= 0
                    else bar.get_height() - text_offset_corr * 0.3
                )
                ax4.text(
                    bar.get_x() + bar.get_width() / 2,
                    y_pos,
                    f"{value:.3f}",
                    ha="center",
                    va="bottom" if value >= 0 else "top",
                    fontweight="bold",
                    fontsize=10,
                    color=color,
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white",
                        alpha=0.8,
                        edgecolor="none",
                    ),
                )

        plt.tight_layout(pad=5.0, h_pad=4.0, w_pad=4.0)
        filename = self.histograms_dir / "comparative_analysis.png"
        plt.savefig(
            filename, dpi=150, bbox_inches="tight", facecolor="white", pad_inches=1.0
        )
        plt.close()
        print(f"    ✅ Сравнительный анализ создан: {filename}")

    def create_entropy_comparison_chart(self, metrics_data: Dict[str, Any]):
        """Создает сравнительный график энтропии для всех изображений"""
        if not metrics_data:
            return

        images = list(metrics_data.keys())
        original_entropy = []
        encrypted_entropy = []
        entropy_improvement = []

        for image_name in images:
            main_data = metrics_data[image_name]["main"]
            if main_data:
                entropy_data = main_data["entropy"]
                original_entropy.append(entropy_data["original"])
                encrypted_entropy.append(entropy_data["encrypted"])
                entropy_improvement.append(entropy_data["improvement"])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        fig.suptitle("СРАВНИТЕЛЬНЫЙ АНАЛИЗ ЭНТРОПИИ", fontsize=16, fontweight="bold")

        x = np.arange(len(images))
        width = 0.35

        bars1 = ax1.bar(
            x - width / 2,
            original_entropy,
            width,
            label="Оригинал",
            color="#FF6B6B",
            alpha=0.8,
        )
        bars2 = ax1.bar(
            x + width / 2,
            encrypted_entropy,
            width,
            label="Зашифрованное",
            color="#4ECDC4",
            alpha=0.8,
        )

        ax1.set_ylabel("Энтропия (биты)", fontsize=12)
        ax1.set_title("ЭНТРОПИЯ ШЕННОНА", fontweight="bold", fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels(images, rotation=45, ha="right", fontsize=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=8.0, color="red", linestyle="--", alpha=0.7, label="Идеал (8.0)")

        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.05,
                    f"{height:.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        colors_improvement = ["green" if x > 0 else "red" for x in entropy_improvement]
        bars3 = ax2.bar(x, entropy_improvement, color=colors_improvement, alpha=0.8)

        ax2.set_ylabel("Улучшение энтропии", fontsize=12)
        ax2.set_title("УЛУЧШЕНИЕ ЭНТРОПИИ", fontweight="bold", fontsize=14)
        ax2.set_xticks(x)
        ax2.set_xticklabels(images, rotation=45, ha="right", fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color="black", linestyle="-", alpha=0.5)

        for bar, improvement in zip(bars3, entropy_improvement):
            height = bar.get_height()
            va = "bottom" if improvement >= 0 else "top"
            y_pos = height + 0.01 if improvement >= 0 else height - 0.01
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                f"{improvement:+.3f}",
                ha="center",
                va=va,
                fontsize=9,
                fontweight="bold",
            )

        plt.tight_layout()
        filename = self.comparative_dir / "entropy_comparison.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"  График энтропии создан: {filename}")

    def create_correlation_comparison_chart(self, metrics_data: Dict[str, Any]):
        """Создает сравнительные графики корреляции для всех изображений"""
        if not metrics_data:
            return

        images = list(metrics_data.keys())
        directions = ["horizontal", "vertical", "diagonal"]
        direction_names = ["Горизонтальная", "Вертикальная", "Диагональная"]

        fig, axes = plt.subplots(2, 3, figsize=(24, 12))
        fig.suptitle("СРАВНИТЕЛЬНЫЙ АНАЛИЗ КОРРЕЛЯЦИИ", fontsize=16, fontweight="bold")

        for i, (direction, dir_name) in enumerate(zip(directions, direction_names)):
            original_corr = []
            encrypted_corr = []
            correlation_reduction = []

            for image_name in images:
                main_data = metrics_data[image_name]["main"]
                if main_data:
                    corr_data = main_data["correlations"][direction]
                    original_corr.append(corr_data["original"])
                    encrypted_corr.append(corr_data["encrypted"])
                    correlation_reduction.append(corr_data["reduction"])

            x = np.arange(len(images))
            width = 0.35

            bars1 = axes[0, i].bar(
                x - width / 2,
                original_corr,
                width,
                label="Оригинал",
                color="#FF6B6B",
                alpha=0.8,
            )
            bars2 = axes[0, i].bar(
                x + width / 2,
                encrypted_corr,
                width,
                label="Зашифрованное",
                color="#4ECDC4",
                alpha=0.8,
            )

            axes[0, i].set_ylabel("Коэффициент корреляции", fontsize=11)
            axes[0, i].set_title(
                f"{dir_name.upper()} КОРРЕЛЯЦИЯ", fontweight="bold", fontsize=12
            )
            axes[0, i].set_xticks(x)
            axes[0, i].set_xticklabels(images, rotation=45, ha="right", fontsize=9)
            axes[0, i].legend(fontsize=9)
            axes[0, i].grid(True, alpha=0.3)
            axes[0, i].axhline(y=0, color="black", linestyle="-", alpha=0.5)

            colors_reduction = [
                "green" if x > 0 else "red" for x in correlation_reduction
            ]
            bars3 = axes[1, i].bar(
                x, correlation_reduction, color=colors_reduction, alpha=0.8
            )

            axes[1, i].set_ylabel("Улучшение корреляции", fontsize=11)
            axes[1, i].set_title(
                f"{dir_name.upper()} - УЛУЧШЕНИЕ", fontweight="bold", fontsize=12
            )
            axes[1, i].set_xticks(x)
            axes[1, i].set_xticklabels(images, rotation=45, ha="right", fontsize=9)
            axes[1, i].grid(True, alpha=0.3)
            axes[1, i].axhline(y=0, color="black", linestyle="-", alpha=0.5)

            for bar, reduction in zip(bars3, correlation_reduction):
                height = bar.get_height()
                va = "bottom" if reduction >= 0 else "top"
                y_pos = height + 0.01 if reduction >= 0 else height - 0.01
                axes[1, i].text(
                    bar.get_x() + bar.get_width() / 2.0,
                    y_pos,
                    f"{reduction:+.3f}",
                    ha="center",
                    va=va,
                    fontsize=8,
                    fontweight="bold",
                )

        plt.tight_layout()
        filename = self.comparative_dir / "correlation_comparison.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"  График корреляции создан: {filename}")

    def create_security_metrics_chart(self, metrics_data: Dict[str, Any]):
        """Создает сравнительные графики метрик безопасности"""
        if not metrics_data:
            return

        images = list(metrics_data.keys())
        npcr_values = []
        uaci_values = []
        avalanche_values = []

        for image_name in images:
            main_data = metrics_data[image_name]["main"]
            if main_data:
                npcr_uaci = main_data["npcr_uaci"]
                npcr_values.append(npcr_uaci["npcr"])
                uaci_values.append(npcr_uaci["uaci"])
                avalanche_values.append(main_data["avalanche_effect"])

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 8))
        fig.suptitle(
            "СРАВНИТЕЛЬНЫЙ АНАЛИЗ МЕТРИК БЕЗОПАСНОСТИ", fontsize=16, fontweight="bold"
        )

        x = np.arange(len(images))
        bars1 = ax1.bar(x, npcr_values, color="#45B7D1", alpha=0.8)
        ax1.set_ylabel("NPCR (%)", fontsize=12)
        ax1.set_title(
            "NPCR (Number of Pixels Change Rate)", fontweight="bold", fontsize=14
        )
        ax1.set_xticks(x)
        ax1.set_xticklabels(images, rotation=45, ha="right", fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(
            y=99.6, color="red", linestyle="--", alpha=0.7, label="Идеал (99.6%)"
        )

        for bar, value in zip(bars1, npcr_values):
            color = "green" if value > 99 else "red"
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 0.1,
                f"{value:.2f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                color=color,
                fontweight="bold",
            )

        bars2 = ax2.bar(x, uaci_values, color="#96CEB4", alpha=0.8)
        ax2.set_ylabel("UACI (%)", fontsize=12)
        ax2.set_title(
            "UACI (Unified Average Changing Intensity)", fontweight="bold", fontsize=14
        )
        ax2.set_xticks(x)
        ax2.set_xticklabels(images, rotation=45, ha="right", fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(
            y=33.4, color="red", linestyle="--", alpha=0.7, label="Идеал (33.4%)"
        )

        for bar, value in zip(bars2, uaci_values):
            color = "green" if abs(value - 33.4) < 5 else "red"
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 0.1,
                f"{value:.2f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                color=color,
                fontweight="bold",
            )

        bars3 = ax3.bar(x, avalanche_values, color="#FECA57", alpha=0.8)
        ax3.set_ylabel("Avalanche Effect (%)", fontsize=12)
        ax3.set_title("AVALANCHE EFFECT", fontweight="bold", fontsize=14)
        ax3.set_xticks(x)
        ax3.set_xticklabels(images, rotation=45, ha="right", fontsize=10)
        ax3.grid(True, alpha=0.3)
        ax3.axhline(
            y=50.0, color="red", linestyle="--", alpha=0.7, label="Идеал (50.0%)"
        )

        for bar, value in zip(bars3, avalanche_values):
            color = "green" if abs(value - 50.0) < 5 else "red"
            ax3.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 0.1,
                f"{value:.2f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                color=color,
                fontweight="bold",
            )

        plt.tight_layout()
        filename = self.comparative_dir / "security_metrics_comparison.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"  График метрик безопасности создан: {filename}")

    def create_radar_chart(self, metrics_data: Dict[str, Any]):
        """Создает радарные диаграммы для сравнения характеристик"""
        if not metrics_data:
            return

        images = list(metrics_data.keys())

        if len(images) > 5:
            images = images[:5]
            print(f"  Для радарной диаграммы выбрано первых 5 изображений: {images}")

        categories = ["Энтропия", "NPCR", "UACI", "Avalanche", "Корреляция"]

        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection="polar"))

        normalized_data = []

        for image_name in images:
            main_data = metrics_data[image_name]["main"]
            if main_data:
                entropy_norm = main_data["entropy"]["encrypted"] / 8.0
                npcr_norm = main_data["npcr_uaci"]["npcr"] / 100.0
                uaci_norm = main_data["npcr_uaci"]["uaci"] / 33.4
                avalanche_norm = main_data["avalanche_effect"] / 50.0

                corr_data = main_data["correlations"]
                avg_corr_improvement = (
                    corr_data["horizontal"]["reduction"]
                    + corr_data["vertical"]["reduction"]
                    + corr_data["diagonal"]["reduction"]
                ) / 3
                correlation_norm = min(1.0, max(0.0, (avg_corr_improvement + 1) / 2))

                normalized_values = [
                    entropy_norm,
                    npcr_norm,
                    uaci_norm,
                    avalanche_norm,
                    correlation_norm,
                ]
                normalized_data.append(normalized_values)

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        for i, (image_name, values) in enumerate(zip(images, normalized_data)):
            values += values[:1]
            ax.plot(
                angles,
                values,
                "o-",
                linewidth=2,
                label=image_name,
                color=self.colors[i % len(self.colors)],
            )
            ax.fill(angles, values, alpha=0.1, color=self.colors[i % len(self.colors)])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=10)
        ax.grid(True)

        plt.title(
            "РАДАРНАЯ ДИАГРАММА ХАРАКТЕРИСТИК\n(Нормализованные значения)",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )
        plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0), fontsize=10)

        filename = self.comparative_dir / "radar_chart_comparison.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"  Радарная диаграмма создана: {filename}")

    def create_heatmap_comparison(self, metrics_data: Dict[str, Any]):
        """Создает тепловую карту для сравнения всех метрик"""
        if not metrics_data:
            return

        images = list(metrics_data.keys())
        metrics_list = [
            "Энтропия_шифр",
            "NPCR",
            "UACI",
            "Avalanche",
            "Корр_гориз_улучш",
            "Корр_верт_улучш",
            "Корр_диаг_улучш",
        ]

        data_matrix = []

        for image_name in images:
            main_data = metrics_data[image_name]["main"]
            if main_data:
                row = [
                    main_data["entropy"]["encrypted"],
                    main_data["npcr_uaci"]["npcr"],
                    main_data["npcr_uaci"]["uaci"],
                    main_data["avalanche_effect"],
                    main_data["correlations"]["horizontal"]["reduction"],
                    main_data["correlations"]["vertical"]["reduction"],
                    main_data["correlations"]["diagonal"]["reduction"],
                ]
                data_matrix.append(row)

        if not data_matrix:
            return

        data_matrix = np.array(data_matrix)

        fig, ax = plt.subplots(figsize=(16, 10))

        im = ax.imshow(data_matrix, cmap="RdYlGn", aspect="auto")

        ax.set_xticks(np.arange(len(metrics_list)))
        ax.set_yticks(np.arange(len(images)))
        ax.set_xticklabels(metrics_list, rotation=45, ha="right", fontsize=11)
        ax.set_yticklabels(images, fontsize=11)

        for i in range(len(images)):
            for j in range(len(metrics_list)):
                text = ax.text(
                    j,
                    i,
                    f"{data_matrix[i, j]:.2f}",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=9,
                    fontweight="bold",
                )

        plt.colorbar(im, ax=ax, shrink=0.6)
        plt.title(
            "ТЕПЛОВАЯ КАРТА СРАВНЕНИЯ МЕТРИК", fontsize=16, fontweight="bold", pad=20
        )

        plt.tight_layout()
        filename = self.comparative_dir / "heatmap_comparison.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"  Тепловая карта создана: {filename}")

    def generate_comprehensive_comparison(self):
        """Генерирует все сравнительные графики"""
        print(" Generating comprehensive comparative charts...")

        metrics_data = self.load_metrics_data()

        if not metrics_data:
            print(" No metrics data found for comparative analysis!")
            return

        print(f" Creating comparative charts for {len(metrics_data)} images...")

        self.create_entropy_comparison_chart(metrics_data)
        self.create_correlation_comparison_chart(metrics_data)
        self.create_security_metrics_chart(metrics_data)
        self.create_radar_chart(metrics_data)
        self.create_heatmap_comparison(metrics_data)

        print(" All comparative charts generated successfully!")
        print(f"  Charts saved to: {self.comparative_dir}")

    def generate_summary_report(self):
        """Генерация сводного отчета с таблицами и графиками"""
        print(" Starting summary visualization...")

        metrics_data = self.load_metrics_data()

        if not metrics_data:
            print(" No metrics data found!")
            return

        print(f" Processing {len(metrics_data)} images")

        print(" Creating comparative tables...")
        self.generate_comparative_tables(metrics_data)

        print(" Creating summary charts...")
        self.create_summary_dashboard(metrics_data)
        self.create_comparative_summary_chart(metrics_data)

        print(" Creating specialized comparative charts...")
        self.generate_comprehensive_comparison()

        print(f" Summary report completed!")
        print(f"    Tables: {self.tables_dir}")
        print(f"    Charts: {self.histograms_dir}")
        print(f"    Comparative: {self.comparative_dir}")


if __name__ == "__main__":
    visualizer = CryptoVisualizer("results")
    visualizer.generate_summary_report()
