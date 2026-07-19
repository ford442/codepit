#!/usr/bin/env python3
"""Refactor BUILDER.ipynb: secrets, helpers, bug fixes, DRY project cells."""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy

NOTEBOOK_PATH = "/workspace/BUILDER.ipynb"

SECRETS_CELL = """# @title 🔑 Colab Secrets

from google.colab import userdata
import os

SECRET_KEYS = [
    "DEPLOY_TOKEN",
    "DEPLOY_USER",
    "DEPLOY_PASS",
    "MAPS_API_KEY",
    "REACT_APP_MAPS_API_KEY",
]

for key in SECRET_KEYS:
    try:
        os.environ[key] = userdata.get(key)
        print(f"✅ {key} exported.")
    except userdata.SecretNotFoundError:
        print(f"⚠️  {key} not set (add via 🔑 Secrets if needed).")

# Keep React / deploy env aliases in sync
if "REACT_APP_MAPS_API_KEY" not in os.environ and "MAPS_API_KEY" in os.environ:
    os.environ["REACT_APP_MAPS_API_KEY"] = os.environ["MAPS_API_KEY"]
elif "MAPS_API_KEY" not in os.environ and "REACT_APP_MAPS_API_KEY" in os.environ:
    os.environ["MAPS_API_KEY"] = os.environ["REACT_APP_MAPS_API_KEY"]
"""

HELPER_CELL = """# @title 🔧 Build & Deploy Helpers
import os
import subprocess

BUILD_SPACE = "/content/build_space"
EMS_SOURCE = f"{BUILD_SPACE}/emsdk/emsdk_env.sh"


def _run(cmd, cwd=None, env=None, check=True):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    print(f"$ {cmd}" + (f"  (cwd={cwd})" if cwd else ""))
    result = subprocess.run(cmd, shell=True, cwd=cwd, env=merged)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {cmd}")
    return result


def clone_or_pull(project_name, branch="main", recursive=False, git_repo=None):
    target = f"{BUILD_SPACE}/{project_name}"
    repo = git_repo or f"https://github.com/ford442/{project_name}.git"
    recursive_flag = "--recursive " if recursive else ""
    if not os.path.exists(target):
        print(f"⬇️ Cloning {repo}...")
        _run(f"git clone {recursive_flag}{repo} {target}")
    else:
        print(f"🔄 Pulling {project_name}...")
        _run("git pull", cwd=target)
    _run(f"git checkout {branch}", cwd=target, check=False)
    _run("git pull", cwd=target, check=False)
    return target


def run_npm_build(project_name, use_emsdk=False, cwd=None):
    cwd = cwd or f"{BUILD_SPACE}/{project_name}"
    if use_emsdk:
        _run(
            f"bash -c 'source {EMS_SOURCE} && npm install && npm run build'",
            cwd=cwd,
        )
    else:
        _run("npm install", cwd=cwd)
        _run("npm run build", cwd=cwd)


def patch_html_to_relative(html_path, extra_replacements=None):
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML not found: {html_path}")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    replacements = [
        ('src="/', 'src="./'),
        ('href="/', 'href="./'),
        ("src='/", "src='./"),
        ("href='/", "href='./"),
    ]
    if extra_replacements:
        replacements = list(extra_replacements) + replacements
    for old, new in replacements:
        content = content.replace(old, new)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Patched paths in {html_path}")


def finalize_deploy(
    project_name,
    html_subpath="dist/index.html",
    deploy_script="deploy.py",
    work_subdir=None,
    extra_env=None,
    extra_replacements=None,
    skip_deploy=False,
    skip_patch=False,
):
    base = f"{BUILD_SPACE}/{project_name}"
    if work_subdir:
        base = f"{base}/{work_subdir}"
    html_path = (
        html_subpath
        if html_subpath.startswith("/")
        else f"{base}/{html_subpath}"
    )
    if not os.path.exists(html_path):
        raise FileNotFoundError(
            f"Build output missing: {html_path}. Did the build succeed?"
        )
    if not skip_patch:
        patch_html_to_relative(html_path, extra_replacements)
    out_dir = os.path.dirname(html_path)
    ink_path = f"{out_dir}/1ink.1ink"
    _run(f"iconv -f UTF-8 -t UTF-16 {html_path} -o {ink_path}")
    if not skip_deploy:
        deploy_cwd = base
        if not os.path.exists(os.path.join(deploy_cwd, deploy_script)):
            deploy_cwd = f"{BUILD_SPACE}/{project_name}"
        _run(f"python3 {deploy_script}", cwd=deploy_cwd, env=extra_env)
    print(f"✅ Deploy complete for {project_name}")


def sftp_upload(local_path, remote_path, host=None, username=None, password=None, port=22):
    import paramiko

    host = host or os.environ.get("SFTP_HOST", "1ink.us")
    username = username or os.environ.get("DEPLOY_USER", os.environ.get("SFTP_USER", ""))
    password = password or os.environ.get("DEPLOY_PASS", os.environ.get("SFTP_PASSWORD", ""))
    if not username or not password:
        raise RuntimeError(
            "SFTP credentials missing. Set DEPLOY_USER and DEPLOY_PASS in Colab secrets."
        )
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_path, remote_path)
    sftp.close()
    transport.close()
    print(f"✅ Uploaded {local_path} → {remote_path}")
"""

