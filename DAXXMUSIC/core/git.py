import asyncio
import shlex
import os
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config
from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    """
    Runs a shell command asynchronously and returns
    (stdout, stderr, returncode, pid)
    """
    async def _run():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(_run())


def git():
    """
    Updates the bot from the upstream GitHub repository if running locally.
    Skips updates on Heroku (no .git directory).
    """
    REPO_LINK = config.UPSTREAM_REPO

    # Skip git auto-update on Heroku
    if not os.path.exists(".git"):
        LOGGER(__name__).info("No .git directory found. Skipping git auto-update on Heroku.")
        return

    # Handle private token if provided
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = REPO_LINK

    try:
        repo = Repo(".")
        LOGGER(__name__).info("Git repository found. Using VPS deployer mode.")
    except InvalidGitRepositoryError:
        LOGGER(__name__).info("No valid git repository found. Initializing new repo...")
        repo = Repo.init(".")
        try:
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        except Exception:
            origin = repo.remote("origin")

    branch_name = config.UPSTREAM_BRANCH.lower()  # ensure lowercase branch
    try:
        origin = repo.remote("origin")
        origin.fetch()
        # Create branch if not exists
        if branch_name not in repo.heads:
            repo.create_head(branch_name, origin.refs[branch_name])
        # Track upstream
        repo.heads[branch_name].set_tracking_branch(origin.refs[branch_name])
        repo.heads[branch_name].checkout(True)
        # Pull latest changes
        try:
            origin.pull(branch_name)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        LOGGER(__name__).info("Successfully fetched updates from upstream repository.")
        # Install new requirements
        install_req("pip3 install --no-cache-dir -r requirements.txt")
    except Exception as e:
        LOGGER(__name__).warning(f"Git auto-update skipped or failed: {e}")