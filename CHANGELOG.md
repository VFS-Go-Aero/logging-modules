# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-03-28
### Added
- Project created
- `drone_logger/drone_logger_node.py` added as initial ROS node stub
- `drone_logger/package.xml`, `setup.py`, `setup.cfg` added for package setup
- `drone_logger/drone_logger/__init__.py` added
- New `drone_logger/logger.py` implementing Logger class for drone data logging and tracking with structured timestamped dataset entries.
- Replaced node-based logger runtime in `drone_logger_node.py` with class-based centralized logging.
- Added package dependency declarations in `drone_logger/package.xml` for enhanced integration and functionality.

### Changed
- `drone_logger/drone_logger/logger.py` introduced as primary logging interface.
- `drone_logger/drone_logger/drone_logger_node.py` trimmed from old ad-hoc implementation.

### Removed
- Legacy `drone_logger_node.py` behavior superseded by new Logger class.