# Projects that use the standard clone → npm build → deploy pattern
STANDARD_PROJECTS: dict[str, dict] = {
    "go.1ink.us": {},
    "1inkulous": {},
    "plant-growth-sim": {},
    "rebirth_website": {},
    "wind_manager": {},
    "weeks_on_fire": {"html_subpath": "out/index.html"},
    "yoga_studio": {"html_subpath": "out/index.html", "deploy_script": "deploy_old.py"},
    "scheduler": {},
    "webgl-diceroller": {},
    "brain_viz": {},
    "dice_roller": {},
    "clip_stacker": {"deploy_script": "deploy_old.py"},
    "marbles": {},
    "weather_clock": {},
    "mod-player": {},
    "harborglow": {},
    "chromashift": {"use_emsdk": True},  # kept custom build below; only deploy fixed
    "cloud_notes": {},
    "pachinball": {"branch": "216673b05dccc7cf2678debae04f537ac450778f"},
    "rain_chime": {"branch": "main", "skip_checkout_pull": False},
    "the_jokesters": {},  # complex - not standard
}

# Explicit per-project HTML output paths for non-standard cells (path fixes only)
PATH_FIXES = {
    "weeks_on_fire": {"html_subpath": "out/index.html"},
    "webgpu-ts": {"html_subpath": "build/index.html"},
    "benching_machine_utf": {
        "html_subpath": "dist/utf8-control/index.html",
        "work_subdir": "utf_benchmark",
        "iconv_from_html": True,
    },
}

SKIP_STANDARD_CONVERT = {
    "xmrig_wasm",
    "benching_machine",
    "chromashift",
    "korg_prophecy_emu",
    "image_video_effects",
    "Project-M",
    "ui_componants",
    "Watershed",
    "BespokeSynth_WASM",
    "SolarSystem-3D-WASM",
    "webgpu_streetview",
    "the_jokesters",
    "flac_player",
    "wasm-platformer",
    "os13k",
    "supertonic-tts",
    "iptv",
    "openmpt",
    "jc303_wasm",
    "anuraOS",
    "visual6502",
    "sinsy",
    "web_sequencer",
    "Tetris_WebGPU",
    "marbles",
    "pachinball",
}


def cell_source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_cell_source(cell: dict, text: str) -> None:
    cell["source"] = [line + "\n" for line in text.split("\n")]
    if cell["source"]:
        cell["source"][-1] = cell["source"][-1].rstrip("\n")


def make_standard_cell(title: str, project_name: str, opts: dict) -> str:
    branch = opts.get("branch", "main")
    html_subpath = opts.get("html_subpath", "dist/index.html")
    deploy_script = opts.get("deploy_script", "deploy.py")
    use_emsdk = opts.get("use_emsdk", False)
    recursive = opts.get("recursive", False)

    lines = [
        f"# @title 🔨 {title}",
        "import os",
        "",
        f'PROJECT_NAME = "{project_name}"',
        f'GIT_REPO = f"https://github.com/ford442/{{PROJECT_NAME}}.git"',
        f"USE_EMSDK = {use_emsdk}",
        f'BRANCH = "{branch}"',
        f'HTML_SUBPATH = "{html_subpath}"',
        f'DEPLOY_SCRIPT = "{deploy_script}"',
        f"RECURSIVE_CLONE = {recursive}",
        "",
        "target_dir = clone_or_pull(PROJECT_NAME, branch=BRANCH, recursive=RECURSIVE_CLONE, git_repo=GIT_REPO)",
        "print(\"🚀 Starting Build...\")",
        "run_npm_build(PROJECT_NAME, use_emsdk=USE_EMSDK, cwd=target_dir)",
        "print(\"✅ Build Complete.\")",
        "finalize_deploy(PROJECT_NAME, html_subpath=HTML_SUBPATH, deploy_script=DEPLOY_SCRIPT)",
    ]
    return "\n".join(lines)


