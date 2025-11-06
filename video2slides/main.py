"""CLI interface for Video2Slides using Typer."""

import os
from pathlib import Path

import typer
from eliot import start_action

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
        help="Path to output PPTX file (default: <video_name>.pptx in output-dir or current directory)",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        help="Directory for output PPTX file (default: current directory)",
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
    use_gpu: bool = typer.Option(
        True,
        "--gpu/--no-gpu",
        help="Use GPU acceleration if available (default: True, will fallback to CPU if not available)",
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

        # Specify output directory
        video2slides input_video.mp4 --output-dir ./presentations

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
        video_path_abs = str(video.resolve())
        
        # Determine output path
        if output:
            output_str = str(output)
            output_path_obj = Path(output_str)
            # If output is a directory or ends with /, treat as directory
            if (
                output_str.endswith("/")
                or output_str.endswith("\\")
                or (output_path_obj.exists() and output_path_obj.is_dir())
            ):
                # Output is a directory - use video name in that directory
                base_dir = output_path_obj.resolve()
                video_stem = Path(video_path_abs).stem
                sanitized_stem = Video2Slides._sanitize_filename(video_stem)
                output_path = str(base_dir / f"{sanitized_stem}.pptx")
            else:
                # Output is a file path
                output_path_obj = Path(output_str)
                if output_dir:
                    # If output-dir is set and output is relative, resolve relative to output_dir
                    if not output_path_obj.is_absolute():
                        output_path = str(Path(output_dir).resolve() / output_path_obj)
                    else:
                        output_path = str(output_path_obj.resolve())
                else:
                    output_path = str(output_path_obj.resolve())
        else:
            # No output specified - use video name in output_dir or current directory
            base_dir = Path(output_dir).resolve() if output_dir else Path.cwd()
            video_stem = Path(video_path_abs).stem
            sanitized_stem = Video2Slides._sanitize_filename(video_stem)
            output_path = str(base_dir / f"{sanitized_stem}.pptx")
        
        converter = Video2Slides(
            video_path_abs,
            output_path,
            interval,
            keep_aspect_ratio=keep_aspect,
            similarity_threshold=similarity,
            ignore_corners=ignore_corners,
            corner_size_percent=corner_size,
            use_gpu=use_gpu,
        )
        pptx_path_abs = Path(converter.output_path).absolute()

        if not verbose:
            typer.echo(f"🎬 Video: {video_path_abs}")
            typer.echo(f"📊 Output: {pptx_path_abs}")
            typer.echo(f"⏱️  Frame interval: {interval} second(s)")
            typer.echo(f"🎯 Similarity threshold: {similarity}")
            
            # Display GPU status
            if converter.gpu_accelerator and converter.gpu_accelerator.use_gpu:
                typer.echo("⚡ GPU acceleration: Enabled (CUDA)")
            else:
                typer.echo("💻 GPU acceleration: Disabled (CPU only)")
            
            if keep_aspect:
                typer.echo("📐 Maintaining aspect ratio: Yes")
            if ignore_corners:
                typer.echo(f"🔲 Ignoring corners: Yes ({corner_size * 100:.0f}% of frame)")

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

        typer.echo(f"✅ Conversion completed successfully: {Path(converter.output_path).absolute()}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def youtube(
    url: str = typer.Argument(
        ...,
        help="YouTube video URL",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to output PPTX file (default: <video_title>.pptx in output-dir or current directory)",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        help="Directory for downloading video and output PPTX file (default: current directory)",
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
        0.75,
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
    use_gpu: bool = typer.Option(
        True,
        "--gpu/--no-gpu",
        help="Use GPU acceleration if available (default: True, will fallback to CPU if not available)",
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
    keep_video: bool = typer.Option(
        True,
        "--keep-video/--delete-video",
        help="Keep (default) or delete downloaded video file after conversion",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force re-download even if video already exists",
    ),
) -> None:
    """
    Download a YouTube video and convert it to a PowerPoint presentation in one go.

    Examples:

        # Download and convert in one command
        video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0

        # Extract 1 frame every 2 seconds
        video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 -i 2

        # Keep aspect ratio and specify output
        video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 -k -o presentation.pptx

        # Use output directory for both video and PPTX
        video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 --output-dir ./downloads

        # Delete the downloaded video file after conversion (by default videos are kept)
        video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 --delete-video
        
        # Force re-download even if video already exists
        video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 --force
    """
    try:
        import yt_dlp  # type: ignore[import-untyped]
    except ImportError:
        typer.echo(
            "❌ yt-dlp is required for YouTube downloads but could not be imported.",
            err=True,
        )
        typer.echo("   Please reinstall video2slides: pip install video2slides", err=True)
        raise typer.Exit(code=1)

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
            typer.echo(f"📥 Downloading YouTube video: {url}")

        # Determine base directory for both video and PPTX
        base_dir = Path(output_dir).resolve() if output_dir else Path.cwd()

        # Download the video
        video_path = _download_youtube_video(
            url,
            base_dir,
            verbose=verbose,
            force=force,
        )

        video_path_abs = Path(video_path).absolute()

        # Determine output path
        if output:
            output_str = str(output)
            output_path_obj = Path(output_str)
            # If output is a directory or ends with /, treat as directory
            if (
                output_str.endswith("/")
                or output_str.endswith("\\")
                or (output_path_obj.exists() and output_path_obj.is_dir())
            ):
                # Output is a directory - use video name in that directory
                video_stem = Path(video_path).stem
                sanitized_stem = Video2Slides._sanitize_filename(video_stem)
                if output_path_obj.is_absolute():
                    output_path = str(output_path_obj.resolve() / f"{sanitized_stem}.pptx")
                else:
                    output_path = str(base_dir / output_path_obj / f"{sanitized_stem}.pptx")
            else:
                # Output is a file path
                if output_path_obj.is_absolute():
                    output_path = str(output_path_obj.resolve())
                else:
                    # Relative path - resolve relative to output_dir
                    output_path = str(base_dir / output_path_obj)
        else:
            # No output specified - use video name in output_dir or current directory
            video_stem = Path(video_path).stem
            sanitized_stem = Video2Slides._sanitize_filename(video_stem)
            output_path = str(base_dir / f"{sanitized_stem}.pptx")

        converter = Video2Slides(
            str(video_path_abs),
            output_path,
            interval,
            keep_aspect_ratio=keep_aspect,
            similarity_threshold=similarity,
            ignore_corners=ignore_corners,
            corner_size_percent=corner_size,
            use_gpu=use_gpu,
        )
        pptx_path_abs = Path(converter.output_path).absolute()

        if not verbose:
            typer.echo(f"✅ Downloaded: {video_path_abs}")
            typer.echo(f"🎬 Video: {video_path_abs}")
            typer.echo(f"📊 Output: {pptx_path_abs}")
            typer.echo(f"⏱️  Frame interval: {interval} second(s)")
            typer.echo(f"🎯 Similarity threshold: {similarity}")
            
            # Display GPU status
            if converter.gpu_accelerator and converter.gpu_accelerator.use_gpu:
                typer.echo("⚡ GPU acceleration: Enabled (CUDA)")
            else:
                typer.echo("💻 GPU acceleration: Disabled (CPU only)")
            
            if keep_aspect:
                typer.echo("📐 Maintaining aspect ratio: Yes")
            if ignore_corners:
                typer.echo(f"🔲 Ignoring corners: Yes ({corner_size * 100:.0f}% of frame)")

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

        # Optionally remove downloaded video (only if user explicitly requested deletion)
        if not keep_video and video_path and os.path.exists(video_path):
            os.remove(video_path)
            if not verbose:
                typer.echo(f"🗑️  Removed downloaded video: {os.path.basename(video_path)}")

        typer.echo(f"✅ Conversion completed successfully: {Path(converter.output_path).absolute()}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(code=1) from e


def _download_youtube_video(url: str, output_dir: Path, verbose: bool = False, force: bool = False) -> str:
    """
    Download a YouTube video using yt-dlp.

    Args:
        url: YouTube video URL
        output_dir: Directory to save the downloaded video
        verbose: Whether to show verbose output
        force: Force re-download even if video already exists

    Returns:
        Path to the downloaded video file
    """
    import yt_dlp  # type: ignore[import-untyped]

    with start_action(action_type="download_youtube_video", video_url=url):
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
            "quiet": not verbose,
            "no_warnings": verbose,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)

            # Check if file already exists
            if os.path.exists(filename) and not force:
                if not verbose:
                    typer.echo(f"✅ Video already exists, using existing file: {os.path.basename(filename)}")
                return filename

            # Download if not exists or force is True
            if force and os.path.exists(filename):
                if not verbose:
                    typer.echo(f"🔄 Force re-downloading: {os.path.basename(filename)}")
            elif not verbose:
                typer.echo(f"📥 Downloading to: {os.path.basename(filename)}")
            ydl.extract_info(url, download=True)

        return filename


if __name__ == "__main__":
    app()
