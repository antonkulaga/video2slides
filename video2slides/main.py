"""CLI interface for Video2Slides using Typer."""

from pathlib import Path

import typer

from video2slides.converter import Video2Slides

app = typer.Typer(
    name="video2slides",
    help="Convert video files to PowerPoint presentations",
    add_completion=False,
)


@app.command()
def convert(
    video: Path = typer.Argument(
        ...,
        help="Path to input video file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to output PPTX file (default: <video_name>_slides.pptx in current directory)",
    ),
    interval: int = typer.Option(
        1,
        "--interval",
        "-i",
        help="Frame extraction interval in seconds",
        min=1,
    ),
    keep_aspect: bool = typer.Option(
        False,
        "--keep-aspect",
        "-k",
        help="Maintain video aspect ratio in slides (otherwise stretch to fill)",
    ),
    similarity: float = typer.Option(
        0.95,
        "--similarity",
        "-s",
        help="Similarity threshold (0-1) for detecting slide changes (higher = more strict, fewer frames)",
        min=0.0,
        max=1.0,
    ),
    ignore_corners: bool = typer.Option(
        True,
        "--ignore-corners/--no-ignore-corners",
        help="Ignore corner regions when comparing frames (useful for speaker video)",
    ),
    corner_size: float = typer.Option(
        0.15,
        "--corner-size",
        help="Size of corners to ignore as percentage (0-1) when ignore-corners is enabled",
        min=0.0,
        max=0.5,
    ),
    log_file: Path | None = typer.Option(
        None,
        "--log-file",
        "-l",
        help="Path to eliot JSON log file (optional)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed JSON logging to stdout",
    ),
) -> None:
    """
    Convert a video file to a PowerPoint presentation.

    Examples:

        # Basic usage (extract 1 frame per second, filter duplicates)
        video2slides input_video.mp4

        # Extract 1 frame every 5 seconds with aspect ratio preserved
        video2slides input_video.mp4 -i 5 -k -o output.pptx

        # More strict similarity (fewer frames, only major changes)
        video2slides input_video.mp4 -s 0.98

        # Less strict similarity (more frames, detect subtle changes)
        video2slides input_video.mp4 -s 0.90

        # Disable corner filtering (compare entire frame including speaker)
        video2slides input_video.mp4 --no-ignore-corners

        # With detailed logging to file
        video2slides input_video.mp4 -l conversion.log
    """
    # Setup eliot logging only if requested
    if log_file:
        from eliot import to_file

        to_file(open(str(log_file), "w"))
    elif verbose:
        import sys

        from eliot import FileDestination, add_destinations

        add_destinations(FileDestination(file=sys.stdout))

    try:
        if not verbose:
            typer.echo(f"🎬 Converting video: {video.name}")
            typer.echo(f"⏱️  Frame interval: {interval} second(s)")
            typer.echo(f"🎯 Similarity threshold: {similarity}")
            if keep_aspect:
                typer.echo("📐 Maintaining aspect ratio: Yes")
            if ignore_corners:
                typer.echo(f"🔲 Ignoring corners: Yes ({corner_size * 100:.0f}% of frame)")

        converter = Video2Slides(
            str(video),
            str(output) if output else None,
            interval,
            keep_aspect_ratio=keep_aspect,
            similarity_threshold=similarity,
            ignore_corners=ignore_corners,
            corner_size_percent=corner_size,
        )

        if not verbose:
            typer.echo("📹 Extracting frames...")

        converter.extract_frames()

        if not verbose:
            typer.echo(f"✅ Extracted {len(converter.frames)} unique frames")
            typer.echo("📊 Generating PowerPoint presentation...")

        converter.generate_ppt()

        if not verbose:
            typer.echo("🧹 Cleaning up temporary files...")

        converter.cleanup()

        typer.echo(f"✅ Conversion completed successfully: {converter.output_path}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