def extract_title_and_project(src: str) -> tuple[str | None, str | None]:
    title_m = re.search(r"# @title 🔨 (.+)", src)
    proj_m = re.search(r'PROJECT_NAME\s*=\s*["\']([^"\']+)["\']', src)
    return (
        title_m.group(1).strip() if title_m else None,
        proj_m.group(1) if proj_m else None,
    )


def is_convertible_standard(src: str, project: str | None) -> bool:
    if not project or project in SKIP_STANDARD_CONVERT:
        return False
    if "paramiko" in src or "MAPS_API" in src:
        return False
    if "shutil.rmtree" in src or "build:physics" in src or "build-web.sh" in src:
        return False
    if "rubberband" in src or "onnxruntime" in src:
        return False
    if "emmake" in src and "npm run build" not in src:
        return False
    if "%cd {target_dir}/web" in src or "%cd {target_dir}/utf_benchmark" in src:
        return False
    if "finalize_deploy" in src:
        return False
    if "!cp " in src or "shutil.copy" in src:
        return False
    has_boilerplate_tail = (
        "html_file_path" in src and "iconv" in src and "deploy" in src
    )
    has_standard_build = "npm run build" in src and "git clone" in src
    return has_boilerplate_tail and has_standard_build


def apply_global_fixes(src: str) -> str:
    # Credentials
    src = src.replace('password  = "GoogleBez12!"', 'password = os.environ.get("DEPLOY_PASS", os.environ.get("SFTP_PASSWORD", ""))')
    src = src.replace('username  = "ford442"', 'username = os.environ.get("DEPLOY_USER", os.environ.get("SFTP_USER", ""))')
    src = re.sub(
        r'!export DEPLOY_USER=ford442 && export DEPLOY_PASS=GoogleBez12! && python3 deploy\.py',
        '!python3 deploy.py  # DEPLOY_USER / DEPLOY_PASS from Colab secrets',
        src,
    )

    # API keys → secrets (remove hardcoded keys from active lines)
    src = re.sub(
        r"!export MAPS_API_KEY=AIza[A-Za-z0-9_-]+\n",
        "# MAPS_API_KEY loaded from Colab secrets (run 🔑 cell first)\n",
        src,
    )
    src = re.sub(
        r"#!export REACT_APP_MAPS_API_KEY=AIza[A-Za-z0-9_-]+.*\n",
        "",
        src,
    )
    src = re.sub(
        r"!echo 'REACT_APP_MAPS_API_KEY=AIza[A-Za-z0-9_-]+' > \.env\.local",
        '!echo "REACT_APP_MAPS_API_KEY=$REACT_APP_MAPS_API_KEY" > .env.local',
        src,
    )
    src = re.sub(
        r'!export REACT_APP_MAPS_API_KEY="AIza[A-Za-z0-9_-]+" && export MAPS_API_KEY="AIza[A-Za-z0-9_-]+" && python3 deploy\.py',
        '!python3 deploy.py  # MAPS_API_KEY / REACT_APP_MAPS_API_KEY from Colab secrets',
        src,
    )

    # Uncomment write-back
    src = src.replace(
        "        #with open(html_file_path, 'w', encoding='utf-8') as file:\n"
        "            #file.write(content)\n"
        "        print(\"✅ Successfully updated paths in index.html to be relative.\")",
        "        with open(html_file_path, 'w', encoding='utf-8') as file:\n"
        "            file.write(content)\n"
        "        print(\"✅ Successfully updated paths in index.html to be relative.\")",
    )

    # Add single-quote patching where double-quote patching exists but singles don't
    if "content.replace('href=\"/'" in src and "content.replace(\"href='/\"" not in src:
        src = src.replace(
            "        content = content.replace('href=\"/', 'href=\"./')\n",
            "        content = content.replace('href=\"/', 'href=\"./')\n"
            "        content = content.replace(\"src='/\", \"src='./\")\n"
            "        content = content.replace(\"href='/\", \"href='./\")\n",
        )

    # WasmEdge typo
    src = src.replace(
        'echo "${RED}$INSTALL_PY_URL not reachable{NC}"',
        'echo "${RED}$INSTALL_PY_URL not reachable${NC}"',
    )

    # weeks_on_fire: iconv uses dist but should use out
    if 'PROJECT_NAME = "weeks_on_fire"' in src:
        src = src.replace(
            "iconv -f UTF-8 -t UTF-16 ./dist/index.html -o ./dist/1ink.1ink",
            "iconv -f UTF-8 -t UTF-16 ./out/index.html -o ./out/1ink.1ink",
        )

    # webgpu-ts: iconv should use build not dist
    if 'PROJECT_NAME = "webgpu-ts"' in src:
        src = src.replace(
            "iconv -f UTF-8 -t UTF-16 ./dist/index.html -o ./dist/1ink.1ink",
            "iconv -f UTF-8 -t UTF-16 ./build/index.html -o ./build/1ink.1ink",
        )

    # UTF-16 bench marker nested path
    if "utf_benchmark/dist/utf8-control" in src and "iconv" in src:
        src = re.sub(
            r"!cd /content/build_space/\{PROJECT_NAME\}/utf_benchmark/dist/utf8-control && iconv -f UTF-8 -t UTF-16 \./dist/utf8-control/index\.html -o \./dist/utf8-control/1ink\.1ink",
            "!cd /content/build_space/{PROJECT_NAME}/utf_benchmark/dist/utf8-control && iconv -f UTF-8 -t UTF-16 ./index.html -o ./1ink.1ink",
            src,
        )

    # supertonic fixes
    if 'PROJECT_NAME = "supertonic-tts"' in src:
        src = src.replace(
            "!git clone GIT_REPO /content/build_space/{PROJECT_NAME}\n",
            "",
        )
        src = src.replace(
            "/content/build_space/supertonic-TTS/assets",
            "/content/build_space/supertonic-tts/assets",
        )

    return src


