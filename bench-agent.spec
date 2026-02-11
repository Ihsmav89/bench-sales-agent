# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Bench Sales Agent Web UI

import os
import sys
from pathlib import Path

block_cipher = None

# Find the package source
src_dir = os.path.join(os.getcwd(), 'src')
templates_dir = os.path.join(src_dir, 'bench_sales_agent', 'web', 'templates')

a = Analysis(
    [os.path.join(src_dir, 'bench_sales_agent', 'web', 'app.py')],
    pathex=[src_dir],
    binaries=[],
    datas=[
        (templates_dir, 'bench_sales_agent/web/templates'),
    ],
    hiddenimports=[
        'bench_sales_agent',
        'bench_sales_agent.web',
        'bench_sales_agent.web.routes',
        'bench_sales_agent.web.routes.dashboard',
        'bench_sales_agent.web.routes.consultants',
        'bench_sales_agent.web.routes.jobs',
        'bench_sales_agent.web.routes.vendors',
        'bench_sales_agent.web.routes.submissions',
        'bench_sales_agent.web.routes.search',
        'bench_sales_agent.web.routes.emails',
        'bench_sales_agent.web.routes.chat',
        'bench_sales_agent.web.routes.market',
        'bench_sales_agent.agent',
        'bench_sales_agent.data.database',
        'bench_sales_agent.models',
        'bench_sales_agent.search.xray_engine',
        'bench_sales_agent.search.job_board_urls',
        'bench_sales_agent.templates.emails',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='bench-agent-web',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
