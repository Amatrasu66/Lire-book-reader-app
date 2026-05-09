"""
app.py — Flask application entry point for Book Listener backend.

Responsibilities:
  - Create and configure the Flask app instance.
  - Register blueprints.
  - Enable CORS.
  - Ensure storage directories exist.
  - Register global error handlers.
  - Run the development server.
"""

import logging

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

import config
from upload_routes import upload_bp
from file_manager import ensure_directories


# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Application factory ────────────────────────────────────────────────────────

def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Using an app factory (rather than a module-level `app = Flask(...)`) makes
    the codebase testable and ready for multi-environment configs.
    """
    app = Flask(__name__, static_folder=config.STATIC_DIR)

    # ── Config ─────────────────────────────────────────────────────────────────
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"]      = config.UPLOAD_DIR

    # ── CORS ───────────────────────────────────────────────────────────────────
    # In production, replace "*" with your frontend's exact origin.
    # E.g.: CORS(app, origins=["https://booklistener.app"])
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ── Blueprints ─────────────────────────────────────────────────────────────
    app.register_blueprint(upload_bp)

    # ── Filesystem bootstrap ───────────────────────────────────────────────────
    ensure_directories()

    # ── Global error handlers ──────────────────────────────────────────────────

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(exc):
        max_mb = config.MAX_CONTENT_LENGTH // (1024 * 1024)
        return jsonify(
            {
                "success": False,
                "error": f"File exceeds the maximum allowed size of {max_mb} MB.",
            }
        ), 413

    @app.errorhandler(404)
    def handle_not_found(exc):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(exc):
        return jsonify({"success": False, "error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def handle_internal_error(exc):
        logger.exception("Unhandled server error: %s", exc)
        return jsonify({"success": False, "error": "Internal server error."}), 500

    logger.info("Book Listener API ready on http://%s:%d", config.HOST, config.PORT)
    return app


# ── Entry point ────────────────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
