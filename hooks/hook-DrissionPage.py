
# PyInstaller钩子文件，确保DrissionPage模块被正确打包
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 收集所有子模块
hiddenimports = collect_submodules('DrissionPage')
hiddenimports += collect_submodules('DataRecorder')

# 收集数据文件
datas = collect_data_files('DrissionPage')
datas += collect_data_files('DataRecorder')
