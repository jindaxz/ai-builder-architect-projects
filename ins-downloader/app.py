import os
import shutil
import tempfile
import threading

from flask import Flask, after_this_request, jsonify, render_template, request, send_file
from instaloader import Instaloader, Profile
from instaloader.exceptions import (
    BadCredentialsException,
    ConnectionException,
    InstaloaderException,
    ProfileNotExistsException,
)


def _configure_loader() -> Instaloader:
    """
    Create a base Instaloader instance with sane defaults.
    """
    loader = Instaloader(
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        download_video_thumbnails=False,
        download_videos=False,
        download_geotags=False,
        post_metadata_txt_pattern="",
        dirname_pattern="{target}",
        filename_pattern="{shortcode}",
    )

    username = os.environ.get("INSTAGRAM_USERNAME")
    password = os.environ.get("INSTAGRAM_PASSWORD")
    if username and password:
        try:
            loader.login(username, password)
        except BadCredentialsException as error:
            raise RuntimeError(
                "Invalid INSTAGRAM_USERNAME/INSTAGRAM_PASSWORD credentials."
            ) from error

    return loader


app = Flask(__name__, static_folder="static", template_folder="templates")
loader = _configure_loader()
loader_lock = threading.Lock()


def _download_profile_archive(username: str, max_posts: int) -> tuple[str, str]:
    """
    Download up to max_posts for username and return (archive_path, temp_dir).
    """
    temp_dir = tempfile.mkdtemp(prefix="insta_")
    download_root = os.path.join(temp_dir, "downloads")

    with loader_lock:
        loader.dirname_pattern = os.path.join(download_root, "{target}")
        profile = Profile.from_username(loader.context, username)
        downloaded = 0

        for post in profile.get_posts():
            loader.download_post(post, target=profile.username)
            downloaded += 1
            if downloaded >= max_posts:
                break

    if downloaded == 0:
        raise InstaloaderException("No posts available for this profile.")

    archive_base = os.path.join(temp_dir, f"{profile.username}_images")
    archive_path = shutil.make_archive(
        archive_base,
        "zip",
        root_dir=os.path.join(download_root, profile.username),
    )

    return archive_path, temp_dir


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/download")
def download():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    max_posts = payload.get("max_posts", 12)

    if not username:
        return jsonify({"error": "Instagram username is required."}), 400

    try:
        max_posts = int(max_posts)
    except (TypeError, ValueError):
        return jsonify({"error": "max_posts must be a number."}), 400

    if max_posts < 1 or max_posts > 50:
        return jsonify({"error": "max_posts must be between 1 and 50."}), 400

    try:
        archive_path, temp_dir = _download_profile_archive(username, max_posts)
    except ProfileNotExistsException:
        return jsonify({"error": "This profile does not exist or is private."}), 404
    except ConnectionException:
        return jsonify({"error": "Instagram request failed. Try again later."}), 502
    except InstaloaderException as error:
        return jsonify({"error": str(error)}), 400

    @after_this_request
    def cleanup(response):
        shutil.rmtree(temp_dir, ignore_errors=True)
        return response

    download_name = os.path.basename(archive_path)
    return send_file(
        archive_path,
        as_attachment=True,
        download_name=download_name,
        mimetype="application/zip",
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
