import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QVBoxLayout, QPushButton,
    QLabel, QListWidget, QMessageBox, QComboBox, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QDialog, QHBoxLayout
)

def load_data(file_path):
    """自动识别分隔符并读取csv/dat/xlsx文件"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    elif ext in ['.csv', '.dat', '.txt']:
        # 尝试自动分隔符
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
        if ',' in first_line:
            sep = ','
        elif '\t' in first_line:
            sep = '\t'
        else:
            sep = r'\s+'
        df = pd.read_csv(file_path, sep=sep, engine='python')
        # 修正无表头问题
        if all([str(c).lower().startswith('unnamed') or str(c).lower().startswith('untitled') for c in df.columns]):
            df = pd.read_csv(file_path, sep=sep, header=None, engine='python')
        return df
    else:
        raise ValueError("不支持的文件格式")

def compute_time_averages(df, time_col, intervals):
    """对df按time_col进行多区间均值分组"""
    out = {}
    # 时间列标准化
    df = df.copy()
    df['__t'] = pd.to_datetime(df[time_col])
    df = df.sort_values('__t')
    for interval in intervals:
        sec = int(interval)
        df['__group'] = (df['__t'].astype('int64') // (sec*10**9))
        agg = df.groupby('__group').mean(numeric_only=True)
        agg['区间起始时间'] = df.groupby('__group')['__t'].min()
        agg['日期'] = agg['区间起始时间'].dt.date.astype(str)
        agg['时间'] = agg['区间起始时间'].dt.time.astype(str)
        # 排序
        fixed_cols = ['区间起始时间', '日期', '时间']
        remain_cols = [c for c in agg.columns if c not in fixed_cols]
        out[sec] = agg[fixed_cols + remain_cols].reset_index(drop=True)
    return out

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('均值数据统计工具')
        self.resize(650, 450)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_btn = QPushButton('选择数据文件夹/文件')
        self.load_btn.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_btn)

        self.info_label = QLabel('请选择数据源')
        self.layout.addWidget(self.info_label)

        self.time_col_combo = QComboBox()
        self.data_col_list = QListWidget()
        self.data_col_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(QLabel('时间列选择'))
        self.layout.addWidget(self.time_col_combo)
        self.layout.addWidget(QLabel('需要统计均值的数据列(多选)'))
        self.layout.addWidget(self.data_col_list)

        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['30', '60', '300', '3600'])
        self.layout.addWidget(QLabel('统计区间(秒)'))
        self.layout.addWidget(self.interval_combo)

        self.compute_btn = QPushButton('统计均值并导出')
        self.compute_btn.clicked.connect(self.compute)
        self.layout.addWidget(self.compute_btn)

        self.df = None

    def load_data(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        dfs = []
        if folder:
            for fname in os.listdir(folder):
                fpath = os.path.join(folder, fname)
                if fname.endswith(('.dat', '.csv', '.xlsx', '.xls')):
                    try:
                        df = load_data(fpath)
                        dfs.append(df)
                    except Exception as e:
                        print(f"跳过 {fname}，读取失败: {e}")
            if dfs:
                self.df = pd.concat(dfs, ignore_index=True)
        else:
            file, _ = QFileDialog.getOpenFileName(self, "选择单个文件", "", "数据文件 (*.dat *.csv *.xlsx *.xls)")
            if file:
                try:
                    self.df = load_data(file)
                except Exception as e:
                    QMessageBox.warning(self, "读取错误", f"无法读取: {file}\n{e}")
                    return
        if self.df is not None:
            self.info_label.setText(f"数据加载成功，共 {len(self.df)} 行。")
            self.time_col_combo.clear()
            self.data_col_list.clear()
            cols = [c for c in self.df.columns if not (str(c).lower().startswith('unnamed') or str(c).lower().startswith('untitled'))]
            self.time_col_combo.addItems(cols)
            for c in cols:
                item = QListWidgetItem(c)
                item.setCheckState(2)  # Qt.Checked
                self.data_col_list.addItem(item)
        else:
            self.info_label.setText("未能读取数据，请重试。")

    def compute(self):
        if self.df is None:
            QMessageBox.warning(self, "错误", "请先加载数据！")
            return
        time_col = self.time_col_combo.currentText()
        data_cols = [self.data_col_list.item(i).text()
             for i in range(self.data_col_list.count())
             if self.data_col_list.item(i).checkState() == 2 and self.data_col_list.item(i).text() != time_col]
        use_cols = [time_col] + data_cols
        if not data_cols:
            QMessageBox.warning(self, "错误", "请至少选择一个数据列！")
            return
        interval = int(self.interval_combo.currentText())
        # 只选要统计的列和时间列
        use_cols = [time_col] + data_cols
        try:
            avgs = compute_time_averages(self.df[use_cols], time_col, [interval])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"计算失败，请检查数据！\n{e}")
            return
        result_df = avgs[interval]
        out_path, _ = QFileDialog.getSaveFileName(self, "保存统计表", "均值数据统计.xlsx", "Excel文件 (*.xlsx)")
        if out_path:
            result_df.to_excel(out_path, index=False)
            QMessageBox.information(self, "成功", f"均值统计表已保存到:\n{out_path}")
            self.preview_table(result_df)

    def preview_table(self, df):
        dialog = QDialog(self)
        dialog.setWindowTitle("统计结果预览（前20行）")
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setRowCount(min(20, len(df)))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(df.columns.tolist())
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                val = df.iat[i, j]
                item = QTableWidgetItem(str(val))
                table.setItem(i, j, item)
        layout.addWidget(table)
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        dialog.resize(800, 400)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainApp()
    main_win.show()
    sys.exit(app.exec_())