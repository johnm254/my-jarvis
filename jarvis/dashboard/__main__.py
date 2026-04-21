"""Main entry point for JARVIS dashboard backend."""

import argparse
import sys

from jarvis.dashboard.app import run_server


def main():
    """Parse command-line arguments and start the dashboard server."""
    parser = argparse.ArgumentParser(
        description='JARVIS Dashboard Backend Server'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host address to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Port number (default: from configuration)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down JARVIS Dashboard Backend...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