def fix_glm_cell(src: str) -> str:
    if "Install GLM" not in src:
        return src
    return """# @title 🛠️ Install GLM
!sudo apt-get install -y libglew-dev zzip-zlib-config

# GLM is header-only; clone for include path
!rm -rf /content/build_space/glm
!git clone --depth 1 https://github.com/g-truc/glm.git /content/build_space/glm
print("✅ GLM headers available at /content/build_space/glm")
"""


def fix_assimp_cell(src: str) -> str:
    if "Install assimp" not in src:
        return src
    return """# @title 🛠️ Install assimp
!sudo apt-get install -y zzip-zlib-config
!source /content/build_space/emsdk/emsdk_env.sh
!rm -rf /content/build_space/assimp
!git clone --depth 1 https://github.com/assimp/assimp.git /content/build_space/assimp
!mkdir -p /content/build_space/assimp/build
!cd /content/build_space/assimp/build && emcmake cmake .. \\
        -DCMAKE_BUILD_TYPE=Release \\
        -DASSIMP_BUILD_TESTS=OFF \\
        -DASSIMP_BUILD_ASSIMP_TOOLS=OFF \\
        -DASSIMP_BUILD_SAMPLES=OFF \\
        -DASSIMP_NO_EXPORT=ON \\
        -DASSIMP_BUILD_ZLIB=ON

!cd /content/build_space/assimp/build && emmake make -j$(nproc)
"""


def fix_ram_cell(src: str) -> str:
    if "Initialize RAM Drive" not in src:
        return src
    return src.replace(
        "# 1. Setup RAM Drive for speed (4GB)\n"
        "if not os.path.exists(\"/content/build_space\"):\n"
        "  !sudo mkdir /content/build_space\n"
        "  !sudo mount -t ramfs -o size=4096M ramfs /content/build_space\n"
        "  !sudo chmod 0777 -R /content/build_space\n"
        "  print(\"✅ RAM Drive mounted at /content/build_space\")\n"
        "\n"
        "# 2. Install Generic Build Tools\n"
        "print(\"⬇️ Installing Base Build Tools (CMake, Ninja, Zip)...\")\n"
        "!sudo apt-get update -qq\n"
        "!sudo apt install aptitude -y\n"
        "!sudo aptitude install -y -q build-essential cmake ninja-build unzip git curl wget python3-pip\n"
        "!sudo aptitude install -y git make libsdl2-dev fontconfig\n",
        "# 1. Setup RAM Drive (default 6GB; override with RAM_DRIVE_MB env var)\n"
        "RAM_MB = int(os.environ.get('RAM_DRIVE_MB', '6144'))\n"
        "if not os.path.exists(\"/content/build_space\"):\n"
        "  !sudo mkdir /content/build_space\n"
        f"  !sudo mount -t ramfs -o size={{RAM_MB}}M ramfs /content/build_space\n"
        "  !sudo chmod 0777 -R /content/build_space\n"
        "  print(f\"✅ RAM Drive mounted at /content/build_space ({RAM_MB} MB)\")\n"
        "\n"
        "# 2. Install Generic Build Tools\n"
        "print(\"⬇️ Installing Base Build Tools (CMake, Ninja, Zip)...\")\n"
        "!sudo apt-get update -qq\n"
        "!sudo apt-get install -y build-essential cmake ninja-build unzip git curl wget python3-pip\n"
        "!sudo apt-get install -y make libsdl2-dev fontconfig\n",
    )


