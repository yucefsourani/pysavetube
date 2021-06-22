# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
data_files = [("README.md","."),("LICENSE","."),
              ("com.github.yucefsourani.pysavetube.ico","."),
              ("pixmaps","./pixmaps"),("pysavetube-data","./pysavetube-data"),
              ("locale","./locale")]
binary_files = []
a = Analysis(['pysavetube.py'],
             pathex=['.'],
             binaries=binary_files,
             datas=data_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='pysavetube',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,icon='com.github.yucefsourani.pysavetube.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='pysavetube')
