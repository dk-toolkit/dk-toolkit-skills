#!/bin/bash
# DK Toolkit Skills - Plugin Installer
# Installs plugins by symlinking them to ~/.claude/skills/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.claude/skills"
SPECIFIC_PLUGIN=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --plugin)
            SPECIFIC_PLUGIN="$2"
            shift 2
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --help|-h)
            echo "DK Toolkit Skills - Plugin Installer"
            echo ""
            echo "Usage:"
            echo "  ./install.sh                    Install all plugins"
            echo "  ./install.sh --plugin <name>    Install a specific plugin"
            echo "  ./install.sh --uninstall        Remove all plugin symlinks"
            echo ""
            echo "Available plugins:"
            for dir in "$SCRIPT_DIR"/*/; do
                if [ -f "$dir/plugin.json" ]; then
                    name=$(basename "$dir")
                    echo "  - $name"
                fi
            done
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create skills directory if it doesn't exist
mkdir -p "$SKILLS_DIR"

# Uninstall mode
if [ "$UNINSTALL" = true ]; then
    echo "Uninstalling DK Toolkit plugins..."
    for dir in "$SCRIPT_DIR"/*/; do
        if [ -f "$dir/plugin.json" ]; then
            name=$(basename "$dir")
            target="$SKILLS_DIR/$name"
            if [ -L "$target" ]; then
                rm "$target"
                echo "  Removed: $name"
            fi
        fi
    done
    # Remove learnings symlink
    if [ -L "$SKILLS_DIR/_learnings" ]; then
        rm "$SKILLS_DIR/_learnings"
        echo "  Removed: _learnings"
    fi
    echo "Done! All DK Toolkit plugins have been uninstalled."
    exit 0
fi

# Install mode
echo "DK Toolkit Skills - Plugin Installer"
echo "====================================="
echo ""
echo "Skills directory: $SKILLS_DIR"
echo ""

install_plugin() {
    local plugin_dir="$1"
    local name=$(basename "$plugin_dir")

    # Skip if not a valid plugin directory
    if [ ! -f "$plugin_dir/plugin.json" ]; then
        return
    fi

    local target="$SKILLS_DIR/$name"

    # Check if already installed
    if [ -L "$target" ]; then
        echo "  [skip] $name (already installed)"
        return
    elif [ -d "$target" ]; then
        echo "  [warn] $name - directory exists at $target (not a symlink, skipping)"
        return
    fi

    # Create symlink
    ln -s "$plugin_dir" "$target"
    echo "  [ok]   $name"
}

if [ -n "$SPECIFIC_PLUGIN" ]; then
    # Install specific plugin
    plugin_path="$SCRIPT_DIR/$SPECIFIC_PLUGIN"
    if [ -d "$plugin_path" ] && [ -f "$plugin_path/plugin.json" ]; then
        echo "Installing plugin: $SPECIFIC_PLUGIN"
        install_plugin "$plugin_path"
    else
        echo "Error: Plugin '$SPECIFIC_PLUGIN' not found."
        echo "Available plugins:"
        for dir in "$SCRIPT_DIR"/*/; do
            if [ -f "$dir/plugin.json" ]; then
                echo "  - $(basename "$dir")"
            fi
        done
        exit 1
    fi
else
    # Install all plugins
    echo "Installing all plugins..."
    echo ""
    for dir in "$SCRIPT_DIR"/*/; do
        install_plugin "$dir"
    done

    # Install learnings directory
    learnings_target="$SKILLS_DIR/_learnings"
    if [ -d "$SCRIPT_DIR/_learnings" ]; then
        if [ ! -L "$learnings_target" ] && [ ! -d "$learnings_target" ]; then
            ln -s "$SCRIPT_DIR/_learnings" "$learnings_target"
            echo "  [ok]   _learnings"
        else
            echo "  [skip] _learnings (already exists)"
        fi
    fi
fi

echo ""
echo "Installation complete!"
echo ""
echo "Installed plugins are now available in Claude Code."
echo "Trigger them by using relevant phrases or invoke directly with /skill-name."
