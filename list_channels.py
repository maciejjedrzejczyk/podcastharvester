#!/usr/bin/env python3
"""
Utility script to list available channel names from configuration files.
This helps users identify the exact channel names for the --channels parameter.
"""

import json
import argparse
from pathlib import Path


def list_channels(config_file: str, search_term: str = None):
    """List all channel names from a configuration file."""
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not isinstance(config, list):
            print("Error: Configuration file must contain a list of channels")
            return
        
        print(f"Available channels in {config_file}:")
        print("=" * 60)
        
        matching_channels = []
        
        for i, channel in enumerate(config, 1):
            channel_name = channel.get('channel_name', 'Unknown')
            url = channel.get('url', 'No URL')
            
            # Filter by search term if provided
            if search_term:
                if search_term.lower() not in channel_name.lower():
                    continue
            
            matching_channels.append(channel_name)
            print(f"{i:3d}. {channel_name}")
            print(f"     URL: {url}")
            print()
        
        print("=" * 60)
        if search_term:
            print(f"Found {len(matching_channels)} channels matching '{search_term}'")
        else:
            print(f"Total channels: {len(config)}")
        
        if matching_channels:
            print("\nTo use specific channels, copy the exact names:")
            print("--channels \"" + ",".join(matching_channels[:5]) + "\"")
            if len(matching_channels) > 5:
                print(f"... and {len(matching_channels) - 5} more")
        
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="List available channel names from configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  List all channels:
    python list_channels.py --config channels_config_full.json

  Search for specific channels:
    python list_channels.py --config channels_config_full.json --search "cold"

  List test channels:
    python list_channels.py --config test_channels.json
        """
    )
    
    parser.add_argument('--config', required=True, help='JSON configuration file')
    parser.add_argument('--search', help='Search term to filter channel names')
    
    args = parser.parse_args()
    
    list_channels(args.config, args.search)


if __name__ == "__main__":
    main()
