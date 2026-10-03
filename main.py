Update main.py
Status
Deploy failed
Duration
34.5s
Deployed
Oct 3, 2026
at
1:10:03 PM
GMT+5:30

Trigger
Auto-Deploy
Source
c58c954
Notices
Exited with status 1 while running your code.
Read our docs for common ways to troubleshoot your deploy.

All logs
Search
Search logs


Live tail



Collecting opentelemetry-api>=1.44.0 (from fastapi)
  Using cached opentelemetry_api-1.45.0-py3-none-any.whl.metadata (1.4 kB)
Collecting click>=7.0 (from uvicorn)
  Using cached click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
Collecting h11>=0.8 (from uvicorn)
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting charset_normalizer<4,>=2 (from requests)
  Using cached charset_normalizer-3.5.2-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (46 kB)
Collecting idna<4,>=2.5 (from requests)
  Using cached idna-3.20-py3-none-any.whl.metadata (7.2 kB)
Collecting urllib3<3,>=1.26 (from requests)
  Using cached urllib3-2.8.0-py3-none-any.whl.metadata (7.4 kB)
Collecting certifi>=2023.5.7 (from requests)
  Using cached certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
Collecting annotated-types>=0.6.0 (from pydantic>=2.9.0->fastapi)
  Using cached annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.46.5 (from pydantic>=2.9.0->fastapi)
  Using cached pydantic_core-2.46.5-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
Collecting anyio<5,>=4.0.0 (from starlette>=0.46.0->fastapi)
  Using cached anyio-4.15.1-py3-none-any.whl.metadata (4.7 kB)
Using cached fastapi-0.142.2-py3-none-any.whl (144 kB)
Using cached uvicorn-0.54.0-py3-none-any.whl (87 kB)
Using cached pypdf-6.19.0-py3-none-any.whl (395 kB)
Using cached requests-2.34.2-py3-none-any.whl (73 kB)
Using cached charset_normalizer-3.5.2-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (255 kB)
Using cached idna-3.20-py3-none-any.whl (69 kB)
Using cached urllib3-2.8.0-py3-none-any.whl (135 kB)
Using cached python_multipart-0.0.32-py3-none-any.whl (30 kB)
Using cached annotated_doc-0.0.5-py3-none-any.whl (5.3 kB)
Using cached certifi-2026.7.22-py3-none-any.whl (136 kB)
Using cached click-8.5.0-py3-none-any.whl (125 kB)
Using cached h11-0.16.0-py3-none-any.whl (37 kB)
Using cached opentelemetry_api-1.45.0-py3-none-any.whl (60 kB)
Using cached pydantic-2.13.5-py3-none-any.whl (472 kB)
Using cached pydantic_core-2.46.5-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
Using cached annotated_types-0.8.0-py3-none-any.whl (13 kB)
Using cached starlette-1.7.0-py3-none-any.whl (78 kB)
Using cached anyio-4.15.1-py3-none-any.whl (132 kB)
Using cached typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Using cached typing_inspection-0.4.4-py3-none-any.whl (14 kB)
Installing collected packages: urllib3, typing-extensions, python-multipart, pypdf, idna, h11, click, charset_normalizer, certifi, annotated-types, annotated-doc, uvicorn, typing-inspection, requests, pydantic-core, opentelemetry-api, anyio, starlette, pydantic, fastapi
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 certifi-2026.7.22 charset_normalizer-3.5.2 click-8.5.0 fastapi-0.142.2 h11-0.16.0 idna-3.20 opentelemetry-api-1.45.0 pydantic-2.13.5 pydantic-core-2.46.5 pypdf-6.19.0 python-multipart-0.0.32 requests-2.34.2 starlette-1.7.0 typing-extensions-4.16.0 typing-inspection-0.4.4 urllib3-2.8.0 uvicorn-0.54.0
[notice] A new release of pip is available: 25.3 -> 26.2.1
[notice] To update, run: pip install --upgrade pip
==> Uploading build...
==> Uploaded in 1.8s. Compression took 1.1s
==> Build successful 🎉
==> Deploying...
==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/bin/uvicorn", line 7, in <module>
    sys.exit(main())
             ~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/click/core.py", line 1631, in __call__
    return self.main(*args, **kwargs)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/click/core.py", line 1552, in main
    rv = self.invoke(ctx)
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/click/core.py", line 1415, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/click/core.py", line 910, in invoke
    return callback(*args, **kwargs)
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/uvicorn/main.py", line 448, in main
    run(
    ~~~^
        app,
        ^^^^
    ...<49 lines>...
        reset_contextvars=reset_contextvars,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/uvicorn/main.py", line 620, in run
    config.load_app()
    ~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/uvicorn/config.py", line 434, in load_app
    return import_from_string(self.app)
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
  File "/opt/render/project/python/Python-3.14.3/lib/python3.14/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1398, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1342, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 938, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 755, in exec_module
  File "<frozen importlib._bootstrap_external>", line 893, in get_code
  File "<frozen importlib._bootstrap_external>", line 823, in source_to_code
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "/opt/render/project/src/main.py", line 78
    pdf_html = (
               ^
SyntaxError: '(' was never closed
==> Exited with status 1
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
Need better ways to work with logs? Try theRender
