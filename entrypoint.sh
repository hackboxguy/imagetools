#!/bin/sh

# Function to show usage
show_usage() {
    echo "Usage: docker run --rm -v \$(pwd)/data:/data gamut-analyzer COMMAND [ARGS]"
    echo ""
    echo "Available commands:"
    echo "  analyze-2d-gamut    - Run 2D gamut analysis"
    echo "      --inputcsv=FILE --reference=TYPE --output=FILE"
    echo ""
    echo "  analyze-3d-gamut    - Run 3D gamut analysis"
    echo "      --inputcsv=FILE --reference=TYPE --output=FILE"
    echo ""
    echo "  analyze-uniformity  - Run uniformity analysis"
    echo "      --inputcsv=FILE --zones=NUMBER --output=FILE"
}

# Check if a command was provided
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Get the command (first argument)
CMD="$1"
shift  # Remove the command from the arguments

# Execute the appropriate script based on the command
case "$CMD" in
    "analyze-2d-gamut")
        exec /usr/local/bin/analyze-2d-gamut.py "$@"
        ;;
    "analyze-3d-gamut")
        exec /usr/local/bin/analyze-3d-gamut.py "$@"
        ;;
    "analyze-uniformity")
        exec /usr/local/bin/analyze-uniformity.py "$@"
        ;;
    "--help"|"-h")
        show_usage
        exit 0
        ;;
    *)
        echo "Error: Unknown command '$CMD'"
        show_usage
        exit 1
        ;;
esac
