
# PyInstaller钩子文件，确保openpyxl模块被正确打包
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 收集所有子模块
hiddenimports = collect_submodules('openpyxl')

# 特别添加已知可能缺失的模块
hiddenimports += [
    'openpyxl.cell._writer',
    'openpyxl.cell.cell',
    'openpyxl.worksheet._writer',
    'openpyxl.styles.fonts',
    'openpyxl.styles.fills',
]

# 收集数据文件
datas = collect_data_files('openpyxl')
