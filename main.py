import random
import sys
import os

def glitch_random(data, skip_header, intensity):
    """Random byte flips"""
    file_size = len(data)
    num_corrupt = max(1, int(file_size * intensity))
    for _ in range(num_corrupt):
        pos = random.randint(skip_header, file_size - 1)
        data[pos] = random.randint(0, 255)
    return data

def glitch_bitflip(data, skip_header, step=47):
    """Flip bits at regular intervals"""
    for i in range(skip_header, len(data), step):
        data[i] ^= 0xFF
    return data

def glitch_shift(data, skip_header, shift=1):
    """Shift bytes (inserts/deletes, changes timing)"""
    for i in range(skip_header, len(data) - shift, shift * 100):
        if i + shift < len(data):
            data[i], data[i + shift] = data[i + shift], data[i]
    return data

def glitch_duplicate(data, skip_header):
    """Duplicate random chunks (frame repeats)"""
    for _ in range(50):
        start = random.randint(skip_header, len(data) - 1000)
        length = random.randint(100, 500)
        chunk = data[start:start + length]
        insert_pos = random.randint(skip_header, len(data) - 1)
        for j, b in enumerate(chunk):
            if insert_pos + j < len(data):
                data[insert_pos + j] = b
    return data

def glitch_block(data, skip_header):
    """Corrupt blocks of data (square artifacts)"""
    for _ in range(20):
        pos = random.randint(skip_header, len(data) - 1000)
        block_size = random.randint(50, 200)
        fill_byte = random.randint(0, 255)
        for i in range(block_size):
            if pos + i < len(data):
                data[pos + i] = fill_byte
    return data

def glitch_rainbow(data, skip_header):
    """Color shift by modifying byte patterns"""
    for i in range(skip_header, len(data)):
        if i % 3 == 0:
            data[i] = (data[i] + 50) % 256
    return data

def glitch_all(data, skip_header, intensity):
    """Apply all glitch patterns"""
    data = glitch_random(data, skip_header, intensity * 0.5)
    data = glitch_bitflip(data, skip_header, random.randint(30, 100))
    data = glitch_block(data, skip_header)
    if random.random() > 0.5:
        data = glitch_duplicate(data, skip_header)
    return data

def glitch_mp4(input_file, output_file, pattern="random", intensity=0.005):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    skip_header = min(65536, int(file_size * 0.1))  # Preserve headers
    
    print(f"File size: {file_size} bytes")
    print(f"Pattern: {pattern}, Intensity: {intensity*100}%")
    
    if pattern == "random":
        data = glitch_random(data, skip_header, intensity)
    elif pattern == "bitflip":
        data = glitch_bitflip(data, skip_header)
    elif pattern == "shift":
        data = glitch_shift(data, skip_header)
    elif pattern == "duplicate":
        data = glitch_duplicate(data, skip_header)
    elif pattern == "block":
        data = glitch_block(data, skip_header)
    elif pattern == "rainbow":
        data = glitch_rainbow(data, skip_header)
    elif pattern == "all":
        data = glitch_all(data, skip_header, intensity)
    else:
        print("Unknown pattern, using random")
        data = glitch_random(data, skip_header, intensity)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity]")
        print("\nPatterns:")
        print("  random    - random byte flips")
        print("  bitflip   - regular pattern bit flips")
        print("  shift     - byte shifts (warp effect)")
        print("  duplicate - frame duplication (stutter)")
        print("  block     - solid color blocks")
        print("  rainbow   - color shifting")
        print("  all       - everything combined")
        print("\nIntensity values (0.0001 to 0.05):")
        print("  0.0001 = 1 corruption per 10MB (extremely subtle)")
        print("  0.0005 = very light, occasional single glitch")
        print("  0.001 = light glitches (few per minute)")
        print("  0.002 = noticeable glitches")
        print("  0.003 = moderate glitches")
        print("  0.005 = default, heavy glitches")
        print("  0.008 = very heavy, frequent artifacts")
        print("  0.01 = extreme, major corruption")
        print("  0.02 = rave party, barely watchable")
        print("  0.05 = maximum, may not play")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "random"
    intensity = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
    
    glitch_mp4(input_file, output_file, pattern, intensity)
