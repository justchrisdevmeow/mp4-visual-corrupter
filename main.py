import random
import sys
import os

def glitch_random(data, skip_header, intensity):
    """Random byte flips - scales with intensity"""
    file_size = len(data)
    num_corrupt = max(1, int(file_size * intensity))
    for _ in range(num_corrupt):
        pos = random.randint(skip_header, file_size - 1)
        data[pos] = random.randint(0, 255)
    return data

def glitch_bitflip(data, skip_header, intensity):
    """Bit flips at intervals - more intensity = smaller interval"""
    step = max(5, int(100 / max(intensity, 0.001)))
    for i in range(skip_header, len(data), step):
        data[i] ^= 0xFF
    return data

def glitch_shift(data, skip_header, intensity):
    """Byte shifts - more intensity = more shifts"""
    num_shifts = max(1, int(50 * intensity))
    for _ in range(num_shifts):
        shift = random.randint(1, 10)
        for i in range(skip_header, len(data) - shift, shift * 20):
            if i + shift < len(data):
                data[i], data[i + shift] = data[i + shift], data[i]
    return data

def glitch_duplicate(data, skip_header, intensity):
    """Frame duplication - more intensity = more duplicates"""
    num_dup = max(1, int(150 * intensity))
    for _ in range(num_dup):
        start = random.randint(skip_header, len(data) - 2000)
        length = random.randint(100, 800)
        chunk = data[start:start + length]
        insert_pos = random.randint(skip_header, len(data) - 1)
        for j, b in enumerate(chunk):
            if insert_pos + j < len(data):
                data[insert_pos + j] = b
    return data

def glitch_block(data, skip_header, intensity):
    """Solid color blocks - more intensity = more blocks"""
    num_blocks = max(1, int(80 * intensity))
    for _ in range(num_blocks):
        pos = random.randint(skip_header, len(data) - 2000)
        block_size = random.randint(30, 300)
        fill_byte = random.randint(0, 255)
        for i in range(block_size):
            if pos + i < len(data):
                data[pos + i] = fill_byte
    return data

def glitch_rainbow(data, skip_header, intensity):
    """Color shifting - more intensity = more frequent shifts"""
    step = max(1, int(100 / max(intensity, 0.001)))
    for i in range(skip_header, len(data)):
        if i % step == 0:
            data[i] = (data[i] + random.randint(10, 80)) % 256
    return data

def glitch_all(data, skip_header, intensity):
    """All patterns combined"""
    data = glitch_random(data, skip_header, intensity * 1.5)
    data = glitch_bitflip(data, skip_header, intensity)
    data = glitch_block(data, skip_header, intensity)
    data = glitch_shift(data, skip_header, intensity * 0.5)
    if random.random() > 0.5:
        data = glitch_duplicate(data, skip_header, intensity * 0.3)
    if random.random() > 0.7:
        data = glitch_rainbow(data, skip_header, intensity * 0.8)
    return data

def glitch_mp4(input_file, output_file, pattern="random", intensity=0.005):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    skip_header = min(65536, int(file_size * 0.1))  # Preserve headers
    
    print(f"File: {input_file}")
    print(f"Pattern: {pattern}, Intensity: {intensity*100:.2f}%")
    print(f"File size: {file_size} bytes, Skipping first {skip_header} bytes")
    
    if pattern == "random":
        data = glitch_random(data, skip_header, intensity)
    elif pattern == "bitflip":
        data = glitch_bitflip(data, skip_header, intensity)
    elif pattern == "shift":
        data = glitch_shift(data, skip_header, intensity)
    elif pattern == "duplicate":
        data = glitch_duplicate(data, skip_header, intensity)
    elif pattern == "block":
        data = glitch_block(data, skip_header, intensity)
    elif pattern == "rainbow":
        data = glitch_rainbow(data, skip_header, intensity)
    elif pattern == "all":
        data = glitch_all(data, skip_header, intensity)
    else:
        print(f"Unknown pattern '{pattern}', using random")
        data = glitch_random(data, skip_header, intensity)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity]")
        print("\nPatterns:")
        print("  random    - random byte flips (scales with intensity)")
        print("  bitflip   - regular pattern bit flips (scales)")
        print("  shift     - byte shifts (scales)")
        print("  duplicate - frame duplication (scales)")
        print("  block     - solid color blocks (scales)")
        print("  rainbow   - color shifting (scales)")
        print("  all       - everything combined")
        print("\nIntensity: 0.001 (very subtle) to 0.05 (heavy)")
        print("Default: 0.005")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "random"
    intensity = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
    
    glitch_mp4(input_file, output_file, pattern, intensity)
