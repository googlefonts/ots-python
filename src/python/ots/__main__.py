import sys
import ots
import argparse


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="ots",
        description=(
            "command-line interface for the OpenType Sanitizer\n\n"
            "positional arguments:\n"
            "  font_file       the input font file\n"
            "  dest_font_file  optional destination file\n"
            "  font_index      select font in OpenType Collections\n"
        ),
        usage="ots [-h] [--version] font_file [dest_font_file] [font_index]",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=ots.__version__)
    _, args = parser.parse_known_args(args)
    if args:
        return ots.sanitize(*args)
    else:
        parser.print_usage()


if __name__ == "__main__":
    sys.exit(main())
