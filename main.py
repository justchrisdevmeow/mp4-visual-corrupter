import random
import sys
import os

def glitch_random(data, skip_header, intensity, file_size):
    # intensity now = corruptions per 100KB
    corruptions_per_kb = intensity * 10
    num_corrupt = max(1, int(file_size / 1000 * corruptions_per_kb))
    for _ in range(num_corrupt):
        pos = random.randint(skip_header, file_size - 1)
        data[pos] = random.randint(0, 255)
    return data

def glitch_bitflip(data, skip_header, intensity):
    # intensity = flips per 100KB
    step = max(50, int(5000 / max(intensity, 0.001)))
    for i in range(skip_header, len(data), step):
        data[i] ^= 0xFF
    return data

def glitch_shift(data, skip_header, intensity, file_size):
    num_shifts = max(1, int(file_size / 50000 * intensity * 50))
    for _ in range(num_shifts):
        shift = random.randint(1, 10)
        for i in range(skip_header, len(data) - shift, shift * 100):
            if i + shift < len(data):
                data[i], data[i + shift] = data[i + shift], data[i]
    return data

def glitch_duplicate(data, skip_header, intensity, file_size):
    num_dup = max(1, int(file_size / 50000 * intensity * 30))
    for _ in range(num_dup):
        start = random.randint(skip_header, len(data) - 2000)
        length = random.randint(100, 500)
        chunk = data[start:start + length]
        insert_pos = random.randint(skip_header, len(data) - 1)
        for j, b in enumerate(chunk):
            if insert_pos + j < len(data):
                data[insert_pos + j] = b
    return data

def glitch_block(data, skip_header, intensity, file_size):
    num_blocks = max(1, int(file_size / 100000 * intensity * 20))
    for _ in range(num_blocks):
        pos = random.randint(skip_header, len(data) - 2000)
        block_size = random.randint(50, 200)
        fill_byte = random.randint(0, 255)
        for i in range(block_size):
            if pos + i < len(data):
                data[pos + i] = fill_byte
    return data

def glitch_rainbow(data, skip_header, intensity):
    step = max(10, int(200 / max(intensity, 0.001)))
    for i in range(skip_header, len(data)):
        if i % step == 0:
            data[i] = (data[i] + random.randint(10, 50)) % 256
    return data

def glitch_custom(data, skip_header, intensity, patterns, file_size):
    for pattern in patterns:
        if pattern == "random":
            data = glitch_random(data, skip_header, intensity, file_size)
        elif pattern == "bitflip":
            data = glitch_bitflip(data, skip_header, intensity)
        elif pattern == "shift":
            data = glitch_shift(data, skip_header, intensity, file_size)
        elif pattern == "duplicate":
            data = glitch_duplicate(data, skip_header, intensity, file_size)
        elif pattern == "block":
            data = glitch_block(data, skip_header, intensity, file_size)
        elif pattern == "rainbow":
            data = glitch_rainbow(data, skip_header, intensity)
    return data

def glitch_mp4(input_file, output_file, pattern="random", intensity=0.5, custom_patterns=None):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    skip_header = min(65536, int(file_size * 0.1))
    
    print(f"File: {input_file}")
    print(f"Size: {file_size} bytes")
    print(f"Pattern: {pattern}, Intensity: {intensity}")
    
    if pattern == "random":
        data = glitch_random(data, skip_header, intensity, file_size)
    elif pattern == "bitflip":
        data = glitch_bitflip(data, skip_header, intensity)
    elif pattern == "shift":
        data = glitch_shift(data, skip_header, intensity, file_size)
    elif pattern == "duplicate":
        data = glitch_duplicate(data, skip_header, intensity, file_size)
    elif pattern == "block":
        data = glitch_block(data, skip_header, intensity, file_size)
    elif pattern == "rainbow":
        data = glitch_rainbow(data, skip_header, intensity)
    elif pattern == "all":
        data = glitch_all(data, skip_header, intensity, file_size)
    elif pattern == "custom" and custom_patterns:
        print(f"Custom patterns: {custom_patterns}")
        data = glitch_custom(data, skip_header, intensity, custom_patterns, file_size)
    else:
        data = glitch_random(data, skip_header, intensity, file_size)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

def glitch_all(data, skip_header, intensity, file_size):
    data = glitch_random(data, skip_header, intensity * 2, file_size)
    data = glitch_bitflip(data, skip_header, intensity * 2)
    data = glitch_block(data, skip_header, intensity * 2, file_size)
    if random.random() > 0.5:
        data = glitch_duplicate(data, skip_header, intensity, file_size)
    if random.random() > 0.7:
        data = glitch_rainbow(data, skip_header, intensity)
    return data

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity] [custom:pattern1,pattern2]")
        print("\nPatterns: random, bitflip, shift, duplicate, block, rainbow, all")
        print("  custom:block,duplicate,rainbow")
        print("\nIntensity: 0.1 to 50 (higher = more glitches)")
        print("  0.5 = very subtle")
        print("  5 = noticeable")
        print("  20 = heavy")
        print("  50 = extreme")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "random"
    intensity = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0
    
    custom_patterns = None
    if pattern.startswith("custom:"):
        custom_patterns = pattern.split(":")[1].split(",")
        pattern = "custom"
    
    glitch_mp4(input_file, output_file, pattern, intensity, custom_patterns)