def fix_chromashift_deploy(src: str) -> str:
    if 'PROJECT_NAME = "chromashift"' not in src:
        return src
    return src.replace(
        "!export DEPLOY_USER=ford442 && export DEPLOY_PASS=GoogleBez12! && python3 deploy.py",
        "!python3 deploy.py  # DEPLOY_USER / DEPLOY_PASS from Colab secrets",
    )


def ensure_paramiko_import(src: str) -> str:
    if "paramiko" in src and "import os" not in src.split("import paramiko")[0]:
        return "import os\n" + src
    if "os.environ.get(\"DEPLOY_PASS\"" in src and "import os" not in src:
        return "import os\n" + src
    return src


def main() -> int:
    with open(NOTEBOOK_PATH, encoding="utf-8") as f:
        nb = json.load(f)

    converted = 0
    helper_inserted = any(
        "Build & Deploy Helpers" in cell_source(c) for c in nb["cells"]
    )

    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            # Insert helper after BUILD markdown
            if (
                not helper_inserted
                and cell["cell_type"] == "markdown"
                and cell_source(cell).strip() == "# BUILD 🔨"
            ):
                helper_cell = {
                    "cell_type": "code",
                    "metadata": {"cellView": "form", "id": "builder_helpers_cell"},
                    "source": [],
                    "execution_count": None,
                    "outputs": [],
                }
                set_cell_source(helper_cell, HELPER_CELL)
                nb["cells"].insert(i + 1, helper_cell)
                helper_inserted = True
            continue

        src = cell_source(cell)

        # Secrets cell (first token cell)
        if src.startswith("# @title token") or src.startswith("# @title 🔑"):
            set_cell_source(cell, SECRETS_CELL)
            continue

        if "Initialize RAM Drive" in src:
            set_cell_source(cell, fix_ram_cell(src))
            continue

        if "Build & Deploy Helpers" in src:
            set_cell_source(cell, HELPER_CELL)
            continue

        if "Install GLM" in src:
            set_cell_source(cell, fix_glm_cell(src))
            continue

        if "Install assimp" in src:
            set_cell_source(cell, fix_assimp_cell(src))
            continue

        src = apply_global_fixes(src)
        src = fix_chromashift_deploy(src)
        src = ensure_paramiko_import(src)

        title, project = extract_title_and_project(src)
        if is_convertible_standard(src, project):
            opts = STANDARD_PROJECTS.get(project, {})
            # Detect branch from source if not in opts
            if "branch" not in opts:
                branch_m = re.search(r"!git checkout (\S+)", src)
                if branch_m and branch_m.group(1) not in ("main", "#!git"):
                    opts = {**opts, "branch": branch_m.group(1)}
            if "USE_EMSDK = True" in src:
                opts = {**opts, "use_emsdk": True}
            if 'html_file_path = f\'{target_dir}/out/index.html\'' in src:
                opts = {**opts, "html_subpath": "out/index.html"}
            elif 'html_file_path = f\'{target_dir}/build/index.html\'' in src:
                opts = {**opts, "html_subpath": "build/index.html"}
            elif 'html_file_path = f\'{target_dir}/build/web/index.html\'' in src:
                opts = {**opts, "html_subpath": "build/web/index.html"}
            if (
                'deploy_old.py' in src
                and re.search(r'^!python3 deploy_old\.py', src, re.M)
            ):
                opts = {**opts, "deploy_script": "deploy_old.py"}

            new_src = make_standard_cell(title or project, project, opts)
            set_cell_source(cell, new_src)
            converted += 1
        else:
            set_cell_source(cell, src)

    if not helper_inserted:
        # Fallback: insert before first project cell
        for i, cell in enumerate(nb["cells"]):
            if "# BUILD" in cell_source(cell):
                helper_cell = {
                    "cell_type": "code",
                    "metadata": {"cellView": "form", "id": "builder_helpers_cell"},
                    "source": [],
                    "execution_count": None,
                    "outputs": [],
                }
                set_cell_source(helper_cell, HELPER_CELL)
                nb["cells"].insert(i + 1, helper_cell)
                helper_inserted = True
                break

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✅ Notebook updated: helper inserted={helper_inserted}, standard cells converted={converted}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
