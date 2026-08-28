from PIL import Image
from pathlib import Path

# App Store Connect accepted dimensions
ACCEPTED_DIMENSIONS = [
    # iphone 6.5 pol
    (1242, 2688),
    (2688, 1242),
    (1284, 2778),
    (2778, 1284),

    # ipad 13 pol
    (2064, 2752),
    (2752, 2064),
    (2048, 2732),
    (2732, 2048),
]

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def calculate_dimension_distance(current_size, target_size):
    """Calculate the distance between two dimensions."""
    width, height = current_size
    target_width, target_height = target_size

    return abs(width - target_width) + abs(height - target_height)


def find_closest_dimension(width, height):
    """Find the closest App Store Connect accepted dimension."""
    return min(
        ACCEPTED_DIMENSIONS,
        key=lambda target: calculate_dimension_distance(
            (width, height),
            target
        )
    )


def resize_image(input_path, output_folder):
    """Adjust an image to the closest accepted dimension."""
    image = Image.open(input_path).convert("RGBA")

    original_width, original_height = image.size

    target_width, target_height = find_closest_dimension(
        original_width,
        original_height
    )

    background_color = image.getpixel((0, 0))

    canvas = Image.new(
        "RGBA",
        (target_width, target_height),
        background_color
    )

    scale = min(
        target_width / original_width,
        target_height / original_height,
        1.0
    )

    if scale < 1.0:
        new_width = round(original_width * scale)
        new_height = round(original_height * scale)

        image = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
    else:
        new_width = original_width
        new_height = original_height

    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2

    canvas.alpha_composite(
        image,
        (x_offset, y_offset)
    )

    output_filename = (
        Path(input_path).stem + "_fixed.png"
    )

    output_path = output_folder / output_filename

    canvas.convert("RGB").save(
        output_path,
        "PNG",
        optimize=True
    )

    print(
        f"Done {Path(input_path).name}: "
        f"{original_width}x{original_height} "
        f"-> {target_width}x{target_height}"
    )


def main():
    input_folder = Path("images")
    output_folder = Path("fixed")

    # Create the input folder if it doesn't exist
    if not input_folder.exists():
        input_folder.mkdir(parents=True)

        print("=" * 50)
        print("Images folder created.")
        print("=" * 50)
        print()
        print("The 'images' folder did not exist, so it was")
        print("created automatically.")
        print()
        print("Please place your images inside the 'images'")
        print("folder and run the program again.")
        print()

        return

    # Create the output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)

    image_files = [
        file
        for file in input_folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not image_files:
        print("=" * 50)
        print("No images found.")
        print("=" * 50)
        print()
        print("Please place your images inside the 'images'")
        print("folder and run the program again.")
        print()

        return

    print(f"{len(image_files)} image(s) found.\n")

    for image_file in image_files:
        try:
            resize_image(image_file, output_folder)
        except Exception as error:
            print(
                f"Error processing {image_file.name}: {error}"
            )

    print("\nDone!")
    print("Fixed images are available in the 'fixed' folder.")


if __name__ == "__main__":
    main()